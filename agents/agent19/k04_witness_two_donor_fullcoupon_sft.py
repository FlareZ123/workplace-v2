"""H-17 MT-witness-geometry full selected coupon constructor.

Original selected row129 is excluded before parsing PAYLOAD. This constructs
forty complete candidates under five source-observed recurrence offset geometries.
No source or acceptance data are modified.
"""
import hashlib
import itertools
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE = ROOT / "evidence" / "print" / "spool-reconstruction.log"
TARGETS = ROOT / "acceptance.json"
ROUTE = ROOT / "evidence" / "recovery-routing.json"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
LIMIT = 0xffffffff


def undo_right(v, n):
    y=v
    for _ in range(6):
        y = v ^ (y >> n)
    return y&LIMIT


def undo_left(v,n,mask):
    y=v
    for _ in range(6):
        y = v ^ ((y<<n)&mask)
    return y&LIMIT


def temper(v):
    y=v^(v>>11)
    y^=(y<<7)&0x9d2c5680
    y^=(y<<15)&0xefc60000
    y^=y>>18
    return y&LIMIT


def untemper(v):
    y=undo_right(v,18)
    y=undo_left(y,15,0xefc60000)
    y=undo_left(y,7,0x9d2c5680)
    return undo_right(y,11)


def twist(a,b):
    x=((a&0x80000000)|(b&0x7fffffff))
    return (x>>1)^ (0x9908b0df if b&1 else 0)


def reconstruct(source_native, partner_native, absent_msb):
    assert len(source_native)==len(partner_native)==4
    out=[]
    for j in range(4):
        # The preceding input for source lane zero is an unobserved MSB only.
        a = (0x80000000 if absent_msb else 0) if j==0 else source_native[j-1]
        b = source_native[j]
        out.append(partner_native[j]^twist(a,b))
    return out


def view(block, byte_order, reverse):
    words=[int.from_bytes(block[i:i+4],byte_order) for i in (0,4,8,12)]
    return words[::-1] if reverse else words


def encode(words, byte_order, reverse):
    values=words[::-1] if reverse else words
    return b''.join(temper(w).to_bytes(4,byte_order) for w in values)


def test_controls():
    rng=random.Random(426817)
    state=list(rng.getstate()[1][:-1])
    assert len(state)==624
    # CPython states are the 624 native generator words at an MT twist boundary.
    native=[x&LIMIT for x in state]
    for j in range(4):
        native.append(native[j+397]^twist(native[j],native[j+1]))
    # Starts 1,397,624 put target at (+623) relative to source and
    # partner at (+396), exactly our geometry.
    a=native[1:5]
    b=native[397:401]
    expected=native[624:628]
    assert expected==reconstruct(a,b,bool(native[0]&0x80000000))
    assert expected!=reconstruct(a,b,not bool(native[0]&0x80000000))
    for endian, reverse in itertools.product(('little','big'),(False,True)):
        src=encode(a,endian,reverse)
        par=encode(b,endian,reverse)
        av=[untemper(v) for v in view(src,endian,reverse)]
        bv=[untemper(v) for v in view(par,endian,reverse)]
        actual=encode(reconstruct(av,bv,bool(native[0]&0x80000000)),endian,reverse)
        assert actual==encode(expected,endian,reverse)
    print("synthetic MT native/coupon whole-packet reconstruction: PASS (all four views)")


def run():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    assert json.loads(TARGETS.read_text())['slot_sha256']['K04']==TARGET
    assert bytes.fromhex(json.loads(ROUTE.read_text())['K04']['masked_component'])==MASK
    raw=[line for line in SOURCE.read_text().splitlines() if line and not line.startswith("#")]
    assert len(raw)==133
    # Validate selector metadata before reading any selected byte content.
    assert all(k in raw[129] for k in ('JOB=PS-261003-0417','ATTEMPT=2','STATE=ACK','CLASS=RECOVER'))
    packets=[]
    for idx,line in enumerate(raw):
        if idx==129:
            packets.append(None)
            continue
        match=re.search(r'\bPAYLOAD=([0-9A-F]{32})\b',line)
        assert match, idx
        packets.append(bytes.fromhex(match.group(1)))
    witness_offsets=((52,83),(53,83),(53,84),(53,87),(54,84))
    # Frozen source-blind full-packet holdout across every intact destination.
    controls=0; whole_controls=[]; word_match_hist=[0]*5
    for l in range(0,133):
        if l==129:continue
        for dk,dl in witness_offsets:
            r=l-dl;k=r+dk
            if r<0 or k<0 or k>=l or 129 in (r,k):continue
            for endian,reverse in itertools.product(('little','big'),(False,True)):
                a=[untemper(w) for w in view(packets[r],endian,reverse)]
                b=[untemper(w) for w in view(packets[k],endian,reverse)]
                for msb in (False,True):
                    predicted=encode(reconstruct(a,b,msb),endian,reverse)
                    correct=sum(predicted[i:i+4]==packets[l][i:i+4] for i in (0,4,8,12))
                    word_match_hist[correct]+=1;controls+=1
                    if correct==4:whole_controls.append((r,k,l,endian,reverse,msb))
    print('Historical intact packet holdout checks:',controls)
    print('Word-match histogram across four lanes:',word_match_hist)
    print('Historical complete-packet matches:',len(whole_controls),whole_controls[:4])
    matched=[]; checks=0
    for dk,dl in witness_offsets:
        r=129-dl;k=r+dk
        assert r<k<129
        for endian,reverse in itertools.product(('little','big'),(False,True)):
            a=[untemper(w) for w in view(packets[r],endian,reverse)]
            b=[untemper(w) for w in view(packets[k],endian,reverse)]
            for msb in (False,True):
                coupon=encode(reconstruct(a,b,msb),endian,reverse)
                component=bytes(x^y for x,y in zip(coupon,MASK))
                checks+=1
                if hashlib.sha256(component).hexdigest()==TARGET:
                    matched.append((r,k,endian,reverse,msb,coupon.hex().upper(),component.hex().upper()))
    assert checks==5*4*2
    print('Historical witness row pairs:',[(129-dl,129-dl+dk) for dk,dl in witness_offsets])
    print('Complete full-component commitment checks:',checks)
    print('Historical original K04 commitment hits:',len(matched))
    for hit in matched:print('K04_ACCEPTED_CANDIDATE',hit)
    return bool(matched)


if __name__=='__main__':
    test_controls()
    run()