#!/usr/bin/env python3
"""K04 selected ACK tail8: local three-word inverse and blind first-flank check.

Conditional issuer is xoroshiro128++ 1.0 with no omitted same-job draws.
For unswapped word serializers, copied ACK bytes8..15 are hypothetical
output3, followed by the two intact 18:03 REQUESTED output words4/5.
Invert that local *consecutive triad* at state3, roll back three state
updates, then require exact 18:01 REQUESTED output0/1 as a BLIND holdout.
ACK bytes0..7 and original K04 target are never fitted by the solver.
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
sys.path.insert(0, str(AGENTS / "agent36"))
sys.path.insert(0, str(AGENTS / "agent50"))
from k04_dual_inverse_borrow_reference import BorrowCircuit, MASK64, SEED, stream
from k04_xoroshiropp_xorcnf_sft import ROOT, SOURCE_SHA, decode, encode, parse_source


def rol(x: int, k: int) -> int:
    return ((x << k) | (x >> (64 - k))) & MASK64


def ror(x: int, k: int) -> int:
    return ((x >> k) | (x << (64 - k))) & MASK64


def forward(state: tuple[int, int]) -> tuple[int, int]:
    a, b = state
    t = a ^ b
    return ((rol(a, 49) ^ t ^ (t << 21)) & MASK64, rol(t, 28))


def backward(state: tuple[int, int]) -> tuple[int, int]:
    a1, b1 = state
    t = ror(b1, 28)
    a0 = ror(a1 ^ t ^ ((t << 21) & MASK64), 49)
    return a0, a0 ^ t


def circuit_for_triad(words: list[int], seed: tuple[int, int] | None = None):
    assert len(words) == 3
    circuit = BorrowCircuit()
    (a0, t0), _ = circuit.build_first_pair(words[0], words[1], seed=seed)
    a1, b1 = circuit.step_from_t(a0, t0)
    a2, b2 = circuit.step(a1, b1)
    circuit.constrain_output(a2, b2, words[2])
    return circuit, a0, t0


def run_triad(words: list[int], time_limit: int, view: int, original: bool) -> dict:
    from pycryptosat import Solver

    circuit, a0, t0 = circuit_for_triad(words)
    solver = Solver(threads=1, time_limit=float(time_limit))
    for variables, rhs in circuit.xors:
        solver.add_xor_clause(variables, rhs)
    for clause in circuit.clauses:
        solver.add_clause(clause)
    started = time.monotonic()
    status, model = solver.solve()
    result = dict(
        stage="historical_reverse_triad" if original else "unseeded_planted_reverse_triad",
        view=view, solver="CryptoMiniSat-5.14.7 native-XOR",
        generator="xoroshiro128++ 1.0, two 64-bit outputs per job attempt",
        selected_ack_head8_excluded=True, first_requested_held_out=True,
        fitted_output_positions=[3, 4, 5],
        status="SAT" if status is True else "UNSAT" if status is False else "UNKNOWN",
        elapsed_seconds=round(time.monotonic()-started, 3),
        variables=circuit.count, clauses=len(circuit.clauses), xor_clauses=len(circuit.xors),
        K04_status="NOT_EVALUATED",
    )
    if status is not True:
        return result
    a3 = sum(int(model[x]) << k for k, x in enumerate(a0))
    t3 = sum(int(model[x]) << k for k, x in enumerate(t0))
    state3 = (a3, a3 ^ t3)
    initial = state3
    for _ in range(3):
        initial = backward(initial)
    emitted = stream(initial, 6)
    assert emitted[3:6] == words
    result["initial_state"] = [f"{x:016X}" for x in initial]
    result["complete_middle_words"] = [f"{x:016X}" for x in emitted[2:4]]
    result["complete_generated_words"] = [f"{x:016X}" for x in emitted]
    return result


def controls() -> None:
    rng = random.Random(0xF17E2026)
    for i in range(100):
        state = SEED if i == 0 else (rng.getrandbits(64), rng.getrandbits(64))
        assert backward(forward(state)) == state
        assert forward(backward(state)) == state
        state3 = state
        for _ in range(3):
            state3 = forward(state3)
        words = stream(state3, 3)
        circuit, a0, t0 = circuit_for_triad(words, seed=state3)
        circuit.validate_witness()
        assert circuit.bits_to_int(a0) == state3[0]
        assert circuit.bits_to_int(t0) == (state3[0] ^ state3[1])
    print(json.dumps({"control": "100 seeded inverse+triad CNF/XOR circuits",
                      "status": "PASS"}), flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--limit-seconds", type=int, default=240)
    p.add_argument("--synthetic-only", action="store_true")
    args = p.parse_args()
    assert 1 <= args.limit_seconds <= 300
    controls()

    state3 = SEED
    for _ in range(3):
        state3 = forward(state3)
    planted = run_triad(stream(state3, 3), args.limit_seconds, 0, False)
    if planted["status"] == "SAT":
        planted["planted_state_recovered"] = planted["initial_state"] == [f"{v:016X}" for v in SEED]
        planted["planted_middle_recovered"] = planted["complete_middle_words"] == [f"{v:016X}" for v in stream(SEED, 6)[2:4]]
    print(json.dumps(planted, sort_keys=True), flush=True)
    if args.synthetic_only or planted.get("planted_middle_recovered") is not True:
        print(json.dumps({"original": "SKIPPED", "reason": "unseeded planted complete-middle gate unsolved",
                          "K04_status": "NOT_EVALUATED"}), flush=True)
        return

    first, middle, third = parse_source()
    for view in (0, 1):
        copied_words = decode(middle, view)
        later_words = decode(third, view)
        known_triad = [copied_words[1], *later_words]
        outcome = run_triad(known_triad, args.limit_seconds, view, True)
        outcome["source_sha256"] = SOURCE_SHA
        if outcome["status"] == "SAT":
            full = [int(v, 16) for v in outcome["complete_generated_words"]]
            outcome["blind_requested1_match"] = full[:2] == decode(first, view)
            coupon = encode(full[2:4], view)
            outcome["full_coupon"] = coupon.hex().upper()
            outcome["copied_tail8_match"] = coupon[8:] == middle[8:]
            assert outcome["copied_tail8_match"]
            # A complete selected coupon is always a commitment candidate.
            # The earlier REQUESTED1 replay is an independent producer holdout.
            mask = bytes.fromhex(json.loads((ROOT / "evidence/recovery-routing.json").read_text())["K04"]["masked_component"])
            expected = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"]
            component = bytes(a ^ b for a, b in zip(coupon, mask))
            hit = hashlib.sha256(component).hexdigest() == expected.lower()
            outcome["full_component"] = component.hex().upper()
            outcome["K04_status"] = "PASS" if hit else "MISS_FULL_CANDIDATE"
        print(json.dumps(outcome, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
