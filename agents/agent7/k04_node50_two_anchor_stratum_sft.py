"""H-17 exact two-anchor node50 control-schedule gate, selected K04 excluded.

Uses the same source-only p951 MT geometry as the published Agent49 module.
Evaluates 17 original CRC-valid node50 CONTROL words between two native
stage anchors, with monotone gap 4..maxgap and exact pairwise MT equations.
No selected spool ACK, K04 or K08 commitment, mask, or final phrase is read.
"""
import hashlib
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent49"))
from k04_p951_symbolic_basis import source, get, untemper, temper

REC = (ROOT / "resources/evidence/recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(REC).hexdigest() == (
    "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
)
b, model = source(ROOT / "resources")
assert b.rank == 15365

node = {}
for i in range(88):
    record = REC[16 + 24*i:16 + 24*(i+1)]
    ts, nid, event, latch, seq = struct.unpack_from("<IHBBI", record)
    if nid == 50:
        control, aux, crc = struct.unpack_from("<III", record, 12)
        assert zlib.crc32(record[:20]) == crc
        node[seq] = control
assert sorted(node) == list(range(72))

STAGES = range(-677, -567)
ANCHORS = {25: -677, 41: -568}

# Reduce each native state bit against the exact intact-spool source basis.
reduced = {}
for stage in STAGES:
    equations = []
    for vec in get(model, stage):
        constant = 0
        while vec:
            pivot = vec.bit_length() - 1
            if pivot not in b.rows:
                break
            v, bit = b.rows[pivot]
            vec ^= v
            constant ^= bit
        equations.append((vec, constant))
    reduced[stage] = equations


def local_constraints(value, stage):
    """32 native bits modulo the original source, or None if contradictory."""
    native = untemper(value)
    rows = {}
    for bit_index, (vec, constant) in enumerate(reduced[stage]):
        bit = ((native >> bit_index) & 1) ^ constant
        while vec:
            pivot = vec.bit_length() - 1
            if pivot not in rows:
                rows[pivot] = (vec, bit)
                break
            v, rhs = rows[pivot]
            vec ^= v
            bit ^= rhs
        if not vec and bit:
            return None
    return rows


def pair_compatible(left_basis, value, stage):
    """Reject a concrete two-word pair if exact source GF2 parity disagrees."""
    native = untemper(value)
    for bit_index, (vec, constant) in enumerate(reduced[stage]):
        bit = ((native >> bit_index) & 1) ^ constant
        while vec:
            pivot = vec.bit_length() - 1
            if pivot not in left_basis:
                break
            v, rhs = left_basis[pivot]
            vec ^= v
            bit ^= rhs
        if not vec and bit:
            return False
    return True


def count_paths(observed, max_gap):
    """Count bounded stage paths with source and consecutive-word consistency."""
    frontier = {-677: 1}
    for seq in range(25, 41):
        next_frontier = {}
        for stage, paths in frontier.items():
            lhs = local_constraints(observed[seq], stage)
            if lhs is None:
                continue
            for next_stage in range(stage + 4, min(stage + max_gap, -568) + 1):
                if next_stage not in reduced:
                    continue
                if seq + 1 == 41 and next_stage != -568:
                    continue
                if local_constraints(observed[seq + 1], next_stage) is None:
                    continue
                if not pair_compatible(lhs, observed[seq + 1], next_stage):
                    continue
                next_frontier[next_stage] = next_frontier.get(next_stage, 0) + paths
        frontier = next_frontier
        if not frontier:
            return 0, seq + 1
    return sum(frontier.values()), 41


for seq, stage in ANCHORS.items():
    assert local_constraints(node[seq], stage) is not None
    assert all(vec == 0 for vec, _ in reduced[stage])

for bound, last in ((11, 28), (14, 33), (17, 37),
                    (20, 38), (30, 38), (40, 38)):
    count, stop = count_paths(node, bound)
    assert (count, stop) == (0, last), (bound, count, stop)
    print(f"ORIGINAL seq25-41 maximum_gap={bound} full_paths={count} stop_seq={stop}")

# Positive control: complete one actual MT-state representative satisfying
# every intact printer equation. Mint all 17 synthetic recorder values at
# thirteen seven-draw and three six-draw gaps; retain real endpoint values.
state = 0
for pivot in sorted(b.rows):
    equation, rhs = b.rows[pivot]
    if rhs ^ ((equation & state).bit_count() % 2):
        state |= 1 << pivot


def source_value(stage):
    return sum((((equation & state).bit_count() % 2) << bit_index)
               for bit_index, equation in enumerate(temper(get(model, stage))))


synthetic = dict(node)
positions = [-677]
for gap in [6]*3 + [7]*13:
    positions.append(positions[-1] + gap)
assert len(positions) == 17 and positions[-1] == -568
for offset, stage in enumerate(positions):
    synthetic[25 + offset] = source_value(stage)
assert synthetic[25] == node[25] and synthetic[41] == node[41]
synthetic_paths, stop = count_paths(synthetic, 7)
assert synthetic_paths > 0 and stop == 41
print(f"SYNTHETIC exact original-source MT positive: PASS {synthetic_paths} paths")
print("No authenticated selected original K04 coupon or K08 final words")
