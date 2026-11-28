#!/usr/bin/env python3
"""Source-safe K04 xoroshiro128++ serialized-stream byte-slip reducer.

Conditional hypothesis: a physical 16-byte coupon can be copied starting at
any byte boundary after a complete REQUESTED1 packet, including a boundary
inside the subsequent packet. This differs from word-wise repacking of an odd
starting 64-bit word when the packet serializer reverses word order.

Historical mode must run only in a trusted LOCAL environment, never CI.
It evaluates the original full K04 commitment on every source-free firstpacket
SAT model BEFORE any optional REQUESTED3 holdout. Summary is aggregate-only;
verified component values, if any, go to a 0600 out-of-repo escrow file.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import re
import stat
import sys
import time

MASK64 = (1 << 64) - 1
ROOT = Path(__file__).resolve().parents[2]


def rol(v: int, n: int) -> int:
    return ((v << n) | (v >> (64 - n))) & MASK64


def stream(a: int, b: int, n: int) -> list[int]:
    out = []
    for _ in range(n):
        out.append((rol((a + b) & MASK64, 17) + a) & MASK64)
        t = a ^ b
        a, b = rol(a, 49) ^ t ^ ((t << 21) & MASK64), rol(t, 28)
    return out


def pack_packet(pair: tuple[int, int], endian: str, order: str) -> bytes:
    if order == 'ba':
        pair = pair[::-1]
    return b''.join(x.to_bytes(8, endian) for x in pair)


def serialized_bytes(state: tuple[int, int], packet_count: int,
                     endian: str, order: str) -> bytes:
    words = stream(*state, packet_count * 2)
    return b''.join(pack_packet((words[i], words[i + 1]), endian, order)
                    for i in range(0, len(words), 2))


def assess_state(state: tuple[int, int], mask: bytes, target_sha: str,
                 endian: str, order: str, max_pre: int, max_later: int,
                 later_pair: tuple[int, int] | None = None):
    """Return bounded counts and *only* passing 16-byte components for escrow.

    pre=0..max_pre counts full hidden packets after first known packet;
    slip=0..15 adds an independent byte offset. Withholding optional later
    packet does not veto a committed original candidate.
    """
    assert len(mask) == 16 and re.fullmatch('[0-9a-f]{64}', target_sha)
    assert 0 <= max_pre <= 16 and 0 <= max_later <= 16
    payload = serialized_bytes(state, max_pre + max_later + 4, endian, order)
    later = (pack_packet(later_pair, endian, order)
             if later_pair is not None else None)
    counts = {'candidates': 0, 'commit_hits': 0,
              'unaligned_commit_hits': 0, 'replay_views': 0,
              'joint_hits': 0, 'slip_classes_examined': 0}
    hits = []
    for hidden in range(max_pre + 1):
        for slip in range(16):
            begin = 16 * (hidden + 1) + slip
            raw_coupon = payload[begin:begin + 16]
            assert len(raw_coupon) == 16
            component = bytes(a ^ b for a, b in zip(raw_coupon, mask))
            committed = hashlib.sha256(component).hexdigest() == target_sha
            counts['candidates'] += 1
            counts['slip_classes_examined'] |= 1 << slip
            counts['commit_hits'] += int(committed)
            counts['unaligned_commit_hits'] += int(committed and (slip % 8 != 0))
            if committed:
                hits.append(component.hex().upper())
            if later is not None:
                first_later_packet = (begin + 16 + 15) // 16
                stop = min(max_pre + max_later + 4,
                           first_later_packet + max_later + 1)
                replay = any(payload[16 * j:16 * (j + 1)] == later
                             for j in range(first_later_packet, stop))
                counts['replay_views'] += int(replay)
                counts['joint_hits'] += int(replay and committed)
    return counts, hits


def synthetic_controls():
    rng = random.Random(20261128)
    total = non_word = 0
    for seed in (1029, 9131):
        sr = random.Random(seed)
        state = (sr.getrandbits(64), sr.getrandbits(64))
        mask = bytes(rng.getrandbits(8) for _ in range(16))
        for endian in ('big', 'little'):
            for order in ('ab', 'ba'):
                payload = serialized_bytes(state, 22, endian, order)
                # Packet boundary agrees with packet-only reducer.
                words = stream(*state, 22 * 2)
                for gap in range(9):
                    assert payload[16 * (gap + 1):16 * (gap + 2)] == \
                        pack_packet((words[2 * (gap + 1)],
                                     words[2 * (gap + 1) + 1]), endian, order)
                    for slip in range(16):
                        begin = 16 * (gap + 1) + slip
                        raw = payload[begin:begin + 16]
                        complete = bytes(a ^ b for a, b in zip(raw, mask))
                        target = hashlib.sha256(complete).hexdigest()
                        counts, hits = assess_state(state, mask, target,
                                                    endian, order, 8, 8)
                        assert counts['candidates'] == 144
                        assert counts['commit_hits'] == 1
                        assert hits == [complete.hex().upper()]
                        assert counts['unaligned_commit_hits'] == int(slip % 8 != 0)
                        assert counts['slip_classes_examined'] == 65535
                        total += 1
                        non_word += int(slip % 8 != 0)
                # Later packet is independent from acceptance gate.
                gap, slip = 8, 15
                begin = 16 * (gap + 1) + slip
                complete = bytes(a ^ b for a, b in zip(
                    payload[begin:begin + 16], mask))
                target = hashlib.sha256(complete).hexdigest()
                actual = (words[2 * 12], words[2 * 12 + 1])
                ok, hits = assess_state(state, mask, target,
                                        endian, order, 8, 8, actual)
                assert ok['commit_hits'] == 1 and ok['joint_hits'] == 1
                poison, hits2 = assess_state(state, mask, target,
                    endian, order, 8, 8, (actual[0] ^ 1, actual[1]))
                assert poison['commit_hits'] == 1 and poison['joint_hits'] == 0
                assert hits == hits2 == [complete.hex().upper()]
    assert total == 1152 and non_word == 1008
    # Packet-stream BA offset8 differs from odd-word BA repack.
    st = (random.Random(5).getrandbits(64), random.Random(6).getrandbits(64))
    words = stream(*st, 8)
    fixed_packet = serialized_bytes(st, 4, 'big', 'ba')
    assert fixed_packet[24:40] != pack_packet((words[3], words[4]), 'big', 'ba')
    print(json.dumps({'synthetic_only': True,
        'complete_commitment_positives': total,
        'new_non_64bit_aligned_positives': non_word,
        'serializer_views': 4, 'initial_states': 2,
        'poisoned_later_does_not_veto_commitment': True,
        'packet_stream_vs_odd_word_repack_distinguished': True,
        'original_K04_recovered': False}, sort_keys=True))


def escrow_hits(path: Path, components: list[str]):
    if not components:
        return
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, 'a', encoding='ascii') as out:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('Escrow must be a regular file')
        os.fchmod(fd, 0o600)
        for component in components:
            assert re.fullmatch('[0-9A-F]{32}', component)
            out.write(json.dumps({'verified_K04_component': component}) + '\n')
        out.flush()
        os.fsync(fd)


def branch(args):
    idx, first, later, mask, target, endian, order, timeout_ms, pre, lag = args
    from agents.agent4.k04_xoropp_zero_witness_synthetic import POSITIONS
    from agents.agent37.k04_xoropp_samebucket_collision_sft import query_models
    anchor = sum(((idx >> j) & 1) << pos for j, pos in enumerate(POSITIONS))
    states, terminal = query_models(first, anchor, timeout_ms)
    if terminal == 'truncated':
        terminal = 'unknown'
    if terminal not in ('unsat', 'unknown'):
        raise AssertionError('Every cube requires terminal UNSAT or UNKNOWN')
    totals = dict(candidates=0, commit_hits=0, unaligned_commit_hits=0,
                  replay_views=0, joint_hits=0)
    hits = []
    for state in states:
        c, h = assess_state(state, mask, target, endian, order, pre, lag, later)
        for key in totals:
            totals[key] += c[key]
        hits.extend(h)
    return terminal, len(states), totals, hits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--synthetic', action='store_true')
    ap.add_argument('--resources-root', type=Path, default=ROOT / 'resources')
    ap.add_argument('--endian', choices=('big', 'little'), default='big')
    ap.add_argument('--order', choices=('ab', 'ba'), default='ab')
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--count', type=int, default=1)
    ap.add_argument('--timeout-ms', type=int, default=5000)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--max-pre-packets', type=int, default=8)
    ap.add_argument('--max-later-packets', type=int, default=8)
    ap.add_argument('--summary-json', type=Path)
    ap.add_argument('--local-hit-escrow', type=Path)
    ns = ap.parse_args()
    if ns.synthetic:
        synthetic_controls()
        return
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        ap.error('Original source must never run in public CI')
    if ns.local_hit_escrow is None:
        ap.error('Original-source scan requires private out-of-repo escrow')
    escrow = ns.local_hit_escrow.expanduser().resolve()
    if ROOT == escrow or ROOT in escrow.parents or not escrow.parent.is_dir():
        ap.error('Escrow must be in an existing directory outside repository')
    if ns.summary_json and ns.summary_json.resolve() == escrow:
        ap.error('Aggregate summary cannot overwrite confidential escrow')
    if not (0 <= ns.start < 4096 and 1 <= ns.count <= 4096 - ns.start):
        ap.error('Invalid 12-bit anchor interval')
    if not (1 <= ns.workers <= 4 and 100 <= ns.timeout_ms <= 30000
            and 0 <= ns.max_pre_packets <= 16 and 0 <= ns.max_later_packets <= 16):
        ap.error('Invalid worker/solver/phase bounds')
    sys.path.insert(0, str(ROOT))
    from agents.agent37.k04_xoropp_acceptance_first_source_local import read_named_sources
    first, later, mask, target = read_named_sources(ns.resources_root,
                                                   ns.endian, ns.order)
    started = time.monotonic()
    totals = dict(done=0, unsat=0, unknown=0, states=0,
                  candidates=0, commit_hits=0, unaligned_commit_hits=0,
                  replay_views=0, joint_hits=0)
    jobs = ((idx, first, later, mask, target, ns.endian, ns.order,
             ns.timeout_ms, ns.max_pre_packets, ns.max_later_packets)
            for idx in range(ns.start, ns.start + ns.count))
    with mp.Pool(ns.workers) as pool:
        for terminal, nstates, c, hits in pool.imap_unordered(branch, jobs):
            totals['done'] += 1
            totals[terminal] += 1
            totals['states'] += nstates
            for field in c:
                totals[field] += c[field]
            escrow_hits(escrow, hits)
            if totals['done'] % 100 == 0 or totals['done'] == ns.count:
                summary = {'hypothesis': 'serialized packet stream with byte slip',
                    'view': ns.endian + '/' + ns.order,
                    'cube_interval': [ns.start, ns.start + ns.count],
                    'pre_hidden_packets_max': ns.max_pre_packets,
                    'later_hidden_packets_max': ns.max_later_packets,
                    'all_cubes_examined': totals['done'] == ns.count,
                    'model_complete': totals['unknown'] == 0,
                    'aggregate': totals.copy(),
                    'elapsed_seconds': round(time.monotonic() - started, 2),
                    'source_or_candidate_bytes_in_output': False}
                print('AGGREGATE_ONLY', json.dumps(summary, sort_keys=True), flush=True)
                if ns.summary_json:
                    ns.summary_json.write_text(json.dumps(summary, indent=2) + '\n')

if __name__ == '__main__':
    main()
