"""Read-only original-source SFT: late MT stage-shift quotient for missing K04.

Depends on two existing, source-pinned standard-library modules from agents 23/49.
Does not consume the disputed original ACK2 coupon, K04 mask or hash.
"""
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent23"))
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_mt_stagefree_gap_bounds_sft import relations
from k04_p951_symbolic_basis import Basis, STARTS, get, packets, untemper, words


def components(edges):
    parents = list(range(len(STARTS)))

    def find(i):
        while parents[i] != i:
            i = parents[i]
        return i

    for a, b, _ in edges:
        parents[find(a)] = find(b)
    groups = defaultdict(list)
    for i in range(len(STARTS)):
        groups[find(i)].append(i)
    return groups, find


def source_rank_and_target_quotient(starts, original, symbolic):
    basis = Basis()
    try:
        for row, packet in enumerate(original):
            if row == 129:
                continue
            for lane in range(4):
                native = untemper(int.from_bytes(packet[4 * lane:4 * lane + 4], "little"))
                for bit, expression in enumerate(get(symbolic, starts[row] + lane)):
                    basis.insert(expression, (native >> bit) & 1)
    except AssertionError:
        return None  # Complete original-source incompatibility, no target inference.

    # Quotient dimension of the withheld 128 physical bits modulo only the
    # authentic, selected-withheld printer rows in this candidate chronology.
    # A rank-only copy avoids assigning artificial target bit values.
    rows = {pivot: expression for pivot, (expression, value) in basis.rows.items()}
    increment = 0
    individually_fixed = 0
    for lane in range(4):
        for expression in get(symbolic, starts[129] + lane):
            if basis.predict(expression) is not None:
                individually_fixed += 1
            x = expression
            while x:
                pivot = x.bit_length() - 1
                if pivot not in rows:
                    rows[pivot] = x
                    increment += 1
                    break
                x ^= rows[pivot]
    return basis.rank, increment, individually_fixed


def main():
    original, selected = packets(ROOT)
    assert selected == 129 and len(original) == 133 and original[129] == b""
    source = (ROOT / "resources" / "evidence" / "print" / "spool-reconstruction.log").read_bytes()
    edges = relations(source)
    assert len(edges) == 49
    assert all(STARTS[b] - STARTS[a] == delta for a, b, delta in edges)

    groups, find = components(edges)
    focus = [groups[find(row)] for row in (127, 128, 129, 130, 132)]
    assert len({tuple(group) for group in focus}) == 5
    baseline = STARTS[:]
    symbolic = words()
    assert source_rank_and_target_quotient(baseline, original, symbolic) == (15365, 128, 0)

    admissible = 0
    consistent = []
    for shifts in product(range(-3, 4), repeat=5):
        starts = baseline[:]
        for group, step in zip(focus, shifts):
            for row in group:
                starts[row] += step
        if starts[0] != 0 or any(b - a < 4 for a, b in zip(starts, starts[1:])):
            continue
        if not all(starts[b] - starts[a] == delta for a, b, delta in edges):
            raise AssertionError("Shifting a linked component violated its exact relation")
        admissible += 1
        result = source_rank_and_target_quotient(starts, original, symbolic)
        if result is not None:
            consistent.append((shifts, starts[129], *result))

    assert admissible == 196, admissible
    assert len(consistent) == 21, consistent
    stage_counts = Counter(p for shifts, p, rank, deficit, known in consistent)
    quotient_counts = Counter(deficit for shifts, p, rank, deficit, known in consistent)
    assert stage_counts == {950: 6, 951: 9, 952: 6}, stage_counts
    assert quotient_counts == {128: 21}, quotient_counts
    assert all(rank == 15365 and known == 0 for shifts, p, rank, deficit, known in consistent)

    print("SOURCE EXACT RELATIONS", len(edges), "SELECTED-WITHHELD")
    print("LATE COMPONENTS", focus)
    print("GAP-VALID SCHEDULES", admissible)
    print("WHOLE-SOURCE-CONSISTENT SCHEDULES", len(consistent))
    print("SELECTED STAGES", dict(sorted(stage_counts.items())))
    print("TARGET QUOTIENT", dict(sorted(quotient_counts.items())))
    print("RESULT: 21 historical-source-compatible late geometries, zero selected bits recovered.")


if __name__ == "__main__":
    main()
