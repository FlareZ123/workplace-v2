"""H17 K04 five ticket-indexed spool packets as candidate GF256 secret shares.

A speculative algebraic reconstruction, not source-authenticated share mapping.
Reads unchanged original exported records, checks complete K04 SHA256. Stdlib.
Usage: python agents/agent29/k04_ticket_shamir_original_sft.py resources
"""
import csv
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv)==2 else Path(__file__).resolve().parents[2]/'resources'
SPOOL = ROOT/'evidence/print/spool-reconstruction.log'
FLEET = ROOT/'evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt'
DOCKET = ROOT/'evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv'
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
assert hashlib.sha256(FLEET.read_bytes()).hexdigest() == '10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf'
routing = json.loads((ROOT/'evidence/recovery-routing.json').read_text())
acceptance = json.loads((ROOT/'acceptance.json').read_text())
mask = bytes.fromhex(routing['K04']['masked_component'])
target = acceptance['slot_sha256']['K04']
assert mask.hex().upper() == '8556C8CB6140A7F9A5123AC7571BEE1C'
assert target == '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'

# One-based ticket-to-spool-ordinal relationship is a hypothesis, not a fact.
tickets=[]
for line in FLEET.read_text().splitlines():
    m=re.search(r'^L-29/N\s+(\d+)\s+ST-(\d+)\s+(.*)$',line)
    if m:tickets.append((int(m.group(1)),int(m.group(2)),m.group(3)))
assert [row[1] for row in tickets] == [94,81,106,99,112]
assert [row[0] for row in tickets] == [1,2,3,4,5]
posted=set()
with DOCKET.open(newline='') as f:
    for row in csv.DictReader(line for line in f if not line.startswith('#')):
        if (row['posting'],row['run'],row['account'],row['source'],row['folio_or_jacket']) == ('POSTED','R3','FA-17','L29','H17-POL-17/A3'):
            posted.add(int(row['line_ref'][3:]))
assert posted == {x[1] for x in tickets}
rows=[]
for line in SPOOL.read_text().splitlines():
    if line.startswith('2026-'):
        fields=dict(re.findall(r'([A-Z]+)=([^ ]+)',line))
        rows.append((fields['JOB'],fields['PAYLOAD']))
assert len(rows)==133
regular=rows[:128]
assert all(name == f'PS-261003-{300+i:04d}' for i,(name,_) in enumerate(regular))
donors=[]
for _,ticket,_ in tickets:
    name,payload=regular[ticket-1]
    assert name == f'PS-261003-{ticket+299:04d}'
    donors.append(bytes.fromhex(payload))
assert len(donors)==5 and all(len(s)==16 for s in donors)

# Generic GF(256) finite-field arithmetic for both common polynomials.
def mul(a,b,poly):
    out=0
    for _ in range(8):
        if b&1:out^=a
        hi=a&0x80
        a=(a<<1)&255
        if hi:a^=poly&255
        b>>=1
    return out

def inv(a,poly):
    assert a
    x=1
    for _ in range(254):x=mul(x,a,poly)
    assert mul(x,a,poly)==1
    return x

def interpolate(xs,ys,x,poly):
    assert len(xs)==len(ys) and len(set(xs))==len(xs)
    out=bytearray(16)
    for i,(xi,vi) in enumerate(zip(xs,ys)):
        coef=1
        for j,xj in enumerate(xs):
            if i!=j:
                coef=mul(coef,mul(x^xj,inv(xi^xj,poly),poly),poly)
        for k in range(16):out[k]^=mul(coef,vi[k],poly)
    return bytes(out)

# Actual synthetic withheld-16B positive for a degree-4 Shamir polynomial.
secret=bytes.fromhex('9F439620AA750E7E22F1D091C3D8EB26')
coeffs=[secret]+[hashlib.sha256(f'h17-c{i}'.encode()).digest()[:16] for i in range(1,5)]
def evaluate(xs,poly):
    outputs=[]
    for x in xs:
        current=bytearray(16)
        for c in reversed(coeffs):
            current=bytearray(mul(v,x,poly)^w for v,w in zip(current,c))
        outputs.append(bytes(current))
    return outputs
for poly in (0x11b,0x11d):
    points=evaluate([94,81,106,99,112],poly)
    assert interpolate([94,81,106,99,112],points,0,poly)==secret

# Frozen thresholds, coordinate systems, candidate sites and source views.
xs_options={
    'ticket_number':[x[1] for x in tickets],
    'tab_number':[x[0] for x in tickets],
    'mapped_spool_job_lowbyte':[(x[1]+299)&255 for x in tickets],
}
xs_target=(0,6,4,129,161,169,255)
checked=set();hit=[];tests=0
for poly in (0x11b,0x11d):
    for xtag,xs in xs_options.items():
        for indices in itertools.chain.from_iterable(itertools.combinations(range(5),k) for k in (2,3,4,5)):
            subset_x=[xs[i] for i in indices]
            for flipped in (False,True):
                y=[donors[i][::-1] if flipped else donors[i] for i in indices]
                for pre_mask in (False,True):
                    ys=[bytes(a^b for a,b in zip(v,mask)) if pre_mask else v for v in y]
                    for target_x in xs_target:
                        if target_x in subset_x:continue
                        coupon=interpolate(subset_x,ys,target_x,poly)
                        comp=bytes(a^b for a,b in zip(coupon,mask))
                        tests+=1
                        if hashlib.sha256(comp).hexdigest()==target:
                            hit.append((poly,xtag,indices,flipped,pre_mask,target_x,coupon.hex()))
                        checked.add(comp)
print(json.dumps({'source':'ORIGINAL','synthetic_gf256_positive':True,'distinct_components':len(checked),'complete_assignments':tests,'original_hits':hit},sort_keys=True))
assert tests==4248 and len(checked)==4176 and not hit
