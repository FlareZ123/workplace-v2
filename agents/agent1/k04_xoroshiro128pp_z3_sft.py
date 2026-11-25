#!/usr/bin/env python3
"""Direct-borrow first-pair inversion for the H-17 K04 xoroshiro128++ hypothesis.

The first output determines u0=ROTR(y0-a0,17). A bitwise borrow chain derives
t0=a0 XOR b0 from u0 and the sole 64-bit unknown a0. A second borrow chain
expresses the y1 constraint without either 64-bit output addition. The selected
18:02 ACK payload is withheld from fitting.

Every complete middle candidate is replayed, masked, and checked against the
original K04 commitment before any holdout or uniqueness disposition. The 18:03
REQUESTED packet is a blind diagnostic for the first unconditioned model only.
"""
import argparse
import hashlib
import json
import random
import re
import time
from pathlib import Path

from z3 import BitVec, BitVecVal, Concat, Extract, Or, RotateLeft, RotateRight, Then, sat, unsat, unknown

MASK = (1 << 64) - 1
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SEED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)
MAX_MIDDLE_MODELS = 8
MAX_TOTAL_SOLVE_SECONDS = 300
ROOT = Path(__file__).resolve().parents[2] / "resources"

# Public CI output must never contain a raw 128-bit candidate, 64-bit state
# word, component, or other reversible recovery value.
PUBLIC_FORBIDDEN_KEYS = {
    "sum_state0", "initial_state", "middle_words", "predicted_middle_words",
    "predicted_later_words", "predicted_coupon_hex", "predicted_component_hex",
    "coupon_hex", "component_hex", "state_hex", "generated_hex", "middle_hex",
    "observed_flank_words", "component_sha256", "target_sha256",
}

def assert_public_safe(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in PUBLIC_FORBIDDEN_KEYS:
                raise AssertionError(f"unsafe public output field: {key}")
            assert_public_safe(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            assert_public_safe(item)
    elif isinstance(value, str) and re.fullmatch(r"(?:[0-9A-Fa-f]{16}|[0-9A-Fa-f]{32})", value):
        raise AssertionError("unsafe raw 64/128-bit value in public output")

def emit_public_result(value):
    assert_public_safe(value)
    print(json.dumps(value, sort_keys=True), flush=True)



def rol(x, n):
    return ((x << n) | (x >> (64 - n))) & MASK


def ror(x, n):
    return ((x >> n) | (x << (64 - n))) & MASK


def subtract_with_borrow(minuend, subtrahend):
    """Exact 64-bit subtraction using the direct one-bit borrow recurrence."""
    borrow = 0
    result = 0
    for i in range(64):
        ui = (minuend >> i) & 1
        ai = (subtrahend >> i) & 1
        result |= (ui ^ ai ^ borrow) << i
        borrow = ((1 - ui) & ai) | (((1 - ui) | ai) & borrow)
    return result


def direct_borrow_t0(y0, a0):
    """Recover t0=a0 XOR b0 from the first output and a0, without 64-bit add."""
    u0 = ror((y0 - a0) & MASK, 17)
    borrow = 0
    t0 = 0
    for i in range(64):
        ui = (u0 >> i) & 1
        ai = (a0 >> i) & 1
        t0 |= (ui ^ borrow) << i
        borrow = ((1 - ui) & ai) | (((1 - ui) | ai) & borrow)
    return t0


def stream(state, count=6):
    a, b = state
    out = []
    for _ in range(count):
        total = (a + b) & MASK
        out.append((rol(total, 17) + a) & MASK)
        t = a ^ b
        a, b = (rol(a, 49) ^ t ^ (t << 21)) & MASK, rol(t, 28)
    return out


def z3_step(a, b):
    t = a ^ b
    return RotateLeft(a, 49) ^ t ^ (t << 21), RotateLeft(t, 28)


def z3_output(a, b):
    return RotateLeft(a + b, 17) + a


def borrow_next(x, y, prior):
    # One-bit exact subtraction borrow recurrence: MAJ(~x, y, prior).
    return (~x & y) | ((~x | y) & prior)


def inverse_first_pair(y0, y1, variable_name="first_a0"):
    """Return (a0, t0, constraints, (a1,b1)) for two successive outputs.

    The only free bit-vector is a0. Both 64-bit additions in the forward
    output function are eliminated into exact subtraction/borrow constraints.
    """
    a0 = BitVec(variable_name, 64)
    u0 = RotateRight(BitVecVal(y0, 64) - a0, 17)
    r0 = BitVecVal(0, 1)
    t_bits = []
    for i in range(64):
        ui, ai = Extract(i, i, u0), Extract(i, i, a0)
        t_bits.append(ui ^ r0)
        if i < 63:
            r0 = borrow_next(ui, ai, r0)
    t0 = Concat(*reversed(t_bits))

    a1 = RotateLeft(a0, 49) ^ t0 ^ (t0 << 21)
    b1 = RotateLeft(t0, 28)
    u1 = RotateRight(BitVecVal(y1, 64) - a1, 17)
    r1 = BitVecVal(0, 1)
    diff_bits = []
    for i in range(64):
        ui, ai = Extract(i, i, u1), Extract(i, i, a1)
        diff_bits.append(ui ^ ai ^ r1)
        if i < 63:
            r1 = borrow_next(ui, ai, r1)
    required_b1 = Concat(*reversed(diff_bits))
    return a0, t0, [required_b1 == b1], (a1, b1)


def decode(packet, view):
    endian = "little" if view & 1 else "big"
    words = [int.from_bytes(packet[i:i + 8], endian) for i in (0, 8)]
    return words[::-1] if view & 2 else words


def encode(words, view):
    endian = "little" if view & 1 else "big"
    words = list(words)
    if view & 2:
        words.reverse()
    return b"".join(int(x).to_bytes(8, endian) for x in words)


def self_test():
    rng = random.Random(0x50D0A11)
    tests = [SEED] + [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(100)]
    for state in tests:
        outputs = stream(state, 6)
        y0, y1 = outputs[:2]
        t0 = direct_borrow_t0(y0, state[0])
        recovered_b0 = state[0] ^ t0
        assert t0 == (state[0] ^ state[1])
        assert recovered_b0 == state[1]
        a1, b1 = (rol(state[0], 49) ^ t0 ^ (t0 << 21)) & MASK, rol(t0, 28)
        u1 = ror((y1 - a1) & MASK, 17)
        assert subtract_with_borrow(u1, a1) == b1
        assert stream((state[0], recovered_b0), 6) == outputs
    for probe in ("0123456789ABCDEF", "00112233445566778899AABBCCDDEEFF"):
        try:
            assert_public_safe({"synthetic_probe": probe})
        except AssertionError:
            pass
        else:
            raise AssertionError("public output guard accepted a raw 64/128-bit value")
    try:
        assert_public_safe({"predicted_coupon_hex": "synthetic"})
    except AssertionError:
        pass
    else:
        raise AssertionError("public output guard accepted a forbidden candidate field")
    emit_public_result({
        "self_test": "PASS",
        "algebraic_unknown_bits": 64,
        "randomized_inverse_cases": len(tests),
        "first_output_exactly_eliminated": True,
        "second_output_borrow_constraint_replayed": True,
    })


def _remaining(deadline, per_check):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return 0.0
    return min(float(per_check), remaining)


def parse_source():
    path = ROOT / "evidence/print/spool-reconstruction.log"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = {}
    for line in raw.decode("ascii").splitlines():
        if line.startswith("2026-"):
            stamp, *fields = line.split()
            rows[stamp] = dict(x.split("=", 1) for x in fields)
    assert len(rows) == 133
    trio = [rows[f"2026-10-03T18:0{minute}:00Z"] for minute in (1, 2, 3)]
    assert all(x["JOB"] == "PS-261003-0417" and x["CLASS"] == "RECOVER" for x in trio)
    assert [(x["ATTEMPT"], x["STATE"]) for x in trio] == [
        ("1", "REQUESTED"), ("2", "ACK"), ("3", "REQUESTED")
    ]
    return [bytes.fromhex(x["PAYLOAD"]) for x in trio]


def solve_first_pair(first, holdout, ack2_payload, view, timeout_seconds,
                     check_candidate=True, expected_middle=None,
                     max_middle_models=MAX_MIDDLE_MODELS):
    started = time.monotonic()
    deadline = started + MAX_TOTAL_SOLVE_SECONDS
    y0, y1 = first
    a0_expr, t0_expr, inverse_constraints, (a1_expr, b1_expr) = inverse_first_pair(y0, y1)
    a2_expr, b2_expr = z3_step(a1_expr, b1_expr)
    y2_expr = z3_output(a2_expr, b2_expr)
    a3_expr, b3_expr = z3_step(a2_expr, b2_expr)
    y3_expr = z3_output(a3_expr, b3_expr)
    a4_expr, b4_expr = z3_step(a3_expr, b3_expr)
    y4_expr = z3_output(a4_expr, b4_expr)
    a5_expr, b5_expr = z3_step(a4_expr, b4_expr)
    y5_expr = z3_output(a5_expr, b5_expr)
    middle_exprs = (y2_expr, y3_expr)
    holdout_exprs = (y4_expr, y5_expr)

    # Bit-blast the direct-borrow inverse core; the middle/holdout expressions
    # are added only for model replay and distinct-middle blocking.
    solver = Then("simplify", "bit-blast", "sat").solver()
    first_timeout = _remaining(deadline, timeout_seconds)
    result = {
        "experiment": "xoroshiro128pp_direct_borrow_first_pair",
        "solver_logic": "QF_BV",
        "algebraic_unknown_bits": 64,
        "first_observed_output_exactly_eliminated": True,
        "view": view,
        "fit_scope": "18:01 REQUESTED outputs 0/1 only",
        "holdout_scope": "18:03 REQUESTED outputs 4/5; first unconditioned model only",
        "withheld_from_fit": "18:02 ACK payload",
        "source_sha256": SOURCE_SHA,
        "timeout_seconds": timeout_seconds,
        "middle_model_cap": max_middle_models,
        "total_solver_budget_seconds": MAX_TOTAL_SOLVE_SECONDS,
        "holdout_selection_policy": "first unconditioned model only; never used to select candidates",
        "commitment_selection_policy": "hash every complete masked middle candidate before any holdout or uniqueness disposition",
        "component_commitment_status": "NOT_EVALUATED",
        "component_candidate_models_hashed": 0,
    }
    if first_timeout <= 0:
        result.update({
            "status": "UNKNOWN",
            "reason_unknown": "overall solver time budget exhausted before first solve",
            "coupon_status": "WITHHELD_SOLVE_UNKNOWN",
            "K04_original_PASS": None,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        })
        return result

    solver.set(timeout=max(1, int(first_timeout * 1000)))
    solver.add(*inverse_constraints)
    check = solver.check()
    if check != sat:
        result["status"] = str(check).upper()
        if check == unknown:
            result["reason_unknown"] = solver.reason_unknown()
        result.update({
            "coupon_status": "WITHHELD_SOLVE_" + str(check).upper(),
            "K04_original_PASS": None,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        })
        return result

    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text()) if check_candidate else None
    mask = bytes.fromhex(routing["K04"]["masked_component"]) if check_candidate else None
    acceptance = json.loads((ROOT / "acceptance.json").read_text()) if check_candidate else None
    target_sha = acceptance["slot_sha256"]["K04"] if check_candidate else None

    def inspect_model(model, index):
        a0 = model.eval(a0_expr).as_long()
        t0 = model.eval(t0_expr).as_long()
        b0 = a0 ^ t0
        state = (a0, b0)
        replay = stream(state)
        assert replay[:2] == list(first)
        assert t0 == (a0 ^ b0)
        middle = tuple(replay[2:4])
        symbolic_middle = tuple(model.eval(expr).as_long() for expr in middle_exprs)
        symbolic_holdout = tuple(model.eval(expr).as_long() for expr in holdout_exprs)
        assert middle == symbolic_middle
        assert tuple(replay[4:6]) == symbolic_holdout
        coupon = encode(middle, view)
        # Keep the complete candidate internal. Public output carries only
        # model indices and commitment/holdout booleans.
        record = {
            "model_index": index,
            "complete_middle_constructed": True,
        }
        hit = False
        if check_candidate:
            component = bytes(x ^ y for x, y in zip(coupon, mask))
            hit = hashlib.sha256(component).hexdigest() == target_sha
            record.update({
                "K04_original_PASS": hit,
                "component_commitment_status": "PASS" if hit else "MISS",
            })
        if expected_middle is not None:
            record["middle_matches_planted_control"] = middle == tuple(expected_middle)
        return record, hit, state, replay

    first_model = solver.model()
    first_record, first_hit, first_state, first_replay = inspect_model(first_model, 0)
    candidate_records = [first_record]
    commitment_hit = first_hit
    planted_middle_seen = bool(first_record.get("middle_matches_planted_control", False))
    planted_middle_model_index = 0 if planted_middle_seen else None
    found_alternative = False
    uniqueness_status = None
    enumeration_status = "NOT_NEEDED"

    if first_hit:
        # A commitment hit is decisive; do not spend the remaining budget on
        # uniqueness enumeration after the cryptographic candidate is found.
        result["commitment_hit_model_index"] = 0
        result["commitment_hit_candidate"] = first_record
        enumeration_status = "COMMITMENT_HIT"
        uniqueness_status = "UNKNOWN"
    else:
        # Block the first complete middle pair before asking for alternatives.
        solver.add(Or(
            middle_exprs[0] != BitVecVal(first_replay[2], 64),
            middle_exprs[1] != BitVecVal(first_replay[3], 64),
        ))
        # Each alternative is required to have a different complete middle pair.
        # The candidate is hashed immediately after extraction, before the next
        # uniqueness/holdout disposition.
        if max_middle_models <= 1:
            enumeration_status = "MODEL_CAP_REACHED"
            uniqueness_status = "UNKNOWN"
        else:
            while len(candidate_records) < max_middle_models:
                remaining = _remaining(deadline, timeout_seconds)
                if remaining <= 0:
                    enumeration_status = "TOTAL_BUDGET_EXHAUSTED"
                    uniqueness_status = "SAT" if found_alternative else "UNKNOWN"
                    break
                solver.set(timeout=max(1, int(remaining * 1000)))
                alternative = solver.check()
                if alternative == unsat:
                    enumeration_status = "EXHAUSTED"
                    uniqueness_status = "SAT" if found_alternative else "UNSAT"
                    break
                if alternative == unknown:
                    enumeration_status = "UNKNOWN"
                    uniqueness_status = "SAT" if found_alternative else "UNKNOWN"
                    result["enumeration_reason_unknown"] = solver.reason_unknown()
                    break
                alt_model = solver.model()
                record, hit, alt_state, alt_replay = inspect_model(alt_model, len(candidate_records))
                candidate_records.append(record)
                found_alternative = True
                uniqueness_status = "SAT"
                if hit:
                    commitment_hit = True
                    result["commitment_hit_model_index"] = record["model_index"]
                    result["commitment_hit_candidate"] = record
                if expected_middle is not None and alt_replay[2:4] == list(expected_middle):
                    planted_middle_seen = True
                    planted_middle_model_index = record["model_index"]
                    enumeration_status = "PLANTED_MIDDLE_FOUND"
                    break
                if hit:
                    enumeration_status = "COMMITMENT_HIT"
                    break
                solver.add(Or(
                    middle_exprs[0] != BitVecVal(alt_replay[2], 64),
                    middle_exprs[1] != BitVecVal(alt_replay[3], 64),
                ))
            else:
                enumeration_status = "CAP_REACHED"
                uniqueness_status = "SAT"

    # Hashes above precede this independent holdout comparison. Only the first
    # unconditioned model is reported against REQUESTED3; it is never a filter.
    first_holdout = tuple(first_replay[4:6])
    result.update({
        "status": "SAT",
        "first_model_middle_constructed": True,
        "holdout_matches_full_18_03_packet": first_holdout == tuple(holdout),
        "holdout_model_index": 0,
        "holdout_is_blind": True,
        "predicted_middle_matches_withheld_ACK2": encode(first_replay[2:4], view) == ack2_payload,
        "uniqueness_status": uniqueness_status or "UNKNOWN",
        "middle_unique": uniqueness_status == "UNSAT",
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "candidate_models": candidate_records,
        "candidate_models_examined": len(candidate_records),
        "enumeration_status": enumeration_status,
        "planted_middle_seen": planted_middle_seen,
        "planted_middle_model_index": planted_middle_model_index,
    })

    if check_candidate:
        result["K04_original_PASS"] = commitment_hit
        result["component_commitment_status"] = "PASS" if commitment_hit else "MISS_WITHIN_EVALUATED_MODELS"
        result["component_candidate_models_hashed"] = len(candidate_records)
        if commitment_hit:
            result["coupon_status"] = "K04_COMMITMENT_HIT"
        elif enumeration_status in ("CAP_REACHED", "MODEL_CAP_REACHED"):
            result["coupon_status"] = "NO_COMMITMENT_HIT_WITHIN_MODEL_CAP"
        elif enumeration_status in ("TOTAL_BUDGET_EXHAUSTED", "UNKNOWN"):
            result["coupon_status"] = "NO_COMMITMENT_HIT_WITHIN_BUDGET"
        elif result["middle_unique"]:
            result["coupon_status"] = "NO_COMMITMENT_HIT_UNIQUE_MIDDLE"
        else:
            result["coupon_status"] = "NO_COMMITMENT_HIT"
    else:
        result["K04_original_PASS"] = None
        result["middle_matches_seed"] = planted_middle_seen
        result["coupon_status"] = (
            "SYNTHETIC_PLANTED_MIDDLE_RECOVERED"
            if planted_middle_seen else "SYNTHETIC_PLANTED_MIDDLE_NOT_FOUND"
        )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--view", type=int, choices=range(4), default=0)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--max-middle-models", type=int, default=MAX_MIDDLE_MODELS)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--synthetic-only", action="store_true",
                      help="run only the unseeded first-pair positive control")
    mode.add_argument("--source-only", action="store_true",
                      help="run source solve; caller must gate on positive-control success")
    args = parser.parse_args()
    assert 1 <= args.timeout_seconds <= 300
    assert 1 <= args.max_middle_models <= 64

    self_test()
    if not args.source_only:
        outputs = stream(SEED)
        synthetic = solve_first_pair(
            outputs[:2], outputs[4:6], b"", 0, args.timeout_seconds, False,
            expected_middle=outputs[2:4], max_middle_models=args.max_middle_models
        )
        synthetic["experiment"] = "synthetic_positive_control"
        control_pass = (
            synthetic.get("status") == "SAT"
            and synthetic.get("planted_middle_seen") is True
        )
        synthetic["control_pass"] = control_pass
        synthetic["control_gate_policy"] = (
            "unseeded SAT plus planted middle recovered within explicit distinct-middle cap; "
            "first-model holdout and uniqueness are separate diagnostics"
        )
        emit_public_result(synthetic)
        if args.synthetic_only:
            if not control_pass:
                raise SystemExit(2)
            return
        if not control_pass:
            emit_public_result({
                "experiment": "original_first_pair_only",
                "status": "NOT_RUN",
                "coupon_status": "WITHHELD_CONTROL_FAILED",
                "reason": "unseeded planted middle was not recovered within the explicit model cap",
            })
            raise SystemExit(2)

    if args.synthetic_only:
        return

    first, ack2_payload, holdout = parse_source()
    original = solve_first_pair(
        decode(first, args.view), decode(holdout, args.view), ack2_payload,
        args.view, args.timeout_seconds, True,
        max_middle_models=args.max_middle_models
    )
    original["experiment"] = "original_first_pair_only"
    original["control_gate"] = (
        "positive-control workflow dependency passed" if args.source_only
        else "unseeded planted control passed in this process"
    )
    emit_public_result(original)


if __name__ == "__main__":
    main()
