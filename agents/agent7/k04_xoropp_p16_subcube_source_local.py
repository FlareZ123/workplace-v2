#!/usr/bin/env python3
"""Source-safe exact P16 refinement of xoroshiro128++ first-packet inversion.

For each 12-bit initial-a0 cube, enumerate ALL 16 assignments to four additional
a0 bits. Each of the resulting 65536 disjoint 16-bit subcubes is checked by an
exact firstpacket SMT equation, with all SAT states model-blocked until terminal
UNSAT. UNKNOWN or model cap is unresolved, never an exclusion. Every SAT state
is tested against a complete K04 coupon SHA before optional REQUESTED3 replay.

--synthetic: wholly source-free seeded controls, safe in CI.
Historical mode: local-only, CI denied, aggregate stdout, out-of-repo 0600
escrow for any exact original K04 hit. Never reads BX25-08 or PDF derivatives.
"""
from __future__ import annotations
import argparse, ctypes, hashlib, json, multiprocessing as mp, os, random
import re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import circuit, stream, ror
from agents.agent7.k04_xoropp_byte_slip_reducer import (
    assess_state, escrow_hits, serialized_bytes,
)

P12 = (0, 1, 2, 3, 22, 23, 24, 25, 45, 46, 47, 48)
NEW4 = (4, 5, 6, 7)
P16 = P12 + NEW4
MASK64 = (1 << 64) - 1
assert len(P16) == 16 and len(set(P16)) == 16


def cube_anchor(cube):
    assert 0 <= cube < 65536
    return sum(((cube >> j) & 1) << pos for j, pos in enumerate(P16))


def exact_states(first, cube, timeout_ms=350, max_models=32):
    """Return every SAT state seen, terminal UNSAT/UNKNOWN; cap becomes UNKNOWN."""
    script = circuit({0: first[0], 1: first[1]},
                     cube_anchor(cube), P16, timeout_ms)
    lib = ctypes.CDLL('libz3.so.4')
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
        return (lib.Z3_eval_smtlib2_string(ctx, command.encode()) or b'').decode().strip()

    try:
        status = ask(script)
        states = []
        while status == 'sat':
            raw = ask('(get-value (' + ' '.join(f'a0_{j}' for j in range(64)) + '))')
            bits = {int(j): int(v == 'true')
                    for j, v in re.findall(r'\(a0_(\d+)\s+(true|false)\)', raw)}
            if len(bits) != 64:
                raise AssertionError('Incomplete SAT model, never a valid candidate')
            a = sum(bits[j] << j for j in range(64))
            b = (ror((first[0] - a) & MASK64, 17) - a) & MASK64
            assert stream(a, b, 2) == list(first)
            assert all(((a >> p) & 1) == ((cube >> j) & 1)
                       for j, p in enumerate(P16))
            states.append((a, b))
            if len(states) >= max_models:
                return states, 'unknown'
            change = ' '.join(f'(not a0_{j})' if bits[j] else f'a0_{j}'
                              for j in range(64))
            ask('(assert (or ' + change + '))')
            status = ask('(check-sat)')
        if status not in ('unsat', 'unknown'):
            raise AssertionError('Unexpected solver status ' + status)
        return states, status
    finally:
        lib.Z3_del_context(ctx)


def synthetic_controls():
    totals = dict(fixtures=0, conditioned_parent_cubes=0,
                  P16_subcubes=0, terminal_unsat=0, terminal_unknown=0,
                  SAT_states_examined=0, true_states_recovered=0,
                  planted_full_commitment_hits=0)
    started = time.monotonic()
    for seed in range(123210, 123218):
        rng = random.Random(seed)
        state = (rng.getrandbits(64), rng.getrandbits(64))
        outputs = stream(*state, 40)
        parent = sum(((state[0] >> p) & 1) << j for j, p in enumerate(P12))
        mask = rng.randbytes(16)
        gap, slip = rng.randrange(9), rng.randrange(16)
        payload = serialized_bytes(state, 24, 'big', 'ab')
        at = 16 * (1 + gap) + slip
        correct = bytes(x ^ m for x, m in zip(payload[at:at + 16], mask))
        target = hashlib.sha256(correct).hexdigest()
        found = []
        for sub in range(16):
            cube = parent | (sub << 12)
            states, terminal = exact_states(outputs[:2], cube, 350)
            totals['P16_subcubes'] += 1
            totals['terminal_unsat'] += int(terminal == 'unsat')
            totals['terminal_unknown'] += int(terminal == 'unknown')
            totals['SAT_states_examined'] += len(states)
            for candidate_state in states:
                totals['true_states_recovered'] += int(candidate_state == state)
                c, h = assess_state(candidate_state, mask, target,
                                    'big', 'ab', 8, 8, None)
                totals['planted_full_commitment_hits'] += c['commit_hits']
                found.extend(h)
        assert found == [correct.hex().upper()], ('Incomplete planted control', seed)
        totals['fixtures'] += 1
        totals['conditioned_parent_cubes'] += 1
    assert totals['true_states_recovered'] == totals['fixtures']
    print(json.dumps({'synthetic_only': True, 'original_source_loaded': False,
           'timeout_ms': 350, 'elapsed_seconds': round(time.monotonic() - started, 2),
           **totals}, sort_keys=True))


def source_worker(job):
    cube, first, later, mask, target, endian, order, ms, retry_ms, cap, pre, lag = job
    states, terminal = exact_states(first, cube, ms, cap)
    first_terminal = terminal
    if terminal == 'unknown' and retry_ms > ms:
        retry_states, terminal = exact_states(first, cube, retry_ms, cap)
        states = list(set(states).union(retry_states))
    counts = {'candidates': 0, 'commit_hits': 0,
              'unaligned_commit_hits': 0, 'replay_views': 0, 'joint_hits': 0}
    verified = []
    for state in states:
        c, hits = assess_state(state, mask, target, endian, order, pre, lag, later)
        for k in counts:
            counts[k] += c[k]
        verified.extend(hits)
    return cube, terminal, len(states), counts, verified, first_terminal


def read_original(endian, order):
    from agents.agent37.k04_xoropp_acceptance_first_source_local import read_named_sources
    pins = {
        'evidence/print/spool-reconstruction.log':
            '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
        'evidence/recovery-routing.json':
            'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
        'acceptance.json':
            '681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f',
    }
    for rel, digest in pins.items():
        path = ROOT / 'resources' / rel
        if path.suffix.lower() == '.pdf':
            raise RuntimeError('PDF prohibited')
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Original source pin mismatch')
    return read_named_sources(ROOT / 'resources', endian, order)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--synthetic', action='store_true')
    ap.add_argument('--layout', choices=('flat', 'parent-major'), default='parent-major')
    ap.add_argument('--start', type=int, default=0,
                    help='Starting 16-bit subcube in flat layout, P12 parent in parent-major')
    ap.add_argument('--count', type=int, default=16,
                    help='Subcube count in flat layout, P12 parent count in parent-major')
    ap.add_argument('--timeout-ms', type=int, default=350)
    ap.add_argument('--retry-timeout-ms', type=int, default=700,
                    help='Retry ONLY unresolved subcubes; never recheck proved UNSAT')
    ap.add_argument('--max-models', type=int, default=32)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--endian', choices=('big', 'little'), default='big')
    ap.add_argument('--order', choices=('ab', 'ba'), default='ba')
    ap.add_argument('--max-pre-packets', type=int, default=8)
    ap.add_argument('--max-later-packets', type=int, default=8)
    ap.add_argument('--local-hit-escrow', type=Path, required=False)
    ap.add_argument('--summary-json', type=Path)
    args = ap.parse_args()
    if args.synthetic:
        synthetic_controls()
        return
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        ap.error('Historical source processing is forbidden in public CI')
    if args.local_hit_escrow is None:
        ap.error('Original-source mode requires out-of-repo private escrow')
    maximum = 4096 if args.layout == 'parent-major' else 65536
    if not (0 <= args.start < maximum and 1 <= args.count <= maximum - args.start
            and 100 <= args.timeout_ms <= args.retry_timeout_ms <= 30000
            and 1 <= args.workers <= 4
            and 1 <= args.max_models <= 1024
            and 0 <= args.max_pre_packets <= 16):
        ap.error('Invalid bounded search settings')
    if not 0 <= args.max_later_packets <= 16:
        ap.error('Invalid later packet gap')
    escrow = args.local_hit_escrow.expanduser().resolve()
    if ROOT == escrow or ROOT in escrow.parents or not escrow.parent.is_dir():
        ap.error('Escrow must live outside repository in an existing directory')
    if args.summary_json and args.summary_json.resolve() == escrow:
        ap.error('Summary cannot overwrite private verified components')
    first, later, mask, target = read_original(args.endian, args.order)
    if args.layout == 'parent-major':
        buckets = (parent + (sub << 12)
                   for parent in range(args.start, args.start + args.count)
                   for sub in range(16))
        total = 16 * args.count
    else:
        buckets = range(args.start, args.start + args.count)
        total = args.count
    counts = {'done': 0, 'unsat': 0, 'unknown': 0, 'models': 0,
              'candidates': 0, 'commit_hits': 0, 'unaligned_commit_hits': 0,
              'replay_views': 0, 'joint_hits': 0,
              'complete_parents': 0, 'open_parents': 0,
              'first_stage_unknown': 0, 'retry_resolved': 0,
              'retry_still_unknown': 0}
    progress = {}
    start = time.monotonic()
    tasks = ((cube, first, later, mask, target, args.endian, args.order,
              args.timeout_ms, args.retry_timeout_ms, args.max_models,
              args.max_pre_packets, args.max_later_packets)
             for cube in buckets)
    with mp.Pool(args.workers) as pool:
        for cube, status, nmodels, c, hits, first_terminal in pool.imap_unordered(source_worker, tasks, chunksize=1):
            counts['done'] += 1
            counts[status] += 1
            counts['models'] += nmodels
            if first_terminal == 'unknown':
                counts['first_stage_unknown'] += 1
                counts['retry_resolved' if status == 'unsat' else 'retry_still_unknown'] += 1
            for k in c:
                counts[k] += c[k]
            if hits:
                escrow_hits(escrow, hits)
            parent = cube & 4095
            done, open_count = progress.get(parent, (0, 0))
            done += 1
            open_count += int(status == 'unknown')
            progress[parent] = (done, open_count)
            if args.layout == 'parent-major' and done == 16:
                counts['complete_parents' if open_count == 0 else 'open_parents'] += 1
            if counts['done'] % 100 == 0 or counts['done'] == total:
                report = {
                    'local_only': True, 'phase': 'P16 complete-firstpacket',
                    'layout': args.layout, 'start': args.start, 'count': args.count,
                    'endian': args.endian, 'order': args.order,
                    'first_timeout_ms': args.timeout_ms,
                    'retry_timeout_ms': args.retry_timeout_ms,
                    'original_source_or_candidate_values_exposed': False,
                    'all_subcubes_examined': counts['done'] == total,
                    'all_subcubes_decided': counts['unknown'] == 0,
                    'elapsed_s': round(time.monotonic() - start, 2),
                    'aggregate': counts.copy(),
                }
                print('AGGREGATE_ONLY', json.dumps(report, sort_keys=True), flush=True)
                if args.summary_json:
                    args.summary_json.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
