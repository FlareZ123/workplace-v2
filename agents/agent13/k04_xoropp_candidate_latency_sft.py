#!/usr/bin/env python3
"""Synthetic-only K04 early-candidate latency control; no original H-17 sources.

This deliberately supplies each synthetic state's true P12 cube ONLY to
measure conditional first-model latency. Historical use must enumerate all
4096 cubes and must not infer UNSAT from UNKNOWN or from a first SAT model.
For source-safe historical candidate-first triage see the neighboring local
runner and Agent37's exact-state private ledger.
"""
import argparse
import hashlib
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import solve, stream

P12 = (0, 1, 2, 3, 22, 23, 24, 25, 45, 46, 47, 48)

def test(n, timeout):
    rng = random.Random(20261128)
    tally = dict(fixtures=0, sat=0, unknown=0, unsat=0,
                 committed_full_coupon=0, nonmatching_first_state=0)
    for _ in range(n):
        true = (rng.getrandbits(64), rng.getrandbits(64))
        outputs = stream(*true, 21)
        cube = sum(((true[0] >> p) & 1) << j
                   for j, p in enumerate(P12))
        anchor = sum(((cube >> j) & 1) << p
                     for j, p in enumerate(P12))
        mask = rng.randbytes(16)
        start = rng.randrange(2, 20)
        raw = b"".join(w.to_bytes(8, "big")
                       for w in outputs[start:start + 2])
        expected = bytes(x ^ y for x, y in zip(raw, mask))
        digest = hashlib.sha256(expected).digest()
        status, candidate_state = solve(
            {0: outputs[0], 1: outputs[1]}, anchor, P12, timeout)
        if status not in ("sat", "unsat", "unknown"):
            raise RuntimeError("Unexpected solver status")
        tally[status] += 1
        tally["fixtures"] += 1
        if candidate_state is not None:
            assert status == "sat"
            assert stream(*candidate_state, 2) == outputs[:2]
            predicted = stream(*candidate_state, 21)
            hits = []
            for offset in range(2, 20):
                coupon = b"".join(w.to_bytes(8, "big")
                                  for w in predicted[offset:offset + 2])
                component = bytes(x ^ y for x, y in zip(coupon, mask))
                if hashlib.sha256(component).digest() == digest:
                    hits.append((offset, component))
            assert len(hits) <= 1
            if hits:
                assert hits == [(start, expected)]
                tally["committed_full_coupon"] += 1
            else:
                tally["nonmatching_first_state"] += 1
    # A SAT model is an EARLY candidate, never a within-cube closure proof.
    # The remaining UNKNOWN and nonmatching-first-state cases are unresolved.
    print({
        "source_free": True,
        "true_P12_cube_provided_only_as_planted_control": True,
        "selected_ACK2_or_original_commitment_loaded": False,
        "first_state_timeout_ms": timeout,
        "full_coupon_word_starts": [2, 19],
        "all_nonmatching_and_unknown_cases_remain_unresolved": True,
        **tally,
    })

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", type=int, default=48)
    ap.add_argument("--timeout-ms", type=int, default=3000)
    args = ap.parse_args()
    if not 1 <= args.fixtures <= 10000 or not 100 <= args.timeout_ms <= 30000:
        ap.error("Invalid synthetic-only benchmark size")
    test(args.fixtures, args.timeout_ms)
