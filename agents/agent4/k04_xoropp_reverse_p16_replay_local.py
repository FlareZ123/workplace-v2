#!/usr/bin/env python3
"""LOCAL ONLY: replay cached reverse K04 states through a new complete-coupon reducer.

NO SMT calls. Accepts only owner-private, source-pinned P16 model ledgers
previously generated from intact REQUESTED3. Re-evaluates every unique
cached full state against 144 complete backwards byte-slip coupon windows
using the unchanged K04 commitment, independent of REQUESTED1 replay.
UNKNOWN remains unresolved; this can discover hits but never certify a
negative beyond the producer's explicit covered/decided buckets.

Source mode is CI denied; no PDF or source-original/candidate bytes printed.
A verified complete component is escrowed in owner-only local storage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import stat

from agents.agent7.k04_xoropp_laterfirst_p16_byte_slip import (
    full_coupon_scan, prehistory,
)
from agents.agent7.k04_xoropp_p16_subcube_source_local import read_original

ROOT = Path(__file__).resolve().parents[2]
METHODS = {"laterfirst-P16-v1", "laterfirst-P16-144-byte-slip-v2"}


def private_path(path, must_exist=True):
    path = path.expanduser().absolute()
    if (path == ROOT or ROOT in path.parents or path.is_symlink() or
            not path.parent.is_dir() or
            stat.S_IMODE(path.parent.stat().st_mode) & 0o077 or
            (must_exist and not path.is_file()) or
            (path.exists() and stat.S_IMODE(path.stat().st_mode) & 0o077)):
        raise RuntimeError("Private paths require owner-only non-symlinks outside repo")
    return path


def load_states(path, endian, order):
    models = set()
    dispositions = {"unsat": 0, "unknown": 0}
    visited = set()
    for line in path.read_text().splitlines():
        row = json.loads(line)
        if row.get("method") not in METHODS:
            raise ValueError("Unexpected cached solver method")
        if (row.get("layout") not in (None, endian + "/" + order) or
                row.get("endian", endian) != endian or
                row.get("order", order) != order):
            raise ValueError("Cached packet layout mismatch")
        key = (row["parent"], row["child"])
        if not 0 <= key[0] < 4096 or not 0 <= key[1] < 16:
            raise ValueError("Invalid disjoint P16 subcube")
        status = row.get("terminal", row.get("status"))
        if status not in dispositions:
            raise ValueError("Unresolved malformed terminal disposition")
        dispositions[status] += 1
        visited.add(key)
        for pair in row.get("models", row.get("states", [])):
            a, b = [int(w, 16) for w in pair]
            if not 0 <= a < 1 << 64 or not 0 <= b < 1 << 64:
                raise ValueError("Bad cached full generator state")
            models.add((a, b))
    return models, dispositions, visited


def synthetic():
    rng = random.Random(4026)
    positives = 0
    for _ in range(2):
        state = (rng.getrandbits(64), rng.getrandbits(64))
        mask = rng.randbytes(16)
        for endian in ("big", "little"):
            for order in ("ab", "ba"):
                raw = prehistory(state, endian, order)
                for gap, slip in ((0, 0), (4, 7), (8, 15)):
                    at = len(raw) - 16 - 16 * (gap + 1) - slip
                    expected = bytes(x ^ y for x, y in zip(raw[at:at+16], mask))
                    c, found = full_coupon_scan(
                        state, mask, hashlib.sha256(expected).hexdigest(),
                        endian, order)
                    assert c["complete_coupons"] == 144
                    assert c["accepts"] == 1
                    assert found == [expected.hex().upper()]
                    positives += 1
    print({"synthetic_only": True, "complete_144_window_controls": positives})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--endian", choices=("big", "little"), default="little")
    p.add_argument("--order", choices=("ab", "ba"), default="ab")
    p.add_argument("--ledger", type=Path)
    p.add_argument("--hit-escrow", type=Path)
    a = p.parse_args()
    if a.synthetic:
        return synthetic()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        p.error("Historical source reduction forbidden in public CI")
    if a.ledger is None or a.hit_escrow is None:
        p.error("--ledger and --hit-escrow required")
    ledger = private_path(a.ledger)
    escrow = private_path(a.hit_escrow, must_exist=False)
    if ledger == escrow:
        p.error("Source state ledger and hit escrow must differ")
    first, later, mask, target = read_original(a.endian, a.order)
    models, dispositions, visited = load_states(ledger, a.endian, a.order)
    totals = {"unique_children_visited": len(visited),
              "historical_states_replayed": 0,
              "full_coupon_sha_checks": 0,
              "original_K04_acceptances": 0,
              "later_firstpacket_only": True,
              "source_material_emitted": False,
              "terminal_status_rows": dispositions}
    for state in models:
        c, hits = full_coupon_scan(state, mask, target,
                                   a.endian, a.order, first)
        totals["historical_states_replayed"] += 1
        totals["full_coupon_sha_checks"] += c["complete_coupons"]
        totals["original_K04_acceptances"] += c["accepts"]
        if hits:
            fd = os.open(escrow, os.O_CREAT | os.O_WRONLY | os.O_APPEND |
                         getattr(os, "O_NOFOLLOW", 0), 0o600)
            with os.fdopen(fd, "a") as out:
                for component in hits:
                    out.write(component + "\n")
                out.flush()
                os.fsync(out.fileno())
    print("AGGREGATE_ONLY", json.dumps(totals, sort_keys=True))


if __name__ == "__main__":
    main()
