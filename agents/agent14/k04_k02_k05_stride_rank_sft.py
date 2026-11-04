"""Read-only K04 target-quotient geometry for noncontiguous selected K05 latches.

Derive the MT source linear spans from 132 original intact printer packets,
with selected printer row129 entirely omitted. K02 is a conditional donor at
native stage 1178 or 1405. Four hypothetical K05 word stages have the same
strictly increasing stride, with stage0 later than the K02 donor. The RHS of
each source equation is replaced by zero because the *rank* is value-invariant.
No K04 commitment, K04 copied ACK, or K08 source value is used in stage scans.

Run: python agents/agent14/k04_k02_k05_stride_rank_sft.py
"""
from collections import Counter
from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

mt.LAST = 3900
SOURCE = ROOT / "resources"
PINS = {
    "telemetry/freeze-export.jsonl": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
    "recorder/trip-recorder.raw": "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
}
for path, expected in PINS.items():
    assert hashlib.sha256((SOURCE / "evidence" / path).read_bytes()).hexdigest() == expected

base, symbolic = mt.source(SOURCE)
assert base.rank == 15365
base.rows = {pivot: (equation, 0) for pivot, (equation, _) in base.rows.items()}
target = [v for stage in range(951, 955) for v in mt.get(symbolic, stage)]


def extend(previous, stages):
    result = mt.Basis()
    result.rows = previous.rows.copy()
    result.rank = previous.rank
    for stage in stages:
        for equation in mt.get(symbolic, stage):
            result.insert(equation, 0)
    return result


def quotient(previous):
    result = mt.Basis()
    result.rows = previous.rows.copy()
    result.rank = previous.rank
    for equation in target:
        result.insert(equation, 0)
    return result.rank - previous.rank


strides = list(range(1, 33)) + [40, 48, 64, 97, 170, 227, 397, 624]
for donor in (1178, 1405):
    conditioned = extend(base, range(donor, donor + 4))
    assert conditioned.rank == 15493
    assert quotient(conditioned) == 33
    summary = Counter()
    reductions = []
    for stride in strides:
        for offset in range(97, 481):
            positions = [donor + offset + stride * latch for latch in range(4)]
            if positions[-1] > mt.LAST:
                continue
            result = extend(conditioned, positions)
            dimension = quotient(result)
            summary[dimension] += 1
            if dimension < 33:
                reductions.append((stride, offset, dimension))
    assert sum(summary.values()) == 15360
    expected = (
        [(227, 111, 32), (227, 169, 2), (227, 170, 31),
         (227, 338, 3), (227, 339, 30)]
        if donor == 1178 else
        [(227, 111, 3), (227, 112, 30),
         (227, 338, 3), (227, 339, 30)]
    )
    assert reductions == expected, (donor, reductions)
    print("DONOR", donor, "SOURCE_RANK", conditioned.rank,
          "SCANNED", sum(summary.values()),
          "DIMENSIONS", dict(sorted(summary.items())),
          "REDUCED", reductions)

# Wider twist-phase scan: eight different K02 donor generations, every
# possible first-K05 stage from 1041 through 2401, K05 latch stride 227.
# The rank screen uses no original K02/K05 RHS or K04 acceptance feedback.
low = []
for generation in range(1, 9):
    donor = 951 + 227 * generation
    source = extend(base, range(donor, donor + 4))
    for first in range(1041, 2402):
        result = extend(source, [first + 227*i for i in range(4)])
        dimension = quotient(result)
        if dimension <= 16:
            low.append((donor, first, dimension))
expected_low = [
    (1178, 1120, 2), (1178, 1347, 2), (1178, 1516, 3),
    (1178, 1743, 3), (1178, 2139, 4),
    (1405, 1120, 2), (1405, 1347, 2), (1405, 1516, 3),
    (1405, 1743, 3), (1405, 2139, 4),
]
assert low == expected_low, low
print("TWIST_PHASE_SCAN", 8 * (2402 - 1041), "LOW_DIMENSION", low)
print("SOURCE-ONLY RANK GEOMETRY PASS; K04, K08 VALUES STILL UNKNOWN")
