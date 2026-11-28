#!/usr/bin/env python3
"""Synthetic-only zero-external-bit candidate generator for xoroshiro128++ erased-middle packets.

Each assignment of the 12 sparse initial-a bits is an EXACT partition of the
64-bit a0 state domain, not a guessed external witness. Fit only first packet
outputs y0,y1, independently verify the later intact y4,y5, then predict y2,y3.
This mathematical pilot does NOT read printer evidence, route masks, commitments,
any original source file, or the quarantined PDF. No historical K04 is claimed.

Requires libz3.so.4; reuses Agent27's exact Boolean output-conditioned solver.
"""
from __future__ import annotations
import argparse
import multiprocessing as mp
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import solve, stream

POSITIONS = (0, 1, 2, 3, 22, 23, 24, 25, 45, 46, 47, 48)
assert len(POSITIONS) == len(set(POSITIONS)) == 12

def run_branch(args):
    branch, first, later, timeout_ms = args
    # There is NO externally supplied or precomputed state witness.
    anchor = sum(((branch >> j) & 1) << p for j, p in enumerate(POSITIONS))
    status, state = solve(first, anchor, POSITIONS, timeout_ms)
    holdout = bool(state is not None and tuple(stream(*state, 6)[4:6]) == tuple(later))
    return branch, status, holdout, state if holdout else None

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seed', type=int, default=20261128)
    ap.add_argument('--first-branch', type=int, default=0)
    ap.add_argument('--branch-limit', type=int, default=4096)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--timeout-ms', type=int, default=5000)
    args = ap.parse_args()
    assert 0 <= args.first_branch < 4096
    assert 1 <= args.branch_limit <= 4096 - args.first_branch
    assert 1 <= args.workers <= 8
    assert 100 <= args.timeout_ms <= 30000

    # Private to this synthetic test: used to generate observations and
    # check success AFTER solving, never to choose or condition a branch.
    rng = random.Random(args.seed)
    true_state = (rng.getrandbits(64), rng.getrandbits(64))
    full = stream(*true_state, 6)
    first = {0: full[0], 1: full[1]}
    later = full[4:6]
    observed = (0, 1)
    heldout = (4, 5)
    t0 = time.monotonic()
    counts = {'sat': 0, 'unsat': 0, 'unknown': 0}
    completed = 0
    accepted = False

    pool = mp.Pool(args.workers)
    try:
        assignments = ((j, first, later, args.timeout_ms) for j in
                       range(args.first_branch, args.first_branch + args.branch_limit))
        for branch, status, matched, state in pool.imap_unordered(
                run_branch, assignments, chunksize=1):
            completed += 1
            counts[status] = counts.get(status, 0) + 1
            if matched:
                assert status == 'sat' and state == true_state
                assert stream(*state, 6)[2:4] == full[2:4]
                accepted = True
                print({'seed': args.seed, 'result': 'COMPLETE_SYNTHETIC_RECOVERY',
                       'external_a0_bits': 0, 'branch_index': branch,
                       'completed_queries': completed, 'statuses': counts,
                       'middle_recovered': True, 'later_heldout_matched': True,
                       'initial_state_exact': True,
                       'elapsed_seconds': round(time.monotonic() - t0, 3)},
                      flush=True)
                break
            if completed % 100 == 0:
                print({'seed': args.seed, 'queries_completed': completed,
                       'statuses': counts,
                       'elapsed_seconds': round(time.monotonic() - t0, 1)},
                      flush=True)
    finally:
        if accepted:
            pool.terminate()
        else:
            pool.close()
        pool.join()
    if not accepted:
        print({'seed': args.seed, 'result': 'NO_COMPLETE_MATCH_IN_FINISHED_QUERIES',
               'external_a0_bits': 0, 'queries_completed': completed,
               'statuses': counts,
               'coverage_complete': args.first_branch == 0 and
                                    args.branch_limit == 4096,
               'unknown_is_not_unsat': True,
               'elapsed_seconds': round(time.monotonic() - t0, 3)},
              flush=True)
    return 0 if accepted else 1

if __name__ == '__main__':
    raise SystemExit(main())
