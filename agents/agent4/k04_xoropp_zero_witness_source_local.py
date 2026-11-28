#!/usr/bin/env python3
"""LOCAL-ONLY original-source application of the zero-external-state-bit xoroshiro128++ erasure solver.

The conditional model treats PS-261003-0417 REQUESTED attempts 1 and 3 as
two-output packets separated by the selected erased pair and up to eight\nadditional unobserved pairs before REQUESTED3. The selected middle is always\noutputs 2 and 3; only the later independent holdout phase can vary.
The physical coupon and the generator identity are NOT authenticated.

This tool reads only three named non-PDF text files, never scans archives or
PDFs, refuses CI, prints only aggregate dispositions and writes no candidate
key, original source bytes, recovered state, or emitted middle packet.

One SMT model is returned per state-bit bucket. A nonmatching SAT model does
not exclude other models in that bucket, and UNKNOWN never means UNSAT.
Use distinct --start/--count intervals to split a long 4096-bucket experiment.
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
from agents.agent4.k04_xoropp_zero_witness_synthetic import POSITIONS
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import solve, stream


def requested_packet(log: Path, attempt: int) -> bytes:
    pattern = re.compile(
        rf'\bJOB=PS-261003-0417 ATTEMPT={attempt} STATE=REQUESTED '
        rf'CLASS=RECOVER PAYLOAD=([0-9A-F]{{32}})\b'
    )
    values = []
    with log.open('r', encoding='utf-8') as f:
        for line in f:
            m = pattern.search(line)
            if m:
                values.append(bytes.fromhex(m.group(1)))
    if len(values) != 1:
        raise ValueError(f'Expected exactly one requested attempt {attempt}')
    return values[0]


def unpack(raw: bytes, endian: str, order: str) -> tuple[int, int]:
    result = [int.from_bytes(raw[j:j + 8], endian) for j in (0, 8)]
    if order == 'ba':
        result.reverse()
    return result[0], result[1]


def pack(pair: tuple[int, int], endian: str, order: str) -> bytes:
    words = list(pair)
    if order == 'ba':
        words.reverse()
    return b''.join(w.to_bytes(8, endian) for w in words)


def branch_job(args):
    idx, first, later, timeout_ms, max_skipped = args
    anchor = sum(((idx >> j) & 1) << pos for j, pos in enumerate(POSITIONS))
    status, state = solve({0: first[0], 1: first[1]}, anchor, POSITIONS, timeout_ms)
    replay = stream(*state, 6 + 2 * max_skipped) if state is not None else []
    phases = range(4, 6 + 2 * max_skipped, 2)
    valid = bool(state is not None and any(
        tuple(replay[j:j + 2]) == tuple(later) for j in phases
    ))
    middle = tuple(replay[2:4]) if valid else None
    # The selected ACK2 remains the first erased pair; only later phase varies.
    # Deliberately omit state and branch index from returned diagnostics.
    return status, valid, middle


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--resources-root', type=Path, default=ROOT / 'resources')
    p.add_argument('--endian', choices=('big', 'little'), default='big')
    p.add_argument('--order', choices=('ab', 'ba'), default='ab')
    p.add_argument('--start', type=int, default=0)
    p.add_argument('--count', type=int, default=1024)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--timeout-ms', type=int, default=5000)
    p.add_argument('--max-later-skipped-packets', type=int, default=0)
    p.add_argument('--summary-json', type=Path)
    args = p.parse_args()

    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        raise SystemExit('Historical source processing is prohibited in CI')
    if not (0 <= args.start < 4096 and 1 <= args.count <= 4096 - args.start):
        p.error('The interval must lie inside 0..4095')
    if not 0 <= args.max_later_skipped_packets <= 8:
        p.error('max-later-skipped-packets must be 0..8')
    if not (1 <= args.workers <= 4 and 100 <= args.timeout_ms <= 30000):
        p.error('workers must be 1..4 and timeout-ms 100..30000')

    root = args.resources_root
    log = root / 'evidence' / 'print' / 'spool-reconstruction.log'
    first = unpack(requested_packet(log, 1), args.endian, args.order)
    later = unpack(requested_packet(log, 3), args.endian, args.order)
    route = json.loads((root / 'evidence' / 'recovery-routing.json')
                       .read_text(encoding='utf-8'))
    acceptance = json.loads((root / 'acceptance.json')
                            .read_text(encoding='utf-8'))
    mask = bytes.fromhex(route['K04']['masked_component'])
    target = acceptance['slot_sha256']['K04']
    assert len(mask) == 16 and re.fullmatch('[0-9a-f]{64}', target)

    t0 = time.monotonic()
    statuses = {'sat': 0, 'unsat': 0, 'unknown': 0}
    done = holdout_hits = acceptance_hits = 0
    with mp.Pool(args.workers) as pool:
        jobs = ((i, first, later, args.timeout_ms,
                 args.max_later_skipped_packets)
                for i in range(args.start, args.start + args.count))
        for status, valid, middle in pool.imap_unordered(
                branch_job, jobs, chunksize=1):
            done += 1
            statuses[status] = statuses.get(status, 0) + 1
            if valid:
                holdout_hits += 1
                coupon = pack(middle, args.endian, args.order)
                candidate = bytes(v ^ m for v, m in zip(coupon, mask))
                if hashlib.sha256(candidate).hexdigest() == target:
                    acceptance_hits += 1
            if done % 100 == 0:
                print({'branches_completed': done, 'statuses': statuses,
                       'complete_later_packet_replays': holdout_hits,
                       'commitment_hits': acceptance_hits,
                       'elapsed_seconds': round(time.monotonic() - t0, 1)},
                      flush=True)

    result = {
        'model': 'conditional_xoroshiro128pp_1.0',
        'hypothesis': 'requested1 / erased ACK2 / requested3 sequential stream',
        'layout': args.endian + '/' + args.order,
        'external_state_bits': 0,
        'max_later_skipped_packets': args.max_later_skipped_packets,
        'interval': [args.start, args.start + args.count],
        'branches_completed': done,
        'branch_statuses': statuses,
        'complete_later_packet_replays': holdout_hits,
        'original_K04_commitment_hits': acceptance_hits,
        'all_branches_examined': args.start == 0 and args.count == 4096,
        'all_examined_branches_decided': statuses.get('unknown', 0) == 0,
        'sat_models_per_branch': 'first only',
        'historical_coupon_authenticated': False,
        'elapsed_seconds': round(time.monotonic() - t0, 1),
        'source_bytes_in_output': False,
    }
    print('AGGREGATE_ONLY', json.dumps(result, sort_keys=True), flush=True)
    if args.summary_json:
        args.summary_json.write_text(
            json.dumps(result, sort_keys=True, indent=2) + '\n',
            encoding='utf-8'
        )


if __name__ == '__main__':
    main()
