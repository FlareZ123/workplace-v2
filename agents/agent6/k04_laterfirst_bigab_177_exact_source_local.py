#!/usr/bin/env python3
"""K04 exact later-first big/AB 177-byte-window source search, local only.

Fit the intact REQUESTED3 16-byte pair, not the unverified selected ACK2.
Partition all possible 128-bit xoroshiro128++ states into exact P12 parents
and P16/P20/P22 disjoint children. Every recovered state is fully blocked.
For each state, scan EVERY 16-byte window from its 24 prior 64-bit outputs,
then reduce and check the *unchanged full* K04 commitment (177 windows).
Timeout UNKNOWN never closes a state region. No original bytes, inferred
state or candidate key may be written to public GitHub or workflow logs.

Builds on Agent15's independently controlled exact one-transition circuit.
It does not assert xoroshiro128++ produced the historical coupon.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent15.k04_laterfirst_p16_p20_source_local import (
    P12, P16, P20, exact_states, firstpair, earlier_words, source, advance, invert
)

P22 = P20 + (12, 13)
P24 = P22 + (14, 15)
P28 = P24 + (16, 17, 18, 19)
LEVEL = {16: P16, 20: P20, 22: P22, 24: P24, 28: P28}


def prior_bytes(state):
    """192 bytes of consecutive outputs strictly *before* later request."""
    newest_first = earlier_words(*state, 24)
    raw = b"".join(v.to_bytes(8, "big") for v in reversed(newest_first))
    assert len(raw) == 192
    return raw


def full_coupon_hits(state, mask, commitment):
    """The entire 177-window prehistory, including non-word boundaries."""
    raw = prior_bytes(state)
    hits = []
    for offset in range(177):
        payload = raw[offset:offset + 16]
        component = bytes(a ^ b for a, b in zip(payload, mask))
        if hashlib.sha256(component).hexdigest() == commitment:
            hits.append(component)
    return hits


def investigate_parent(job):
    parent, observed, mask, target, first_ms, child_ms, depth = job
    counters = {
        "p16": 0, "p16_unsat": 0,
        "p20": 0, "p20_unsat": 0,
        "p22": 0, "p22_unsat": 0,
        "p24": 0, "p24_unsat": 0,
        "p28": 0, "p28_unsat": 0,
        "open_leaves": 0,
        "complete_models": 0,
        "full_commit_checks": 0,
        "original_hits": 0,
    }
    seen = set()
    hits = []

    def subdivide(level, cube):
        models, status = exact_states(
            observed, cube, first_ms if level == 16 else child_ms,
            max_models=64, positions=LEVEL[level],
        )
        counters[f"p{level}"] += 1
        counters[f"p{level}_unsat"] += int(status == "unsat")
        for state in models:
            if state not in seen:
                seen.add(state)
                counters["complete_models"] += 1
                counters["full_commit_checks"] += 177
                new = full_coupon_hits(state, mask, target)
                counters["original_hits"] += len(new)
                hits.extend(new)

        if status == "unknown" and level < depth:
            next_level = {16: 20, 20: 22, 22: 24, 24: 28}[level]
            for sub in range(1 << (next_level - level)):
                subdivide(next_level, cube | (sub << level))
        elif status == "unknown":
            counters["open_leaves"] += 1

    for child in range(16):
        subdivide(16, parent | (child << 12))
    return parent, counters, hits


def synthetic_controls():
    rng = random.Random(62368)
    for _ in range(10000):
        a, b = rng.getrandbits(64), rng.getrandbits(64)
        assert invert(*advance(a, b)) == (a, b)

    reached = 0
    for i in range(6):
        state = (rng.getrandbits(64), rng.getrandbits(64))
        observed = firstpair(*state)
        for positions in (P16, P20, P22, P24, P28):
            anchor = sum(((state[0] >> p) & 1) << j
                         for j, p in enumerate(positions))
            models, terminal = exact_states(
                observed, anchor, 5000, positions=positions)
            reached += int(state in models)
        mask = rng.randbytes(16)
        raw = prior_bytes(state)
        offset = rng.randrange(177)
        planted = bytes(a ^ b for a, b in
                        zip(raw[offset:offset + 16], mask))
        target = hashlib.sha256(planted).hexdigest()
        assert full_coupon_hits(state, mask, target) == [planted]

    assert reached == 30, "Planted P16/P20/P22/P24/P28 state solver must reach all"
    print(json.dumps({
        "synthetic_only": True, "original_source_loaded": False,
        "inverse_roundtrips": 10000, "state_fixtures": 6,
        "planted_state_reached": reached,
        "planted_full_coupon_hits": 6, "complete_byte_windows": 177
    }, sort_keys=True))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--resources-root", type=Path)
    ap.add_argument("--start", type=int, default=116)
    ap.add_argument("--count", type=int, default=16)
    ap.add_argument("--timeout-ms", type=int, default=350)
    ap.add_argument("--retry-timeout-ms", type=int, default=350)
    ap.add_argument("--depth", type=int, choices=(16, 20, 22, 24, 28), default=24)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--escrow", type=Path)
    args = ap.parse_args()
    if args.synthetic:
        return synthetic_controls()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        ap.error("Original-source mode is forbidden in public CI")
    if not args.resources_root or not args.escrow:
        ap.error("Requires local source root and private out-of-repository escrow")
    if not (0 <= args.start < 4096
            and 0 < args.count <= 4096 - args.start):
        ap.error("Invalid exact parent range")
    if not (100 <= args.timeout_ms <= args.retry_timeout_ms <= 10000):
        ap.error("Invalid solver budgets")
    if not (1 <= args.workers <= 4):
        ap.error("At most four workers")
    if not args.escrow.parent.exists():
        ap.error("Escrow directory must exist")
    if ROOT == args.escrow.resolve() or ROOT in args.escrow.resolve().parents:
        ap.error("Escrow must be outside repository")
    # Source() pins original non-PDF spool bytes and only loads route/acceptance.
    observed, mask, target = source(args.resources_root, "big", "ab")
    counts = {
        "parents_completed": 0, "parents_fully_closed": 0,
        "p16": 0, "p16_unsat": 0,
        "p20": 0, "p20_unsat": 0,
        "p22": 0, "p22_unsat": 0,
        "p24": 0, "p24_unsat": 0,
        "p28": 0, "p28_unsat": 0,
        "open_leaves": 0,
        "complete_models": 0, "full_commit_checks": 0,
        "original_hits": 0
    }
    started = time.monotonic()
    jobs = ((parent, observed, mask, target,
             args.timeout_ms, args.retry_timeout_ms, args.depth)
            for parent in range(args.start, args.start + args.count))
    with mp.Pool(args.workers) as pool:
        for _, result, found in pool.imap_unordered(
                investigate_parent, jobs, chunksize=1):
            counts["parents_completed"] += 1
            counts["parents_fully_closed"] += int(result["open_leaves"] == 0)
            for k, value in result.items():
                counts[k] += value
            if found:
                fd = os.open(
                    args.escrow, os.O_WRONLY | os.O_APPEND | os.O_CREAT |
                    getattr(os, "O_NOFOLLOW", 0), 0o600)
                with os.fdopen(fd, "a") as fh:
                    os.fchmod(fh.fileno(), 0o600)
                    for component in found:
                        fh.write(component.hex().upper() + "\n")
                    fh.flush()
                    os.fsync(fh.fileno())
            if (counts["parents_completed"] % 8 == 0 or
                    counts["parents_completed"] == args.count):
                print(json.dumps({
                    "aggregate_only": True,
                    "hypothesis": "later-first xoroshiro128++",
                    "serializer": "big/AB",
                    "parent_range_start": args.start,
                    "parent_count": args.count,
                    "partition_depth": args.depth,
                    "elapsed_seconds": round(time.monotonic() - started, 1),
                    **counts,
                }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
