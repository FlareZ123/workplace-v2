#!/usr/bin/env python3
"""Resumable fast fresh-context exact H-17 K04 later-first source search.

Uses the proven fast first-packet per-subcube solver, rather than Z3's slower
push/pop incremental tactic under bounded time. Fits ONLY intact later PS-0417
REQUESTED3, never the unverified selected physical ACK2. Exact disjoint
P12→P16→P20→P22→P24→P28 partition; full model blocking to UNSAT or explicit
UNKNOWN. Every compatible state gets 177 complete 16-byte backward byte-window
checks against the unchanged K04 commitment before any chronology diagnostic.

Original-source execution: local only, never CI; any accepted component and
per-parent resumable completion ledger remain chmod0600 outside GitHub.
"""
from __future__ import annotations
import argparse
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent6.k04_laterfirst_bigab_177_exact_source_local import (
    investigate_parent, synthetic_controls, source
)

VERSION = "K04-LATERFIRST-BIGAB-177-FRESH-RESUME-V1"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
METRICS = (
    "p16", "p16_unsat", "p20", "p20_unsat",
    "p22", "p22_unsat", "p24", "p24_unsat",
    "p28", "p28_unsat", "open_leaves",
    "complete_models", "full_commit_checks", "original_hits"
)

def private_path(value):
    path = value.resolve()
    if ROOT == path or ROOT in path.parents:
        raise ValueError("Private output must be outside the repository")
    if not path.parent.is_dir():
        raise ValueError("Private directory does not exist")
    if path.exists() and path.stat().st_mode & 0o077:
        raise ValueError("Private output must be chmod0600")
    return path

def append_secure(path, line):
    fd = os.open(
        path, os.O_WRONLY | os.O_APPEND | os.O_CREAT |
        getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as handle:
        os.fchmod(handle.fileno(), 0o600)
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())

def read_ledger(path, fingerprint):
    records = {}
    if not path.exists():
        return records
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if not line:
            raise ValueError(f"Empty private ledger entry at {line_no}")
        obj = json.loads(line)
        if obj.get("fingerprint") != fingerprint:
            raise ValueError("Private ledger differs in source, solver or depth")
        parent = obj["parent"]
        if not isinstance(parent, int) or not 0 <= parent < 4096:
            raise ValueError("Invalid exact parent in ledger")
        if parent in records:
            raise ValueError("Duplicate exact parent in ledger")
        metrics = obj["counters"]
        if set(metrics) != set(METRICS) or metrics["p16"] != 16:
            raise ValueError("Incomplete private ledger record")
        records[parent] = metrics
    return records

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--resources-root", type=Path)
    ap.add_argument("--start", type=int, default=2048)
    ap.add_argument("--count", type=int, default=128)
    ap.add_argument("--timeout-ms", type=int, default=350)
    ap.add_argument("--retry-timeout-ms", type=int, default=350)
    ap.add_argument("--depth", type=int, choices=(16, 20, 22, 24, 28),
                    default=24)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--escrow", type=Path)
    ap.add_argument("--ledger", type=Path)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    if args.synthetic:
        return synthetic_controls()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        ap.error("Original-source mode strictly forbidden in CI")
    if not args.resources_root or not args.escrow or not args.ledger:
        ap.error("Original source, private escrow and private ledger required")
    if not (0 <= args.start < 4096 and
            0 < args.count <= 4096 - args.start):
        ap.error("Invalid disjoint P12 interval")
    if not (100 <= args.timeout_ms <= args.retry_timeout_ms <= 10000):
        ap.error("Invalid exact SAT budgets")
    if not (1 <= args.workers <= 4):
        ap.error("At most four workers")

    escrow, ledger = private_path(args.escrow), private_path(args.ledger)
    if escrow == ledger:
        ap.error("Component escrow and resume ledger must be distinct files")
    if ledger.exists() and not args.resume:
        ap.error("Existing ledger requires --resume")
    # Source is SHA-pinned original non-PDF spool and unchanged route/acceptance.
    later, mask, commitment = source(args.resources_root, "big", "ab")
    fingerprint = (f"{VERSION}:{SOURCE_SHA}:"
                   f"{args.timeout_ms}:{args.retry_timeout_ms}:{args.depth}")
    prior = read_ledger(ledger, fingerprint) if args.resume else {}
    requested = set(range(args.start, args.start + args.count))
    pending = sorted(requested - set(prior))
    counters = {"parents_completed": 0, "parents_fully_closed": 0}
    counters.update({name: 0 for name in METRICS})
    for parent in sorted(requested & set(prior)):
        counters["parents_completed"] += 1
        counters["parents_fully_closed"] += int(prior[parent]["open_leaves"] == 0)
        for name in METRICS:
            counters[name] += prior[parent][name]

    start = time.monotonic()
    jobs = ((p, later, mask, commitment, args.timeout_ms,
             args.retry_timeout_ms, args.depth) for p in pending)
    with mp.Pool(args.workers) as pool:
        for parent, report, hits in pool.imap_unordered(
                investigate_parent, jobs, chunksize=1):
            if report["p16"] != 16:
                raise RuntimeError("Incomplete P12 parent partition")
            if report["full_commit_checks"] != 177 * report["complete_models"]:
                raise RuntimeError("Incomplete coupon acceptance reducer")
            # Complete original matches must be privately escrowed first.
            for component in hits:
                append_secure(escrow, component.hex().upper())
            # Fsync each exact parent as a resumable *private* completion event.
            append_secure(ledger, json.dumps({
                "fingerprint": fingerprint,
                "parent": parent,
                "counters": report
            }, sort_keys=True))
            counters["parents_completed"] += 1
            counters["parents_fully_closed"] += int(report["open_leaves"] == 0)
            for name in METRICS:
                counters[name] += report[name]
            if (counters["parents_completed"] % 8 == 0 or
                    counters["parents_completed"] == len(requested)):
                print(json.dumps({
                    "aggregate_only": True, "hypothesis": VERSION,
                    "p12_start": args.start, "p12_count": args.count,
                    "resumed_count": len(requested & set(prior)),
                    "elapsed_seconds": round(time.monotonic() - start, 1),
                    **counters
                }, sort_keys=True), flush=True)
    if not pending:
        print(json.dumps({
            "aggregate_only": True, "resumed_only": True,
            "p12_start": args.start, "p12_count": args.count,
            **counters
        }, sort_keys=True), flush=True)

if __name__ == "__main__":
    main()
