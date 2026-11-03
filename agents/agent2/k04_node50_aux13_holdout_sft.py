"""H17: full AUX13 node50 source-control/latch holdout, exact permutation null.

Read-only reproducible original-source experiment. Run from repository root:
    python agents/agent2/k04_node50_aux13_holdout_sft.py

Uses existing source-pinned exact p951 conditional MT basis and previous Agent2
full-word quotient functions. The disputed K04 selected row is omitted.
"""
from fractions import Fraction
from itertools import combinations
from math import comb, factorial
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import source, get, temper, untemper, Basis
from k04_node50_full_syndrome_gap_sft import (
    recorder_controls, quotient, compatible, add_equations,
)

# Previously source-selected stages, unchanged for all nonanchor AUX tests.
ANCHORS = {
    7: -810, 9: -793, 12: -775, 13: -769, 14: -759,
    24: -683, 25: -677, 41: -568, 43: -552, 44: -545,
    45: -540, 61: -417, 63: -397, 64: -390, 70: -339,
}


def bounds(seq):
    low, high = -950, -251
    for i, stage in ANCHORS.items():
        if seq < i:
            low = max(low, stage - 11 * (i - seq))
            high = min(high, stage - 4 * (i - seq))
        elif seq > i:
            low = max(low, stage + 4 * (seq - i))
            high = min(high, stage + 11 * (seq - i))
        else:
            low = high = stage
    assert low <= high
    return low, high


def recorder_fields():
    """Extract original CRC-valid CONTROL, latch, AUX and event from node50."""
    import hashlib
    import struct
    import zlib
    raw = (ROOT / "resources/evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
    )
    result = {}
    for i in range(88):
        row = raw[16 + 24*i:16 + 24*(i+1)]
        _, node, event, latch, seq, control, aux, crc = struct.unpack(
            "<IHBBIIII", row
        )
        if node == 50:
            assert zlib.crc32(row[:20]) == crc
            result[seq] = (control, latch, aux, event)
    assert set(result) == set(range(72))
    return result


def full_source_bits(basis, stages):
    """Compute source-fixed MT output bits independent of all AUX observations."""
    mask, value = {}, {}
    for stage in stages:
        fixed, actual = 0, 0
        for bit, expression in enumerate(temper(get(VECTORS, stage))):
            predicted = basis.predict(expression)
            if predicted is not None:
                fixed |= 1 << bit
                actual |= predicted << bit
        mask[stage], value[stage] = fixed, actual
    return mask, value


def all_choices(basis, vectors, records):
    global VECTORS
    VECTORS = vectors
    mask, value = full_source_bits(basis, range(-815, -330))
    controls = {stage: [quotient(basis, x) for x in get(vectors, stage)]
                for stage in range(-810, -338)}
    options = {}
    for seq in range(7, 71):
        if seq in ANCHORS:
            continue
        low, high = bounds(seq)
        control, latch, _, _ = records[seq]
        native = untemper(control)
        codes = {}
        for stage in range(low, high+1):
            if not compatible(controls[stage], native):
                continue
            latch_mask = mask[stage-1] >> 29
            latch_value = value[stage-1] >> 29
            if (latch ^ latch_value) & latch_mask:
                continue
            for rejections in range(4):
                aux_stage = stage + 1 + rejections
                if any(
                    (value[p] >> 19 | (((1 << 13) - 1) ^ (mask[p] >> 19))) < 6000
                    for p in range(stage+1, aux_stage)
                ):
                    continue
                aux_mask = mask[aux_stage] >> 19
                aux_value = value[aux_stage] >> 19
                if aux_mask == 8191 and aux_value < 6000:
                    details = (stage, rejections, latch_mask.bit_count())
                    codes.setdefault(aux_value, []).append(details)
        options[seq] = codes
    return options, controls, mask, value


def rook_polynomial(edges):
    """Nonattacking match counts in exact row-to-AUX-pool bipartite graph."""
    result = []
    for k in range(len(edges)+1):
        count = 0
        for selection in combinations(edges, k):
            if (len({x[0] for x in selection}) == k
                    and len({x[1] for x in selection}) == k):
                count += 1
        result.append(count)
        if count == 0 and k > 5:
            break
    while result and result[-1] == 0:
        result.pop()
    return result


def exact_tail(rook, n, threshold):
    """Exact distribution tail from the rook polynomial factorial moments."""
    total = Fraction(0)
    for k in range(threshold, len(rook)):
        falling = factorial(n) // factorial(n-k)
        total += (
            (-1)**(k-threshold) * comb(k-1, threshold-1)
            * Fraction(rook[k], falling)
        )
    return total


def main():
    basis, vectors = source(ROOT / "resources")
    assert basis.rank == 15365
    records = recorder_fields()
    assert [records[i][0] for i in range(72)] == [
        recorder_controls()[i] for i in range(72)
    ]
    choices, quotients, mask, value = all_choices(basis, vectors, records)
    actual = {seq: records[seq][2]-2000 for seq in choices}
    hits = {seq: (code, choices[seq][code]) for seq, code in actual.items()
            if code in choices[seq]}
    assert sorted(hits) == [39, 42, 54, 55], hits
    assert value[-583] >> 19 == 1318
    assert value[-584] >> 19 == 7511
    assert (mask[-583] >> 19) == 8191
    assert (mask[-584] >> 19) == 8191
    assert not (
        (mask[-586] >> 29)
        & (records[39][1] ^ (value[-586] >> 29))
    )
    assert actual[39]+1 not in choices[39]

    # Seq39 AUX and source-fixed latch alone select the CONTROL stage.
    # The original seq39 CONTROL is held out until that selection is frozen.
    aux_first = []
    seq = 39
    low, high = bounds(seq)
    for stage in range(low, high+1):
        latch_mask = mask[stage-1] >> 29
        if not latch_mask or (
            (records[seq][1] ^ (value[stage-1] >> 29)) & latch_mask
        ):
            continue
        for rej in range(4):
            at = stage + 1 + rej
            if any(
                (value[p] >> 19 | (((1 << 13)-1) ^ (mask[p] >> 19))) < 6000
                for p in range(stage+1, at)
            ):
                continue
            if mask[at] >> 19 == 8191 and value[at] >> 19 == actual[seq]:
                aux_first.append(stage)
    assert aux_first == [-585], aux_first
    native = untemper(records[seq][0])
    assert compatible(quotients[-585], native)
    inserted = add_equations({}, [
        (eq, rhs ^ ((native >> bit) & 1))
        for bit, (eq, rhs) in enumerate(quotients[-585])
    ])
    assert len(inserted) == 29  # 32 original CONTROL bits, 3 withheld parity checks

    # Exact conditional permutation null: fix CONTROL and latch and all
    # possible stages, permute the original 49 nonanchor AUX labels.
    edges = [
        (seq, orig) for seq, codes in choices.items()
        for orig, code in actual.items() if code in codes
    ]
    assert len(choices) == 49 and len(edges) == 14
    assert len(set(actual.values())) == 49
    rook = rook_polynomial(edges)
    assert rook == [1, 14, 65, 132, 120, 40], rook
    probability = exact_tail(rook, len(choices), len(hits))
    assert probability == Fraction(131, 5720652), probability

    # One source-compatible stage representative for the four AUX-positive
    # nonanchors, chosen without using the selected K04 packet or its hash.
    stage_assignments = {39: -585, 42: -562, 54: -459, 55: -452}
    joint = Basis()
    joint.rows = dict(basis.rows)
    joint.rank = basis.rank
    for seq, stage in stage_assignments.items():
        native = untemper(records[seq][0])
        for bit, expression in enumerate(get(vectors, stage)):
            joint.insert(expression, (native >> bit) & 1)
    target = Basis()
    target.rows = {i: (v, 0) for i, (v, _) in joint.rows.items()}
    target.rank = joint.rank
    for stage in range(951, 955):
        for equation in get(vectors, stage):
            target.insert(equation, 0)
    assert target.rank - joint.rank == 128

    print("ORIGINAL spool, recorder SHA and CRC: PASS")
    print("conditional printer rank:", basis.rank)
    print("nonanchor record count:", len(choices))
    print("13-bit exact AUX original matches:", sorted(hits))
    print("seq39 stage=-585; AUX -584 rejects code7511, -583 accepts code1318")
    print("seq39 source-fixed AUX 13/13, latch 2/2, held-out CONTROL parity 3/3")
    print("nonanchor source-permutation edges:", len(edges))
    print("exact rook polynomial:", rook)
    print("P(at least four):", str(probability), "=", float(probability))
    print("four CONTROL source rank:", joint.rank)
    print("selected K04 native unknown bits:", target.rank-joint.rank)
    print("original K04/K08 recovered: NO")


if __name__ == "__main__":
    main()
