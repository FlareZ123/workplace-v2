#!/usr/bin/env python3
"""LOCAL ONLY: exact P20 UNKNOWN -> P22/P24/P26 disjoint source-state rescue.

Read previous *private* later-first reverse little/AB P20 bucket receipts and
split only their still-UNKNOWN full state subdomains. The next binary state
bits are (12,13), (14,15), (16,17); each unresolved grandchild splits into
all FOUR disjoint smaller cubes, with exact SAT-model blocking. Recovered
full states are checked through the unchanged original whole-coupon SHA256
over ALL 177 legal earlier complete 16-byte byte-slip starts before optional
REQUESTED1 replay. Any descendant UNKNOWN remains open.

Historical source mode is CI denied, reads only pinned non-PDF originals via
Agent7 and writes only to existing owner-private mode0700 directory, files
mode0600. Public console outputs aggregate counts but never original source,
generator state, candidate or K04 commitment. Synthetic mode reads no source.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import stat
import time

from agents.agent15.k04_laterfirst_p16_p20_source_local import (
    P20, exact_states,
)
from agents.agent7.k04_xoropp_p16_subcube_source_local import read_original
from agents.agent4.k04_xoropp_reverse_p16_source_local import (
    full_coupon_scan_177,
)
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import stream

ROOT = Path(__file__).resolve().parents[2]
LAYERS = ((12,13), (14,15), (16,17))
METHOD = "laterfirst-P20-deep-P22-P24-P26-v1"
ALLOW_P20 = {"laterfirst-P20-rescue-144-byte-slip-v1",
             "laterfirst-P20-rescue-177-byte-slip-v2",
             "laterfirst-P20-144-byte-slip-v1"}
P22 = P20 + LAYERS[0]


def owner_private(path, must_exist=False):
    path = path.expanduser().absolute()
    if path == ROOT or ROOT in path.parents or path.is_symlink():
        raise RuntimeError("Never store source-bearing data in repo")
    if not path.parent.is_dir() or path.parent.is_symlink() or (
            stat.S_IMODE(path.parent.stat().st_mode) & 0o077):
        raise RuntimeError("Private parent must be owner-only")
    if must_exist and not path.is_file():
        raise RuntimeError("Required input private receipt missing")
    if path.exists() and stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise RuntimeError("Private data must be mode0600")
    return path


def private_write(path, entry):
    fd = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "a") as target:
        target.write(json.dumps(entry, sort_keys=True) + "\n")
        target.flush()
        os.fsync(target.fileno())


def pending_grandchildren(path, view):
    latest = {}
    for line in path.read_text().splitlines():
        entry = json.loads(line)
        if (entry.get("method") not in ALLOW_P20 or
                entry.get("view", entry.get("layout")) != view):
            raise ValueError("Foreign P20 source layout or method")
        parent, child = entry["parent"], entry["child"]
        if not (0 <= parent < 4096 and 0 <= child < 16):
            raise ValueError("Invalid P16 parent/child")
        subrows = entry.get("P20_subcubes", entry.get("grandchildren", []))
        if len(subrows) != 16:
            raise ValueError("Incomplete P20 partition; cannot infer coverage")
        for subrow in subrows:
            if isinstance(subrow, dict):
                sub, terminal = subrow["sub"], subrow["status"]
            else:
                sub, terminal = subrow
            if not (0 <= sub < 16 and terminal in ("unsat","unknown")):
                raise ValueError("Invalid P20 terminal disposition")
            latest[(parent, child, sub)] = terminal
    return sorted(k for k,v in latest.items() if v == "unknown")


def all_children(later, cube, positions, depth, first_ms, retry_ms, data, models):
    assert 0 <= depth < len(LAYERS)
    added = LAYERS[depth]
    new_positions = positions + added
    finals = []
    for branch in range(4):
        child_cube = cube | (branch << len(positions))
        children, terminal = exact_states(
            later, child_cube, first_ms, positions=new_positions)
        if terminal == "unknown" and retry_ms > first_ms:
            again, terminal = exact_states(
                later, child_cube, retry_ms, positions=new_positions)
            children = list(set(children) | set(again))
        models.update(children)
        label = "P" + str(len(new_positions))
        data[label + "_tested"] = data.get(label + "_tested", 0) + 1
        if terminal == "unknown" and depth + 1 < len(LAYERS):
            data[label + "_refined_unknown"] = (
                data.get(label + "_refined_unknown", 0) + 1)
            finals += all_children(later, child_cube, new_positions,
                                   depth + 1, first_ms, retry_ms,
                                   data, models)
        else:
            data[label + "_" + terminal] = (
                data.get(label + "_" + terminal, 0) + 1)
            finals.append(terminal)
    return finals


def synthetic():
    rng = random.Random(20261128)
    cases = 0
    for _ in range(8):
        state = (rng.getrandbits(64), rng.getrandbits(64))
        later = stream(*state, 2)
        cube = sum(((state[0] >> pos) & 1) << j
                   for j,pos in enumerate(P22))
        models, status = exact_states(later, cube, 3000, positions=P22)
        assert state in models and status == "unsat"
        cases += 1
    print({"synthetic_only": True, "P22_true_full_state_recovered": cases})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--endian", choices=("big","little"), default="little")
    p.add_argument("--order", choices=("ab","ba"), default="ab")
    p.add_argument("--P20-ledger", type=Path)
    p.add_argument("--deep-ledger", type=Path)
    p.add_argument("--hit-escrow", type=Path)
    p.add_argument("--first-ms", type=int, default=350)
    p.add_argument("--retry-ms", type=int, default=1000)
    p.add_argument("--start-parent", type=int, default=0)
    p.add_argument("--parent-count", type=int, default=4096)
    a = p.parse_args()
    if a.synthetic:
        return synthetic()
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        p.error("Historical source processing prohibited in CI")
    if not (0 <= a.start_parent < 4096 and
            1 <= a.parent_count <= 4096 - a.start_parent and
            100 <= a.first_ms <= a.retry_ms <= 30000):
        p.error("Invalid exact historical range/budget")
    if any(x is None for x in (a.P20_ledger,a.deep_ledger,a.hit_escrow)):
        p.error("Three separate private paths required")
    inp = owner_private(a.P20_ledger, must_exist=True)
    out = owner_private(a.deep_ledger)
    escrow = owner_private(a.hit_escrow)
    if len({inp,out,escrow}) != 3:
        p.error("Private source ledger paths must be distinct")
    view = a.endian + "/" + a.order
    selected = pending_grandchildren(inp, view)
    selected = [k for k in selected
                if a.start_parent <= k[0] < a.start_parent+a.parent_count]
    finished = set()
    if out.exists():
        for line in out.read_text().splitlines():
            e = json.loads(line)
            if e.get("method") != METHOD or e.get("view") != view:
                raise ValueError("Private deep-ledger version mismatch")
            if e["terminal"] == "unsat":
                finished.add((e["parent"],e["child"],e["P20_sub"]))
    remaining = [k for k in selected if k not in finished]
    first, later, mask, target = read_original(a.endian,a.order)
    totals = {"selected_P20_unknown": len(selected),
              "already_deep_closed": len(finished & set(selected)),
              "processed": 0, "new_closed": 0, "new_unknown": 0,
              "compatible_source_states": 0, "full_coupon_checks": 0,
              "original_commitment_hits": 0}
    start = time.monotonic()
    for parent, child, sub in remaining:
        cube = parent | (child << 12) | (sub << 16)
        models = set()
        counts = {}
        terminal = all_children(later, cube, P20, 0,
                                a.first_ms, a.retry_ms, counts, models)
        matches = []
        full_checks = 0
        for state in models:
            c,found = full_coupon_scan_177(
                state, mask, target, a.endian, a.order, first)
            full_checks += c["complete_coupons"]
            matches.extend(found)
        assert full_checks == 177 * len(models)
        record = {"method": METHOD, "view": view, "parent": parent,
                  "child": child, "P20_sub": sub,
                  "terminal": "unsat" if all(x == "unsat" for x in terminal)
                              else "unknown",
                  "counts": counts,
                  "states": [[hex(x),hex(y)] for x,y in models],
                  "full_coupon_checks": full_checks, "hits":len(matches)}
        for match in matches:
            private_write(escrow, {"component": match, "method": METHOD})
        private_write(out, record)
        totals["processed"] += 1
        totals["new_closed"] += int(record["terminal"] == "unsat")
        totals["new_unknown"] += int(record["terminal"] == "unknown")
        totals["compatible_source_states"] += len(models)
        totals["full_coupon_checks"] += full_checks
        totals["original_commitment_hits"] += len(matches)
        print("AGGREGATE_ONLY",json.dumps({
            "view":view,"totals":totals,
            "elapsed_seconds":round(time.monotonic()-start,2)},
            sort_keys=True),flush=True)


if __name__ == "__main__":
    main()
