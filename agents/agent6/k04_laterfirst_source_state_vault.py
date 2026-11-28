#!/usr/bin/env python3
"""Private-only preservation of complete K04 later-first source-compatible states.

After a source-private exact parent ledger discovers SAT, rerun ONLY that parent
and recover every reachable complete xoroshiro128++ state. Fit exclusively the
intact later PS-0417 REQUESTED3 16-byte pair in big-endian/AB presentation.
The selected copied ACK2 field and earlier REQUESTED1 are not fitted. Before
any optional chronology diagnostic, test every full 16-byte window of the
24 prior generator output words, XOR the original route mask and compare the
unchanged full original K04 SHA256. Preserve fitting states and actual accepted
components only to chmod0600 files outside the shared repository.

This is conditional mathematical source compatibility, NOT physical producer
authentication. Original run forbidden in public CI; print only aggregate counts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from agents.agent15.k04_laterfirst_p16_p20_source_local import (
    P12, P16, P20, firstpair, exact_states
)
from agents.agent6.k04_laterfirst_bigab_177_exact_source_local import (
    P22, full_coupon_hits, prior_bytes, source
)

POSITIONS = {16: P16, 20: P20, 22: P22}

def scan_parent(parent, observed, mask, commitment, ms=350):
    if not 0 <= parent < 4096:
        raise ValueError("Invalid P12 parent")
    seen = set()
    matches = []
    totals = {
        "p16": 0, "p16_unsat": 0,
        "p20": 0, "p20_unsat": 0,
        "p22": 0, "p22_unsat": 0,
        "terminal_unknown_leaves": 0,
        "complete_states": 0,
        "complete_coupon_checks": 0,
        "original_component_hits": 0,
    }

    def descend(level, cube):
        states, status = exact_states(
            observed, cube, timeout_ms=ms, max_models=64,
            positions=POSITIONS[level])
        totals[f"p{level}"] += 1
        totals[f"p{level}_unsat"] += int(status == "unsat")
        for state in states:
            if state in seen:
                continue
            if firstpair(*state) != tuple(observed):
                raise RuntimeError("State does not replay intact REQUESTED3")
            seen.add(state)
            totals["complete_states"] += 1
            totals["complete_coupon_checks"] += 177
            new_hits = full_coupon_hits(state, mask, commitment)
            totals["original_component_hits"] += len(new_hits)
            matches.extend(new_hits)
        if status == "unknown" and level < 22:
            next_level = {16: 20, 20: 22}[level]
            for sub in range(1 << (next_level - level)):
                descend(next_level, cube | (sub << level))
        elif status == "unknown":
            totals["terminal_unknown_leaves"] += 1

    for child in range(16):
        descend(16, parent | (child << 12))
    assert totals["p16"] == 16
    assert totals["complete_coupon_checks"] == 177 * len(seen)
    return totals, seen, matches

def private_path(path):
    resolved = path.resolve()
    if REPO == resolved or REPO in resolved.parents:
        raise ValueError("Private vault/escrow must be outside the repository")
    if not resolved.parent.is_dir():
        raise ValueError("Existing private parent directory required")
    if path.exists() and path.stat().st_mode & 0o077:
        raise ValueError("Private file must have no group/other permissions")
    return resolved

def append_secret(path, line):
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as handle:
        os.fchmod(handle.fileno(), 0o600)
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())

def synthetic_control():
    rng = random.Random(20261129)
    state = (rng.getrandbits(64), rng.getrandbits(64))
    observed = firstpair(*state)
    parent = sum(((state[0] >> pos) & 1) << j
                 for j, pos in enumerate(P12))
    mask = rng.randbytes(16)
    raw = prior_bytes(state)
    offset = 73
    correct = bytes(x ^ y for x, y in
                    zip(raw[offset:offset + 16], mask))
    commitment = hashlib.sha256(correct).hexdigest()
    totals, recovered, hits = scan_parent(
        parent, observed, mask, commitment, ms=5000)
    assert state in recovered
    assert correct in hits
    assert totals["terminal_unknown_leaves"] == 0
    print(json.dumps({
        "synthetic_only": True,
        "original_source_loaded": False,
        "planted_full_state_recovered": True,
        "planted_complete_component_recovered": True,
        "terminal_parent_closed": True,
        "original_state_or_component_printed": False,
    }, sort_keys=True))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--resources-root", type=Path)
    ap.add_argument("--parent", type=int)
    ap.add_argument("--timeout-ms", type=int, default=350)
    ap.add_argument("--state-vault", type=Path)
    ap.add_argument("--hit-escrow", type=Path)
    a = ap.parse_args()
    if a.synthetic:
        return synthetic_control()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        ap.error("Historical source mode forbidden in CI")
    if (a.resources_root is None or a.parent is None or
            a.state_vault is None or a.hit_escrow is None):
        ap.error("Original local source, exact parent and private outputs required")
    if not (0 <= a.parent < 4096 and 100 <= a.timeout_ms <= 10000):
        ap.error("Invalid parent/budget")
    vault, escrow = private_path(a.state_vault), private_path(a.hit_escrow)
    if vault == escrow:
        ap.error("State vault and component escrow must differ")
    observed, mask, commitment = source(a.resources_root, "big", "ab")
    totals, states, hits = scan_parent(
        a.parent, observed, mask, commitment, a.timeout_ms)
    for state in sorted(states):
        append_secret(vault, json.dumps({
            "original_private": True,
            "parent": a.parent,
            "request_observation": "ATTEMPT3 REQUESTED",
            "serialization": "big/AB",
            "a0": f"{state[0]:016X}",
            "b0": f"{state[1]:016X}",
        }, sort_keys=True))
    for component in hits:
        append_secret(escrow, component.hex().upper())
    print(json.dumps({
        "aggregate_only": True,
        "exact_parent": a.parent,
        **totals,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
