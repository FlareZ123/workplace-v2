#!/usr/bin/env python3
"""LOCAL ONLY: decouple costly firstpacket SMT enumeration from cheap K04 reduction.

Usage (outside CI, with an existing chmod0700 directory OUTSIDE the repo):
 python agents/agent37/k04_xoropp_cached_source_local.py --phase enumerate \
   --private-dir /secure/ledger --endian little --order ab --start 0 --count 4096
 python agents/agent37/k04_xoropp_cached_source_local.py --phase reduce \
   --private-dir /secure/ledger --escrow /secure/private-hits.jsonl \
   --endian little --order ab --start 0 --count 4096

The original ACK2 bytes are NEVER a fit input. The original request1 alone
drives the exact xoroshiro128++ first-packet solver; all SAT states and cube
statuses go only to a local 0700/0600 append-only ledger, never GitHub/CI.
Terminal UNKNOWN and unvisited cubes both remain pending on resume.
Later REQUESTED3 is never a prerequisite for the actual K04 SHA commitment.
Use this for NEW scans; don't interrupt healthy older source scans to refactor.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent37.k04_private_state_ledger_sft import (
    P12, namespace, read_cube, write_attempt, reduce_cached, _secure_dir,
)
from agents.agent37.k04_xoropp_samebucket_collision_sft import query_models
from agents.agent4.k04_xoropp_zero_witness_source_local import requested_packet, unpack

PINS = {
    "evidence/print/spool-reconstruction.log":
        "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/recovery-routing.json":
        "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json":
        "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
MASK = (1 << 64) - 1


def read_inputs(root: Path, endian: str, order: str):
    for relative, expected in PINS.items():
        path = root / relative
        if path.suffix.lower() == ".pdf":
            raise RuntimeError("PDF access forbidden")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Original source hash mismatch")
    spool = root / "evidence/print/spool-reconstruction.log"
    rawfirst = requested_packet(spool, 1)
    first = unpack(rawfirst, endian, order)
    route = json.loads((root / "evidence/recovery-routing.json").read_text())
    checks = json.loads((root / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    original_target = checks["slot_sha256"]["K04"]
    if len(mask) != 16 or not re.fullmatch(r"[0-9a-f]{64}", original_target):
        raise ValueError("Malformed original K04 masked-component commitment")
    circuit = ROOT / "agents/agent27/k04_xoropp_sparse12_gap_synthetic.py"
    meta = {
        "source_sha256": PINS["evidence/print/spool-reconstruction.log"],
        "firstpair_sha256": hashlib.sha256(rawfirst).hexdigest(),
        "serializer": endian + "/" + order,
        "circuit_sha256": hashlib.sha256(circuit.read_bytes()).hexdigest(),
        "generator": "xoroshiro128++ 1.0",
        "P12": P12,
    }
    namespace(meta)  # fail closed if any source/serialization convention changes
    return first, mask, original_target, meta


def solve_cube(job):
    cube, first, timeout_ms = job
    anchor = sum(((cube >> j) & 1) << p for j, p in enumerate(P12))
    states, terminal = query_models(list(first), anchor, timeout_ms)
    if terminal not in ("unsat", "unknown"):
        raise RuntimeError("Unexpected terminal SAT disposition")
    return cube, states, terminal


def escrow_hits(path: Path, hits: list[bytes]):
    if not hits: return
    path = Path(path)
    parent = _secure_dir(path.parent)
    if path.exists() and (path.is_symlink() or path.stat().st_mode & 0o077):
        raise PermissionError("Hit escrow is not a private 0600 regular file")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "a", encoding="ascii") as f:
            for h in hits:
                if len(h) != 16: raise ValueError("Invalid committed component")
                f.write(json.dumps({"verified_K04_component": h.hex().upper()}) + "\n")
            f.flush()
            os.fsync(f.fileno())
    except:
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--phase", choices=("enumerate", "reduce"), required=True)
    p.add_argument("--resources-root", type=Path, default=ROOT / "resources")
    p.add_argument("--private-dir", type=Path, required=True)
    p.add_argument("--escrow", type=Path, help="Required for reduction, outside repo")
    p.add_argument("--endian", choices=("little", "big"), required=True)
    p.add_argument("--order", choices=("ab", "ba"), required=True)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--count", type=int, default=4096)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--timeout-ms", type=int, default=5000)
    p.add_argument("--unknown-only", action="store_true",
                   help="Optional retry subset; default resumes BOTH unvisited + open")
    a = p.parse_args()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        p.error("Historical K04 source processing is forbidden in public CI")
    if not (0 <= a.start < 4096 and 1 <= a.count <= 4096 - a.start):
        p.error("Invalid 4096-cube range")
    if not (1 <= a.workers <= 4 and 100 <= a.timeout_ms <= 30000):
        p.error("Invalid worker/solver budget")
    root = _secure_dir(a.private_dir)
    if a.escrow and (a.escrow.resolve() == ROOT or
                     ROOT in a.escrow.resolve().parents or
                     not a.escrow.parent.is_dir()):
        p.error("Hit escrow must be local, outside the repository")
    first, mask, target, meta = read_inputs(a.resources_root, a.endian, a.order)
    cubes = range(a.start, a.start + a.count)
    started = time.monotonic()

    if a.phase == "enumerate":
        pending = []
        for cube in cubes:
            disposition = read_cube(root, meta, cube)["status"]
            if disposition == "sealed": continue
            if a.unknown_only and disposition != "open": continue
            pending.append(cube)
        # Expensive SAT is executed only for genuinely unsealed source cubes.
        completed = statuses = 0
        with mp.Pool(a.workers) as pool:
            jobs = ((cube, first, a.timeout_ms) for cube in pending)
            for cube, states, terminal in pool.imap_unordered(
                    solve_cube, jobs, chunksize=1):
                write_attempt(root, meta, cube, states, terminal, a.timeout_ms)
                completed += 1
                statuses += int(terminal == "unsat")
                if completed % 100 == 0:
                    print("AGGREGATE_ONLY", {
                        "newly_durable_cubes": completed,
                        "newly_closed": statuses,
                        "remaining_pending_from_this_run": len(pending) - completed,
                    }, flush=True)
        print("AGGREGATE_ONLY", {
            "phase": "enumerate", "requested_cubes": len(cubes),
            "pending_revisited": len(pending), "durably_recorded": completed,
            "terminal_unsat_new": statuses,
            "unknown_or_unvisited_remaining":
                sum(read_cube(root, meta, c)["status"] != "sealed" for c in cubes),
            "duration_seconds": round(time.monotonic() - started, 3),
            "source_values_in_public_output": False,
        }, flush=True)
        return

    if a.escrow is None:
        p.error("Reducing original K04 candidates requires a private --escrow")
    total_states = total_windows = hits = sealed = open_count = unvisited = 0
    for cube in cubes:
        d = read_cube(root, meta, cube)
        sealed += int(d["status"] == "sealed")
        open_count += int(d["status"] == "open")
        unvisited += int(d["status"] == "unvisited")
        total_states += len(d["states"])
        total_windows += len(d["states"]) * 18
        # Every complete two-word coupon, at all 18 half-word starts.
        verified = reduce_cached(d["states"], mask, target, meta["serializer"],
                                 list(range(2, 20))) if d["states"] else []
        escrow_hits(a.escrow, verified)
        hits += len(verified)
    print("AGGREGATE_ONLY", {
        "phase": "reduce", "start": a.start, "end": a.start+a.count,
        "terminal_unsat_cubes": sealed, "open_unknown_cubes": open_count,
        "never_visited_cubes": unvisited, "cached_128bit_states": total_states,
        "original_K04_complete_16byte_candidates_checked": total_windows,
        "original_K04_commitment_hits": hits,
        "selected_coupon_word_starts": [2, 19],
        "original_accepted_bytes_escrowed_private_only": hits,
        "source_values_in_public_output": False,
        "duration_seconds": round(time.monotonic() - started, 3),
    }, flush=True)


if __name__ == "__main__":
    main()
