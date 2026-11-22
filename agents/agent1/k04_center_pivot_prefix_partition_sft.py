#!/usr/bin/env python3
"""Branch decomposition calibration for H-17 conditional xoroshiro128++ output3/4/5.

This differs from a longer timeout or another solver. Fix independently
chosen lower 8/12/16 bits of the hidden state4 word a4 before fitting three
outputs. Source is intentionally unreachable in this calibrated SFT.
"""
from __future__ import annotations
import argparse
import json
import time
import sys
from pathlib import Path

SELF = Path(__file__).resolve()
sys.path.insert(0, str(SELF.parents[1] / "agent1"))
sys.path.insert(0, str(SELF.parents[1] / "agent30"))
from k04_center_pivot_triad_sft import circuit_from_center, forward, backward, MASK64
from k04_xoropp_triad_calibration_sft import STATES
from k04_dual_inverse_borrow_reference import stream


def fit(observed: list[int], prefix_bits: int, prefix: int, seconds: int) -> dict:
    from pycryptosat import Solver
    circuit, a4, t4 = circuit_from_center(observed)
    solver = Solver(threads=1, time_limit=float(seconds))
    for variables, rhs in circuit.xors:
        solver.add_xor_clause(variables, rhs)
    for clause in circuit.clauses:
        solver.add_clause(clause)
    for bit in range(prefix_bits):
        solver.add_clause([a4[bit] if (prefix >> bit) & 1 else -a4[bit]])
    start = time.monotonic()
    status, assignment = solver.solve()
    result = {"status": "SAT" if status is True else "UNSAT" if status is False else "UNKNOWN",
              "seconds": round(time.monotonic() - start, 3),
              "prefix_bits": prefix_bits, "prefix": f"{prefix:0{(prefix_bits+3)//4}X}",
              "variables": circuit.count,
              "cnf_clauses": len(circuit.clauses) + prefix_bits,
              "xor_clauses": len(circuit.xors),
              "original_K04_evaluated": False}
    if status is True:
        a = sum(int(assignment[v]) << bit for bit, v in enumerate(a4))
        t = sum(int(assignment[v]) << bit for bit, v in enumerate(t4))
        initial = (a, a ^ t)
        for _ in range(4):
            initial = backward(initial)
        assert stream(initial, 6)[3:6] == observed
        result["recovered_initial_state"] = [f"{x:016X}" for x in initial]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--state-count", type=int, default=8)
    args = parser.parse_args()
    assert 1 <= args.seconds <= 120
    assert 1 <= args.state_count <= 8
    results: dict[str, int | list[dict]] = {}
    for prefix_bits in (8, 12, 16):
        exact = 0
        unknown = 0
        unsat = 0
        for i, pair in enumerate(STATES[:args.state_count]):
            initial = tuple(int(v, 16) for v in pair)
            state4 = initial
            for _ in range(4):
                state4 = forward(state4)
            state3 = backward(state4)
            observed = stream(state3, 3)
            prefix = state4[0] & ((1 << prefix_bits) - 1)
            row = fit(observed, prefix_bits, prefix, args.seconds)
            matched = row.get("recovered_initial_state") == [f"{x:016X}" for x in initial]
            row.update({"kind": "frozen_correct_prefix_positive",
                        "frozen_index": i, "exact_state_recovered": matched if row["status"] == "SAT" else None,
                        "source_independent": True})
            print(json.dumps(row, sort_keys=True), flush=True)
            exact += int(matched)
            unknown += int(row["status"] == "UNKNOWN")
            unsat += int(row["status"] == "UNSAT")
        results[str(prefix_bits)] = {"exact_recovered": exact,
                                     "unknown": unknown, "unsat": unsat,
                                     "of": args.state_count}
        print(json.dumps({"calibration_prefix_bits": prefix_bits,
                          "summary": results[str(prefix_bits)]}, sort_keys=True), flush=True)
        if exact >= args.state_count - 1:
            break
    print(json.dumps({"all_calibrations": results,
                      "historical_source": "NOT_TESTED",
                      "original_K04_commitment": "NOT_EVALUATED"}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
