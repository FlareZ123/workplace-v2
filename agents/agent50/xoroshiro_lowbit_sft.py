"""Source-only xoroshiro128+ fixed-stride low-bit state inversion.

Read the 128 intact first-attempt printer packets. Never fit the selected 18:02
K04 copied ACK or compare a candidate with its commitment.
"""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spool=(ROOT / 'resources/evidence/print/spool-reconstruction.log').read_bytes()
assert hashlib.sha256(spool).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
lines=spool.decode().splitlines()
regular=[]
for i in range(300,428):
    matches=[x for x in lines if f'JOB=PS-261003-{i:04d} ' in x and 'ATTEMPT=1 STATE=ACK ' in x]
    assert len(matches)==1,(i,matches)
    regular.append(bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})',matches[0]).group(1)))
assert len(regular)==128
M64=(1<<64)-1

def rol64(x,k):
    return ((x<<k)|(x>>(64-k)))&M64

def next_u64(state,constants):
    a,b=state
    result=(a+b)&M64
    x=b^a
    L,B,R=constants
    return result,(rol64(a,L)^x^((x<<B)&M64),rol64(x,R))

def coefficient_stream(constants,limit):
    a=[1<<i for i in range(64)]
    b=[1<<(i+64) for i in range(64)]
    L,B,R=constants
    out=[]
    for _ in range(limit):
        out.append(a[0]^b[0])
        x=[a[i]^b[i] for i in range(64)]
        a=[a[(i-L)%64]^x[i]^(x[i-B] if i>=B else 0) for i in range(64)]
        b=[x[(i-R)%64] for i in range(64)]
    return out

def recover(rows,bits):
    basis={}
    for row,bit in zip(rows,bits):
        v=row;b=bit
        while v:
            pivot=v.bit_length()-1
            if pivot not in basis:
                basis[pivot]=(v,b)
                break
            w,c=basis[pivot]
            v^=w;b^=c
        else:
            if b:return len(basis),None,False
    if len(basis)<128:return len(basis),None,True
    state=0
    for pivot in sorted(basis):
        v,b=basis[pivot]
        if b ^ ((v&state).bit_count()&1):
            state|=1<<pivot
    assert all((r&state).bit_count()%2==v for r,v in zip(rows,bits))
    return 128,state,True

def bit_view(payload,byteorder,swap):
    words=[payload[:8],payload[8:]]
    if swap:words.reverse()
    return [int.from_bytes(x,byteorder)&1 for x in words]

# Full-state inversion and held-out prediction must pass on two planted histories.
for c,stride,endian,swap in [((55,14,36),2,'little',False),((24,16,37),11,'big',True)]:
    state=(0x1234567890ABCDEF,0xFEDCBA0987654321)
    synthetic=[]
    for _ in range(128):
        pair=[]
        for j in range(stride):
            u,state=next_u64(state,c)
            if j<2:pair.append(u)
        if swap:pair.reverse()
        synthetic.append(b''.join(u.to_bytes(8,endian) for u in pair))
    coef=coefficient_stream(c,stride*127+2)
    rows=[coef[stride*i+j] for i in range(64) for j in range(2)]
    bits=[x for p in synthetic[:64] for x in bit_view(p,endian,swap)]
    rank,seed,ok=recover(rows,bits)
    assert rank==128 and ok and seed==(0xFEDCBA0987654321<<64|0x1234567890ABCDEF)
    assert all(((coef[stride*i+j]&seed).bit_count()&1)==x
               for i,p in enumerate(synthetic) for j,x in enumerate(bit_view(p,endian,swap)))

results=[]
for name,c in [('plus2016',(55,14,36)),('plus2018',(24,16,37))]:
    for stride in range(2,33):
        coef=coefficient_stream(c,stride*127+2)
        rows=[coef[stride*i+j] for i in range(128) for j in range(2)]
        for endian in ('little','big'):
            for swap in (False,True):
                bits=[x for p in regular for x in bit_view(p,endian,swap)]
                rank,seed,ok=recover(rows[:128],bits[:128])
                allrank,allstate,allok=recover(rows,bits)
                agree=None
                if seed is not None:
                    agree=sum(((r&seed).bit_count()&1)==x for r,x in zip(rows[128:],bits[128:]))
                results.append((name,stride,endian,swap,rank,agree,allrank,allok))
scores=sorted((r for r in results if r[5] is not None),key=lambda r:r[5],reverse=True)
print(json.dumps({'source_sha256':hashlib.sha256(spool).hexdigest(),
 'regular_packets':128,'models':len(results),'fixed_strides':'2..32',
 'lowbit_source_compatible':sum(r[7] for r in results),
 'train_ranks':dict(Counter(r[4] for r in results)),
 'full_ranks':dict(Counter(r[6] for r in results)),
 'best_holdout_lowbit_matches':scores[:10],
 'synthetic_positives':2,'target_commitment_tests':0},indent=2))
