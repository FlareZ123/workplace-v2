"""K04 p951/K02/K05 rotated common recorder-mask test, selected ACK withheld.

Uses Agent49's exact source-state model. Rotation shift r imposes
K05_native[i] = MTnative[2139+227*i] XOR ROL32(M, r*i) for one M.
"""
from collections import Counter
from pathlib import Path
import hashlib
import itertools
import json
import random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent49"))
import k04_p951_symbolic_basis as mt

mt.LAST=3000
source=Path(__file__).resolve().parents[2]/"resources"
original, symbol=mt.source(source)
assert original.rank==15365
k02=bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
k05=bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572")
mask=bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
accepted="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
assert hashlib.sha256(k05).hexdigest()==json.loads((source/"acceptance.json").read_text())["slot_sha256"]["K05"]
views=[[int.from_bytes(k05[i:i+4],o) for o in ("little","big")] for i in (0,4,8,12)]
views=[x+[mt.untemper(v) for v in x] for x in views]
target=[e for s in range(951,955) for e in mt.get(symbol,s)]

def clone(b):
    r=mt.Basis();r.rows=b.rows.copy();r.rank=b.rank;return r

def donor_modes():
    for endian in ("big","little"):
        for reverse,swap,native in itertools.product((False,True),repeat=3):
            chunks=[k02[i:i+4] for i in (0,4,8,12)]
            if swap:chunks=[p[2:]+p[:2] for p in chunks]
            if reverse:chunks.reverse()
            v=[int.from_bytes(p,endian) for p in chunks]
            yield (endian,reverse,swap,native),[x if native else mt.untemper(x) for x in v]

def quotient(basis):
    pivots={};coefficients=[];constants=[]
    for expression in target:
        rem=val=0
        while expression:
            p=expression.bit_length()-1
            if p in basis.rows:
                eq,bit=basis.rows[p];expression^=eq;val^=bit
            else:
                rem^=1<<p;expression^=1<<p
        coeff=0
        while rem:
            p=rem.bit_length()-1
            if p in pivots:
                vec,tag=pivots[p];rem^=vec;coeff^=tag
            else:
                tag=1<<len(pivots)
                pivots[p]=(rem,tag);coeff^=tag;break
        coefficients.append(coeff);constants.append(val)
    return coefficients,constants,len(pivots)

def temper(x):
    x^=x>>11;x^=(x<<7)&0x9D2C5680;x^=(x<<15)&0xEFC60000;x^=x>>18
    return x&0xffffffff

def component(bits):
    coupon=b"".join(temper(sum(bits[32*i+j]<<j for j in range(32))).to_bytes(4,"little") for i in range(4))
    return bytes(x^y for x,y in zip(coupon,mask))

def candidates(basis):
    coeff,const,dim=quotient(basis)
    if dim>16:return None,dim
    result=[]
    for z in range(1<<dim):
        bits=[v^((c&z).bit_count()&1) for c,v in zip(coeff,const)]
        result.append(component(bits))
    return result,dim

summary=Counter();distinct=set();hits=[]
for donor in (1178,1405):
    for label,words in donor_modes():
        base=clone(original)
        for pos,value in zip(range(donor,donor+4),words):
            for j,e in enumerate(mt.get(symbol,pos)):
                base.insert(e,(value>>j)&1)
        assert base.rank==15493
        for shift in range(32):
            joint=clone(base);summary["assignments"]+=1
            try:
                for i,pos in enumerate((2139,2366,2593,2820)):
                    value=views[i][2]
                    for j,e in enumerate(mt.get(symbol,pos)):
                        joint.insert(e^(1<<(19968+(j-shift*i)%32)),(value>>j)&1)
            except AssertionError:
                continue
            summary["consistent"]+=1
            rec,dim=candidates(joint)
            summary[f"dim{dim}"]+=1
            if rec is not None:
                summary["checks"]+=len(rec)
                distinct.update(rec)
                for candidate in rec:
                    if hashlib.sha256(candidate).hexdigest()==accepted:
                        summary["original_hits"]+=1
                        hits.append([donor,label,shift,candidate.hex().upper()])
assert summary["assignments"]==1024
assert summary["consistent"]==1024
assert summary["checks"]==33792
assert len(distinct)==16384
assert not hits
print("ORIGINAL_SOURCE_ROTATING_MASK",json.dumps({"summary":dict(summary),"distinct":len(distinct),"hits":hits},sort_keys=True),flush=True)

# Genuine seeded MT source with independently sampled common K05 mask.
rng=random.Random(0xA9132026)
state=rng.getrandbits(19968);common=rng.getrandbits(32)
def native(pos):
    return sum(((e&state).bit_count()&1)<<j for j,e in enumerate(mt.get(symbol,pos)))
def rol32(v,n):
    n%=32
    return ((v<<n)|(v>>(32-n)))&0xffffffff if n else v
syn=mt.Basis()
for row,pos in enumerate(mt.STARTS):
    if row==129:continue
    for j in range(4):
        word=native(pos+j)
        for k,e in enumerate(mt.get(symbol,pos+j)):
            syn.insert(e,(word>>k)&1)
assert syn.rank==15365
base=clone(syn)
for pos in range(1178,1182):
    word=native(pos)
    for j,e in enumerate(mt.get(symbol,pos)):
        base.insert(e,(word>>j)&1)
assert base.rank==15493
true=component([(e&state).bit_count()&1 for e in target])
for shift in (0,8,16,24):
    joint=clone(base)
    for i,pos in enumerate((2139,2366,2593,2820)):
        word=native(pos)^rol32(common,shift*i)
        for j,e in enumerate(mt.get(symbol,pos)):
            joint.insert(e^(1<<(19968+(j-shift*i)%32)),(word>>j)&1)
    predicted,dim=candidates(joint)
    assert predicted is not None and sum(x==true for x in predicted)==1
    print("GENUINE_SYNTHETIC_POSITIVE",shift,dim,len(predicted),flush=True)
