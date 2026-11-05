"""H17 compact-state PRNG with categorical interpacket skips, source-only SFT.

Use source originals only. Fit the two xoroshiro128+ state versions under
class/destination-dependent hidden draw counts, with both before/after timing.
"""
from collections import Counter
from itertools import product
import hashlib
import json
import re
from pathlib import Path

spool=(Path(__file__).resolve().parents[2] / 'resources/evidence/print/spool-reconstruction.log').read_bytes()
assert hashlib.sha256(spool).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
records=[]
rawlines=spool.decode()
for n in range(300,428):
    rows=[m for m in re.finditer(r'(?m)^.*JOB=PS-261003-'+f'{n:04d}'+r' ATTEMPT=1 STATE=ACK CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$',rawlines)]
    assert len(rows)==1,(n,len(rows))
    m=rows[0]
    records.append((m.group(1),m.group(3),bytes.fromhex(m.group(2))))
assert len(records)==128

CLS=['LABEL','STORES','RECOVER']; DEST=['bench','store','desk']
metadata=[(CLS.index(c),DEST.index(d)) for c,d,_ in records]
M64=(1<<64)-1

def rotl(x,k):return ((x<<k)|(x>>(64-k)))&M64

def next_word(st,c):
    a,b=st;val=(a+b)&M64;t=b^a;l,q,r=c
    return val,(rotl(a,l)^t^((t<<q)&M64),rotl(t,r))

def matrix_stream(c,limit):
    a=[1<<j for j in range(64)];b=[1<<(64+j) for j in range(64)]
    l,q,r=c;out=[]
    for _ in range(limit):
        out.append(a[0]^b[0])
        x=[a[j]^b[j] for j in range(64)]
        a=[a[(j-l)%64]^x[j]^(x[j-q] if j>=q else 0) for j in range(64)]
        b=[x[(j-r)%64] for j in range(64)]
    return out

def gf2(rows,bits):
    basis={}
    for row,bit in zip(rows,bits):
        v=row;b=bit
        while v:
            i=v.bit_length()-1
            if i not in basis:
                basis[i]=(v,b);break
            w,c=basis[i];v^=w;b^=c
        else:
            if b:return len(basis),None,False
    if len(basis)<128:return len(basis),None,True
    state=0
    for i in sorted(basis):
        v,b=basis[i]
        if b ^ ((v&state).bit_count()&1):state |= 1<<i
    assert all((r&state).bit_count()%2==v for r,v in zip(rows,bits))
    return 128,state,True

views=[]
for e in ('little','big'):
    for swap in (False,True):
        bits=[]
        for _,_,p in records:
            halves=[p[:8],p[8:]]
            if swap:halves.reverse()
            bits.extend(int.from_bytes(x,e)&1 for x in halves)
        views.append((e,swap,bits))

def indices(a,b,phase):
    pos=0;positions=[]
    for i,(cl,de) in enumerate(metadata):
        gap=a[cl]+b[de]
        if phase=='before' and i:pos+=gap
        positions.extend((pos,pos+1))
        pos+=2
        if phase=='after':pos+=gap
    return positions

# Planted complete original-like lowbit source histories, two distinct schedules.
for c,phase,a,b in [((55,14,36),'before',(0,1,0),(0,1,0)),((24,16,37),'after',(1,2,0),(0,1,2))]:
    pp=indices(a,b,phase)
    st=(0x1234567890ABCDEF,0xFEDCBA0987654321);words=[]
    for _ in range(max(pp)+1):
        out,st=next_word(st,c);words.append(out&1)
    matrix=matrix_stream(c,max(pp)+1)
    recovered=gf2([matrix[j] for j in pp[:128]],[words[j] for j in pp[:128]])
    assert recovered == (128,0xFEDCBA0987654321<<64|0x1234567890ABCDEF,True)
    assert all(((matrix[j]&recovered[1]).bit_count()&1)==words[j] for j in pp)

summary=[]
for name,c in [('plus2016',(55,14,36)),('plus2018',(24,16,37))]:
    matrix=matrix_stream(c,6*128+2)
    for phase in ('after','before'):
        checked=0;compatible=0;maxscore=(-1,None);ranks=Counter()
        for vals in product(range(3),repeat=6):
            a,b=vals[:3],vals[3:]
            pp=indices(a,b,phase)
            rows=[matrix[j] for j in pp]
            for endian,swap,bits in views:
                checked+=1
                rank,seed,ok=gf2(rows[:128],bits[:128]);ranks[rank]+=1
                if seed is not None:
                    agree=sum(((r&seed).bit_count()&1)==v for r,v in zip(rows[128:],bits[128:]))
                    if agree>maxscore[0]:maxscore=(agree,(a,b,endian,swap,rank))
                    if agree==128:compatible+=1
                else:
                    rank2,seed2,ok2=gf2(rows,bits)
                    if ok2:compatible+=1
        summary.append({'producer':name,'phase':phase,'models':checked,
                        'compatible_full_256_lowbits':compatible,
                        'train_ranks':dict(ranks),
                        'best_full_rank_holdout_match':maxscore})
print(json.dumps({'source_sha256':hashlib.sha256(spool).hexdigest(),
  'source_packets':len(records), 'source_128bit_state_lowbit_equations':256,
  'category_class':CLS,'category_destination':DEST,'extra_draws_per_category':[0,1,2],
  'synthetic_controls':'PASS: two planted full 128bit states',
  'results':summary},indent=2))
