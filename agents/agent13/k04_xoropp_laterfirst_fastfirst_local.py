#!/usr/bin/env python3
"""Local-only, source-safe K04 *candidate-first* early pass.

The existing 4096-cube exact xoroshiro128++ reconstruction can be expensive to
close UNSAT. This pass extracts one firstpair SAT state (if available), checks
all 18 complete reverse coupon windows against the unchanged original K04
commitment immediately, and persists that state to the pre-existing private
cache. A one-model SAT pass NEVER seals a cube: its terminal marker is UNKNOWN.
A first-query UNSAT really proves an empty cube. Follow this speed-oriented
pass with the exact model-blocking phase for all remaining open cubes.

Reads only named pin-verified non-PDF resources; never uses selected ACK2 as
an input, never outputs original bytes, models, coupons or component digests.
Historical source must remain outside public CI. No generator is authenticated.
"""
from __future__ import annotations
import argparse
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agents.agent27.k04_xoropp_sparse12_gap_synthetic import solve, stream
from agents.agent37.k04_private_state_ledger_sft import (
    P12, read_cube, write_attempt, _secure_dir,
)
from agents.agent37.k04_xoropp_cached_source_local import read_inputs, escrow_hits
from agents.agent1.k04_xoropp_laterfirst_backwards_local import scan_state

def first_model(job):
    cube, first, timeout_ms = job
    anchor = sum(((cube >> j) & 1) << bit for j, bit in enumerate(P12))
    result, state = solve({0: first[0], 1: first[1]},
                          anchor, P12, timeout_ms)
    if result not in ("sat", "unsat", "unknown"):
        raise RuntimeError("Unexpected solver disposition")
    if state is not None:
        assert result == "sat"
        assert stream(*state, 2) == list(first)
    return cube, result, state

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--resources-root", type=Path, default=ROOT / "resources")
    ap.add_argument("--private-dir", type=Path, required=True)
    ap.add_argument("--local-hit-escrow", type=Path, required=True)
    ap.add_argument("--endian", choices=("big", "little"), required=True)
    ap.add_argument("--order", choices=("ab", "ba"), required=True)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=4096)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout-ms", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=20261128,
                    help="Deterministic ordering only; never an original generator seed")
    args = ap.parse_args()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        ap.error("Historical source processing forbidden in public CI")
    if not (0 <= args.start < 4096 and
            1 <= args.count <= 4096 - args.start and
            1 <= args.workers <= 4 and
            100 <= args.timeout_ms <= 30000):
        ap.error("Invalid bounded scan")

    ledger_root = _secure_dir(args.private_dir)
    hit_path = args.local_hit_escrow.expanduser()
    if hit_path.resolve() == ROOT or ROOT in hit_path.resolve().parents:
        ap.error("Private hit escrow must be outside the repository")
    if hit_path.parent.resolve() != ledger_root:
        ap.error("Escrow and cache must share the verified private directory")
    first, earlier, mask, original_target, metadata = read_inputs(
        args.resources_root, args.endian, args.order, 3)
    # In this *later-first* hypothesis, first is intact REQUESTED3;
    # earlier is intact REQUESTED1, a diagnostic only.
    import random
    buckets = [c for c in range(args.start, args.start + args.count)
               if read_cube(ledger_root, metadata, c)["status"] == "unvisited"]
    random.Random(args.seed).shuffle(buckets)
    counts = {"requested": args.count, "unvisited_scheduled": len(buckets),
              "completed": 0, "first_sat_states": 0, "first_query_unsat": 0,
              "first_query_unknown": 0, "full_coupon_windows_checked": 0,
              "verified_original_K04_hits": 0, "privately_escrowed": 0}
    started = time.monotonic()

    with mp.Pool(args.workers) as pool:
        jobs = ((cube, first, args.timeout_ms) for cube in buckets)
        for cube, status, state in pool.imap_unordered(first_model, jobs, chunksize=1):
            # Examine this complete state NOW, before a potentially expensive
            # in-cube model-blocking/UNSAT tail or any retry replay gate.
            verified = []
            if state is not None:
                summary, components = scan_state(
                    state, earlier, first, mask, original_target,
                    args.endian, args.order, 17, 8)
                assert summary["candidate_windows"] == 18
                verified = [bytes.fromhex(component) for component in components]
                counts["full_coupon_windows_checked"] += 18
                counts["first_sat_states"] += 1
            else:
                counts["first_query_unsat"] += int(status == "unsat")
                counts["first_query_unknown"] += int(status == "unknown")
            if verified:
                escrow_hits(hit_path, verified)
                counts["verified_original_K04_hits"] += len(verified)
                counts["privately_escrowed"] += len(verified)
            # "SAT" is only the FIRST model: other compatible states may exist.
            terminal = "unknown" if status == "sat" else status
            write_attempt(ledger_root, metadata, cube,
                          [state] if state else [], terminal, args.timeout_ms)
            counts["completed"] += 1
            if counts["completed"] % 100 == 0 or counts["completed"] == len(buckets):
                print("AGGREGATE_ONLY", {
                    "hypothesis": "xoroshiro128++ later-first first-model triage",
                    "view": args.endian + "/" + args.order,
                    "candidate_word_starts": [2, 19],
                    "selected_ACK2_unfitted": True,
                    "all_open_cubes_still_require_exact_model_blocking": True,
                    "remaining_first_pass": len(buckets) - counts["completed"],
                    "elapsed_seconds": round(time.monotonic() - started, 2),
                    **counts,
                }, flush=True)

if __name__ == "__main__":
    main()
