#!/usr/bin/env python3
"""Sparse-copied-ACK xoroshiro128++ bridge for the H-17 selected K04 coupon.

Research hypothesis: three consecutive RECOVER attempts share six successive
xoroshiro128++ outputs. The physical coupon copy may have lost one eight-byte
half. Require the first/last REQUESTED packets and only the retained ACK2
tail eight bytes; reconstruct the complete center packet without fitting its
other eight bytes. Nothing here authenticates the printer's issuer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "agent36"))
sys.path.insert(0, str(HERE / "agent50"))

from k04_dual_inverse_borrow_reference import BorrowCircuit, MASK64, SEED, stream
from k04_xoroshiropp_xorcnf_sft import ROOT, SOURCE_SHA, decode, encode, parse_source


def build_circuit(first: list[int], third: list[int], retained_word: int,
                  retained_index: int, seed: tuple[int, int] | None = None) -> tuple[BorrowCircuit, list[int], list[int]]:
    circuit = BorrowCircuit()
    (a0, t0), _ = circuit.build_first_pair(first[0], first[1], seed=seed)
    a1, b1 = circuit.step_from_t(a0, t0)
    a2, b2 = circuit.step(a1, b1)
    if retained_index == 0:
        circuit.constrain_output(a2, b2, retained_word)
    a3, b3 = circuit.step(a2, b2)
    if retained_index == 1:
        circuit.constrain_output(a3, b3, retained_word)
    a4, b4 = circuit.step(a3, b3)
    circuit.constrain_output(a4, b4, third[0])
    a5, b5 = circuit.step(a4, b4)
    circuit.constrain_output(a5, b5, third[1])
    return circuit, a0, t0


def fitted_fields(first_packet: bytes, copied_middle: bytes,
                  third_packet: bytes, view: int) -> tuple[list[int], list[int], int, int]:
    assert len(first_packet) == len(copied_middle) == len(third_packet) == 16
    index = 0 if view & 2 else 1
    return (decode(first_packet, view), decode(third_packet, view),
            decode(copied_middle, view)[index], index)


def solve_case(first_packet: bytes, copied_middle: bytes,
               third_packet: bytes, view: int, limit_seconds: int,
               source: bool = False) -> dict:
    from pycryptosat import Solver

    first, third, retained, index = fitted_fields(
        first_packet, copied_middle, third_packet, view
    )
    circuit, a0, t0 = build_circuit(first, third, retained, index)
    solver = Solver(threads=1, time_limit=float(limit_seconds))
    for variables, rhs in circuit.xors:
        solver.add_xor_clause(variables, rhs)
    for clause in circuit.clauses:
        solver.add_clause(clause)
    start = time.monotonic()
    status, model = solver.solve()
    result = {
        "experiment": "original_tail8_copy" if source else "unseeded_planted_tail8_copy",
        "view": view,
        "solver": "pycryptosat-native-xor",
        "fit": "REQUESTED1, REQUESTED3, exactly ACK2 copied bytes8..15",
        "selected_ACK2_head8_withheld": True,
        "planted_seed_withheld": True,
        "variables": circuit.count,
        "cnf_clauses": len(circuit.clauses),
        "xor_clauses": len(circuit.xors),
        "status": "SAT" if status is True else "UNSAT" if status is False else "UNKNOWN",
        "solve_seconds": round(time.monotonic() - start, 3),
        "K04_component_status": "NOT_EVALUATED",
    }
    if status is not True:
        return result

    initial_a = sum(int(model[bit]) << i for i, bit in enumerate(a0))
    initial_t = sum(int(model[bit]) << i for i, bit in enumerate(t0))
    generated = stream((initial_a, (initial_a ^ initial_t) & MASK64), 6)
    assert generated[:2] == first and generated[4:] == third
    coupon = encode(generated[2:4], view)
    assert coupon[8:] == copied_middle[8:]
    result.update(
        reconstructed_coupon=coupon.hex().upper(),
        initial_state=[f"{initial_a:016X}", f"{(initial_a ^ initial_t) & MASK64:016X}"],
        copied_middle_head8_same=(coupon[:8] == copied_middle[:8]),
    )
    if source:
        route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
        acceptance = json.loads((ROOT / "acceptance.json").read_text())
        mask = bytes.fromhex(route["K04"]["masked_component"])
        candidate = bytes(x ^ y for x, y in zip(coupon, mask))
        hit = hashlib.sha256(candidate).hexdigest() == acceptance["slot_sha256"]["K04"].lower()
        result["complete_component"] = candidate.hex().upper()
        result["K04_component_status"] = "PASS" if hit else "MISS_ONE_MODEL"
    return result


def source_free_circuit_controls() -> None:
    rng = random.Random(0x20261122)
    for i in range(20):
        seed = SEED if i == 0 else (rng.getrandbits(64), rng.getrandbits(64))
        outputs = stream(seed, 6)
        for view in range(4):
            first = encode(outputs[:2], view)
            middle = encode(outputs[2:4], view)
            third = encode(outputs[4:6], view)
            a, c, w, index = fitted_fields(first, middle, third, view)
            circuit, a0, t0 = build_circuit(a, c, w, index, seed=seed)
            circuit.validate_witness()
            reconstructed = (circuit.bits_to_int(a0), circuit.bits_to_int(t0))
            assert reconstructed == (seed[0], seed[0] ^ seed[1])
    print(json.dumps({"control": "80 seeded circuits and four serializers validated",
                      "status": "PASS"}), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-seconds", type=int, default=240)
    parser.add_argument("--mode", choices=("control", "both"), default="both")
    args = parser.parse_args()
    assert 1 <= args.limit_seconds <= 300
    source_free_circuit_controls()
    output = stream(SEED, 6)
    first = encode(output[:2], 0)
    real_middle = encode(output[2:4], 0)
    copied = bytes(b ^ 0xA5 for b in real_middle[:8]) + real_middle[8:]
    third = encode(output[4:6], 0)
    result = solve_case(first, copied, third, 0, args.limit_seconds)
    if result["status"] == "SAT":
        result["planted_complete_coupon_recovered"] = result["reconstructed_coupon"] == real_middle.hex().upper()
    print(json.dumps(result, sort_keys=True), flush=True)
    if args.mode == "control" or result.get("planted_complete_coupon_recovered") is not True:
        print(json.dumps({"source": "SKIPPED", "reason": "unseeded complete middle positive not recovered",
                          "K04_component_status": "NOT_EVALUATED"}), flush=True)
        return
    copied_rows = parse_source()  # exact source SHA and 18:01/18:02/18:03 selectors
    for view in range(4):
        result = solve_case(copied_rows[0], copied_rows[1], copied_rows[2],
                            view, args.limit_seconds, source=True)
        result["source_sha256"] = SOURCE_SHA
        print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
