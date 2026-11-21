#!/usr/bin/env python3
"""Independent Z3 bit-vector solve for the H-17 K04 xoroshiro128++ flank hypothesis.

This is an exploratory candidate constructor, not authenticated printer firmware.
It uses only the two PS-0417 RECOVER REQUESTED payloads as observed flanks:
outputs 0/1 and 4/5. The intervening outputs 2/3 are the proposed coupon.
The ACK payload is deliberately not used as a flank or solver constraint.

The full-domain solve is intentionally separate from the prior CryptoMiniSat
prefix matrix. Results are written to JSON so every disposition is preserved.
"""
import argparse
import hashlib
import json
import pathlib
import re
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SEED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)


def rol(value, n):
    mask = (1 << 64) - 1
    return ((value << n) | (value >> (64 - n))) & mask


def stream(state, count=6):
    mask = (1 << 64) - 1
    a, b = state
    words = []
    for _ in range(count):
        words.append((rol((a + b) & mask, 17) + a) & mask)
        t = a ^ b
        a, b = (rol(a, 49) ^ t ^ (t << 21)) & mask, rol(t, 28)
    return words


def decode(payload, view):
    endian = "little" if view & 1 else "big"
    words = [int.from_bytes(payload[i:i + 8], endian) for i in (0, 8)]
    return words[::-1] if view & 2 else words


def encode(words, view):
    endian = "little" if view & 1 else "big"
    ordered = words[::-1] if view & 2 else words
    return b"".join(x.to_bytes(8, endian) for x in ordered)


def parse_source():
    path = ROOT / "resources/evidence/print/spool-reconstruction.log"
    original = path.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest != SOURCE_SHA:
        raise ValueError(f"source SHA mismatch: {digest}")
    rows = {}
    for line in original.decode("ascii").splitlines():
        if line.startswith("2026-"):
            stamp, *fields = line.split()
            rows[stamp] = dict(item.split("=", 1) for item in fields)
    if len(rows) != 133:
        raise ValueError(f"expected 133 spool rows, found {len(rows)}")
    first = rows["2026-10-03T18:01:00Z"]
    middle = rows["2026-10-03T18:02:00Z"]
    last = rows["2026-10-03T18:03:00Z"]
    trio = (first, middle, last)
    if not all(row["JOB"] == "PS-261003-0417" and row["CLASS"] == "RECOVER"
               for row in trio):
        raise ValueError("PS-0417 RECOVER trio identity mismatch")
    if [(row["ATTEMPT"], row["STATE"]) for row in trio] != [
        ("1", "REQUESTED"), ("2", "ACK"), ("3", "REQUESTED")
    ]:
        raise ValueError("PS-0417 RECOVER attempt/state sequence mismatch")
    # ACK is checked for sequence integrity but its payload is not consumed.
    return bytes.fromhex(first["PAYLOAD"]), bytes.fromhex(last["PAYLOAD"])


def load_k04():
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    commitment = acceptance["slot_sha256"]["K04"]
    if len(mask) != 16:
        raise ValueError("K04 mask is not 16 bytes")
    return mask, commitment


def z3_outputs(s0, s1, count=6):
    from z3 import RotateLeft
    words = []
    for _ in range(count):
        words.append(RotateLeft(s0 + s1, 17) + s0)
        t = s0 ^ s1
        s0, s1 = RotateLeft(s0, 49) ^ t ^ (t << 21), RotateLeft(t, 28)
    return words


def solve_known(view, known, timeout_ms, prefix_bits=0, prefix=0):
    from z3 import BitVec, BitVecVal, Extract, Or, Solver, sat, unsat
    s0 = BitVec("s0", 64)
    s1 = BitVec("s1", 64)
    outputs = z3_outputs(s0, s1, 6)
    solver = Solver()
    solver.set(timeout=timeout_ms)
    solver.set(random_seed=0)
    for index, value in known.items():
        solver.add(outputs[index] == BitVecVal(value, 64))
    if prefix_bits:
        if not 1 <= prefix_bits <= 64:
            raise ValueError("prefix_bits must be between 1 and 64")
        solver.add(Extract(prefix_bits - 1, 0, s0) == BitVecVal(prefix, prefix_bits))

    started = time.monotonic()
    status = solver.check()
    elapsed = round(time.monotonic() - started, 3)
    result = {
        "status": "SAT" if status == sat else "UNSAT" if status == unsat else "UNKNOWN",
        "seconds": elapsed,
        "timeout_ms": timeout_ms,
        "prefix_bits": prefix_bits,
        "prefix": hex(prefix) if prefix_bits else None,
    }
    if status != sat:
        if status != unsat:
            result["reason_unknown"] = solver.reason_unknown()
        return result

    model = solver.model()
    state = (
        model.eval(s0, model_completion=True).as_long(),
        model.eval(s1, model_completion=True).as_long(),
    )
    generated = stream(state)
    middle = generated[2:4]
    result["state_hex"] = [f"{word:016X}" for word in state]
    result["generated_hex"] = [f"{word:016X}" for word in generated]
    result["middle_hex"] = [f"{word:016X}" for word in middle]

    solver.push()
    solver.add(Or(outputs[2] != BitVecVal(middle[0], 64),
                  outputs[3] != BitVecVal(middle[1], 64)))
    started = time.monotonic()
    alternative = solver.check()
    result["uniqueness_seconds"] = round(time.monotonic() - started, 3)
    result["unique_middle"] = alternative == unsat
    result["uniqueness_status"] = (
        "UNIQUE" if alternative == unsat else
        "ALTERNATIVE" if alternative == sat else "UNKNOWN"
    )
    if alternative == sat:
        alt_model = solver.model()
        result["alternative_middle_hex"] = [
            f"{alt_model.eval(outputs[i], model_completion=True).as_long():016X}"
            for i in (2, 3)
        ]
    elif alternative != unsat:
        result["uniqueness_reason_unknown"] = solver.reason_unknown()
    solver.pop()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--view", type=int, choices=range(4), required=True)
    parser.add_argument("--timeout-ms", type=int, default=300000)
    parser.add_argument("--control-timeout-ms", type=int, default=120000)
    parser.add_argument("--result-path", default="k04-xoroshiro128pp-z3-result.json")
    args = parser.parse_args()

    from z3 import get_version_string
    p0, p4 = parse_source()
    mask, commitment = load_k04()
    observed0 = decode(p0, args.view)
    observed4 = decode(p4, args.view)
    known = {0: observed0[0], 1: observed0[1],
             4: observed4[0], 5: observed4[1]}

    synthetic_words = stream(SEED)
    synthetic_known = {0: synthetic_words[0], 1: synthetic_words[1],
                       4: synthetic_words[4], 5: synthetic_words[5]}
    control = solve_known(
        args.view, synthetic_known, args.control_timeout_ms,
        prefix_bits=16, prefix=SEED[0] & 0xFFFF
    )
    control["expected_middle_hex"] = [f"{word:016X}" for word in synthetic_words[2:4]]
    control["middle_matches_seed"] = (
        control.get("middle_hex") == control["expected_middle_hex"]
    )
    if control["status"] != "SAT" or not control["middle_matches_seed"]:
        result = {
            "view": args.view,
            "z3_version": get_version_string(),
            "source_sha256": SOURCE_SHA,
            "control": control,
            "original": {"status": "NOT_RUN", "reason": "synthetic control did not recover planted middle"},
        }
    else:
        original = solve_known(args.view, known, args.timeout_ms)
        original["observed_flank_words"] = {
            "outputs_0_1": [f"{word:016X}" for word in observed0],
            "outputs_4_5": [f"{word:016X}" for word in observed4],
        }
        if original["status"] == "SAT":
            coupon = encode([int(word, 16) for word in original["middle_hex"]], args.view)
            component = bytes(a ^ b for a, b in zip(coupon, mask))
            digest = hashlib.sha256(component).hexdigest()
            original["coupon_hex"] = coupon.hex().upper()
            original["component_hex"] = component.hex().upper()
            original["component_sha256"] = digest
            original["K04_commitment_match"] = digest == commitment
        result = {
            "view": args.view,
            "z3_version": get_version_string(),
            "source_sha256": SOURCE_SHA,
            "control": control,
            "original": original,
        }

    result["model_note"] = (
        "Conjectural xoroshiro128++ producer: REQUESTED1 and REQUESTED3 are "
        "observed flanks; outputs 2/3 are proposed coupon. ACK2 is not used."
    )
    pathlib.Path(args.result_path).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
