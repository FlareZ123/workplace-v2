"""Independent Agent18 regression for H-17 K04 MT lane indexing.

The selected PS-0417 attempt-2 payload at raw row129 is metadata-checked and
skipped before its PAYLOAD bytes are decoded. This script independently
reconstructs the historical witness tuples and guards right/left lane offsets.
If SciPy is installed, it also reproduces the bounded integer stage checks.
"""
from __future__ import annotations

import collections
import hashlib
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK32 = 0xFFFFFFFF
TARGET_ROW = 129


def undo_right(value: int, shift: int) -> int:
    """Invert y = x ^ (x >> shift), recovering high bits first."""
    result = 0
    for bit in range(31, -1, -1):
        current = (value >> bit) & 1
        if bit + shift < 32:
            current ^= (result >> (bit + shift)) & 1
        result |= current << bit
    return result & MASK32


def undo_left(value: int, shift: int, mask: int) -> int:
    """Invert y = x ^ ((x << shift) & mask), recovering low bits first."""
    result = 0
    for bit in range(32):
        current = (value >> bit) & 1
        if bit - shift >= 0 and ((mask >> bit) & 1):
            current ^= (result >> (bit - shift)) & 1
        result |= current << bit
    return result & MASK32


def untemper(value: int) -> int:
    value = undo_right(value, 18)
    value = undo_left(value, 15, 0xEFC60000)
    value = undo_left(value, 7, 0x9D2C5680)
    return undo_right(value, 11)


def twist_pair(left: int, right: int) -> int:
    joined = (left & 0x80000000) | (right & 0x7FFFFFFF)
    return (joined >> 1) ^ (0x9908B0DF if right & 1 else 0)


def right_lane_offsets(p: int, i: int, q: int) -> tuple[int, int]:
    """p is the right input lane in twist_pair(native[r][p-1], native[r][p])."""
    assert p in (1, 2, 3)
    return 396 + p - i, 623 + p - q


def left_lane_offsets(p0: int, i: int, q: int) -> tuple[int, int]:
    """p0 is the left input lane; p0 = p - 1."""
    assert p0 in (0, 1, 2)
    return 397 + p0 - i, 624 + p0 - q


def verify_seeded_fixture() -> None:
    rng = random.Random(0x17A11CE)
    state = [untemper(rng.getrandbits(32)) for _ in range(1400)]
    for p in (1, 2, 3):
        p0 = p - 1
        i = q = p0
        t = p0
        assert state[t + 624] == (
            state[t + 397] ^ twist_pair(state[t], state[t + 1])
        )
        assert right_lane_offsets(p, i, q) == (397, 624)
        assert left_lane_offsets(p0, i, q) == (397, 624)
        # This is the specific old +1 error: p was treated as p0.
        assert (397 + p - i, 624 + p - q) == (398, 625)


def parse_source():
    raw = SPOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA256
    rows = [
        line for line in raw.decode("utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    assert len(rows) == 133
    native = []
    states = []
    for index, line in enumerate(rows):
        state_match = re.search(r"\bSTATE=(\w+)", line)
        assert state_match, index
        states.append(state_match.group(1))
        if index == TARGET_ROW:
            assert all(token in line for token in (
                "JOB=PS-261003-0417", "ATTEMPT=2", "STATE=ACK",
                "CLASS=RECOVER", "DEST=bench",
            ))
            # Deliberately do not parse or decode this row's PAYLOAD field.
            native.append(None)
            continue
        payload_match = re.search(r"\bPAYLOAD=([0-9A-F]{32})\b", line)
        assert payload_match, index
        payload = bytes.fromhex(payload_match.group(1))
        native.append(tuple(
            untemper(int.from_bytes(payload[offset:offset + 4], "little"))
            for offset in (0, 4, 8, 12)
        ))
    assert set(states) == {"ACK", "REQUESTED"}
    assert states[128] == states[130] == "REQUESTED"
    return native, states


def discover_witnesses(native):
    by_word = collections.defaultdict(list)
    for row_index, words in enumerate(native):
        if words is None:
            continue
        for lane, word in enumerate(words):
            by_word[word].append((row_index, lane))

    witnesses = []
    for r, words in enumerate(native):
        if words is None:
            continue
        for p in (1, 2, 3):
            mixed = twist_pair(words[p - 1], words[p])
            for k in range(r + 1, len(native)):
                if native[k] is None:
                    continue
                for i in range(4):
                    expected = mixed ^ native[k][i]
                    for l, q in by_word.get(expected, ()):
                        if l > k:
                            witnesses.append((r, p, k, i, l, q))
    return sorted(witnesses)


def interval_equations(witnesses):
    equations = []
    for r, p, k, i, l, q in witnesses:
        equations.append((r, k, 396 + p - i))
        equations.append((r, l, 623 + p - q))
    return equations


def solve_with_scipy(witnesses, states, ack_bounds, target_signature=None,
                     objective=None):
    try:
        import numpy as np
        from scipy.optimize import Bounds, LinearConstraint, milp
        from scipy.sparse import lil_matrix, csr_matrix
    except ImportError:
        return "scipy-unavailable", None

    equations = interval_equations(witnesses)
    if target_signature is not None:
        dk, dl, p, i, q = target_signature
        r = TARGET_ROW - dl
        k = r + dk
        assert 0 <= r < k < TARGET_ROW
        equations.extend((
            (r, k, 396 + p - i),
            (r, TARGET_ROW, 623 + p - q),
        ))

    matrix = lil_matrix((len(equations), 133), dtype=float)
    rhs = np.zeros(len(equations))
    for row_number, (start, end, value) in enumerate(equations):
        matrix[row_number, start:end] = 1
        rhs[row_number] = value

    lower = np.zeros(133)
    upper = np.zeros(133)
    for row_number, state in enumerate(states):
        if state == "ACK":
            lower[row_number], upper[row_number] = ack_bounds
        else:
            assert state == "REQUESTED"
            lower[row_number] = upper[row_number] = 0

    if objective is None:
        cost = np.zeros(133)
    else:
        cost = np.zeros(133)
        cost[:TARGET_ROW] = 1
        if objective == "max":
            cost *= -1
        else:
            assert objective == "min"

    result = milp(
        cost,
        integrality=np.ones(133, dtype=int),
        bounds=Bounds(lower, upper),
        constraints=LinearConstraint(csr_matrix(matrix), rhs, rhs),
        options={"time_limit": 30},
    )
    if result.status == 2:
        return "infeasible", None
    if result.status != 0:
        raise RuntimeError(f"MILP did not finish: {result.message}")
    value = round(result.fun)
    if objective == "max":
        value = -value
    return "optimal", value


def main() -> None:
    verify_seeded_fixture()
    native, states = parse_source()
    witnesses = discover_witnesses(native)
    assert len(witnesses) == 25, len(witnesses)
    signatures = sorted({
        (k - r, l - r, p, i, q)
        for r, p, k, i, l, q in witnesses
    })
    assert len(signatures) == 23, len(signatures)

    for r, p, k, i, l, q in witnesses:
        right = right_lane_offsets(p, i, q)
        left = left_lane_offsets(p - 1, i, q)
        assert right == left
        assert (397 + p - i, 624 + p - q) == (
            right[0] + 1, right[1] + 1
        )

    geometries = sorted({(k - r, l - r) for r, p, k, i, l, q in witnesses})
    assert geometries == [
        (52, 83), (53, 83), (53, 84), (53, 87), (54, 84)
    ]
    print("seeded_fixture=PASS")
    print("source_witnesses=25 unique_signatures=23")
    print(f"raw_row_geometries={geometries}")
    print("right_left_equivalence=PASS for all 25 tuples")
    print("old_right_lane_formula=+1 for all 25 tuples")

    status_min, minimum = solve_with_scipy(
        witnesses, states, (6, 9), objective="min"
    )
    status_max, maximum = solve_with_scipy(
        witnesses, states, (6, 9), objective="max"
    )
    if status_min == status_max == "scipy-unavailable":
        print("stage_interval=SKIPPED (SciPy unavailable)")
        return
    assert status_min == status_max == "optimal"
    assert (minimum, maximum) == (942, 955), (minimum, maximum)
    print(f"stage_interval_[ACK6,9]=[{minimum},{maximum}]")

    feasibility = collections.Counter()
    for signature in signatures:
        status, _ = solve_with_scipy(
            witnesses, states, (4, 100), target_signature=signature
        )
        feasibility[status] += 1
    assert feasibility == {"infeasible": 23}, feasibility
    print("target_signature_feasibility_[ACK4,100]=0/23")


if __name__ == "__main__":
    main()
