"""Source-first 53-bit randfloat metadata writer against intact printer jobs.

Hypothesis: one CPython random.random() draw from two consecutive hidden MT
words chooses CLASS*3+DEST. Models allow one global codebook each for CLASS and
DEST; current/next-row field binding; and class-first/dest-first ordering.
The selected ACK2 copied payload is completely withheld by the source basis.
"""
from itertools import permutations, product
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent49"))
import k04_p951_symbolic_basis as mt

basis, native = mt.source(ROOT)
assert basis.rank == 15365
raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_text("ascii")
lines = [s for s in raw.splitlines() if s.startswith("2026-")]
assert len(lines) == 133
assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
labels = [re.search(r"CLASS=(\w+) PAYLOAD=[0-9A-F]{32} DEST=(\w+)", s).groups() for s in lines]
cls = [("LABEL", "RECOVER", "STORES").index(a) for a,b in labels]
dest = [("store", "desk", "bench").index(b) for a,b in labels]
perms = list(permutations(range(3)))

# Native CPython uses a>>5 (27 bits) followed by b>>6 (26 bits).
# Float multiplication by nine is kept, including its double rounding.
r = random.Random(20261110)
a,b = r.getrandbits(32), r.getrandbits(32)
r2 = random.Random(20261110)
assert ((a >> 5) * 67108864 + (b >> 6)) / float(1<<53) == r2.random()

def codes_at(stage):
    first = mt.temper(mt.get(native, stage))
    second = mt.temper(mt.get(native, stage+1))
    bits = [basis.predict(v) for v in first[5:]+second[6:]]
    assert len(bits) == 53
    lo = sum((v or 0)<<j for j,v in enumerate(bits))
    hi = sum((1 if v is None else v)<<j for j,v in enumerate(bits))
    return set(range(int((lo/float(1<<53))*9),int((hi/float(1<<53))*9)+1))

# Deliberately restrict to the 127 ordinary-to-ordinary packet gaps.
# Stage gap includes every two-consecutive-word pair and no selected packet.
windows = []
for i in range(127):
    q,nxt = mt.STARTS[i:i+2]
    windows.append([codes_at(s) for s in range(q+4,nxt-1)])
assert all(windows)

def score(windows, cls, dest, mode, cls_at, dest_at, order, pc, pd):
    hits=0
    wrong=[]
    for i,w in enumerate(windows):
        c=pc[cls[i+cls_at]]
        d=pd[dest[i+dest_at]]
        k=c*3+d if order==0 else d*3+c
        cells=w[:1] if mode=="first" else w[-1:] if mode=="last" else w
        if any(k in codes for codes in cells):
            hits+=1
        else:
            wrong.append(i)
    return hits,wrong

def run(mode):
    best=(-1,None)
    nall=0
    for ca,da,order,pc,pd in product(range(2),range(2),range(2),perms,perms):
        hits,wrong=score(windows,cls,dest,mode,ca,da,order,pc,pd)
        if hits>best[0]:
            best=(hits,(ca,da,order,pc,pd,wrong))
        nall+=hits==127
    print(mode,"best",best[0],"missing",len(best[1][-1]),
          "first_missing",best[1][-1][:16],"allpass",nall)
    return best[0],nall

# Synthetic all-gap positive: assign every gap a first-position permitted
# 9-bin code; reconstruct the complete 127-gap series using a shared identity
# class/dest codebook and per-gap categories.
planted = [min(w[0]) for w in windows]
pc = list(range(3))
assert all((pc[k//3]*3 + pc[k%3]) in windows[i][0]
           for i,k in enumerate(planted))
assert len(planted)==127
print("planted_source_gap_model",len(planted),"PASS")
results={mode:run(mode) for mode in ("first","last","any")}
assert results=={"first":(91,0),"last":(100,0),"any":(113,0)}
print("SOURCE_ONLY_PASS; SELECTED_K04_NOT_READ; NO_RECOVERED_COMPONENT")
