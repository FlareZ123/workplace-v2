"""SFT: two CPython 3-way metadata choices between p951 printer packets.

Source-only model exclusion, with genuine seeded two-choice rejection positive.
Depends on Agent49's symbolic p951 printer state and excludes selected row129.
"""
from __future__ import annotations
import hashlib
import itertools
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
from k04_p951_symbolic_basis import STARTS, get, source, temper

LABELS = ("LABEL", "RECOVER", "STORES")
DESTS = ("bench", "desk", "store")
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def gap_accepts(values: list[int | None], codes: dict[str, int], order: str) -> bool:
    """Two successive getrandbits(2) rejection loops, with no other draws."""
    for split in range(1, len(values)):
        for j, actual in enumerate(values):
            need = codes[order[0]] if j == split-1 else (codes[order[1]] if j == len(values)-1 else 3)
            if actual is not None and actual != need:
                break
        else:
            return True
    return False

def score(gaps, rows, label_idx, order, cperm, dperm):
    cmap = dict(zip(LABELS, cperm))
    dmap = dict(zip(DESTS, dperm))
    fits = [gap_accepts(gap, {"C": cmap[rows[i+label_idx][0]],
                              "D": dmap[rows[i+label_idx][1]]}, order)
            for i, gap in enumerate(gaps)]
    return sum(fits[:64]), sum(fits[64:])

def synthetic_positive():
    rng = random.Random(20261103)
    invc = {2: "LABEL", 0: "RECOVER", 1: "STORES"}
    invd = {1: "bench", 2: "desk", 0: "store"}
    starts, raw, rows = [], [], []
    def draw3():
        while True:
            word = rng.getrandbits(32)
            raw.append(word)
            if word >> 30 != 3:
                return word >> 30
    for _ in range(128):
        starts.append(len(raw))
        raw.extend(rng.getrandbits(32) for _ in range(4))
        rows.append((invc[draw3()], invd[draw3()]))
    gaps = [[w >> 30 for w in raw[starts[i]+4:starts[i+1]]] for i in range(127)]
    assert score(gaps, rows, 0, "CD", (2,0,1), (1,2,0)) == (64,63)
    masked = [[w if random.Random(0x4444+i*37+j*97).randrange(4) == 0 else None
               for j,w in enumerate(gap)] for i,gap in enumerate(gaps)]
    assert score(masked, rows, 0, "CD", (2,0,1), (1,2,0)) == (64,63)
    print("PASS genuine seeded 128-packet two-metadata source positive: full and masked")

def main():
    synthetic_positive()
    data = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == SOURCE_SHA
    rows = [(m.group(1).decode(), m.group(2).decode())
            for m in re.finditer(rb"CLASS=(\w+) PAYLOAD=[A-F0-9]{32} DEST=(\w+)", data)]
    assert len(rows) == len(STARTS) == 133
    basis, words = source(ROOT)
    assert basis.rank == 15365
    gaps = []
    fixed = 0
    for i in range(127):
        gap = []
        for pos in range(STARTS[i]+4, STARTS[i+1]):
            masks = temper(get(words, pos))
            high = (basis.predict(masks[30]), basis.predict(masks[31]))
            v = high[0] | (high[1] << 1) if all(t is not None for t in high) else None
            gap.append(v)
            fixed += v is not None
        gaps.append(gap)
    assert fixed == 124 and sum(map(len, gaps)) == 434
    findings = [(score(gaps, rows, idx, order, c, d), idx, order, c, d)
                for idx in (0,1) for order in ("CD","DC")
                for c in itertools.permutations(range(3))
                for d in itertools.permutations(range(3))]
    assert len(findings) == 144
    assert not any(s == (64,63) for s, *_ in findings)
    best = sorted(findings, reverse=True)[:5]
    assert best[0][0] == (47,32)
    print("ORIGINAL 124/434 full high2 gap outputs fixed, 310 remain unknown")
    print("ORIGINAL 144 candidate metadata/rejection rules, zero fits all 127 gaps")
    for rec in best: print("TOP", rec)
    print("Selected K04 event and authentic target hash UNREAD, no target bits")

if __name__ == "__main__":
    main()
