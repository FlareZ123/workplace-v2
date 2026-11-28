#!/usr/bin/env python3
"""LOCAL ONLY: exact P16 later-first full-coupon reducer, with state replay ledger.

Fit only intact PS-0417 REQUESTED3 as two successive xoroshiro128++ words.
Partition every possible initial-a word into 4096 P12 parents x 16 P16
children, enumerate each child's complete models with exact model blocking,
and walk the states backwards over 18 complete two-word coupon windows.
Commitment is checked BEFORE and independently of REQUESTED1 replay.
An original printer producer, selected phase, or physical coupon is NOT proven.

Historical runs: CI denied; only SHA-pinned non-PDF sources; private 0700
directory and 0600 state and hit ledgers outside repository. Public output
contains aggregate counts only. UNKNOWN and unvisited never mean excluded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import stat
import time

from agents.agent1.k04_xoropp_laterfirst_backwards_local import scan_state
from agents.agent7.k04_xoropp_p16_subcube_source_local import exact_states, read_original
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import stream

ROOT = Path(__file__).resolve().parents[2]
METHOD = "laterfirst-P16-v1"
PARENT_COUNT = 4096
CHILDREN = 16


def work_one(job):
    parent, sub, first, later, mask, target, endian, order, ms, retry_ms = job
    cube = parent + (sub << 12)
    models, terminal = exact_states(later, cube, ms)
    first_terminal = terminal
    if terminal == "unknown" and retry_ms > ms:
        retry_models, terminal = exact_states(later, cube, retry_ms)
        models = list(set(models) | set(retry_models))
    # The reducer checks the entire original commitment for every full packet
    # irrespective of whether the earlier request replays.
    counts = {"windows": 0, "hits": 0, "earlier_replays": 0, "joint_hits": 0}
    hits = []
    for state in models:
        c, found = scan_state(state, first, later, mask, target, endian, order,
                              max_gap=17, max_before=8)
        counts["windows"] += c["candidate_windows"]
        counts["hits"] += c["unfiltered_commitment_hits"]
        counts["earlier_replays"] += c["earlier_whole_pair_replays"]
        counts["joint_hits"] += c["joint"]
        hits.extend(found)
    assert counts["windows"] == 18 * len(models)
    assert len(hits) == counts["hits"]
    return {
        "parent": parent, "child": sub, "terminal": terminal,
        "initial_terminal": first_terminal, "counts": counts,
        "models": [[hex(a), hex(b)] for a, b in models],
    }, hits


def private_path(folder, name):
    path = folder / name
    if path.is_symlink():
        raise RuntimeError("Refuse symlink at private path")
    if path.exists() and (stat.S_IMODE(path.stat().st_mode) & 0o077):
        raise RuntimeError("Private file is not owner-only")
    return path


def private_append(path, obj):
    fd = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "a") as dest:
        dest.write(json.dumps(obj, sort_keys=True) + "\n")
        dest.flush()
        os.fsync(dest.fileno())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--endian", choices=("big", "little"), default="little")
    p.add_argument("--order", choices=("ab", "ba"), default="ab")
    p.add_argument("--start", type=int, default=0, help="P12 parent start")
    p.add_argument("--count", type=int, default=128, help="P12 parents")
    p.add_argument("--first-ms", type=int, default=350)
    p.add_argument("--retry-ms", type=int, default=700)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--private-dir", type=Path)
    p.add_argument("--resume", action="store_true")
    a = p.parse_args()
    if a.synthetic:
        rng = random.Random(27644)
        for i in range(3):
            state = (rng.getrandbits(64), rng.getrandbits(64))
            outputs = stream(*state, 2)
            positions = (0, 1, 2, 3, 22, 23, 24, 25, 45, 46, 47, 48,
                         4, 5, 6, 7)
            cube = sum(((state[0] >> pos) & 1) << j
                       for j, pos in enumerate(positions))
            models, terminal = exact_states(outputs, cube, 5000)
            assert state in models and terminal in ("unsat", "unknown")
        print({"synthetic_only": True, "true_P16_state_recovered": 3})
        return

    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        p.error("Historical source use forbidden in CI")
    if not (0 <= a.start < PARENT_COUNT and
            1 <= a.count <= PARENT_COUNT - a.start and
            100 <= a.first_ms <= a.retry_ms <= 30000 and
            1 <= a.workers <= 4):
        p.error("Invalid exact-search partition or budget")
    if a.private_dir is None:
        p.error("Historical mode requires --private-dir")
    private = a.private_dir.resolve()
    if (not private.is_dir() or a.private_dir.is_symlink() or
            stat.S_IMODE(private.stat().st_mode) & 0o077 or
            private == ROOT or ROOT in private.parents):
        p.error("Private directory must be owner-only and outside repository")
    ledger = private_path(private, "laterfirst-P16-" + a.endian + "-" +
                          a.order + "-states.jsonl")
    escrow = private_path(private, "laterfirst-P16-verified-components.jsonl")

    # Only safe pinned spool, routing and commitment files via Agent7 reader.
    # In particular never touch the quarantined PDF.
    first, later, mask, target = read_original(a.endian, a.order)
    completed = set()
    if a.resume and ledger.exists():
        for line in ledger.read_text().splitlines():
            entry = json.loads(line)
            if (entry.get("method") == METHOD and
                entry.get("endian") == a.endian and
                entry.get("order") == a.order and
                entry.get("terminal") == "unsat"):
                completed.add((entry["parent"], entry["child"]))
    jobs = (
        (parent, child, first, later, mask, target, a.endian, a.order,
         a.first_ms, a.retry_ms)
        for parent in range(a.start, a.start + a.count)
        for child in range(CHILDREN)
        if (parent, child) not in completed
    )
    totals = {"done": 0, "previously_complete": len(completed),
              "terminal_unsat": 0, "terminal_unknown": 0,
              "models": 0, "whole_coupon_checks": 0, "acceptances": 0,
              "earlier_request_replays": 0, "joint": 0}
    started = time.monotonic()
    with mp.Pool(a.workers) as pool:
        for entry, hits in pool.imap_unordered(work_one, jobs, chunksize=1):
            private_append(ledger, {
                **entry, "method": METHOD, "endian": a.endian,
                "order": a.order, "first_ms": a.first_ms,
                "retry_ms": a.retry_ms,
            })
            for hit in hits:
                private_append(escrow, {"component": hit, "method": METHOD})
            totals["done"] += 1
            totals["terminal_" + entry["terminal"]] += 1
            totals["models"] += len(entry["models"])
            c = entry["counts"]
            totals["whole_coupon_checks"] += c["windows"]
            totals["acceptances"] += c["hits"]
            totals["earlier_request_replays"] += c["earlier_replays"]
            totals["joint"] += c["joint_hits"]
            if totals["done"] % 256 == 0:
                print("AGGREGATE_ONLY", json.dumps({
                    "model": METHOD, "view": a.endian + "/" + a.order,
                    "parents": [a.start, a.start + a.count],
                    "totals": totals,
                    "elapsed_s": round(time.monotonic() - started, 1),
                }, sort_keys=True), flush=True)
    print("AGGREGATE_ONLY_COMPLETE", json.dumps(totals,sort_keys=True))


if __name__ == "__main__":
    main()
