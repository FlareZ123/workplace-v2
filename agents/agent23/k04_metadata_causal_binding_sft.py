"""H-17 printer CLASS/DEST causal-binding gap test (original source, selected row withheld).

This experiment extends the earlier current-row metadata hypothesis to the
different pre-next and split-class/destination acquisition orders. It tests
whether two sequential Python-style getrandbits(2) / randbelow(3) calls, with
code 3 rejected, can occupy the between-packet native MT gap under the
unverified p951 stage alignment. Original selected coupon row129 and both K04
and K08 acceptance commitments are unused.

Run: python agents/agent23/k04_metadata_causal_binding_sft.py resources
"""
from __future__ import annotations
from itertools import permutations, product
from pathlib import Path
import hashlib
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
import k04_p951_symbolic_basis as mt

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
labels = re.findall(rb"CLASS=(\w+) PAYLOAD=[0-9A-F]{32} DEST=(\w+)", raw)
assert len(labels) == len(mt.STARTS) == 133
assert labels[129] == (b"RECOVER", b"bench")
source, bank = mt.source(root)
assert source.rank == 15365

def code_compatible(bits, value):
    return all(actual is None or actual == (value >> j) & 1 for j, actual in enumerate(bits))

def possible(window, first, second):
    for t in range(len(window) - 1):
        if (all(code_compatible(x, 3) for x in window[:t])
            and code_compatible(window[t], first)
            and all(code_compatible(x, 3) for x in window[t+1:-1])
            and code_compatible(window[-1], second)):
            return True
    return False

# Genuine simulated 2-bit accept/reject sequence: 3, 2, 3, 1.
assert possible([(1, 1), (0, 1), (1, 1), (1, 0)], 2, 1)
assert not possible([(1, 1), (0, 1), (1, 1), (1, 0)], 1, 2)

windows = []
for i in range(127):  # ordinary-job gaps only, excludes exceptional selected event
    q, next_q = mt.STARTS[i:i+2]
    w = []
    for pos in range(q + 4, next_q):
        out = mt.temper(mt.get(bank, pos))
        w.append((source.predict(out[30]), source.predict(out[31])))
    assert len(w) >= 2
    windows.append(w)

classes = ("LABEL", "RECOVER", "STORES")
dests = ("store", "desk", "bench")
name_c = [classes.index(c.decode()) for c, d in labels]
name_d = [dests.index(d.decode()) for c, d in labels]
perms = list(permutations(range(3)))
records = []
for cls_at, dest_at in product((0, 1), repeat=2):
    for order in ("CLASS-DEST", "DEST-CLASS"):
        for pc, pd in product(perms, repeat=2):
            hits = []
            for i, w in enumerate(windows):
                c = pc[name_c[i + cls_at]]
                d = pd[name_d[i + dest_at]]
                pair = (c, d) if order == "CLASS-DEST" else (d, c)
                hits.append(possible(w, *pair))
            records.append((sum(hits), cls_at, dest_at, order, pc, pd, hits))

records.sort(key=lambda x: x[0], reverse=True)
for c, d in product((0, 1), repeat=2):
    best = next(x for x in records if x[1:3] == (c, d))
    print("BEST", "CLASS@" + ("next" if c else "current"),
          "DEST@" + ("next" if d else "current"),
          "gaps", best[0], "/127",
          "train", sum(best[-1][:64]), "/64",
          "holdout", sum(best[-1][64:]), "/63",
          "order/codebooks", best[3:6])

assert { (r[1], r[2]): r[0] for r in
        (next(x for x in records if x[1:3] == (c,d)) for c,d in product((0,1), repeat=2)) } == {
           (0,0):80, (0,1):77, (1,0):84, (1,1):80
        }
winner = max(records, key=lambda x: sum(x[-1][:64]))
assert winner[1:6] == (1,0,"DEST-CLASS",(1,2,0),(0,1,2))
assert (sum(winner[-1][:64]), sum(winner[-1][64:])) == (47,37)

# These three stage gaps contain exactly two available metadata draws.
# The first has source-forced code 3 (reject), leaving too few draws for
# BOTH required accepted categories. This witnesses a causal impossibility
# for every codebook and either order, independent of the label alignment.
forced = [(i, mt.STARTS[i], mt.STARTS[i+1])
          for i, w in enumerate(windows)
          if len(w) == 2 and any(pair == (1,1) for pair in w)]
assert forced == [(22,170,176), (23,176,182), (77,582,588)], forced
print("CODE3_GAP6_HARD_WITNESSES", forced)
print("SOURCE_RANK", source.rank, "selected_coupon_bits_authenticated", 0)
print("ORIGINAL_K04_K08_UNCHANGED")
