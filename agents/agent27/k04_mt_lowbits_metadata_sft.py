"""K04 conditional p951 metadata writer: low/native bit planes and controls.

Source-first, read-only historical printer test. Unlike the earlier tempered
highest-bit CPython randbelow(3) model, includes both lowest-bit and
untempered native-code consumers. No selected target bytes or K04 commitment.
"""
from itertools import permutations, product
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
import k04_p951_symbolic_basis as mt

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
basis, states = mt.source(ROOT)
assert basis.rank == 15365
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_text("ascii")
lines = [line for line in raw.splitlines() if line.startswith("2026-")]
assert len(lines) == 133
assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
labels = [re.search(r"CLASS=(\w+) PAYLOAD=[0-9A-F]{32} DEST=(\w+)", line).groups()
          for line in lines]
cl = [("LABEL", "RECOVER", "STORES").index(x) for x, y in labels]
dest = [("store", "desk", "bench").index(y) for x, y in labels]
perms = list(permutations(range(3)))

def fits(bits: tuple[int | None, ...], code: int) -> bool:
    return all(v is None or v == (code >> i) & 1 for i, v in enumerate(bits))

def two_call(window: list[tuple[int | None, ...]], a: int, b: int) -> bool:
    return any(all(fits(x, 3) for x in window[:cut])
               and fits(window[cut], a)
               and all(fits(x, 3) for x in window[cut + 1:-1])
               and fits(window[-1], b)
               for cut in range(len(window) - 1))

assert two_call([(1, 1), (0, 1), (1, 1), (1, 0)], 2, 1)
assert not two_call([(1, 1), (0, 1), (1, 1), (1, 0)], 1, 2)

def report(kind: str) -> None:
    bit_positions = range(2) if kind.endswith("_low") else range(30, 32)
    windows = []
    for i in range(127):
        q, nxt = mt.STARTS[i:i+2]
        window = []
        for stage in range(q + 4, nxt):
            native = mt.get(states, stage)
            v = mt.temper(native) if kind.startswith("tempered") else native
            window.append(tuple(basis.predict(v[j]) for j in bit_positions))
        windows.append(window)

    scores = {}
    for cls_at, dest_at in product((0, 1), repeat=2):
        best = 0
        for swap in (0, 1):
            for pc, pd in product(perms, repeat=2):
                successes = 0
                for i, window in enumerate(windows):
                    a, b = pc[cl[i + cls_at]], pd[dest[i + dest_at]]
                    if swap:
                        a, b = b, a
                    successes += two_call(window, a, b)
                best = max(best, successes)
        scores[(cls_at, dest_at)] = best
    hard = [i for i, window in enumerate(windows)
            if not any(two_call(window, a, b) for a, b in product(range(3), repeat=2))]
    print(kind, "best_by_binding", scores, "hard_codebook_free_gap_witnesses", len(hard),
          "first_hard_witnesses", hard[:10])
    assert max(scores.values()) == {
        "tempered_low": 71, "tempered_high": 84,
        "native_low": 66, "native_high": 62,
    }[kind]
    assert len(hard) == {
        "tempered_low": 29, "tempered_high": 23,
        "native_low": 32, "native_high": 34,
    }[kind]

def report_joint9(kind: str) -> None:
    positions = range(4) if kind.endswith("_low") else range(28, 32)
    hard = 0
    for i in range(127):
        q, nxt = mt.STARTS[i:i+2]
        window = []
        for stage in range(q+4, nxt):
            native = mt.get(states, stage)
            bits = mt.temper(native) if kind.startswith("tempered") else native
            window.append(tuple(basis.predict(bits[j]) for j in positions))
        # A single randbelow(9) draw must reject values 9..15 until
        # its final accepted 0..8, with no other-consuming draws.
        if (any(not any(fits(bits, k) for k in range(9,16))
                for bits in window[:-1])
            or not any(fits(window[-1], k) for k in range(9))):
            hard += 1
    print(kind, "joint9_hard_source_gaps", hard, "/127")
    assert hard == {
        "tempered_low": 51, "tempered_high": 39,
        "native_low": 61, "native_high": 60,
    }[kind]

for kind in ("tempered_low", "tempered_high", "native_low", "native_high"):
    report(kind)
    report_joint9(kind)
print("SOURCE_PASS RANK_15365 SELECTED_TARGET_WITHHELD")
