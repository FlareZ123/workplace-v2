#!/usr/bin/env python3
"""One-word inverse Z3 backend for the H-17 K04 xoroshiro128++ hypothesis.

Fits only the first REQUESTED packet (outputs 0/1), derives b0 from a0 using
the exact inverse of xoroshiro128++'s first output, predicts the middle pair,
and blindly checks the third REQUESTED packet (outputs 4/5). Every complete
masked middle candidate is checked against the K04 commitment before any
holdout or uniqueness disposition. Nonunique middles are enumerated under a
fixed cap; uniqueness and first-model holdout are reported separately.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

from z3 import BitVec, BitVecVal, Or, RotateLeft, RotateRight, SolverFor, sat, unsat, unknown

MASK = (1 << 64) - 1
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SEED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)
MAX_MIDDLE_MODELS = 8
MAX_TOTAL_SOLVE_SECONDS = 600
ROOT = Path(__file__).resolve().parents[2] / "resources"


def stream(state, count=6):
    a, b = state
    out = []
    for _ in range(count):
        total = (a + b) & MASK
        out.append((((total << 17) | (total >> 47)) + a) & MASK)
        t = a ^ b
        a, b = (((a << 49) | (a >> 15)) ^ t ^ (t << 21)) & MASK, ((t << 28) | (t >> 36)) & MASK
    return out


def decode(payload, view):
    endian = "little" if view & 1 else "big"
    words = [int.from_bytes(payload[i:i + 8], endian) for i in (0, 8)]
    return words[::-1] if view & 2 else words


def encode(words, view):
    endian = "little" if view & 1 else "big"
    words = words[::-1] if view & 2 else words
    return b"".join(int(x).to_bytes(8, endian) for x in words)


def solve_first_pair(first, holdout, view, timeout_seconds, check_candidate,
                     expected_middle=None, max_middle_models=MAX_MIDDLE_MODELS):
    # Exact first-output inverse:
    # u0 = ROTR(y0 - a0, 17) = a0 + b0 (mod 2^64)
    # b0 = u0 - a0; t0 = a0 XOR b0.
    a0 = BitVec("initial_s0", 64)
    u0 = RotateRight(BitVecVal(first[0], 64) - a0, 17)
    b0 = u0 - a0

    a, b = a0, b0
    outputs = []
    for _ in range(6):
        outputs.append(RotateLeft(a + b, 17) + a)
        t = a ^ b
        a, b = RotateLeft(a, 49) ^ t ^ (t << 21), RotateLeft(t, 28)

    solver = SolverFor("QF_BV")
    solver.set(timeout=int(timeout_seconds * 1000))
    solver.set("sat.random_seed", 0)
    solver.set("smt.random_seed", 0)
    # output 0 is an identity by construction; retain it as an executable guard.
    solver.add(outputs[0] == BitVecVal(first[0], 64))
    solver.add(outputs[1] == BitVecVal(first[1], 64))

    started = time.monotonic()
    deadline = started + MAX_TOTAL_SOLVE_SECONDS

    def bounded_check():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        solver.set(timeout=max(1, int(min(timeout_seconds, remaining) * 1000)))
        return solver.check()

    result = {
        "experiment": "z3_one_word_inverse_first_pair_only",
        "view": view,
        "fit_scope": "18:01 REQUESTED outputs 0/1 only",
        "holdout_scope": "18:03 REQUESTED outputs 4/5; first unconditioned model only",
        "withheld_from_fit": "18:02 ACK payload",
        "source_sha256": SOURCE_SHA,
        "timeout_seconds": timeout_seconds,
        "middle_model_cap": max_middle_models,
        "total_solver_budget_seconds": MAX_TOTAL_SOLVE_SECONDS,
        "holdout_selection_policy": "never used to select or filter middle candidates",
        "commitment_selection_policy": "hash each complete masked middle candidate before holdout or uniqueness disposition",
    }

    check = bounded_check()
    if check is None:
        result.update({"status": "UNKNOWN", "reason_unknown": "overall solver time budget exhausted",
                       "coupon_status": "WITHHELD_SOLVE_UNKNOWN",
                       "K04_original_PASS": False if check_candidate else None,
                       "elapsed_seconds": round(time.monotonic() - started, 3)})
        return result
    result["status"] = str(check).upper()
    if check == unknown:
        result["reason_unknown"] = solver.reason_unknown()
        result["coupon_status"] = "WITHHELD_SOLVE_UNKNOWN"
        result["K04_original_PASS"] = False if check_candidate else None
        result["elapsed_seconds"] = round(time.monotonic() - started, 3)
        return result
    if check == unsat:
        result["coupon_status"] = "NO_SAT_MODEL"
        result["K04_original_PASS"] = False if check_candidate else None
        result["elapsed_seconds"] = round(time.monotonic() - started, 3)
        return result

    # First unconditioned model: commitment check is deliberately performed
    # before computing/reporting holdout or asking the uniqueness question.
    first_model = solver.model()
    first_middle = (
        first_model.eval(outputs[2]).as_long(),
        first_model.eval(outputs[3]).as_long(),
    )
    first_state = (
        first_model.eval(a0).as_long(),
        first_model.eval(b0).as_long(),
    )
    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text()) if check_candidate else None
    mask = bytes.fromhex(routing["K04"]["masked_component"]) if check_candidate else None
    acceptance = json.loads((ROOT / "acceptance.json").read_text()) if check_candidate else None
    target_sha = acceptance["slot_sha256"]["K04"] if check_candidate else None

    def inspect_middle(model, index):
        middle = (
            model.eval(outputs[2]).as_long(),
            model.eval(outputs[3]).as_long(),
        )
        coupon = encode(middle, view)
        record = {
            "model_index": index,
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
        return record, hit, middle

    first_record, first_hit, _ = inspect_middle(first_model, 0)
    first_replay = stream(first_state)
    assert first_replay[:2] == list(first)
    result["initial_state"] = [f"{x:016X}" for x in first_state]
    result["predicted_middle_words"] = [f"{x:016X}" for x in first_middle]
    result["predicted_coupon_hex"] = first_record["predicted_coupon_hex"]
    result["predicted_later_words"] = [f"{x:016X}" for x in first_replay[4:6]]
    result["holdout_matches_full_18_03_packet"] = first_replay[4:6] == list(holdout)
    result["holdout_model_index"] = 0
    result["holdout_is_blind"] = True

    candidate_records = [first_record]
    commitment_hit = first_hit
    if first_hit:
        result["commitment_hit_model_index"] = 0
        result["commitment_hit_candidate"] = first_record
    planted_middle_seen = bool(first_record.get("middle_matches_planted_control", False))
    planted_middle_model_index = 0 if planted_middle_seen else None
    enumeration_status = "NOT_NEEDED"

    uniqueness_status = None
    # If the first candidate misses the commitment (or planted control), use the
    # first alternative check both to classify uniqueness and to begin bounded
    # candidate enumeration. Hash each candidate before any other disposition.
    if not commitment_hit and not planted_middle_seen and max_middle_models > 1:
        solver.push()
        solver.add(Or(outputs[2] != BitVecVal(first_middle[0], 64),
                      outputs[3] != BitVecVal(first_middle[1], 64)))
        enumeration_status = "CAP_REACHED"
        for model_index in range(1, max_middle_models):
            next_check = bounded_check()
            if next_check is None:
                enumeration_status = "TOTAL_BUDGET_EXHAUSTED"
                uniqueness_status = "UNKNOWN" if uniqueness_status is None else uniqueness_status
                result["enumeration_reason_unknown"] = "overall solver time budget exhausted"
                break
            if next_check == unsat:
                enumeration_status = "EXHAUSTED"
                uniqueness_status = "UNSAT"
                break
            if next_check == unknown:
                enumeration_status = "UNKNOWN"
                uniqueness_status = "UNKNOWN" if uniqueness_status is None else uniqueness_status
                result["enumeration_reason_unknown"] = solver.reason_unknown()
                break
            if uniqueness_status is None:
                uniqueness_status = "SAT"
            model = solver.model()
            record, hit, middle = inspect_middle(model, model_index)
            candidate_records.append(record)
            if hit:
                commitment_hit = True
                result["commitment_hit_model_index"] = model_index
                result["commitment_hit_candidate"] = record
                enumeration_status = "COMMITMENT_HIT"
                break
            if record.get("middle_matches_planted_control", False):
                planted_middle_seen = True
                planted_middle_model_index = model_index
                enumeration_status = "PLANTED_MIDDLE_FOUND"
                break
            solver.add(Or(outputs[2] != BitVecVal(middle[0], 64),
                          outputs[3] != BitVecVal(middle[1], 64)))
        solver.pop()
    else:
        if not commitment_hit and not planted_middle_seen and max_middle_models <= 1:
            enumeration_status = "MODEL_CAP_REACHED"
        # A first-model commitment hit or planted-middle recovery is already
        # durable; uniqueness is still measured independently afterwards.
        solver.push()
        solver.add(Or(outputs[2] != BitVecVal(first_middle[0], 64),
                      outputs[3] != BitVecVal(first_middle[1], 64)))
        alternative = bounded_check()
        solver.pop()
        if alternative is None:
            uniqueness_status = "UNKNOWN"
            result["uniqueness_reason_unknown"] = "overall solver time budget exhausted"
        elif alternative == unknown:
            uniqueness_status = "UNKNOWN"
            result["uniqueness_reason_unknown"] = solver.reason_unknown()
        else:
            uniqueness_status = str(alternative).upper()

    result["uniqueness_status"] = uniqueness_status or "UNKNOWN"
    result["middle_unique"] = uniqueness_status == "UNSAT"
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    result["candidate_models"] = candidate_records
    result["candidate_models_examined"] = len(candidate_records)
    result["enumeration_status"] = enumeration_status
    result["planted_middle_seen"] = planted_middle_seen
    result["planted_middle_model_index"] = planted_middle_model_index

    if check_candidate:
        result["K04_original_PASS"] = commitment_hit
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
        result["middle_matches_seed"] = planted_middle_seen
        result["coupon_status"] = (
            "SYNTHETIC_PLANTED_MIDDLE_RECOVERED"
            if planted_middle_seen else "SYNTHETIC_PLANTED_MIDDLE_NOT_FOUND"
        )
    return result


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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--view", type=int, choices=range(4), default=0)
    p.add_argument("--timeout-seconds", type=int, default=300)
    p.add_argument("--max-middle-models", type=int, default=MAX_MIDDLE_MODELS)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--synthetic-only", action="store_true",
                      help="run only the unseeded first-pair positive control")
    mode.add_argument("--source-only", action="store_true",
                      help="run source solve; caller must gate on positive-control success")
    args = p.parse_args()

    if not args.source_only:
        outputs = stream(SEED)
        synthetic = solve_first_pair(
            outputs[:2], outputs[4:6], args.view, args.timeout_seconds, False,
            expected_middle=outputs[2:4], max_middle_models=args.max_middle_models
        )
        synthetic["experiment"] = "synthetic_positive_control"
        control_pass = (
            synthetic.get("status") == "SAT"
            and synthetic.get("planted_middle_seen") is True
        )
        synthetic["control_pass"] = control_pass
        synthetic["control_gate_policy"] = (
            "unseeded SAT plus planted middle recovered within explicit model cap; "
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

    rows = parse_source()
    first = decode(rows[0], args.view)
    holdout = decode(rows[2], args.view)
    original = solve_first_pair(
        first, holdout, args.view, args.timeout_seconds, True,
        max_middle_models=args.max_middle_models
    )
    original["experiment"] = "original_first_pair_only"
    original["control_gate"] = (
        "positive-control workflow dependency passed" if args.source_only
        else "unseeded planted control passed in this process"
    )
    original["ack2_payload_matches_first_model_prediction"] = (
        original.get("predicted_coupon_hex") == rows[1].hex().upper()
    ) if "predicted_coupon_hex" in original else None
    print(json.dumps(original, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
