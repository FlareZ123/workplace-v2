"""Xoshiro256+ historical printer full-state exact inversion SFT.

Uses 129 intact source packets before the disputed selected ACK2 event. For
each exact metadata-dependent state-placement hypothesis, all compatible
256-bit starting states are enumerated; the first full intact packet is
held out from the 258 low-bit state equations as 126 high-bit controls.
"""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib
import json
import re
import time

ROOT=Path(__file__).resolve().parents[2]
spool=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
sha=hashlib.sha256(spool).hexdigest()
assert sha=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
lines=spool.decode().splitlines()
original=[]
for job in range(300,428):
    hits=[line for line in lines if f"JOB=PS-261003-{job:04d} " in line and "ATTEMPT=1 STATE=ACK" in line]
    assert len(hits)==1,(job,len(hits))
    original+=hits
hits=[line for line in lines if "JOB=PS-261003-0417 ATTEMPT=1 STATE=REQUESTED" in line]
assert len(hits)==1
original+=hits
assert len(original)==129
regular=[]
for line in original:
    m=re.search(r"CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)",line)
    assert m,line
    regular.append((m.group(1),m.group(3),bytes.fromhex(m.group(2))))
classes=["LABEL","STORES","RECOVER"]
destinations=["bench","store","desk"]
metadata=[(classes.index(c),destinations.index(d)) for c,d,_ in regular]
MASK=(1<<64)-1

def rotl(x,n):return ((x<<n)|(x>>(64-n)))&MASK

def next_word(st):
    a,b,c,d=st
    result=(a+d)&MASK
    t=(b<<17)&MASK
    c^=a;d^=b;b^=c;a^=d;c^=t;d=rotl(d,45)
    return result,(a,b,c,d)

def coefficient_stream(length):
    s=[[1<<(k*64+j) for j in range(64)] for k in range(4)]
    out=[]
    for _ in range(length):
        a,b,c,d=s
        out.append(a[0]^d[0])
        t=[b[j-17] if j>=17 else 0 for j in range(64)]
        c1=[c[j]^a[j] for j in range(64)]
        d1=[d[j]^b[j] for j in range(64)]
        b1=[b[j]^c1[j] for j in range(64)]
        a1=[a[j]^d1[j] for j in range(64)]
        c2=[c1[j]^t[j] for j in range(64)]
        d2=[d1[(j-45)%64] for j in range(64)]
        s=[a1,b1,c2,d2]
    return out

def placements(a,b,timing):
    idx=[];pos=0
    for i,(cl,ds) in enumerate(metadata):
        extra=a[cl]+b[ds]
        if timing=="before" and i:pos+=extra
        idx.extend([pos,pos+1]);pos+=2
        if timing=="after":pos+=extra
    return idx

def read_outputs(data,endian,swap):
    ans=[]
    for _,_,p in data:
        a,b=p[:8],p[8:]
        if swap:a,b=b,a
        ans.extend([int.from_bytes(a,endian),int.from_bytes(b,endian)])
    return ans

def affine_solution(rows,bits):
    pivots={}
    for row,bit in zip(rows,bits):
        v=row;y=bit
        while v:
            lead=v.bit_length()-1
            if lead not in pivots:
                pivots[lead]=(v,y)
                break
            w,z=pivots[lead];v^=w;y^=z
        else:
            if y:return len(pivots),None,None
    free=[i for i in range(256) if i not in pivots]
    def back_substitute(v):
        for lead in sorted(pivots):
            row,y=pivots[lead]
            if y ^ ((row&v).bit_count()&1):
                v|=1<<lead
        return v
    particular=back_substitute(0)
    basis=[back_substitute(1<<f)^particular for f in free]
    return len(pivots),particular,basis

def actual_outputs(seed,indices):
    s=tuple((seed>>(64*k))&MASK for k in range(4))
    out=[]
    for i in range(max(indices)+1):
        w,s=next_word(s)
        if i==indices[len(out)]:
            out.append(w)
            if len(out)==len(indices):break
    return out

# Genuine planted 256-bit original-state controls, with nontrivial gaps.
initial=int("0123456789ABCDEFFEDCBA987654321000112233445566778899AABBCCDDEEFF",16)
for timing,a,b in [
    ("after",(0,1,2),(0,1,2)),
    ("before",(1,2,0),(0,1,0))
]:
    ix=placements(a,b,timing)
    coeff=coefficient_stream(max(ix)+1)
    vals=actual_outputs(initial,ix)
    rank,p,basis=affine_solution([coeff[j] for j in ix],[v&1 for v in vals])
    assert rank==256 and p==initial and basis==[]

start=time.monotonic()
coeff=coefficient_stream(8*len(regular)+2)
views=[(e,swap,read_outputs(regular,e,swap)) for e in ("big","little") for swap in (False,True)]
summary=[]
for timing in ("after","before"):
    models=0;compatible=0;tested=0;full_packet=0
    compatible_dimensions=Counter();ranks=Counter()
    for values in product(range(3),repeat=6):
        a,b=values[:3],values[3:]
        ix=placements(a,b,timing)
        rows=[coeff[j] for j in ix]
        for endian,swap,full in views:
            models+=1
            rank,seed,basis=affine_solution(rows,[v&1 for v in full])
            ranks[rank]+=1
            if basis is None:continue
            compatible+=1
            compatible_dimensions[len(basis)]+=1
            assert len(basis)<=13
            # Enumerate all affine lowbit-compatible original states using
            # reflected Gray-code traversal; high 126 bits of first intact
            # packet provide the independent source-only rejection test.
            for k in range(1<<len(basis)):
                if k:
                    flip=(k&-k).bit_length()-1
                    seed^=basis[flip]
                st=tuple((seed>>(64*j))&MASK for j in range(4))
                o0,st=next_word(st);o1,st=next_word(st)
                tested+=1
                if (o0,o1)==tuple(full[:2]):
                    full_packet+=1
                    print("FIRST_SOURCE_PACKET_MATCH",timing,a,b,endian,swap,hex(seed))
    summary.append({"timing":timing,"models":models,"lowbit_compatible_models":compatible,
                    "all_initial_states_tested":tested,"first_full_source_packet_matches":full_packet,
                    "compatible_dimension_counts":dict(compatible_dimensions),"rank_counts":dict(ranks)})
print(json.dumps({"source_sha256":sha,"intact_pretarget_records":129,
                  "original_lowbit_equations":258,"generator":"xoshiro256+",
                  "genuine_planted_256bit_state_positives":2,
                  "results":summary,"elapsed_s":round(time.monotonic()-start,3)},indent=2))
