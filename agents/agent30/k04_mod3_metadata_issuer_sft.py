#!/usr/bin/env python3
"""Source-only complete-word modulo-3 printer metadata issuer test.

Conditional p951 MT chronology; K04 selected coupon and K08 unused.
"""
from __future__ import annotations

from itertools import permutations, product
from pathlib import Path
import hashlib
import random
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
import k04_p951_symbolic_basis as mt

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
labels = re.findall(rb"CLASS=(\w+) PAYLOAD=[0-9A-F]{32} DEST=(\w+)", raw)
assert len(labels) == len(mt.STARTS) == 133
assert labels[129] == (b"RECOVER", b"bench")
classes = (b"LABEL", b"RECOVER", b"STORES")
dests = (b"store", b"desk", b"bench")
cls = [classes.index(c) for c, d in labels]
dst = [dests.index(d) for c, d in labels]

def source_words(basis, bank):
    known = []
    for i in range(127):
        q, qnext = mt.STARTS[i:i + 2]
        window = []
        for pos in range(q + 4, qnext):
            bits = [basis.predict(expr) for expr in mt.temper(mt.get(bank, pos))]
            window.append(None if None in bits else sum(bit << j for j, bit in enumerate(bits)))
        assert len(window) >= 2
        known.append(window)
    return known

def compatible(window, needed, side):
    pair = window[:2] if side == "first" else window[-2:]
    return all(v is None or v % 3 == label for v, label in zip(pair, needed))

source, bank = mt.source(ROOT)
assert source.rank == 15365
windows = source_words(source, bank)
assert sum(map(len, windows)) == 434
assert sum(v is not None for w in windows for v in w) == 124
codes = list(permutations(range(3)))
for side, expected in (("first", 94), ("last", 96)):
    scores = []
    for cls_at, dst_at in product((0, 1), repeat=2):
        for swap in (False, True):
            for pc, pd in product(codes, repeat=2):
                matches = 0
                for i, window in enumerate(windows):
                    c, d = pc[cls[i + cls_at]], pd[dst[i + dst_at]]
                    needed = (d, c) if swap else (c, d)
                    matches += compatible(window, needed, side)
                scores.append((matches, cls_at, dst_at, swap, pc, pd))
    top = max(scores)
    assert len(scores) == 288 and top[0] == expected, (side, top)
    print(f"ORIGINAL {side}: best {top[0]}/127; "
          f"{127-top[0]} source-forced contradictions; "
          f"cls_at={top[1]} dst_at={top[2]} swap={top[3]}")

# Genuine CPython native MT stream with synthetic metadata and the original
# stage layout; only 132 synthetic intact printer packets constrain the basis.
g = random.Random(839431)
produced = [g.getrandbits(32) for _ in range(967)]
planted = mt.Basis()
for row, q in enumerate(mt.STARTS):
    if row == 129:
        continue
    for lane in range(4):
        native = mt.untemper(produced[q + lane])
        for j, expr in enumerate(mt.get(bank, q + lane)):
            planted.insert(expr, (native >> j) & 1)
assert planted.rank == 15365
synthetic_windows = source_words(planted, bank)
assert all(compatible(w, (produced[mt.STARTS[i] + 4] % 3,
                          produced[mt.STARTS[i] + 5] % 3), "first")
           for i, w in enumerate(synthetic_windows))
print("SYNTHETIC 127/127 genuine seeded MT getrandbits(32)%3 metadata PASS")
print("No original selected physical coupon bits or author-final K08 words.")
