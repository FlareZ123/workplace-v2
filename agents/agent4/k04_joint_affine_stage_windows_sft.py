"""H17 K04: joint-affine rank at all possible fourword MT coupon windows.

Extends the conditional six printer geometries from Agent44 without using the
disputed selected ACK2 as an equation. Prior scan filtered windows by count of
individually unknown native bits and ignored relations between those bits.
Here preserve the complete affine *joint rank* of all 128 output bits.
Any rank<=12 window can be exhaustively reduced to complete K04 candidates.
Original source and commitments are only read, never modified.

Run from repository: python agents/agent4/k04_joint_affine_stage_windows_sft.py
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent44"))
import k04_p951_hidden_stage_coupon_sft as mt
import k04_six_stage_sft as six

MAX_RANK = 12
SOURCE = ROOT / "resources/evidence/print/spool-reconstruction.log"
ROUTING = ROOT / "resources/evidence/recovery-routing.json"
ACCEPTANCE = ROOT / "resources/acceptance.json"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"


def fail(message):
    raise AssertionError(message)


def project_window(expressions, source_basis, start):
    """128 affine reduced forms, ordered little-endian by native bit."""
    return [
        mt.reduce_row(expression << 1, source_basis)
        for word in expressions[start:start + 4]
        for expression in word
    ]


def exact_coordinates(residuals):
    """Map 128 original native bits onto independent GF2 coordinates.

    A residual is (free-variable coefficients << 1) | known parity. Each
    independent residual coefficient introduces an independent coordinate;
    dependent rows receive the XOR of their earlier coordinates.
    """
    pivots = {}
    forms = []
    base = 0
    for bit, residual in enumerate(residuals):
        base |= (residual & 1) << bit
        coefficients = residual >> 1
        coord = 0
        while coefficients:
            pivot = coefficients.bit_length() - 1
            entry = pivots.get(pivot)
            if entry is not None:
                coefficients ^= entry[0]
                coord ^= entry[1]
            else:
                number = len(pivots)
                assert number < 128
                pivots[pivot] = (coefficients, 1 << number)
                coord ^= 1 << number
                break
        forms.append(coord)
    deltas = [0] * len(pivots)
    for bit, form in enumerate(forms):
        while form:
            low = form & -form
            coordinate = low.bit_length() - 1
            deltas[coordinate] ^= 1 << bit
            form ^= low
    assert all(deltas)
    return base, deltas


def coupon_from_native(native):
    """Untempered GF2-native fourword state -> 16 complete printed bytes."""
    return b"".join(
        mt.temper((native >> (word * 32)) & 0xFFFFFFFF).to_bytes(4, "little")
        for word in range(4)
    )


def enumerate_coupons(base, deltas):
    """Gray-code enumeration, exactly 2^joint_rank distinct whole coupons."""
    native = base
    for index in range(1 << len(deltas)):
        if index:
            native ^= deltas[(index & -index).bit_length() - 1]
        yield coupon_from_native(native)


def input_rows():
    raw = SOURCE.read_bytes()
    assert sha256(raw).hexdigest() == SPOOL_SHA
    lines = [line for line in raw.decode("ascii").splitlines()
             if line.startswith("2026-")]
    assert len(lines) == 133
    original = [
        bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1))
        for line in lines
    ]
    assert original[129].hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
    return original


def source_rows(original):
    result = [
        [mt.untemper(word) for word in struct.unpack("<4I", payload)]
        for payload in original
    ]
    result[129] = []  # Never admit selected original target copy as source.
    return result


def controls_for_joint_rank(expressions, starts, original, rows, p):
    """Heldout real whole-packet positive, plus synthetic whole target."""
    if p != 951:
        return
    heldout = 66
    assert heldout not in (129,)
    blind_rows = [row[:] for row in rows]
    blind_rows[heldout] = []
    blind_basis = six.build_source_basis(expressions, blind_rows, starts)
    forms = project_window(expressions, blind_basis, starts[heldout])
    base, deltas = exact_coordinates(forms)
    assert len(deltas) == 1, (heldout, len(deltas))
    predicted = list(enumerate_coupons(base, deltas))
    assert len(predicted) == 2 and len(set(predicted)) == 2
    assert predicted.count(original[heldout]) == 1
    print("AUTHENTIC_WHOLE_ROW66_HELDOUT rank=1 candidates=2 actual_included=1", flush=True)

    # Two independent joint-coordinate bits with an exact complete SHA target,
    # avoiding self-assessed mere prefix correctness.
    source_basis = six.build_source_basis(expressions, rows, starts)
    stage = 888
    base, deltas = exact_coordinates(project_window(expressions, source_basis, stage))
    assert len(deltas) == 1
    coupons = list(enumerate_coupons(base, deltas))
    synthetic_target = sha256(coupons[-1]).digest()
    assert sum(sha256(candidate).digest() == synthetic_target for candidate in coupons) == 1
    print("PLANTED_WHOLE_STAGE888_POSITIVE rank=1 unique=1", flush=True)


def main():
    original = input_rows()
    rows = source_rows(original)
    route = json.loads(ROUTING.read_text())
    acceptance = json.loads(ACCEPTANCE.read_text())
    assert route["K04"]["masked_component"] == "8556C8CB6140A7F9A5123AC7571BEE1C"
    assert acceptance["slot_sha256"]["K04"] == TARGET
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = bytes.fromhex(TARGET)
    total = 0
    actual_hits = []
    over1 = 0
    control_ranks = {}
    for p, starts in sorted(six.GEOMETRIES.items()):
        assert starts[129] == p
        expressions = mt.state_expressions(starts[-1] + 3)
        basis = six.build_source_basis(expressions, rows, starts)
        rank_expected = {950:15366,951:15365,952:15367,953:15368,954:15365,955:15369}
        assert len(basis) == rank_expected[p]
        controls_for_joint_rank(expressions, starts, original, rows, p)
        hist = Counter()
        assignments = 0
        new_stages = []
        for stage in range(starts[-1] + 1):
            residuals = project_window(expressions, basis, stage)
            base, deltas = exact_coordinates(residuals)
            rank = len(deltas)
            hist[rank] += 1
            if rank <= MAX_RANK:
                if rank > 1:
                    new_stages.append((stage, rank))
                for coupon in enumerate_coupons(base, deltas):
                    component = bytes(x ^ y for x, y in zip(coupon, mask))
                    assignments += 1
                    if sha256(component).digest() == target:
                        actual_hits.append((p, stage, coupon.hex().upper(), component.hex().upper()))
                        print("ORIGINAL_K04_MATCH", actual_hits[-1], flush=True)
        assert sum(hist.values()) == starts[-1] + 1
        total += assignments
        over1 += sum(hist[r] for r in range(2, MAX_RANK + 1))
        control_ranks[p] = dict(sorted(hist.items()))
        print("GEOMETRY", p, "SOURCE_RANK", len(basis),
              "STAGE_JOINT_RANK_HIST", sorted(hist.items()),
              "NEW_JOINT_RANK2_TO12_WINDOWS", new_stages,
              "COMPLETE_ORIGINAL_CHECKS", assignments,
              "ORIGINAL_HITS_SO_FAR", len(actual_hits), flush=True)
    assert not actual_hits, "A candidate may be real; independently validate with original verifier"
    assert total >= 2389
    print("ALL_SIX_JOINT_RANK_COMPLETE max_rank", MAX_RANK,
          "source_stage_windows_new", over1,
          "complete_SHA256_original_checks", total,
          "original_hits", len(actual_hits),
          "controls", "PASS", flush=True)


if __name__ == "__main__":
    main()
