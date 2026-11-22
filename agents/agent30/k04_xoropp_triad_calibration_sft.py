#!/usr/bin/env python3
"""Frozen independent-state calibration for the reverse xoroshiro128++ triad.

This is a solver-liveness calibration only: no H-17 source bytes, candidate,
mask, or commitment are read. Each state is fixed before execution. The solver
sees only outputs 3, 4, and 5; the complete initial state and outputs 2/3 are
withheld and compared after inversion.
"""
from __future__ import annotations

import argparse
import json
import time

# Importing the triad runner first installs its exact agent36/agent50 paths.
from k04_xoropp_reverse_tail_triad_sft import forward, run_triad
from k04_dual_inverse_borrow_reference import stream

# Eight independent 128-bit states frozen before the calibration run.
STATES = (
    ("F007C59F9D9F4FB7", "C4CAE249D983EBD2"),
    ("2321A6781869EFE4", "ADE1F00D94B03946"),
    ("09BF52A28180679C", "C9EE30F095FC4904"),
    ("BBEB7C1CD5849259", "C3C0358F7BB3AFDF"),
    ("192CF5F4EBEAA437", "8172B263A2AD16A1"),
    ("E5AE140F20F001EF", "6DC3F607A400549A"),
    ("33BA4F681216A22B", "3D4FA00D07FC8AEB"),
    ("114BB35E07789458", "4282F657EB75517A"),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-seconds", type=int, default=120)
    args = parser.parse_args()
    assert 1 <= args.limit_seconds <= 300

    started_all = time.monotonic()
    rows = []
    for index, pair in enumerate(STATES):
        initial = tuple(int(x, 16) for x in pair)
        state3 = initial
        for _ in range(3):
            state3 = forward(state3)
        observed = stream(state3, 3)

        result = run_triad(observed, args.limit_seconds, index, False)
        expected = stream(initial, 6)
        recovered_state = result.get("initial_state")
        recovered_full = result.get("complete_generated_words")
        exact_state = recovered_state == [f"{x:016X}" for x in initial]
        exact_full = recovered_full == [f"{x:016X}" for x in expected]
        exact_middle = result.get("complete_middle_words") == [
            f"{x:016X}" for x in expected[2:4]
        ]
        row = {
            "calibration_index": index,
            "frozen_state": list(pair),
            "observed_outputs_3_4_5": [f"{x:016X}" for x in observed],
            "status": result["status"],
            "elapsed_seconds": result["elapsed_seconds"],
            "variables": result["variables"],
            "cnf_clauses": result["clauses"],
            "xor_clauses": result["xor_clauses"],
            "exact_initial_state": exact_state if result["status"] == "SAT" else None,
            "exact_full_replay": exact_full if result["status"] == "SAT" else None,
            "exact_withheld_middle": exact_middle if result["status"] == "SAT" else None,
            "recovered_state": recovered_state,
            "recovered_middle_words": result.get("complete_middle_words"),
            "source_independent": True,
            "historical_K04_evaluated": False,
        }
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)

    sat = [r for r in rows if r["status"] == "SAT"]
    unknown = [r for r in rows if r["status"] == "UNKNOWN"]
    unsat = [r for r in rows if r["status"] == "UNSAT"]
    exact = [r for r in sat if r["exact_initial_state"] and
             r["exact_full_replay"] and r["exact_withheld_middle"]]
    summary = {
        "calibration": "eight frozen independent unseeded planted triad inversions",
        "states_total": len(rows),
        "sat": len(sat),
        "unsat": len(unsat),
        "unknown": len(unknown),
        "exact_full_recoveries": len(exact),
        "time_limit_seconds_each": args.limit_seconds,
        "total_elapsed_seconds": round(time.monotonic() - started_all, 3),
        "historical_K04_evaluated": False,
    }
    print(json.dumps({"summary": summary}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
