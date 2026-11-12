#!/usr/bin/env python3
"""Run the exact A7-linked CPython K04 necessary model through Bitwuzla.

A SAT result is only a seed candidate: every candidate is replayed through
real CPython against all 132 intact packets, and the withheld row-129 coupon
must still pass the K04 SHA-256 commitment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

from bitwuzla import Option, Options, Parser, TermManager

from k04_cpython_a7cut_cvc5 import (
    ROOT, TARGET_ROW, ROUTING, ACCEPTANCE, OFFSET,
    source_packets, synthetic_controls, check_forward_real_python,
    original_source, forward_sieve, with_constraints, validate_seed,
)
from k04_cpython_a7linked_cvc5 import link_a7_to_seed

OUTDIR = ROOT / "artifacts/k04-cpython-a7linked-bitwuzla"


class Deadline:
    def __init__(self, seconds: int) -> None:
        self.deadline = time.monotonic() + seconds
        self.expired = False

    def __call__(self) -> bool:
        self.expired = time.monotonic() >= self.deadline
        return self.expired


def verdict_name(result) -> str:
    value = str(result).strip().lower()
    if value in {"sat", "result.sat"}:
        return "SAT"
    if value in {"unsat", "result.unsat"}:
        return "UNSAT"
    if value in {"unknown", "result.unknown"}:
        return "UNKNOWN"
    raise RuntimeError(f"Unexpected Bitwuzla result: {result!r}")


def solve(formula: str, key_words: int, timeout_seconds: int):
    cleaned = "\n".join(
        line for line in formula.splitlines()
        if not line.lstrip().startswith(("(set-option", "(check-sat)", "(get-value"))
    )
    manager = TermManager()
    options = Options()
    options.set(Option.PRODUCE_MODELS, True)
    options.set(Option.SAT_SOLVER, "cadical")
    parser = Parser(manager, options)
    parser.parse(cleaned, True, False)
    solver = parser.bitwuzla()
    deadline = Deadline(timeout_seconds)
    solver.configure_terminator(deadline)
    started = time.monotonic()
    result = verdict_name(solver.check_sat())
    elapsed = round(time.monotonic() - started, 3)
    keys = None
    if result == "SAT":
        keys = []
        for index in range(key_words):
            term = parser.parse_term(f"k{index}")
            value = str(solver.get_value(term).value(16)).lower()
            value = value.removeprefix("0x").removeprefix("#x")
            keys.append(int(value, 16))
    return result, keys, elapsed, deadline.expired


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, choices=(2, 3, 4), default=2)
    ap.add_argument("--stop", type=int, choices=(17, 41, 83), default=17)
    ap.add_argument("--timeout-seconds", type=int, default=600)
    ap.add_argument("--candidate-limit", type=int, default=8)
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    synthetic_controls()
    check_forward_real_python()
    packets = source_packets()
    masks = original_source()
    base = link_a7_to_seed(forward_sieve(args.n, args.stop, masks), args.n)
    blockers = []
    summary = {
        "solver": "Bitwuzla 0.9.1 / CaDiCaL",
        "model": "CPython integer-seed A7-linked",
        "n": args.n, "stop": args.stop, "offset": OFFSET,
        "target_row_excluded": TARGET_ROW, "controls": 132,
        "status": None, "candidate_count": 0, "result": None,
    }

    for attempt in range(args.candidate_limit):
        remaining = args.timeout_seconds - (time.monotonic() - started)
        if remaining <= 2:
            summary["status"] = "GLOBAL_TIMEOUT"
            break
        smt = with_constraints(base, args.n, blockers)
        (OUTDIR / f"n{args.n}_attempt{attempt+1}.smt2").write_text(smt)
        try:
            status, keys, elapsed, timed_out = solve(smt, args.n, max(1, int(remaining)))
        except Exception as exc:
            status, keys, elapsed, timed_out = "ERROR", None, 0.0, False
            (OUTDIR / f"n{args.n}_attempt{attempt+1}.txt").write_text(
                f"{type(exc).__name__}: {exc}\n"
            )
            summary.update(status=status, error=f"{type(exc).__name__}: {exc}")
            break

        (OUTDIR / f"n{args.n}_attempt{attempt+1}.txt").write_text(
            f"status={status}\nelapsed_seconds={elapsed}\nterminator_fired={timed_out}\n"
            + (f"seed_words={','.join(f'{x:08X}' for x in keys)}\n" if keys else "")
        )
        print(f"ATTEMPT={attempt+1} STATUS={status} ELAPSED={elapsed}", flush=True)
        summary["status"] = status
        summary["elapsed_last_attempt_seconds"] = elapsed
        summary["terminator_fired"] = timed_out
        if status != "SAT":
            break

        assert keys is not None
        summary["candidate_count"] += 1
        print("SEED_WORDS=" + ",".join(f"{x:08X}" for x in keys), flush=True)
        seed, target_payload, mismatches = validate_seed(keys, packets)
        summary["intact_packet_matches"] = 132 - len(mismatches)
        print(f"FULL_132_PACKET_MATCHES={132-len(mismatches)}/132", flush=True)
        if not mismatches:
            routing = json.loads(ROUTING.read_text())
            acceptance = json.loads(ACCEPTANCE.read_text())
            mask = bytes.fromhex(routing["K04"]["masked_component"])
            component = bytes(a ^ b for a, b in zip(target_payload, mask))
            digest = hashlib.sha256(component).hexdigest()
            summary.update(
                target_payload=target_payload.hex().upper(),
                component_sha256=digest,
            )
            print(f"K04_COMPONENT_SHA256={digest}", flush=True)
            if digest == acceptance["slot_sha256"]["K04"]:
                summary.update(
                    result="K04_VERIFIED",
                    seed_words=[f"{x:08X}" for x in keys],
                    component=component.hex().upper(),
                )
                print(f"K04_COMPONENT_VERIFIED={component.hex().upper()}", flush=True)
            else:
                summary["result"] = "FULL_SOURCE_MATCH_COMMITMENT_MISMATCH"
            break

        blockers.append(keys)
        print("RELAXED_CANDIDATE_BLOCKED_AFTER_FULL_SOURCE_MISMATCH", flush=True)

    summary["elapsed_seconds"] = round(time.monotonic() - started, 3)
    (OUTDIR / f"n{args.n}_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("SUMMARY=" + json.dumps(summary, sort_keys=True), flush=True)
    return 0 if summary["status"] != "ERROR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
