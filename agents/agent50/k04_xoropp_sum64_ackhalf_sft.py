"""H-17 K04 xoroshiro128++ first-pair inverse using ONE 64-bit unknown.

Exact elimination of the first observed 64-bit xoroshiro128++ output,
followed by constraints from both independent intact REQUESTED1/3 flanks:
  P = s0 + s1 mod 2^64
  s0 = y0 - rotl(P,17), s1 = P - s0.
The second observed output becomes ONE equation in P. No 128-bit
state-vector variables or first-output SAT encoding are needed.

A single 64-bit copied ACK2 half is *conditionally* treated as intact,
while REQUESTED1 and REQUESTED3 supply four other observed outputs. Only
the original K04 commitment can authenticate the reconstructed full coupon. A complete inferred ACK2 coupon is checked
against the original full K04 commitment before any source attribution assessment.
Official xoroshiro128++ 1.0: https://prng.di.unimi.it/xoroshiro128plusplus.c

Dependency: z3-solver. Run:
  python agents/agent50/k04_xoropp_sum64_ackhalf_sft.py --synthetic
  python agents/agent50/k04_xoropp_sum64_inverse_sft.py --source-view 0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = (1 << 64) - 1


def rol(x: int, n: int) -> int:
    return ((x << n) | (x >> (64 - n))) & MASK


def step(a: int, b: int) -> tuple[int, int, int]:
    output = (rol((a + b) & MASK, 17) + a) & MASK
    t = a ^ b
    return output, (rol(a, 49) ^ t ^ ((t << 21) & MASK)) & MASK, rol(t, 28)


def sequence(state: tuple[int, int], count: int = 6) -> list[int]:
    a, b = state
    result = []
    for _ in range(count):
        out, a, b = step(a, b)
        result.append(out)
    return result


def source_packets() -> tuple[bytes, bytes]:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw, re.M,
    )
    assert len(rows) == 133
    assert rows[128][:5] == (b"2026-10-03T18:01:00Z", b"PS-261003-0417",
                              b"1", b"REQUESTED", b"RECOVER")
    assert rows[129][:5] == (b"2026-10-03T18:02:00Z", b"PS-261003-0417",
                              b"2", b"ACK", b"RECOVER")
    assert rows[130][:5] == (b"2026-10-03T18:03:00Z", b"PS-261003-0417",
                              b"3", b"REQUESTED", b"RECOVER")
    # Never parse or decode selected copied ACK2 PAYLOAD.
    return bytes.fromhex(rows[128][5].decode()), bytes.fromhex(rows[130][5].decode())


def decode(packet: bytes, view: int) -> list[int]:
    endian = "little" if view & 1 else "big"
    words = [int.from_bytes(packet[i:i + 8], endian) for i in (0, 8)]
    if view & 2:
        words.reverse()
    return words


def encode(words: list[int], view: int) -> bytes:
    endian = "little" if view & 1 else "big"
    words = list(words)
    if view & 2:
        words.reverse()
    return b"".join(w.to_bytes(8, endian) for w in words)


def solve_two(first: list[int], future: list[int], middle_half: int, middle_value: int, timeout_ms: int, max_models: int) -> dict:
    from z3 import BitVec, BitVecVal, RotateLeft, SolverFor, sat, unsat

    y0, y1 = first
    total = BitVec("sum_state0", 64)
    # y0 was observed. Represent both 64-bit state words as an expression
    # in one 64-bit unknown, removing the first output constraint entirely.
    a0 = BitVecVal(y0, 64) - RotateLeft(total, 17)
    b0 = total - a0
    t = a0 ^ b0
    a1 = RotateLeft(a0, 49) ^ t ^ (t << 21)
    b1 = RotateLeft(t, 28)
    predicted_y1 = RotateLeft(a1 + b1, 17) + a1

    solver = SolverFor("QF_BV")
    solver.set(timeout=timeout_ms)
    solver.add(predicted_y1 == BitVecVal(y1, 64))
    # Derive outputs 2,3 and constrain the *second* intact REQUESTED flank
    # at positions 4,5 without inspecting disputed selected ACK2 bytes.
    aa, bb = a1, b1
    for index in range(2, 6):
        t = aa ^ bb
        aa, bb = RotateLeft(aa, 49) ^ t ^ (t << 21), RotateLeft(t, 28)
        if index == middle_half + 2:
            solver.add(RotateLeft(aa + bb, 17) + aa == BitVecVal(middle_value, 64))
        if index >= 4:
            solver.add(RotateLeft(aa + bb, 17) + aa == BitVecVal(future[index - 4], 64))

    models: list[tuple[int, int]] = []
    status = "UNKNOWN"
    started = time.monotonic()
    for _ in range(max_models):
        status_result = solver.check()
        if status_result != sat:
            status = "UNSAT_OR_EXHAUSTED" if status_result == unsat else "UNKNOWN"
            break
        value = solver.model().eval(total).as_long()
        a = (y0 - rol(value, 17)) & MASK
        b = (value - a) & MASK
        assert sequence((a, b), 2) == first, "symbolic state mismatch"
        assert sequence((a, b), 6)[4:6] == future, "future source mismatch"
        assert sequence((a, b), 6)[middle_half + 2] == middle_value, "copied middle mismatch"
        models.append((a, b))
        solver.add(total != BitVecVal(value, 64))
    else:
        status = "MODEL_LIMIT"
    return {
        "status": status,
        "states": models,
        "model_count": len(models),
        "elapsed_sec": round(time.monotonic() - started, 3),
        "initial_symbolic_state_bits": 64,
        "historical_source_four_outputs_conditioned": True,
        "copied_middle_half_conditioned": middle_half,
        "first_observed_output_exactly_eliminated": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    select = ap.add_mutually_exclusive_group(required=True)
    select.add_argument("--synthetic", action="store_true")
    select.add_argument("--source-view", type=int, choices=range(4))
    ap.add_argument("--ack-half", type=int, choices=(0, 1), default=0)
    ap.add_argument("--timeout-ms", type=int, default=180000)
    ap.add_argument("--max-models", type=int, default=8)
    args = ap.parse_args()
    assert 1 <= args.timeout_ms <= 300000
    assert 1 <= args.max_models <= 64
    if args.synthetic:
        tests = [
            (0x123456789ABCDEF0, 0xFEDCBA9876543210),
            (0x8C3C010CB4754C91, 0x1055BB2244DACC0F),
        ]
        for idx, planted in enumerate(tests):
            original = sequence(planted)
            result = solve_two(original[:2], original[4:6], args.ack_half, original[2 + args.ack_half], args.timeout_ms, args.max_models)
            result["test"] = idx
            result["planted_middle_recovered"] = any(
                sequence(candidate, 4)[2:] == original[2:4]
                for candidate in result["states"]
            )
            result["planted_future_recovered"] = any(
                sequence(candidate, 6) == original
                for candidate in result["states"]
            )
            result.pop("states")
            print(json.dumps(result, sort_keys=True), flush=True)
            assert result["planted_middle_recovered"] and result["planted_future_recovered"], (
                "unseeded full-state inversion failed; original source must remain gated"
            )
        return

    packet1, packet3 = source_packets()
    # Conditional experiment ONLY: trust exactly one 64bit word of the
    # rejected ACK2 copy. Its authenticity is not established.
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    source_lines = re.findall(rb"^\S+ JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=([A-F0-9]{32}) DEST=bench$", raw, re.M)
    assert len(source_lines) == 1
    middle_half = decode(bytes.fromhex(source_lines[0].decode()), args.source_view)[args.ack_half]
    first = decode(packet1, args.source_view)
    withheld_future = decode(packet3, args.source_view)
    result = solve_two(first, withheld_future, args.ack_half, middle_half, args.timeout_ms, args.max_models)
    result.update({
        "original_spool_sha256": SOURCE_SHA,
        "source_view": args.source_view,
        "selected_ACK2_copied_payload_used": True,
        "selected_ACK2_copied_half_assumption": args.ack_half,
        "source_fit_scope": "REQUESTED1 outputs0,1, REQUESTED3 outputs4,5, copied ACK2 speculative one output",
        "component_results": [],
    })
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"].lower()
    for state in result["states"]:
        outputs = sequence(state)
        coupon = encode(outputs[2:4], args.source_view)
        component = bytes(x ^ y for x, y in zip(coupon, mask))
        hit = hashlib.sha256(component).hexdigest().lower() == target
        result["component_results"].append({
            "full_K04_commitment_PASS": hit,
            "complete_coupon_hex": coupon.hex().upper(),
            "complete_component_hex": component.hex().upper(),
            "speculative_REQUESTED3_replay_matches": outputs[4:6] == withheld_future,
        })
    result.pop("states")
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
