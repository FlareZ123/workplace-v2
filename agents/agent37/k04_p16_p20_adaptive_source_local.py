#!/usr/bin/env python3
"""Local-only original K04 source-first P16 -> conditional P20 exact refinement.

The full first packet determines the xoroshiro128++ solver input. All 4,096
P12 parents / 16 P16 children and, for open P16, all 16 P20 grandchildren
form an exhaustive disjoint partition. Never use a planted true cube on
historical data. SAT models are exhaustively blocked when possible; UNKNOWN
is unresolved. Every complete SAT candidate is checked against the original
K04 commitment before any later-packet consistency filter.

Original-source mode is forbidden in public CI. Print aggregate counters only.
The historical source is read via the already checksum-pinned Agent7 reader.
Positive commitment bytes are escrowed only outside the repository (0600).
No PDF is read.
"""
from __future__ import annotations
import argparse, ctypes, hashlib, json, os, random, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent7.k04_xoropp_p16_subcube_source_local import (
    P12, P16, exact_states, read_original,
)
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import circuit, stream, ror
from agents.agent7.k04_xoropp_byte_slip_reducer import assess_state, escrow_hits

P20 = P16 + (8, 9, 10, 11)
MASK = (1 << 64) - 1
assert len(P20) == len(set(P20)) == 20


def fixed_anchor(bits: int, positions: tuple[int, ...]) -> int:
    assert 0 <= bits < (1 << len(positions))
    return sum(((bits >> j) & 1) << p for j, p in enumerate(positions))


def solve_p20(first, cube, timeout_ms=700, max_models=32):
    """Every P20 state seen, plus a terminal UNSAT or UNKNOWN disposition."""
    anchor = fixed_anchor(cube, P20)
    script = circuit({0: first[0], 1: first[1]},
                     anchor, P20, timeout_ms)
    lib = ctypes.CDLL("libz3.so.4")
    P = ctypes.c_void_p
    lib.Z3_mk_config.restype = P
    lib.Z3_mk_context.argtypes = [P]
    lib.Z3_mk_context.restype = P
    lib.Z3_del_config.argtypes = [P]
    lib.Z3_del_context.argtypes = [P]
    lib.Z3_eval_smtlib2_string.argtypes = [P, ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
    cfg = lib.Z3_mk_config()
    ctx = lib.Z3_mk_context(cfg)
    lib.Z3_del_config(cfg)

    def ask(command):
        return (lib.Z3_eval_smtlib2_string(ctx, command.encode()) or b"").decode().strip()

    try:
        status = ask(script)
        output = []
        while status == "sat":
            model = ask("(get-value (" + " ".join(f"a0_{j}" for j in range(64)) + "))")
            bitvals = {int(j): int(v == "true") for j, v in
                       re.findall(r"\(a0_(\d+)\s+(true|false)\)", model)}
            if len(bitvals) != 64:
                raise RuntimeError("Missing Boolean model bit")
            a = sum(bitvals[j] << j for j in range(64))
            b = (ror((first[0] - a) & MASK, 17) - a) & MASK
            if stream(a, b, 2) != list(first):
                raise RuntimeError("State fails full firstpacket replay")
            if any(((a >> p) & 1) != ((cube >> j) & 1)
                   for j, p in enumerate(P20)):
                raise RuntimeError("State contradicts cube")
            output.append((a, b))
            if len(output) >= max_models:
                return output, "unknown"
            blocking = " ".join((f"(not a0_{j})" if bitvals[j] else f"a0_{j}")
                                for j in range(64))
            ask("(assert (or " + blocking + "))")
            status = ask("(check-sat)")
        if status not in ("unsat", "unknown"):
            raise RuntimeError("Unexpected solver status " + status[:80])
        return output, status
    finally:
        lib.Z3_del_context(ctx)


def adaptive_child(first, parent, child, ms, retry, cap):
    """Exhaustive conditional split. A partial P16 SAT never closes open space."""
    p16cube = parent | (child << 12)
    states, terminal = exact_states(first, p16cube, ms, cap)
    meta = {"p16_retry": 0, "p20_children": 0, "p20_unsat": 0}
    if terminal == "unknown" and retry > ms:
        extra, terminal = exact_states(first, p16cube, retry, cap)
        states = list(set(states).union(extra))
        meta["p16_retry"] += 1
    if terminal == "unknown":
        # Cover *every* descendant. Neither a P16 SAT nor a time-limited
        # UNKNOWN rules out other full states in that 16-bit parent.
        seen = set(states)
        child_results = []
        for extra4 in range(16):
            p20cube = p16cube | (extra4 << 16)
            more, decision = solve_p20(first, p20cube, retry, cap)
            seen.update(more)
            child_results.append(decision)
        states = list(seen)
        terminal = "unsat" if all(d == "unsat" for d in child_results) else "unknown"
        meta["p20_children"] = 16
        meta["p20_unsat"] = child_results.count("unsat")
    return states, terminal, meta


def synthetic():
    # Source-independent complete 16-byte commitment tests, including
    # a deliberately non-packet-aligned candidate coupon.
    results = {"fixtures": 0, "recovered": 0, "original_loaded": False}
    for seed in range(123210, 123214):
        rng = random.Random(seed)
        a, b = rng.getrandbits(64), rng.getrandbits(64)
        first = stream(a, b, 2)
        parent = sum(((a >> p) & 1) << j for j, p in enumerate(P12))
        child = sum(((a >> p) & 1) << j for j, p in enumerate(P16[12:]))
        states, status, _ = adaptive_child(first, parent, child, 350, 700, 32)
        if (a, b) in states:
            results["recovered"] += 1
        results["fixtures"] += 1
    assert results["recovered"] == results["fixtures"]
    print(json.dumps(results, sort_keys=True))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--count", type=int, default=16)
    p.add_argument("--endian", choices=("big", "little"), default="little")
    p.add_argument("--order", choices=("ab", "ba"), default="ab")
    p.add_argument("--timeout-ms", type=int, default=350)
    p.add_argument("--retry-timeout-ms", type=int, default=700)
    p.add_argument("--max-models", type=int, default=32)
    p.add_argument("--max-pre-packets", type=int, default=8)
    p.add_argument("--max-later-packets", type=int, default=8)
    p.add_argument("--local-hit-escrow", type=Path)
    a = p.parse_args()
    if a.synthetic:
        return synthetic()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        p.error("Historical source forbidden in CI")
    if not (0 <= a.start < 4096 and 0 < a.count <= 4096 - a.start
            and 100 <= a.timeout_ms <= a.retry_timeout_ms <= 30000
            and 1 <= a.max_models <= 1024
            and 0 <= a.max_pre_packets <= 16 and 0 <= a.max_later_packets <= 16):
        p.error("Invalid search domain")
    if a.local_hit_escrow is None:
        p.error("Original-source mode requires a local private hit escrow")
    escrow = a.local_hit_escrow.resolve()
    if ROOT == escrow or ROOT in escrow.parents or not escrow.parent.is_dir():
        p.error("Escrow must be outside the repository")
    if escrow.parent.stat().st_mode & 0o077:
        p.error("Escrow parent must be chmod 0700")
    first, later, mask, target = read_original(a.endian, a.order)
    started = time.monotonic()
    totals = {"parents": 0, "closed": 0, "open": 0, "p16_unsat": 0,
              "p16_unknown": 0, "states": 0, "candidate_checks": 0,
              "commit_hits": 0, "p16_retry": 0, "p20_children": 0,
              "p20_unsat": 0}
    for parent in range(a.start, a.start + a.count):
        parent_done = True
        for child in range(16):
            models, decision, meta = adaptive_child(
                first, parent, child, a.timeout_ms, a.retry_timeout_ms, a.max_models)
            totals["p16_" + decision] += 1
            for k, v in meta.items():
                totals[k] += v
            if decision == "unknown":
                parent_done = False
            totals["states"] += len(models)
            for state in models:
                c, hits = assess_state(
                    state, mask, target, a.endian, a.order,
                    a.max_pre_packets, a.max_later_packets, later)
                totals["candidate_checks"] += c["candidates"]
                totals["commit_hits"] += c["commit_hits"]
                if hits:
                    escrow_hits(escrow, hits)
        totals["parents"] += 1
        totals["closed" if parent_done else "open"] += 1
        if totals["parents"] % 8 == 0 or totals["parents"] == a.count:
            # No firstpacket words, states, source bytes, original hashes or
            # generated K04 components in public stdout.
            print(json.dumps({
                "local_only": True, "view": a.endian + "/" + a.order,
                "start": a.start, "count": a.count, "totals": totals,
                "elapsed_seconds": round(time.monotonic() - started, 2),
            }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
