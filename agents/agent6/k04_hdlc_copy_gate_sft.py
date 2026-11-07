"""H17 selected spool ACK-2 HDLC-style bit-stuffing copier hypothesis.

Source-grounded clue: N22 crew note compares a printer to a fax. T.30 fax
protocols use bit-stuffed HDLC for control transport. The observed selected
ACK2 16-byte buffer has no six-one run, compatible with HDLC-stuffed bytes,
whereas 90 of the other 132 original printer packets have one or more.

Agent1 previously rejected a *producer-wide HDLC framed packet* assumption from
four other intact late records. Here only the disputed selected **physical
copy** is modeled as optionally using a copier-specific de/stuff path. That
is a separately target-tested, narrower and still historically unverified case.

Explore an explicit start-of-frame HDLC de-stuff or inverse re-stuff, rather
than arbitrary 1-bit slips. The missing physical 128-bit coupon is padded with
all possible trailing bits when de-stuffing removes <=10 bits. This is a
speculative copier-only transformation, not an authentic fax-code assertion.
"""
import hashlib
import json
import re
from pathlib import Path
from collections import Counter
from itertools import product

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / 'evidence/print/spool-reconstruction.log'
ROUTE = ROOT / 'evidence/recovery-routing.json'
ACCEPT = ROOT / 'acceptance.json'
NOTE = ROOT / 'evidence/crew/noticeboard-and-desk-notes.txt'
NOTE_SHA = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
SRC_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
ROUTE_SHA = 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5'
WANT = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'


def bitstring(src: bytes, order: str, reverse: bool):
    return ''.join(f'{v:08b}'[::1 if order == 'msb' else -1]
                   for v in (src[::-1] if reverse else src))


def bytepack(bits: str, order: str, reverse: bool):
    if len(bits) != 128:
        raise ValueError(len(bits))
    raw = bytes(int(bits[i:i+8][::1 if order=='msb' else -1], 2)
                for i in range(0, 128, 8))
    return raw[::-1] if reverse else raw


def invert_bits(s):
    return s.translate(str.maketrans('01','10'))


def unstuff(s, initial_ones):
    out=[]
    n=initial_ones
    for x in s:
        if n == 5:
            if x != '0':
                return None
            n = 0
            continue
        out.append(x)
        n = n+1 if x == '1' else 0
    return ''.join(out)


def stuff(s, initial_ones):
    out=[]
    n=initial_ones
    for x in s:
        if n == 5:
            out.append('0')
            n=0
        out.append(x)
        n=n+1 if x=='1' else 0
    return ''.join(out)


def candidate_codes(raw):
    for order,reverse,polarity,stage in product(('msb','lsb'),(False,True), (False,True), ('unstuff','restuff')):
        s=bitstring(raw,order,reverse)
        if polarity:
            s=invert_bits(s)
        for initial_ones in range(5):
            v=unstuff(s,initial_ones) if stage=='unstuff' else stuff(s,initial_ones)
            if v is None:
                continue
            if len(v)<=128:
                missing=128-len(v)
                if missing>10:
                    continue
                candidates=(v+f'{i:0{missing}b}' if missing else v
                            for i in range(1<<missing))
            else:
                candidates=(v[:128],)
            for b in candidates:
                if polarity:
                    b=invert_bits(b)
                yield (order, reverse, polarity, stage,initial_ones),bytepack(b,order,reverse)


def passes(coupon, mask, wanted):
    return hashlib.sha256(bytes(x^y for x,y in zip(coupon,mask))).hexdigest()==wanted


def main():
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest()==NOTE_SHA
    assert "printer has spent another morning thinking it is a fax machine" in NOTE.read_text()
    assert hashlib.sha256(SPOOL.read_bytes()).hexdigest()==SRC_SHA
    assert hashlib.sha256(ROUTE.read_bytes()).hexdigest()==ROUTE_SHA
    route=json.loads(ROUTE.read_text())
    mask=bytes.fromhex(route['K04']['masked_component'])
    target=json.loads(ACCEPT.read_text())['slot_sha256']['K04']
    assert target==WANT
    rows=[dict(re.findall(r'(\w+)=([^\s]+)',line)) for line in SPOOL.read_text().splitlines() if 'PAYLOAD=' in line]
    assert len(rows)==133
    sel=[r for r in rows if r['JOB']=='PS-261003-0417' and r['CLASS']=='RECOVER' and r['STATE']=='ACK' and r['ATTEMPT']=='2']
    assert len(sel)==1
    c=bytes.fromhex(sel[0]['PAYLOAD'])
    assert c.hex().upper()=='A9A9DC5731A5E2AE879C47215C2559D5'
    others=[bytes.fromhex(r['PAYLOAD']) for r in rows if r is not sel[0]]
    forbidden=sum('111111' in bitstring(b,'msb',False) for b in others)
    assert forbidden==90
    print('SOURCE_FRAMING_CONTROL 132 intact rows containing unstuffed-forbidden 6-one MSB run:',forbidden)
    print('SELECTED_COPY_FIVE_OR_SIX_ONES', sum('11111' in bitstring(c,order,False) for order in ('msb','lsb')))
    plant=bytes.fromhex('12D0F2FFC0FF0EAB9AE6C77E514E20BA')
    stream=stuff(bitstring(plant,'lsb',False),0)
    assert len(stream)>128
    copied=bytepack(stream[:128],'lsb',False)
    synthetic_digest=hashlib.sha256(bytes(x^y for x,y in zip(plant,mask))).hexdigest()
    pos=sum(passes(x,mask,synthetic_digest) for _,x in candidate_codes(copied))
    assert pos>=1
    print('SYNTHETIC_FULL_PHYSICAL_COUPON_POSITIVES',pos)
    scores=Counter()
    checked=set()
    hits=[]
    for stage in ('copy','mask','reduced'):
        initial={'copy':c,'mask':mask,'reduced':bytes(x^y for x,y in zip(c,mask))}[stage]
        for spec,derived in candidate_codes(initial):
            if stage=='copy': comp=bytes(x^y for x,y in zip(derived,mask))
            elif stage=='mask': comp=bytes(x^y for x,y in zip(c,derived))
            else: comp=derived
            scores[stage]+=1
            checked.add(comp)
            if hashlib.sha256(comp).hexdigest()==target:
                hits.append((stage,spec,comp.hex()))
    print('HDLC_ORIGINAL_ASSIGNMENTS',dict(scores),'UNIQUE_COMPONENTS',len(checked),'ORIGINAL_K04_MATCHES',hits)
    assert not hits


if __name__=='__main__': main()
