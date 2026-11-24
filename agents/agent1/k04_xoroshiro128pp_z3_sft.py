#!/usr/bin/env python3
"""One-sum-variable first-pair inversion for the H-17 K04 xoroshiro128++ hypothesis.

The first observed output is eliminated exactly with P=a0+b0 (mod 2^64):
    a0 = y0 - ROTL(P,17)
    b0 = P - a0
The second observed output is then one QF_BV equation in the single 64-bit
unknown P. The selected 18:02 ACK payload is withheld from fitting.

Every complete middle candidate is masked and checked against the original
K04 commitment before any holdout or uniqueness disposition. The 18:03
REQUESTED packet is a blind diagnostic for the first unconditioned model only.
"""
import argparse
import hashlib
import json
import random
import re
import time
from pathlib import Path

from z3 import BitVec, BitVecVal, Or, RotateLeft, SolverFor, sat, simplify, unsat, unknown

MASK = (1 << 64) - 1
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SEED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)
MAX_MIDDLE_MODELS = 8
MAX_TOTAL_SOLVE_SECONDS = 600
ROOT = Path(__file__).resolve().parents[2] / "resources"


def rol(x, n):
    return ((x << n) | (x >> (64 - n))) & MASK


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


def z3_sequence_from_sum(y0, total):
    """Return symbolic initial state, middle outputs, and later holdout."""
    a0 = BitVecVal(y0, 64) - RotateLeft(total, 17)
    b0 = total - a0
    a1, b1 = z3_step(a0, b0)
    y1 = z3_output(a1, b1)
    a2, b2 = z3_step(a1, b1)
    y2 = z3_output(a2, b2)
    a3, b3 = z3_step(a2, b2)
    y3 = z3_output(a3, b3)
    a4, b4 = z3_step(a3, b3)
    y4 = z3_output(a4, b4)
    a5, b5 = z3_step(a4, b4)
    y5 = z3_output(a5, b5)
    return (a0, b0), y1, (y2, y3), (y4, y5)


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
        y0, y1 = stream(state, 2)
        total = (state[0] + state[1]) & MASK
        a0 = (y0 - rol(total, 17)) & MASK
        b0 = (total - a0) & MASK
        recovered = (a0, b0)
        assert recovered == state
        assert stream(recovered, 2) == [y0, y1]
        p_expr = BitVecVal(total, 64)
        _, symbolic_y1, symbolic_middle, symbolic_holdout = z3_sequence_from_sum(y0, p_expr)
        assert simplify(symbolic_y1).as_long() == y1
        assert [simplify(x).as_long() for x in symbolic_middle] == stream(state)[2:4]
        assert [simplify(x).as_long() for x in symbolic_holdout] == stream(state)[4:6]
    print(json.dumps({
        "self_test": "PASS",
        "algebraic_unknown_bits": 64,
        "randomized_inverse_cases": len(tests),
        "first_output_exactly_eliminated": True,
    }, sort_keys=True), flush=True)


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
    total = BitVec("sum_state0", 64)
    (a0_expr, b0_expr), predicted_y1, middle_exprs, holdout_exprs = z3_sequence_from_sum(y0, total)

    solver = SolverFor("QF_BV")
    first_timeout = _remaining(deadline, timeout_seconds)
    result = {
        "experiment": "xoroshiro128pp_one_sum_variable_first_pair",
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
    solver.add(predicted_y1 == BitVecVal(y1, 64))
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
        p_value = model.eval(total).as_long()
        a0 = (y0 - rol(p_value, 17)) & MASK
        b0 = (p_value - a0) & MASK
        state = (a0, b0)
        replay = stream(state)
        assert replay[:2] == list(first)
        middle = tuple(replay[2:4])
        symbolic_middle = tuple(model.eval(expr).as_long() for expr in middle_exprs)
        assert middle == symbolic_middle
        coupon = encode(middle, view)
        record = {
            "model_index": index,
            "sum_state0": f"{p_value:016X}",
            "initial_state": [f"{a0:016X}", f"{b0:016X}"],
            "middle_words": [f"{x:016X}" for x in middle],
            "predicted_coupon_hex": coupon.hex().upper(),
        }
        hit = False
        if check_candidate:
            component = bytes(x ^ y for x, y in zip(coupon, mask))
            hit = hashlib.sha256(component).hexdigest() == target_sha
            record.update({
                "predicted_component_hex": component.hex().upper(),
                "K04_original_PASS": hit,
            })
        if expected_middle is not None:
            record["middle_matches_planted_control"] = middle == tuple(expected_middle)
        return record, hit, state, replay

    first_model = solver.model()
    first_record, first_hit, first_state, first_replay = inspect_model(first_model, 0)
    candidate_records = [first_record]
    # Block the first complete middle pair before asking for alternatives.
    solver.add(Or(
        middle_exprs[0] != BitVecVal(first_replay[2], 64),
        middle_exprs[1] != BitVecVal(first_replay[3], 64),
    ))
    commitment_hit = first_hit
    planted_middle_seen = bool(first_record.get("middle_matches_planted_control", False))
    planted_middle_model_index = 0 if planted_middle_seen else None
    found_alternative = False
    uniqueness_status = None
    enumeration_status = "NOT_NEEDED"

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
        "initial_state": [f"{x:016X}" for x in first_state],
        "sum_state0": first_record["sum_state0"],
        "predicted_middle_words": first_record["middle_words"],
        "predicted_later_words": [f"{x:016X}" for x in first_holdout],
        "holdout_matches_full_18_03_packet": first_holdout == tuple(holdout),
        "holdout_model_index": 0,
        "holdout_is_blind": True,
        "predicted_coupon_hex": first_record["predicted_coupon_hex"],
        "predicted_middle_matches_withheld_ACK2": bytes.fromhex(first_record["predicted_coupon_hex"]) == ack2_payload,
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
        print(json.dumps(synthetic, sort_keys=True), flush=True)
        if args.synthetic_only:
            if not control_pass:
                raise SystemExit(2)
            return
        if not control_pass:
            print(json.dumps({
                "experiment": "original_first_pair_only",
                "status": "NOT_RUN",
                "coupon_status": "WITHHELD_CONTROL_FAILED",
                "reason": "unseeded planted middle was not recovered within the explicit model cap",
            }, sort_keys=True), flush=True)
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
    print(json.dumps(original, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
