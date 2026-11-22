#!/usr/bin/env python3
"""Source-conditional K04 five-output xoroshiro128++ bridge.

Fit complete 18:01 REQUESTED1 words 0/1, assumed intact 18:02 ACK2
last-eight-byte word 3 and complete 18:03 REQUESTED3 words 4/5.
Withhold ACK2 first eight bytes and every acceptance value during inversion.
On SAT, emit a complete 16-byte coupon and test original K04 commitment.
On UNKNOWN do not claim source inconsistency.

The source-to-generator association and copied ACK2 tail fidelity are conjectures.
Requires pycryptosat 5.14.7 and agent30/36/50 source modules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

AGENTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTS / "agent30"))
sys.path.insert(0, str(AGENTS / "agent36"))
sys.path.insert(0, str(AGENTS / "agent50"))
from k04_dual_inverse_borrow_reference import BorrowCircuit, SEED, stream
from k04_xoropp_reverse_fourword_sft import backward, forward, reverse_bits
from k04_xoroshiropp_xorcnf_sft import ROOT, SOURCE_SHA, decode, encode, parse_source


def construct(observed: list[int], seeded_state3: tuple[int, int] | None = None):
    """Native-XOR CNF: constrain known outputs [0,1,3,4,5]."""
    assert len(observed) == 5
    y0, y1, y3, y4, y5 = observed
    circuit = BorrowCircuit()
    (a3, t3), _ = circuit.build_first_pair(y3, y4, seed=seeded_state3)
    a4, b4 = circuit.step_from_t(a3, t3)
    a5, b5 = circuit.step(a4, b4)
    circuit.constrain_output(a5, b5, y5)
    b3 = [circuit.xor(x, y) for x, y in zip(a3, t3)]
    a2, b2 = reverse_bits(circuit, a3, b3)
    a1, b1 = reverse_bits(circuit, a2, b2)
    a0, b0 = reverse_bits(circuit, a1, b1)
    circuit.constrain_output(a1, b1, y1)
    circuit.constrain_output(a0, b0, y0)
    return circuit, a3, t3


def validate_seeded() -> None:
    rng = random.Random(0x23170005)
    for index in range(100):
        seed = SEED if index == 0 else (rng.getrandbits(64), rng.getrandbits(64))
        outputs = stream(seed, 6)
        s3 = seed
        for _ in range(3):
            s3 = forward(s3)
        assert backward(forward(s3)) == s3
        circuit, a3, t3 = construct([outputs[i] for i in (0, 1, 3, 4, 5)], s3)
        circuit.validate_witness()
        assert circuit.bits_to_int(a3) == s3[0]
        assert circuit.bits_to_int(t3) == s3[0] ^ s3[1]
    print(json.dumps({"stage": "seeded_100_state_circuit_witness", "status": "PASS"}), flush=True)


def invert(observed: list[int], budget_seconds: int, label: str, view: int) -> dict:
    from pycryptosat import Solver

    circuit, a3, t3 = construct(observed)
    solver = Solver(threads=1, time_limit=float(budget_seconds))
    for variables, parity in circuit.xors:
        solver.add_xor_clause(variables, parity)
    for clause in circuit.clauses:
        solver.add_clause(clause)
    start = time.monotonic()
    status, model = solver.solve()
    result = {
        "experiment": label,
        "view": view,
        "fit_positions": [0, 1, 3, 4, 5],
        "withheld_position": 2,
        "ACK2_first_eight_bytes_withheld": True,
        "status": "SAT" if status is True else "UNSAT" if status is False else "UNKNOWN",
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "variables": circuit.count,
        "clauses": len(circuit.clauses),
        "xor_clauses": len(circuit.xors),
        "historical_K04_status": "NOT_EVALUATED",
    }
    if status is not True:
        return result
    a = sum(int(model[v]) << bit for bit, v in enumerate(a3))
    t = sum(int(model[v]) << bit for bit, v in enumerate(t3))
    initial = (a, a ^ t)
    for _ in range(3):
        initial = backward(initial)
    words = stream(initial, 6)
    assert [words[i] for i in (0, 1, 3, 4, 5)] == observed
    result["initial_state"] = [f"{v:016X}" for v in initial]
    result["complete_selected_words"] = [f"{v:016X}" for v in words[2:4]]
    result["complete_replayed_words"] = [f"{v:016X}" for v in words]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-seconds", type=int, default=240)
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args()
    assert 1 <= args.limit_seconds <= 300
    validate_seeded()
    expected = stream(SEED, 6)
    synthetic = invert([expected[i] for i in (0, 1, 3, 4, 5)],
                       args.limit_seconds, "unseeded_planted_five_output", 0)
    if synthetic["status"] == "SAT":
        synthetic["exact_initial"] = synthetic["initial_state"] == [f"{v:016X}" for v in SEED]
        synthetic["exact_withheld_word"] = synthetic["complete_selected_words"] == [f"{v:016X}" for v in expected[2:4]]
    print(json.dumps(synthetic, sort_keys=True), flush=True)
    if args.synthetic_only:
        return

    first, middle, third = parse_source()
    for view in (0, 1):
        earlier = decode(first, view)
        copied = decode(middle, view)
        later = decode(third, view)
        observed = [*earlier, copied[1], *later]
        result = invert(observed, args.limit_seconds, "historical_five_output", view)
        result["source_sha256"] = SOURCE_SHA
        if result["status"] == "SAT":
            words = [int(v, 16) for v in result["complete_selected_words"]]
            coupon = encode(words, view)
            assert coupon[8:] == middle[8:]
            result["full_coupon"] = coupon.hex().upper()
            result["copied_ACK2_first8_match"] = coupon[:8] == middle[:8]
            mask = bytes.fromhex(json.loads((ROOT / "evidence/recovery-routing.json").read_text())["K04"]["masked_component"])
            commitment = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"]
            component = bytes(a ^ b for a, b in zip(coupon, mask))
            result["full_component"] = component.hex().upper()
            result["historical_K04_status"] = (
                "PASS" if hashlib.sha256(component).hexdigest() == commitment.lower()
                else "MISS_FULL_CANDIDATE"
            )
        print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
