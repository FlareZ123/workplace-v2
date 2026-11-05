"""Original-source MT symbolic K04 rank test for 72 hypothetical node50 records."""
import random
import sys
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, source, get, temper

base, words = source(root / "resources")
assert base.rank == 15365
target = [v for i in range(951, 955) for v in get(words, i)]

def residual(b):
    remainder = {}
    for v0 in target:
        v = v0
        while v:
            p = v.bit_length()-1
            if p in b.rows: v ^= b.rows[p][0]
            elif p in remainder: v ^= remainder[p]
            else:
                remainder[p] = v
                break
    return len(remainder)

def stages(seed):
    rng = random.Random(seed)
    t = 0
    out = []
    for _ in range(72):
        row = []
        for n in (400, 39, 4, None, 6000):
            if n is None:
                row.append((t, 32)); t += 1; rng.getrandbits(32)
            else:
                k = n.bit_length()
                while True:
                    p = t; t += 1
                    if rng.getrandbits(k) < n: break
                row.append((p, k))
        out.append(row)
    return out

assert residual(base) == 128
hist = Counter()
new_ranks = []
trials = 0
for seed in range(20261101, 20281101):
    rec = stages(seed); trials += 1
    if rec[70][3][0]-rec[7][3][0] != 471: continue
    delta = -810-rec[7][3][0]
    assert rec[70][3][0]+delta == -339
    b = Basis(); b.rows = base.rows.copy(); b.rank = base.rank
    for row in rec:
        for index, width in row:
            exprs = get(words, index+delta)
            if width != 32: exprs = temper(exprs)[32-width:]
            for v0 in exprs:
                v = v0
                while v:
                    p = v.bit_length()-1
                    if p not in b.rows:
                        b.rows[p] = (v, 0); b.rank += 1; break
                    v ^= b.rows[p][0]
    hist[residual(b)] += 1
    new_ranks.append(b.rank-base.rank)
    if sum(hist.values()) == 100: break
assert trials == 5373 and sum(hist.values()) == 100
assert min(hist) == 91 and max(hist) == 128
assert min(new_ranks) == 1637 and max(new_ranks) == 2291
print("anchor-conditioned scenarios", 100, "sampled seeds", trials)
print("selected coupon dimensions free", sorted(hist.items()))
print("observability upper limit only; original K04 remains missing")
