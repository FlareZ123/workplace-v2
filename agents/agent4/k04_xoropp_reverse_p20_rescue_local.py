#!/usr/bin/env python3
"""LOCAL ONLY: adaptive exact P20 rescue of previously UNKNOWN reverse P16 buckets.

Read private, resumable original REQUESTED3 P16 state ledger; select only its
UNRESOLVED P16 children. Split each into all 16 exact P20 grandchildren,
fixing four more a0 bits (8..11), with complete SAT-state blocking and
terminal UNSAT/UNKNOWN. For any recovered state, independently reduce all
177 backwards complete 16-byte byte-slip coupons through the unchanged K04
commitment. Original REQUESTED1 is optional replay, never an acceptance veto.

No tampered ACK2 input, public CI, PDF, source/candidate display or remote
hardware. Private original-source state/verified-hit ledgers are mode 0600.
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

from agents.agent15.k04_laterfirst_p16_p20_source_local import (
    exact_states, P20,
)
from agents.agent7.k04_xoropp_p16_subcube_source_local import read_original
from agents.agent4.k04_xoropp_reverse_p16_source_local import full_coupon_scan_177
from agents.agent7.k04_xoropp_laterfirst_p16_byte_slip import prehistory
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import stream

ROOT = Path(__file__).resolve().parents[2]
METHODS = {"laterfirst-P16-v1", "laterfirst-P16-144-byte-slip-v2", "laterfirst-P16-177-byte-slip-v3"}
OUTMETHOD = "laterfirst-P20-rescue-177-byte-slip-v2"


def owner_only(path, must_exist=False):
    path = path.expanduser().absolute()
    if (path == ROOT or ROOT in path.parents or path.is_symlink() or
            not path.parent.is_dir() or
            stat.S_IMODE(path.parent.stat().st_mode) & 0o077 or
            (must_exist and not path.is_file()) or
            (path.exists() and stat.S_IMODE(path.stat().st_mode) & 0o077)):
        raise RuntimeError("Private paths must be owner-only and outside repo")
    return path


def append_record(path, obj):
    fd = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "a") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_pending(ledger, view, start, stop):
    latest = {}
    for line in ledger.read_text().splitlines():
        row = json.loads(line)
        if row.get("method") not in METHODS:
            raise ValueError("Unrecognized P16 source ledger")
        if (row.get("layout", view) != view or
                row.get("endian", view.split("/")[0]) != view.split("/")[0] or
                row.get("order", view.split("/")[1]) != view.split("/")[1]):
            raise ValueError("Source ledger serializer changed")
        p, c = row["parent"], row["child"]
        if not (0 <= p < 4096 and 0 <= c < 16):
            raise ValueError("Bad P16 child")
        terminal = row.get("terminal", row.get("status"))
        if terminal not in ("unsat", "unknown"):
            raise ValueError("Malformed P16 terminal status")
        latest[(p, c)] = terminal
    return sorted((p, c) for (p, c), status in latest.items()
                  if status == "unknown" and start <= p < stop)


def work_one(job):
    parent, child, first, later, mask, target, endian, order, ms, retry_ms = job
    states = set()
    stats = {"unsat": 0, "unknown": 0, "models": 0,
             "complete_coupon_checks": 0, "commitment_hits": 0,
             "earlier_replays": 0, "joint": 0}
    grandchildren = []
    accepted = []
    for sub in range(16):
        cube = parent | (child << 12) | (sub << 16)
        recovered, terminal = exact_states(
            later, cube, ms, positions=P20)
        if terminal == "unknown" and retry_ms > ms:
            extra, terminal = exact_states(
                later, cube, retry_ms, positions=P20)
            recovered = list(set(recovered) | set(extra))
        stats[terminal] += 1
        states.update(recovered)
        grandchildren.append((sub, terminal))
    for state in states:
        c, matches = full_coupon_scan_177(state, mask, target, endian, order, first)
        stats["models"] += 1
        stats["complete_coupon_checks"] += c["complete_coupons"]
        stats["commitment_hits"] += c["accepts"]
        stats["earlier_replays"] += c["earlier_replays"]
        stats["joint"] += c["joint"]
        accepted.extend(matches)
    assert stats["complete_coupon_checks"] == 177 * len(states)
    assert stats["commitment_hits"] == len(accepted)
    return {
        "parent": parent, "child": child,
        "terminal": "unsat" if stats["unknown"] == 0 else "unknown",
        "counts": stats, "grandchildren": grandchildren,
        "models": [[hex(a), hex(b)] for a, b in states],
    }, accepted


def synthetic():
    rng = random.Random(20261203)
    tested = 0
    for _ in range(4):
        s = (rng.getrandbits(64), rng.getrandbits(64))
        y = stream(*s, 2)
        cube = sum(((s[0] >> p) & 1) << j for j, p in enumerate(P20))
        states, terminal = exact_states(y, cube, 350, positions=P20)
        assert terminal == "unsat" and s in states
        tested += 1
    print({"synthetic_only": True, "P20_true_state_and_exhaustion": tested})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--endian", choices=("big", "little"), default="little")
    p.add_argument("--order", choices=("ab", "ba"), default="ab")
    p.add_argument("--start-parent", type=int, default=0)
    p.add_argument("--parent-count", type=int, default=128)
    p.add_argument("--timeout-ms", type=int, default=350)
    p.add_argument("--retry-ms", type=int, default=700)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--P16-ledger", type=Path)
    p.add_argument("--P20-ledger", type=Path)
    p.add_argument("--hit-escrow", type=Path)
    a = p.parse_args()
    if a.synthetic:
        return synthetic()
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        p.error("Historical processing prohibited in public CI")
    if not (0 <= a.start_parent < 4096 and
            1 <= a.parent_count <= 4096 - a.start_parent and
            100 <= a.timeout_ms <= a.retry_ms <= 30000 and
            1 <= a.workers <= 4):
        p.error("Invalid bounded subcube range or worker budget")
    if not a.P16_ledger or not a.P20_ledger or not a.hit_escrow:
        p.error("Three strictly private ledger/escrow paths required")
    ledger = owner_only(a.P16_ledger, True)
    output = owner_only(a.P20_ledger)
    escrow = owner_only(a.hit_escrow)
    if len({ledger, output, escrow}) != 3:
        p.error("Private paths must differ")
    view = a.endian + "/" + a.order
    pending = load_pending(ledger, view, a.start_parent,
                           a.start_parent + a.parent_count)
    done = set()
    if output.exists():
        for line in output.read_text().splitlines():
            entry = json.loads(line)
            if entry.get("method") != OUTMETHOD or entry.get("view") != view:
                raise ValueError("P20 cache fingerprint mismatch")
            if entry["terminal"] == "unsat":
                done.add((entry["parent"], entry["child"]))
    tasks = [pair for pair in pending if pair not in done]
    first, later, mask, target = read_original(a.endian, a.order)
    total = {"P16_unknown_targets": len(pending),
             "P16_previously_resolved": len(done & set(pending)),
             "processed": 0, "P20_terminal_unsat": 0,
             "P20_terminal_unknown": 0, "full_states": 0,
             "complete_coupon_checks": 0, "original_commitment_hits": 0}
    began = time.monotonic()
    jobs = ((parent, child, first, later, mask, target,
             a.endian, a.order, a.timeout_ms, a.retry_ms)
            for parent, child in tasks)
    with mp.Pool(a.workers) as pool:
        for entry, hits in pool.imap_unordered(work_one, jobs, chunksize=1):
            append_record(output, {**entry, "method": OUTMETHOD, "view": view})
            for match in hits:
                append_record(escrow, {"component": match, "method": OUTMETHOD})
            total["processed"] += 1
            total["P20_terminal_unsat"] += entry["counts"]["unsat"]
            total["P20_terminal_unknown"] += entry["counts"]["unknown"]
            total["full_states"] += entry["counts"]["models"]
            total["complete_coupon_checks"] += entry["counts"]["complete_coupon_checks"]
            total["original_commitment_hits"] += entry["counts"]["commitment_hits"]
            if total["processed"] % 16 == 0 or total["processed"] == len(tasks):
                print("AGGREGATE_ONLY", json.dumps({
                    "hypothesis": OUTMETHOD, "view": view,
                    "elapsed_s": round(time.monotonic() - began, 1),
                    "totals": total}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
