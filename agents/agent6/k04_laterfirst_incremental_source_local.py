#!/usr/bin/env python3
"""H-17 K04 source-safe, resumable incremental later-first exact solver.

Hypothesis: unverified physical selected ACK2 was emitted before intact REQUESTED3
by xoroshiro128++ 1.0. Fit ONLY intact later REQUESTED3 as two big/AB words.
Exhaust exact P12→P16→P20→P22→P24→P28 disjoint state partitions with complete SAT model
blocking; every state gets every full 16-byte window in the previous 24 words
checked by the untouched original K04 commitment (177 windows).
This is a conditional model, NOT proof of the physical printer's producer.

Source mode is local-only; all source, state and candidate bytes are private,
any original commitment hits go to an out-of-repository chmod0600 escrow.
An optional out-of-repo 0600 per-parent ledger supports exact resumption.

PERFORMANCE CAUTION (original local control): persistent incremental Z3 context
proved fewer P16 children terminal UNSAT at 350 ms than the independent
fresh-context implementation on the same source parent, requiring more P20
splits. This is mathematically sound but can run *slower*. Prefer the
fresh-context resumable engine in k04_laterfirst_fresh_resumable_source_local.py
for broad original-source partitions; retain this variant for experimentation.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent15.k04_laterfirst_p16_p20_source_local import (
    P12, P16, P20, circuit, firstpair, ror, advance, invert, source
)
from agents.agent6.k04_laterfirst_bigab_177_exact_source_local import (
    prior_bytes, full_coupon_hits
)

P22 = P20 + (12, 13)
P24 = P22 + (14, 15)
P28 = P24 + (16, 17, 18, 19)
SOURCE_PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ENGINE = "K04-LATERFIRST-BIGAB-177-INCREMENTAL-V2"
MASK64 = (1 << 64) - 1

class IncrementalSolver:
    """One exact Boolean equation per parent; push/pop disjoint anchor bits."""
    def __init__(self, observed, timeout_ms):
        self.observed = tuple(observed)
        z = ctypes.CDLL("libz3.so.4")
        P = ctypes.c_void_p
        z.Z3_mk_config.restype = P
        z.Z3_mk_context.argtypes = [P]
        z.Z3_mk_context.restype = P
        z.Z3_del_config.argtypes = [P]
        z.Z3_del_context.argtypes = [P]
        z.Z3_eval_smtlib2_string.argtypes = [P, ctypes.c_char_p]
        z.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
        cfg = z.Z3_mk_config()
        self.ctx = z.Z3_mk_context(cfg)
        z.Z3_del_config(cfg)
        self.z = z
        script = circuit(observed, 0, bits=(), timeout_ms=timeout_ms)
        assert script.endswith("(check-sat)\n")
        reply = self.ask(script[:-len("(check-sat)\n")])
        if reply:
            raise RuntimeError("Unexpected solver initialization reply")
    def ask(self, query):
        return (self.z.Z3_eval_smtlib2_string(
            self.ctx, query.encode("utf-8")) or b"").decode().strip()
    def push(self, positions, assignment):
        self.ask("(push 1)")
        atoms = " ".join(
            f"(= a0_{pos} {'true' if (assignment >> j) & 1 else 'false'})"
            for j, pos in enumerate(positions))
        self.ask("(assert (and " + atoms + "))")
    def pop(self):
        self.ask("(pop 1)")
    def all_models(self, cap=64):
        states = []
        status = self.ask("(check-sat)")
        while status == "sat":
            raw = self.ask("(get-value (" +
                           " ".join(f"a0_{j}" for j in range(64)) + "))")
            bits = {int(i): int(value == "true") for i, value in
                    re.findall(r"\(a0_(\d+)\s+(true|false)\)", raw)}
            if len(bits) != 64:
                raise RuntimeError("Incomplete model")
            a = sum(bits[j] << j for j in range(64))
            b = (ror((self.observed[0] - a) & MASK64, 17) - a) & MASK64
            if firstpair(a, b) != self.observed:
                raise RuntimeError("SAT model did not replay the intact packet")
            states.append((a, b))
            if len(states) >= cap:
                return states, "unknown"
            change = " ".join(
                f"(not a0_{j})" if bits[j] else f"a0_{j}" for j in range(64))
            self.ask("(assert (or " + change + "))")
            status = self.ask("(check-sat)")
        if status not in ("unsat", "unknown"):
            raise RuntimeError("Unexpected status " + status)
        return states, status
    def close(self):
        self.z.Z3_del_context(self.ctx)
        self.ctx = None

def check_parent(job):
    parent, observed, mask, commitment, timeout_ms, depth = job
    z = IncrementalSolver(observed, timeout_ms)
    totals = {"p16": 0, "p16_unsat": 0,
              "p20": 0, "p20_unsat": 0,
              "p22": 0, "p22_unsat": 0,
              "p24": 0, "p24_unsat": 0,
              "p28": 0, "p28_unsat": 0,
              "unknown_leaf": 0, "states": 0,
              "complete_coupon_checks": 0, "original_hits": 0}
    hits = []
    observed_states = set()
    extra = {16: (8, 9, 10, 11), 20: (12, 13),
             22: (14, 15), 24: (16, 17, 18, 19)}
    def descend(level):
        models, terminal = z.all_models()
        totals[f"p{level}"] += 1
        totals[f"p{level}_unsat"] += int(terminal == "unsat")
        for state in models:
            if state not in observed_states:
                observed_states.add(state)
                totals["states"] += 1
                totals["complete_coupon_checks"] += 177
                matched = full_coupon_hits(state, mask, commitment)
                totals["original_hits"] += len(matched)
                hits.extend(matched)
        if terminal == "unknown" and level < depth:
            positions = extra[level]
            for sub in range(1 << len(positions)):
                z.push(positions, sub)
                descend(level + len(positions))
                z.pop()
        elif terminal == "unknown":
            totals["unknown_leaf"] += 1
    try:
        z.push(P12, parent)
        for child in range(16):
            z.push((4, 5, 6, 7), child)
            descend(16)
            z.pop()
        z.pop()
    finally:
        z.close()
    assert totals["p16"] == 16
    assert totals["complete_coupon_checks"] == totals["states"] * 177
    totals["fully_closed"] = int(totals["unknown_leaf"] == 0)
    return parent, totals, hits

def require_private(path):
    resolved = path.resolve()
    if ROOT == resolved or ROOT in resolved.parents:
        raise ValueError("Private output must be outside repository")
    if not resolved.parent.is_dir():
        raise ValueError("Private parent directory missing")
    if path.exists() and path.stat().st_mode & 0o077:
        raise ValueError("Private output is accessible by group or others")
    return resolved

def append_private(path, line):
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as handle:
        os.fchmod(handle.fileno(), 0o600)
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())

def synthetic():
    # Source-free planted complete SHA256 commitments, including inner byte slips.
    rng = random.Random(627768)
    planted = 0
    for i in range(4):
        state = (rng.getrandbits(64), rng.getrandbits(64))
        later = firstpair(*state)
        parent = sum(((state[0] >> p) & 1) << j
                     for j, p in enumerate(P12))
        mask = rng.randbytes(16)
        raw = prior_bytes(state)
        offset = rng.randrange(177)
        expected = bytes(a ^ b for a, b in
                         zip(raw[offset:offset + 16], mask))
        commitment = hashlib.sha256(expected).hexdigest()
        _, metrics, hits = check_parent(
            (parent, later, mask, commitment, 350, 22))
        assert metrics["fully_closed"] and expected in hits
        planted += 1
    for i in range(10000):
        st = (rng.getrandbits(64), rng.getrandbits(64))
        assert invert(*advance(*st)) == st
    print(json.dumps({
        "synthetic_only": True, "original_source_loaded": False,
        "complete_planted_coupon_recoveries": planted,
        "inverse_roundtrips": 10000,
        "complete_window_count": 177,
        "incremental_partition_depth": 22
    }, sort_keys=True), flush=True)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--resources-root", type=Path)
    ap.add_argument("--start", type=int, default=116)
    ap.add_argument("--count", type=int, default=16)
    ap.add_argument("--timeout-ms", type=int, default=350)
    ap.add_argument("--depth", type=int, choices=(16, 20, 22, 24, 28), default=24)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--escrow", type=Path)
    ap.add_argument("--ledger", type=Path)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    if args.synthetic:
        return synthetic()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        ap.error("Historical original source forbidden in CI")
    if not args.resources_root or not args.escrow:
        ap.error("Need original local source and out-of-repo private escrow")
    if not (0 <= args.start < 4096 and
            0 < args.count <= 4096 - args.start):
        ap.error("Invalid P12 exact interval")
    if not (100 <= args.timeout_ms <= 10000):
        ap.error("Invalid solver budget")
    if not (1 <= args.workers <= 4):
        ap.error("At most four workers")
    escrow = require_private(args.escrow)
    ledger = require_private(args.ledger) if args.ledger else None
    if args.resume and ledger is None:
        ap.error("--resume requires private ledger")
    if ledger and ledger.exists() and not args.resume:
        ap.error("Existing private ledger requires --resume")
    later, mask, commitment = source(args.resources_root, "big", "ab")
    fingerprint = (f"{ENGINE}:{SOURCE_PIN}:{args.timeout_ms}:"
                   f"{args.depth}:full177")
    done = {}
    if ledger and ledger.exists():
        for line in ledger.read_text().splitlines():
            item = json.loads(line)
            if item.get("fingerprint") != fingerprint:
                ap.error("Private ledger is for different model/source/budget")
            parent = item["parent"]
            if parent in done:
                ap.error("Duplicate parent in private ledger")
            done[parent] = item["counters"]
    requested = set(range(args.start, args.start + args.count))
    pending = sorted(requested - set(done))
    counters = {"parents": 0, "fully_closed": 0,
                "p16": 0, "p16_unsat": 0,
                "p20": 0, "p20_unsat": 0,
                "p22": 0, "p22_unsat": 0,
                "p24": 0, "p24_unsat": 0,
                "p28": 0, "p28_unsat": 0,
                "unknown_leaf": 0, "states": 0,
                "complete_coupon_checks": 0, "original_hits": 0}
    for parent in sorted(requested & set(done)):
        counters["parents"] += 1
        for name, value in done[parent].items():
            counters[name] += value
    start_time = time.monotonic()
    jobs = ((parent, later, mask, commitment,
             args.timeout_ms, args.depth) for parent in pending)
    with mp.Pool(args.workers) as pool:
        for parent, result, hits in pool.imap_unordered(
                check_parent, jobs, chunksize=1):
            if hits:
                for component in hits:
                    append_private(escrow, component.hex().upper())
            if ledger:
                append_private(ledger, json.dumps({
                    "fingerprint": fingerprint,
                    "parent": parent, "counters": result
                }, sort_keys=True))
            counters["parents"] += 1
            for key, value in result.items():
                counters[key] += value
            if counters["parents"] % 8 == 0 or counters["parents"] == len(requested):
                print(json.dumps({
                    "aggregate_only": True, "hypothesis": ENGINE,
                    "p12_start": args.start, "p12_count": args.count,
                    "resumed_parents": len(requested & set(done)),
                    "elapsed_seconds": round(time.monotonic()-start_time, 2),
                    **counters
                }, sort_keys=True), flush=True)

if __name__ == "__main__":
    main()
