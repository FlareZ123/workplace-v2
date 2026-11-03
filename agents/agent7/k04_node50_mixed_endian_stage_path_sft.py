"""H-17 source-only conditional node50 stage-bridge rescue and target quotient.

Run from repository root with Python 3. Imports Agent 7 exact original
two-anchor verifier and Agent49 original spool symbolic state implementation.
The disputed printer ACK and both missing-slot commitments are excluded.
All source bytes are read-only. This is a SPECULATIVE writer architecture:
three CRC-valid recorder CONTROL fields interpreted in reversed byte order.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent7"))
from k04_node50_two_anchor_stratum_sft import (
    b, model, node, STAGES, local_constraints, pair_compatible,
    get, temper, untemper
)

SWAPPED = (28, 34, 35)
ORIGINAL_STAGES = {
    25:-677,26:-673,27:-666,28:-658,29:-652,30:-646,31:-640,
    32:-634,33:-630,34:-623,35:-609,36:-605,37:-598,38:-594,
    39:-585,40:-576,41:-568,
    42:-563,43:-552,44:-545,45:-540,46:-531,47:-523,
}


def swap4(x):
    return int.from_bytes(x.to_bytes(4, "little"), "big")


def observed(seq, changed):
    return swap4(node[seq]) if changed else node[seq]


def min_reversals(max_gap):
    """Exact DP for minimum per-record 32-bit byte reversals, seq25..41."""
    frontier = {(-677, 0): (0, 1)}
    for seq in range(26, 42):
        following = {}
        for (previous, previous_reversed), (cost, count) in frontier.items():
            first = local_constraints(observed(seq-1, previous_reversed), previous)
            assert first is not None
            for current in range(previous+4, min(-568, previous+max_gap)+1):
                if current not in STAGES or seq == 41 and current != -568:
                    continue
                for reversed_here in ((0,) if seq == 41 else (0, 1)):
                    output = observed(seq, reversed_here)
                    if local_constraints(output, current) is None:
                        continue
                    if not pair_compatible(first, output, current):
                        continue
                    candidate = (cost + reversed_here, count)
                    k = (current, reversed_here)
                    if k not in following or candidate[0] < following[k][0]:
                        following[k] = candidate
                    elif candidate[0] == following[k][0]:
                        following[k] = (candidate[0], following[k][1] + count)
        frontier = following
        if not frontier:
            return None, seq
    best = frontier[(-568, 0)]
    return best, 41


def put(rows, v, rhs):
    while v:
        pivot = v.bit_length() - 1
        if pivot not in rows:
            rows[pivot] = (v, rhs)
            return
        eq, bit = rows[pivot]
        v ^= eq
        rhs ^= bit
    assert rhs == 0, "combined source-state contradiction"


def predict(rows, v):
    rhs = 0
    while v:
        pivot = v.bit_length() - 1
        if pivot not in rows:
            return None
        eq, bit = rows[pivot]
        v ^= eq
        rhs ^= bit
    return rhs


assert b.rank == 15365
assert min_reversals(11)[0] is None
assert min_reversals(13)[0] is None
for gap in (14, 20, 40):
    best, stop = min_reversals(gap)
    assert stop == 41 and best[0] == 3
    print("min_reversed_control_fields", gap, best)

# A CONSTRUCTIVE joint state witness for all 23 original node50 CONTROL
# values at an observed-value-selected stage path. This does not
# authenticate a historical generator, emitter, stage or byte order.
rows = dict(b.rows)
for seq, stage in ORIGINAL_STAGES.items():
    native = untemper(observed(seq, seq in SWAPPED))
    for j, vec in enumerate(get(model, stage)):
        put(rows, vec, (native >> j) & 1)
assert len(rows) == 15927, len(rows)

# Four K04 native words at selected printer stage 951. Inserting all
# 128 possible bit equations measures the actual target quotient rank.
test = dict(rows)
for stage in range(951, 955):
    for vec in get(model, stage):
        while vec:
            pivot = vec.bit_length() - 1
            if pivot not in test:
                test[pivot] = (vec, 0)
                break
            vec ^= test[pivot][0]
assert len(test) - len(rows) == 127
fixed = [
    (stage, j) for stage in range(951, 955)
    for j, vec in enumerate(get(model, stage))
    if predict(rows, vec) is not None
]
assert fixed == [(951, 30)], fixed
print("joint_rank", len(rows), "source_rank_added", len(rows) - b.rank)
print("target_rank_remaining", len(test) - len(rows))
print("only_individual_selected_native_bit_fixed", fixed)
print("original_selected_ACK_excluded_from_all_source_constraints PASS")
