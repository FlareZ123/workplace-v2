"""K04: original TRP2 four-cohort 227-apart *future MT donor* candidate model.

Run as Python with a repository resources directory argument (default resources).
Hypothetical placement, not an authentic recorder/printer index mapping.
"""
import hashlib
import itertools
import json
import random
import re
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('resources')
REC_SHA = '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK32=0xffffffff


def untemper(x):
    for shift,left,mask in ((18,False,MASK32),(15,True,0xefc60000),(7,True,0x9d2c5680),(11,False,MASK32)):
        y=x
        for _ in range(6):y=x^(((y<<shift)&mask) if left else (y>>shift))
        x=y&MASK32
    return x


def temper(x):
    x ^= x>>11
    x ^= (x<<7)&0x9d2c5680
    x ^= (x<<15)&0xefc60000
    return (x ^ (x>>18))&MASK32


def untwist(x):
    return (((x^(0x9908b0df if x>>31 else 0))<<1)|(x>>31))&MASK32


def predicted(a,b,old_msb):
    """Recover 127/128 target state bits from four full32 future donor pairs."""
    mixed=[untwist(x^y) for x,y in zip(a,b)]
    if mixed[0]>>31!=old_msb:return ()
    prefix=[(mixed[j+1]&0x80000000)|(mixed[j]&0x7fffffff) for j in range(3)]
    return [prefix+[(mixed[3]&0x7fffffff)|(bit<<31)] for bit in (0,1)]


def bytes_out(words):
    return b''.join(temper(w).to_bytes(4,'little') for w in words)


for seed in (0,1,2026,0xDEADBEEF):
    rng=random.Random(seed)
    states=[untemper(rng.getrandbits(32)) for _ in range(1578)]
    candidates=predicted(states[1347:1351],states[1574:1578],states[950]>>31)
    assert len(candidates)==2 and states[951:955] in candidates
print('SYNTHETIC_FOUR_FUTURE_RECURRENCE_CONTROLS_PASS')

recorder=(ROOT/'evidence/recorder/trip-recorder.raw').read_bytes()
assert hashlib.sha256(recorder).hexdigest()==REC_SHA
cohorts={g:{} for g in (200,300,900,990)}
for row in range(88):
    at=16+24*row
    ts,node,event,latch,seq,control,aux,crc=struct.unpack_from('<IHBBI4sII',recorder,at)
    if (node,event)!=(49,82):continue
    group=next((g for g in cohorts if g<=seq<g+4),None)
    if group is None:continue
    cohorts[group][seq-group]=(untemper(int.from_bytes(control,'little')),zlib.crc32(recorder[at:at+20])==crc)
assert all(len(c)==4 for c in cohorts.values())
assert all(cohorts[g][i][1]==(g!=900) for g in cohorts for i in range(4))

spool=(ROOT/'evidence/print/spool-reconstruction.log').read_bytes()
assert hashlib.sha256(spool).hexdigest()==SPOOL_SHA
payloads=re.findall(rb'PAYLOAD=([0-9A-F]{32})',spool)
assert len(payloads)==133
prev=bytes.fromhex(payloads[128].decode())
old_msb=untemper(int.from_bytes(prev[12:16],'little'))>>31

# The source-stage complete native candidate is formed BEFORE mask/hash use.
native_candidates={}
source_order_pairs=source_order_gate=assignments=passed_gate=0
for first,second in itertools.permutations(cohorts,2):
    original_a=[cohorts[first][i][0] for i in range(4)]
    original_b=[cohorts[second][i][0] for i in range(4)]
    source_order_pairs+=1
    source_order_gate+=bool(predicted(original_a,original_b,old_msb))
    for order_a in itertools.permutations(range(4)):
        a=[original_a[i] for i in order_a]
        for order_b in itertools.permutations(range(4)):
            b=[original_b[i] for i in order_b]
            assignments+=1
            choices=predicted(a,b,old_msb)
            if not choices:continue
            passed_gate+=1
            for words in choices:
                native_candidates.setdefault(bytes_out(words),(first,second,order_a,order_b))
assert (source_order_pairs,source_order_gate,assignments,passed_gate,len(native_candidates))==(12,8,6912,3888,3888)

routing=json.loads((ROOT/'evidence/recovery-routing.json').read_text())
acceptance=json.loads((ROOT/'acceptance.json').read_text())
mask=bytes.fromhex(routing['K04']['masked_component'])
target=acceptance['slot_sha256']['K04']
hits=[]
for native,provenance in native_candidates.items():
    candidate=bytes(x^y for x,y in zip(native,mask))
    if hashlib.sha256(candidate).hexdigest()==target:
        hits.append({'source_pair':provenance,'coupon':native.hex().upper(),'K04':candidate.hex().upper()})
print(json.dumps({'source_order_pairs':source_order_pairs,'source_order_predecessor_bit_pass':source_order_gate,
    'permuted_cohort_assignments':assignments,'predecessor_bit_pass':passed_gate,
    'two_last_msb_choices_per_pass':2,'unique_complete_K04_candidates':len(native_candidates),
    'original_commitment_matches':len(hits),'hits':hits},indent=2))
