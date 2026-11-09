"""Source-first HST-4 PV predictor: Marsaglia xorshift128, exact rounded bins.

Tests 112 original PV records with selected K04 printer payload and commitments
completely excluded. A genuinely seeded holdout predicts 96 synthetic PV rows.
Run with optional path to resource root (default: repository resources/).
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2] / "resources"
source = (ROOT / "evidence/telemetry/freeze-export.jsonl").read_bytes()
assert hashlib.sha256(source).hexdigest() == "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
rows = sorted((json.loads(line) for line in source.splitlines() if b'"field": "PV"' in line), key=lambda r:r["seq"])
assert [row["seq"] for row in rows] == list(range(100,212))
values = [round(row["value"] * 1000) for row in rows]
MASK32 = (1<<32)-1
BITS128 = (1<<128)-1

def interval(m):
    # Exact inverse of round(12 + 76 * uint32 / 2**32, 3), millivalue m.
    lo = -(-((2*m-24001)*(1<<32))//152000)
    hi = -(-((2*m-23999)*(1<<32))//152000)-1
    return max(lo,0),min(hi,MASK32)

def advance_symbolic(state):
    x,y,z,w = state
    t = [a ^ b for a,b in zip(x,[0]*11+x[:21])]
    nxt = [w[i] ^ (w[i+19] if i+19<32 else 0)
           ^ t[i] ^ (t[i+8] if i+8<32 else 0) for i in range(32)]
    return (y,z,w,nxt),nxt

def advance_native(state):
    x,y,z,w = state
    t = (x ^ ((x<<11)&MASK32)) & MASK32
    v = (w^(w>>19)^t^(t>>8)) & MASK32
    return (y,z,w,v),v

def insert(pivots, mask, bit):
    row = mask | (bit<<128)
    while row&BITS128:
        index = ((row&BITS128)&-(row&BITS128)).bit_length()-1
        if index not in pivots:
            pivots[index] = row
            return True
        row ^= pivots[index]
    return (row>>128)==0

def source_gate(millis, byte_swap, stride):
    state = tuple([1<<(32*k+j) for j in range(32)] for k in range(4))
    pivots={}
    for sample,m in enumerate(millis):
        for _ in range(stride):
            state,output = advance_symbolic(state)
        lo,hi = interval(m)
        assert lo<=hi
        high_prefix=32-(lo^hi).bit_length()
        for k in range(high_prefix):
            bitidx=31-k
            nativeidx=(3-bitidx//8)*8+bitidx%8 if byte_swap else bitidx
            if not insert(pivots,output[nativeidx],(lo>>bitidx)&1):
                return {"valid":False,"fail_record":sample,"rank":len(pivots)}
    return {"valid":True,"rank":len(pivots),"pivots":pivots}

models = {(swap,stride):source_gate(values,swap,stride)
          for swap in (False,True) for stride in range(1,17)}
assert len(models)==32
assert all(not result["valid"] for result in models.values())
print("Original 32 complete producer configurations rejected; latest first contradiction at 0-based record",
      max(result["fail_record"] for result in models.values()))
print("Per-configuration first contradiction", {str(k):v["fail_record"] for k,v in models.items()})

# Planted genuine 128-bit state with fixed stride seven. The first 16 outputs
# determine all 128 initial bits. The next 96 readings are withheld entirely.
initial=(0x98FE1A47,0x5CE05BB2,0x813D0A44,0x701B42F9)
state=initial
planted=[]
for _ in range(112):
    for _ in range(7):
        state,word=advance_native(state)
    planted.append(12000+(76000*word+(1<<31))//(1<<32))
train=source_gate(planted[:16],False,7)
assert train["valid"] and train["rank"]==128
recovered=0
for index in sorted(train["pivots"],reverse=True):
    row=train["pivots"][index]
    rhs=(row>>128)^(((row&BITS128&~(1<<index))&recovered).bit_count()&1)
    recovered |= rhs<<index
state=tuple((recovered>>(32*i))&MASK32 for i in range(4))
assert state==initial
predictions=[]
for _ in range(112):
    for _ in range(7):
        state,word=advance_native(state)
    predictions.append(12000+(76000*word+(1<<31))//(1<<32))
assert predictions[16:]==planted[16:]
print("Planted: all 96 truly withheld complete PV millivalues reproduced PASS")
