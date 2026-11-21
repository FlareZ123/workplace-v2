#!/usr/bin/env python3
"""Independent Z3 bit-vector backend for the H-17 K04 xoroshiro128++ hypothesis.

This is a solver-backend pilot, not a new producer claim. It fits only the
first REQUESTED packet (outputs 0/1), withholds ACK2, predicts the middle
coupon, and blindly checks the third REQUESTED packet (outputs 4/5).
"""
import argparse
import hashlib
import json
from pathlib import Path

from z3 import BitVec, BitVecVal, Or, RotateLeft, SolverFor, sat, unsat, unknown

MASK = (1 << 64) - 1
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SEED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)
ROOT = Path(__file__).resolve().parents[2] / "resources"


def stream(state):
    a, b = state
    out = []
    for _ in range(6):
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


def solve_first_pair(first, holdout, view, timeout_seconds, check_candidate):
    s0, s1 = BitVec("initial_s0", 64), BitVec("initial_s1", 64)
    a, b = s0, s1
    outputs = []
    for _ in range(6):
        outputs.append(RotateLeft(a + b, 17) + a)
        t = a ^ b
        a, b = RotateLeft(a, 49) ^ t ^ (t << 21), RotateLeft(t, 28)

    solver = SolverFor("QF_BV")
    solver.set(timeout=int(timeout_seconds * 1000))
    solver.set("sat.random_seed", 0)
    solver.set("smt.random_seed", 0)
    solver.add(outputs[0] == BitVecVal(first[0], 64))
    solver.add(outputs[1] == BitVecVal(first[1], 64))
    result = {
        "experiment": "z3_first_pair_only",
        "view": view,
        "fit_scope": "18:01 REQUESTED outputs 0/1 only",
        "holdout_scope": "18:03 REQUESTED outputs 4/5 only",
        "withheld_from_fit": "18:02 ACK payload",
        "source_sha256": SOURCE_SHA,
        "timeout_seconds": timeout_seconds,
    }
    check = solver.check()
    result["status"] = str(check).upper()
    if check == unknown:
        result["reason_unknown"] = solver.reason_unknown()
        result["coupon_status"] = "WITHHELD_SOLVE_UNKNOWN"
        return result
    if check == unsat:
        result["coupon_status"] = "NO_SAT_MODEL"
        return result

    model = solver.model()
    state = (model.eval(s0).as_long(), model.eval(s1).as_long())
    replay = stream(state)
    assert replay[:2] == list(first)
    result["initial_state"] = [f"{x:016X}" for x in state]
    result["predicted_middle_words"] = [f"{x:016X}" for x in replay[2:4]]
    result["predicted_later_words"] = [f"{x:016X}" for x in replay[4:6]]
    result["holdout_matches_full_18_03_packet"] = replay[4:6] == list(holdout)

    middle0 = model.eval(outputs[2]).as_long()
    middle1 = model.eval(outputs[3]).as_long()
    solver.push()
    solver.add(Or(outputs[2] != BitVecVal(middle0, 64),
                  outputs[3] != BitVecVal(middle1, 64)))
    alternative = solver.check()
    solver.pop()
    result["uniqueness_status"] = str(alternative).upper()
    result["middle_unique"] = alternative == unsat
    if alternative == unknown:
        result["uniqueness_reason_unknown"] = solver.reason_unknown()

    if not result["middle_unique"]:
        result["coupon_status"] = "WITHHELD_NONUNIQUE" if alternative == sat else "WITHHELD_UNIQUENESS_UNKNOWN"
        return result

    coupon = encode(replay[2:4], view)
    result["predicted_coupon_hex"] = coupon.hex().upper()
    if not check_candidate:
        result["coupon_status"] = "SYNTHETIC_UNIQUE_MIDDLE_HOLDOUT_PASS" if result["holdout_matches_full_18_03_packet"] else "SYNTHETIC_HOLDOUT_FAIL"
        return result

    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    component = bytes(x ^ y for x, y in zip(coupon, mask))
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    hit = hashlib.sha256(component).hexdigest() == acceptance["slot_sha256"]["K04"]
    result.update({
        "predicted_component_hex": component.hex().upper(),
        "K04_original_PASS": hit,
        "coupon_status": "UNIQUE_MIDDLE_HASH_PASS" if hit else "UNIQUE_MIDDLE_HASH_MISS",
    })
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
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--synthetic-only", action="store_true",
                      help="run only the unseeded first-pair positive control")
    mode.add_argument("--source-only", action="store_true",
                      help="run source solve; caller must gate on positive-control success")
    args = p.parse_args()

    if not args.source_only:
        outputs = stream(SEED)
        synthetic = solve_first_pair(outputs[:2], outputs[4:6], args.view,
                                     args.timeout_seconds, False)
        synthetic["experiment"] = "synthetic_positive_control"
        synthetic["expected_middle_hex"] = [f"{x:016X}" for x in outputs[2:4]]
        synthetic["middle_matches_seed"] = (
            synthetic.get("predicted_middle_words") == synthetic["expected_middle_hex"]
        )
        control_pass = (
            synthetic.get("status") == "SAT"
            and synthetic.get("middle_unique") is True
            and synthetic.get("holdout_matches_full_18_03_packet") is True
            and synthetic["middle_matches_seed"] is True
        )
        synthetic["control_pass"] = control_pass
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
                "reason": "unseeded planted control did not prove SAT, unique middle, exact later holdout and planted middle",
            }, sort_keys=True), flush=True)
            raise SystemExit(2)

    if args.synthetic_only:
        return

    rows = parse_source()
    first = decode(rows[0], args.view)
    holdout = decode(rows[2], args.view)
    original = solve_first_pair(first, holdout, args.view,
                                args.timeout_seconds, True)
    original["experiment"] = "original_first_pair_only"
    original["control_gate"] = (
        "positive-control workflow dependency passed" if args.source_only
        else "unseeded planted control passed in this process"
    )
    original["ack2_payload_matches_prediction"] = (
        original.get("predicted_coupon_hex") == rows[1].hex().upper()
    ) if "predicted_coupon_hex" in original else None
    print(json.dumps(original, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
