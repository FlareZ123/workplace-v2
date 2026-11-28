#!/usr/bin/env python3
"""LOCAL ONLY: check K04 original commitment for every xoroshiro first-packet model.

Unlike a holdout-first approach, an exact K04 coupon SHA hit is checked and
counted BEFORE and INDEPENDENTLY OF whether REQUESTED3 is a same-generator
future packet. The original source does not authenticate that third-retry join.

Reads only exact named non-PDF spool/routing/acceptance files, refuses public CI,
never prints any original payload, inferred state, coupon, component, source
digest, or target digest. Only aggregate counters leave workers. No candidate
or verifier modifications. An UNKNOWN cube is NEVER classified as excluded.

For the explicit solver model and synthetic collision calibration see:
 agents/agent37/k04_xoropp_samebucket_collision_sft.py
 agents/agent37/k04_xoropp_acceptance_independent_holdout_sft.py
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
from agents.agent4.k04_xoropp_zero_witness_source_local import (
    requested_packet, unpack, pack,
)
from agents.agent4.k04_xoropp_zero_witness_synthetic import POSITIONS
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import stream
from agents.agent37.k04_xoropp_samebucket_collision_sft import query_models

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def read_named_sources(root: Path, endian: str, order: str):
    log = root / "evidence" / "print" / "spool-reconstruction.log"
    assert hashlib.sha256(log.read_bytes()).hexdigest() == SPOOL_SHA256
    first = unpack(requested_packet(log, 1), endian, order)
    later = unpack(requested_packet(log, 3), endian, order)
    route = json.loads((root / "evidence" / "recovery-routing.json").read_text())
    checks = json.loads((root / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    digest = checks["slot_sha256"]["K04"]
    assert len(mask) == 16 and re.fullmatch(r"[0-9a-f]{64}", digest)
    return first, later, mask, digest


def evaluate_cube(args):
    bucket, first, later, mask, original_digest, endian, order, timeout_ms, lag, pre_gap = args
    anchor = sum(((bucket >> j) & 1) << pos for j, pos in enumerate(POSITIONS))
    # Model-exhaustive within a cube if terminal UNSAT. UNKNOWN is unresolved.
    states, terminal = query_models(list(first), anchor, timeout_ms)
    assert terminal in ("unsat", "unknown")
    hits, replay_count, joint = 0, 0, 0
    for state in states:
        values = stream(*state, 6 + 2 * (lag + pre_gap))
        assert tuple(values[:2]) == tuple(first)
        # The selected physical ACK2 need not be the very next PRNG packet
        # after REQUESTED1. Test *whole* 16-byte coupons at source-bounded
        # alternative gap positions, not guessed partial/nibble repairs.
        for skipped in range(pre_gap + 1):
            selected_position = 2 + 2 * skipped
            missing_raw = pack(
                tuple(values[selected_position:selected_position + 2]),
                endian, order,
            )
            component = bytes(a ^ b for a, b in zip(missing_raw, mask))
            committed = hashlib.sha256(component).hexdigest() == original_digest
            # A later retry, if same-stream, must be AFTER this selected packet.
            replay = any(
                tuple(values[t:t + 2]) == tuple(later)
                for t in range(
                    selected_position + 2,
                    selected_position + 4 + 2 * lag,
                    2,
                )
            )
            # Critically original acceptance is NOT conditioned on replay.
            hits += int(committed)
            replay_count += int(replay)
            joint += int(committed and replay)
    return terminal, len(states), hits, replay_count, joint


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--resources-root", type=Path, default=ROOT / "resources")
    p.add_argument("--endian", choices=("big", "little"), default="little")
    p.add_argument("--order", choices=("ab", "ba"), default="ab")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--count", type=int, default=512)
    p.add_argument("--timeout-ms", type=int, default=5000)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--max-later-skipped-packets", type=int, default=0)
    p.add_argument("--max-before-selected-skipped-packets", type=int, default=0)
    p.add_argument("--summary-json", type=Path)
    args = p.parse_args()

    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        raise SystemExit("Original-source K04 test prohibited in public CI")
    if not (0 <= args.start < 4096 and 1 <= args.count <= 4096 - args.start):
        p.error("Partition range must be within 0..4095")
    if not (1 <= args.workers <= 4 and 100 <= args.timeout_ms <= 30000):
        p.error("workers 1..4 and timeout-ms 100..30000 required")
    if not 0 <= args.max_later_skipped_packets <= 8:
        p.error("later skipped packets 0..8 required")
    if not 0 <= args.max_before_selected_skipped_packets <= 8:
        p.error("before-selected skipped packets 0..8 required")

    first, later, route_mask, target = read_named_sources(
        args.resources_root, args.endian, args.order
    )
    start = time.monotonic()
    terminal_counts = {"unsat": 0, "unknown": 0}
    done = sat_buckets = states_tested = accepts_any = replays = both = 0

    with mp.Pool(args.workers) as pool:
        work = (
            (b, first, later, route_mask, target, args.endian, args.order,
             args.timeout_ms, args.max_later_skipped_packets,
             args.max_before_selected_skipped_packets)
            for b in range(args.start, args.start + args.count)
        )
        for terminal, nstates, h, r, j in pool.imap_unordered(
            evaluate_cube, work, chunksize=1
        ):
            done += 1
            terminal_counts[terminal] += 1
            sat_buckets += int(nstates > 0)
            states_tested += nstates
            accepts_any += h
            replays += r
            both += j
            if done % 100 == 0 or done == args.count:
                result = {
                    "hypothesis": "xoroshiro128++ firstpair to selected middle",
                    "view": args.endian + "/" + args.order,
                    "range": [args.start, args.start + args.count],
                    "branches_completed": done,
                    "total_branches": args.count,
                    "sat_buckets": sat_buckets,
                    "firstpacket_states_checked": states_tested,
                    "terminal_model_blocker_status": terminal_counts.copy(),
                    "K04_original_commitment_hits_ANY_state_and_selected_gap": accepts_any,
                    "whole_16byte_candidate_packets_tested": states_tested * (
                        args.max_before_selected_skipped_packets + 1
                    ),
                    "later_full_packet_replays": replays,
                    "JOINT_original_commitment_and_later_replay": both,
                    "max_later_skipped_packets": args.max_later_skipped_packets,
                    "max_before_selected_skipped_packets": args.max_before_selected_skipped_packets,
                    "all_branches_examined": done == args.count,
                    "all_examined_branches_decided": terminal_counts["unknown"] == 0,
                    "historical_generator_or_coupon_authenticated": False,
                    "source_bytes_in_output": False,
                    "elapsed_seconds": round(time.monotonic() - start, 3),
                }
                print("AGGREGATE_ONLY", json.dumps(result, sort_keys=True), flush=True)
                if args.summary_json:
                    args.summary_json.write_text(
                        json.dumps(result, sort_keys=True, indent=2) + "\n"
                    )


if __name__ == "__main__":
    main()
