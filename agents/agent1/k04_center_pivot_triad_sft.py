#!/usr/bin/env python3
"""K04 xoroshiro128++ central-pivot triad: fit word4, predict word3 backward and word5 forward.

Independent, exactly source-gated alternative to the left-anchored three-word
inverse. The conditional copier hypothesis trusts ACK2 tail8 and REQUESTED3,
not ACK2 head8. No source or commitment enters synthetic calibration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

AGENTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTS / "agent36"))
sys.path.insert(0, str(AGENTS / "agent50"))
from k04_dual_inverse_borrow_reference import BorrowCircuit, MASK64, SEED, stream
from k04_xoroshiropp_xorcnf_sft import ROOT, SOURCE_SHA, decode, encode, parse_source

FROZEN = (
    (0xF007C59F9D9F4FB7, 0xC4CAE249D983EBD2),
    (0x2321A6781869EFE4, 0xADE1F00D94B03946),
    (0x09BF52A28180679C, 0xC9EE30F095FC4904),
    (0xBBEB7C1CD5849259, 0xC3C0358F7BB3AFDF),
)


def rol(x: int, k: int) -> int:
    return ((x << k) | (x >> (64 - k))) & MASK64


def forward(state: tuple[int, int]) -> tuple[int, int]:
    a, b = state
    t = a ^ b
    return ((rol(a, 49) ^ t ^ (t << 21)) & MASK64, rol(t, 28))


def backward(state: tuple[int, int]) -> tuple[int, int]:
    a1, b1 = state
    t = rol(b1, 36)
    a0 = rol(a1 ^ t ^ ((t << 21) & MASK64), 15)
    return a0, a0 ^ t


def circuit_from_center(words: list[int], seed4: tuple[int, int] | None = None):
    assert len(words) == 3
    c = BorrowCircuit()
    a4 = c.word(None if seed4 is None else seed4[0])
    t4 = c.get_t_from_output(a4, words[1])
    b4 = [c.xor(a, t) for a, t in zip(a4, t4)]
    t3 = c.rotated(b4, -28)
    mix = [c.xor(a4[i], t3[i], t3[i - 21] if i >= 21 else 0) for i in range(64)]
    a3 = c.rotated(mix, -49)
    b3 = [c.xor(a, t) for a, t in zip(a3, t3)]
    c.constrain_output(a3, b3, words[0])
    a5, b5 = c.step_from_t(a4, t4)
    c.constrain_output(a5, b5, words[2])
    return c, a4, t4


def solve(words: list[int], seconds: int) -> dict:
    from pycryptosat import Solver

    c, a4, t4 = circuit_from_center(words)
    solver = Solver(threads=1, time_limit=float(seconds))
    for variables, rhs in c.xors:
        solver.add_xor_clause(variables, rhs)
    for clause in c.clauses:
        solver.add_clause(clause)
    start = time.monotonic()
    status, assignment = solver.solve()
    r = {
        "status": "SAT" if status is True else "UNSAT" if status is False else "UNKNOWN",
        "seconds": round(time.monotonic() - start, 3),
        "variables": c.count, "cnf_clauses": len(c.clauses),
        "xor_clauses": len(c.xors), "fitted_outputs": [3, 4, 5],
        "original_K04_commitment": "NOT_EVALUATED",
    }
    if status is not True:
        return r
    a = sum(int(assignment[v]) << i for i, v in enumerate(a4))
    t = sum(int(assignment[v]) << i for i, v in enumerate(t4))
    center = (a, a ^ t)
    initial = center
    for _ in range(4):
        initial = backward(initial)
    words6 = stream(initial, 6)
    assert words6[3:6] == words
    r["initial_state"] = [f"{v:016X}" for v in initial]
    r["generated_words"] = [f"{v:016X}" for v in words6]
    return r


def controls() -> None:
    states = [SEED, *FROZEN]
    for seed in states:
        state4 = seed
        for _ in range(4):
            state4 = forward(state4)
        observed = stream(state4, 2)
        state3 = backward(state4)
        words = [stream(state3, 1)[0], *observed]
        c, a4, t4 = circuit_from_center(words, seed4=state4)
        c.validate_witness()
        assert c.bits_to_int(a4) == state4[0]
        assert c.bits_to_int(t4) == state4[0] ^ state4[1]
        assert backward(forward(seed)) == seed
        assert forward(backward(seed)) == seed
    print(json.dumps({"control": "five seeded center-pivot circuits with inverse and byte-exact witnesses", "status": "PASS"}), flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--limit-seconds", type=int, default=120)
    p.add_argument("--source-limit-seconds", type=int, default=180)
    p.add_argument("--source", action="store_true")
    args = p.parse_args()
    assert 1 <= args.limit_seconds <= 300
    assert 1 <= args.source_limit_seconds <= 300
    controls()
    passed = 0
    previously_unknown_recovered = 0
    for i, seed in enumerate(FROZEN):
        state3 = seed
        for _ in range(3):
            state3 = forward(state3)
        observed = stream(state3, 3)
        r = solve(observed, args.limit_seconds)
        exact = r.get("initial_state") == [f"{v:016X}" for v in seed]
        if exact:
            passed += 1
            previously_unknown_recovered += int(i != 3)
        r.update({"kind": "frozen_unseeded_control", "index": i,
                  "exact_recovery": exact if r["status"] == "SAT" else None})
        print(json.dumps(r, sort_keys=True), flush=True)
    summary = {"controls_exact": passed, "of": len(FROZEN),
               "old_circuit_unknown_cases_recovered": previously_unknown_recovered}
    print(json.dumps(summary, sort_keys=True), flush=True)
    if not args.source or passed < 2 or previously_unknown_recovered == 0:
        print(json.dumps({"original_source": "SKIPPED",
                          "reason": "source opt-in disabled or inversion liveness gate insufficient",
                          "K04": "NOT_EVALUATED"}), flush=True)
        return

    first, middle, later = parse_source()
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    for view in (0, 1):
        selected_tail = decode(middle, view)[1]
        known = [selected_tail, *decode(later, view)]
        r = solve(known, args.source_limit_seconds)
        r.update({"kind": "historical_center_pivot", "view": view,
                  "source_sha256": SOURCE_SHA, "copied_ack2_head8_excluded": True})
        if r["status"] == "SAT":
            out = [int(s, 16) for s in r["generated_words"]]
            coupon = encode(out[2:4], view)
            assert coupon[8:] == middle[8:]
            component = bytes(a ^ b for a, b in zip(coupon, mask))
            hit = hashlib.sha256(component).hexdigest() == acceptance["slot_sha256"]["K04"]
            r.update({"full_coupon": coupon.hex().upper(),
                      "full_component": component.hex().upper(),
                      "blind_requested1_match": out[:2] == decode(first, view),
                      "original_K04_commitment": "PASS" if hit else "MISS"})
        print(json.dumps(r, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
