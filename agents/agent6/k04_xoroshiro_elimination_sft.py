"""Source-pinned xoroshiro128++ elimination-mode test with target-output uniqueness.

This is a bounded test of the existing conjectural same-job flank model.
It never uses the copied PS-0417 ACK2 bytes to infer state. A result is promoted
only if the missing 16-byte middle packet is unique and its masked component
passes the original K04 SHA256 commitment.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import time
from pathlib import Path

# Enable model generation and incremental blocking before Boolector is created.
os.environ["BTORMODELGEN"] = "1"
os.environ["BTORINCREMENTAL"] = "1"

import pyboolector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "agents/agent50/k04_xoroshiropp_boolector_sft.py"
SPEC = importlib.util.spec_from_file_location("agent50_xoroshiro_boolector", SOURCE)
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)


def solve_unique(first, last):
    bt = pyboolector.Boolector()
    initial_a = bt.Var(bt.BitVecSort(64), "initial_s0")
    initial_b = bt.Ror(bt.Const(first[0], 64) - initial_a, 17) - initial_a
    a, b = initial_a, initial_b
    outputs = []
    for _ in range(6):
        outputs.append(bt.Rol(a + b, 17) + a)
        t = a ^ b
        a, b = bt.Rol(a, 49) ^ t ^ (t << 21), bt.Rol(t, 28)

    for index, value in zip((0, 1, 4, 5), (*first, *last)):
        bt.Assert(outputs[index] == bt.Const(value, 64))

    started = time.monotonic()
    status = bt.Sat()
    elapsed_first = time.monotonic() - started
    if status == bt.UNSAT:
        return {"status": "UNSAT", "elapsed_first_s": round(elapsed_first, 3)}
    if status != bt.SAT:
        return {"status": "UNKNOWN", "code": int(status),
                "elapsed_first_s": round(elapsed_first, 3)}

    state = (int(initial_a.assignment, 2), int(initial_b.assignment, 2))
    values = BASE.series(*state)
    assert values[:2] == list(first) and values[4:] == list(last)
    middle = values[2:4]

    # Block the recovered initial s0. In elimination mode s1 is fixed by
    # output[0], so this blocks the complete 128-bit initial state.
    bt.Assert(initial_a != bt.Const(state[0], 64))
    started = time.monotonic()
    alternate_status = bt.Sat()
    elapsed_alt = time.monotonic() - started
    if alternate_status == bt.UNSAT:
        unique_middle = True
        alt_middle = None
    elif alternate_status == bt.SAT:
        alt_state = (int(initial_a.assignment, 2), int(initial_b.assignment, 2))
        alt_values = BASE.series(*alt_state)
        assert alt_values[:2] == list(first) and alt_values[4:] == list(last)
        alt_middle = alt_values[2:4]
        unique_middle = alt_middle == middle
    else:
        unique_middle = None
        alt_middle = None

    return {
        "status": "SAT",
        "unique_middle": unique_middle,
        "middle": middle,
        "alternative_middle": alt_middle,
        "elapsed_first_s": round(elapsed_first, 3),
        "elapsed_alternative_s": round(elapsed_alt, 3),
    }


def evaluate(view, first, last, target, mask):
    decoded_first = BASE.decode(first, view)
    decoded_last = BASE.decode(last, view)
    result = solve_unique(decoded_first, decoded_last)
    output = {
        "view": view,
        "model": "xoroshiro128++ same-job REQUESTED/ACK/REQUESTED flank",
        "solver": "Boolector elimination (64-bit s0, s1 derived from output0)",
        "result": result["status"],
        "unique_middle": result.get("unique_middle"),
        "elapsed_first_s": result.get("elapsed_first_s"),
        "elapsed_alternative_s": result.get("elapsed_alternative_s"),
    }
    if result["status"] != "SAT" or result.get("unique_middle") is not True:
        return output

    coupon = BASE.encode(result["middle"], view)
    component = bytes(x ^ y for x, y in zip(coupon, mask))
    digest = hashlib.sha256(component).hexdigest()
    output["K04_commitment_pass"] = digest == target
    if digest == target:
        output["complete_coupon"] = coupon.hex().upper()
        output["K04_component"] = component.hex().upper()
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--view", type=int, choices=range(4), required=True)
    parser.add_argument("--control-only", action="store_true")
    args = parser.parse_args()

    # Reuse the source-pinned parser; it validates the exact 133-row log and
    # explicitly excludes the copied ACK2 payload from state inversion.
    before, after = BASE.original_records()
    seed = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)
    synthetic = BASE.series(*seed)
    positive = solve_unique(synthetic[:2], synthetic[4:])
    assert positive["status"] == "SAT", positive
    assert positive["middle"] == synthetic[2:4], positive
    assert positive["unique_middle"] is True, positive
    print(json.dumps({
        "positive_control": "PASS",
        "positive_unique_middle": True,
        "view": args.view,
    }, sort_keys=True), flush=True)
    if args.control_only:
        return

    if args.view & 1:
        mask = bytes.fromhex(json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())["K04"]["masked_component"])
    else:
        mask = bytes.fromhex(json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())["K04"]["masked_component"])
    target = json.loads((ROOT / "resources/acceptance.json").read_text())["slot_sha256"]["K04"]
    result = evaluate(args.view, before, after, target, mask)
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
