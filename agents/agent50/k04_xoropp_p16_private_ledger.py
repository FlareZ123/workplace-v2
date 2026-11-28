#!/usr/bin/env python3
"""Local-only exact K04 P16 producer cache with source-private state replay.

The original selected ACK2 payload is withheld. Every recovered initial state
is screened against the COMPLETE coupon commitment before independently
checking later REQUESTED3. Raw states and verified components are written only
to 0600 out-of-repository files; no original material goes to stdout.
Resume includes UNVISITED and OPEN UNKNOWN cubes, requiring an increased
timeout for the latter. Terminal UNSAT buckets are never re-solved just because
a reducer changes.
"""
from __future__ import annotations
import argparse, json, multiprocessing as mp, os, stat, time
from pathlib import Path
from agents.agent7.k04_xoropp_p16_subcube_source_local import exact_states, read_original
from agents.agent7.k04_xoropp_byte_slip_reducer import assess_state, escrow_hits

SRC_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
ANCHOR = [0,1,2,3,22,23,24,25,45,46,47,48,4,5,6,7]
SCHEMA = 'p16-agent7-firstpair-v1'


def private_path(value, root, create):
    p = Path(value).expanduser().absolute()
    if p.is_symlink() or p.parent.is_symlink() or root == p or root in p.parents:
        raise ValueError('Private path must be outside repository, no symlink')
    if not p.parent.is_dir() or p.parent.stat().st_mode & 0o077:
        raise ValueError('Private parent must exist and have no group/other permissions')
    if p.exists():
        st = p.stat()
        if not stat.S_ISREG(st.st_mode) or st.st_mode & 0o077:
            raise ValueError('Private file must be regular 0600')
    elif not create:
        raise FileNotFoundError(p)
    return p


def read_ledger(path, layout):
    latest = {}
    if not path.exists(): return latest
    for line in path.read_text().splitlines():
        row = json.loads(line)
        if row.get('schema') != SCHEMA or row.get('source_sha256') != SRC_SHA or row.get('layout') != layout:
            raise ValueError('Producer cache fingerprint mismatch')
        if row.get('anchor_positions') != ANCHOR or row.get('bucket') not in range(65536):
            raise ValueError('Producer cache anchor mismatch')
        bucket = row['bucket']
        if bucket in latest:
            old = latest[bucket]
            if old['terminal'] == 'unsat':
                raise ValueError('Already completed cube must never be resubmitted')
            if row['timeout_ms'] < old['timeout_ms']:
                raise ValueError('Retry timeout cannot shrink')
            row['states'] = sorted(set(old['states']) | set(row['states']))
        latest[bucket] = row
    return latest


def append_private(path, obj):
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT |
                 getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise RuntimeError('Invalid private output')
        os.fchmod(fd, 0o600)
        os.write(fd, (json.dumps(obj, sort_keys=True) + '\n').encode())
        os.fsync(fd)
    finally:
        os.close(fd)


def source_job(job):
    cube, first, later, mask, target, endian, order, ms, retry_ms, cap, pre, lag = job
    states, terminal = exact_states(first, cube, ms, cap)
    if terminal == 'unknown' and retry_ms > ms:
        extra, terminal = exact_states(first, cube, retry_ms, cap)
        states = list(set(states + extra))
    counters = dict(candidates=0, commit_hits=0, replay_views=0,
                    joint_hits=0, unaligned_commit_hits=0)
    hits = []
    for state in states:
        count, found = assess_state(state, mask, target, endian, order,
                                    pre, lag, later)
        for k in counters: counters[k] += count[k]
        hits.extend(found)
    return cube, terminal, states, counters, hits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--start-parent', type=int, default=0)
    ap.add_argument('--parent-count', type=int, default=16)
    ap.add_argument('--endian', choices=('big','little'), default='big')
    ap.add_argument('--order', choices=('ab','ba'), default='ab')
    ap.add_argument('--timeout-ms', type=int, default=350)
    ap.add_argument('--retry-timeout-ms', type=int, default=700)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--max-models', type=int, default=32)
    ap.add_argument('--max-pre-packets', type=int, default=8)
    ap.add_argument('--max-later-packets', type=int, default=8)
    ap.add_argument('--ledger', type=str, required=True)
    ap.add_argument('--hit-escrow', type=str, required=True)
    ns = ap.parse_args()
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        ap.error('Original-source use forbidden on public CI')
    if not (0 <= ns.start_parent < 4096 and
            1 <= ns.parent_count <= 4096-ns.start_parent and
            100 <= ns.timeout_ms <= ns.retry_timeout_ms <= 30000 and
            1 <= ns.workers <= 4 and 1 <= ns.max_models <= 1024 and
            0 <= ns.max_pre_packets <= 16 and 0 <= ns.max_later_packets <= 16):
        ap.error('Invalid bounds')
    root = Path(__file__).resolve().parents[2]
    ledger = private_path(ns.ledger, root, True)
    escrow = private_path(ns.hit_escrow, root, True)
    if ledger == escrow: ap.error('Private cache and hit escrow must differ')
    first, later, mask, target = read_original(ns.endian, ns.order)
    layout = ns.endian + '/' + ns.order
    prev = read_ledger(ledger, layout)
    cohort = [parent+(sub<<12)
              for parent in range(ns.start_parent, ns.start_parent+ns.parent_count)
              for sub in range(16)]
    unresolved = [c for c in cohort if c in prev and prev[c]['terminal'] == 'unknown']
    if any(prev[c]['timeout_ms'] >= ns.retry_timeout_ms for c in unresolved):
        ap.error('Open UNKNOWN cubes require a higher retry budget; '
                 'prefer exact P18 refinement to repeating equivalent timeout work')
    queue = [c for c in cohort if c not in prev or prev[c]['terminal'] == 'unknown']
    tasks = ((cube, first, later, mask, target, ns.endian, ns.order,
              ns.timeout_ms, ns.retry_timeout_ms, ns.max_models,
              ns.max_pre_packets, ns.max_later_packets) for cube in queue)
    tally = {
        'requested_subcubes': ns.parent_count*16,
        'already_proven': sum(prev.get(c,{}).get('terminal')=='unsat' for c in cohort),
        'open_or_unvisited_queued': len(queue),
        'processed': 0, 'terminal_unsat': 0, 'terminal_unknown': 0,
        'SAT_states': 0, 'full_coupon_checks': 0,
        'original_K04_matches': 0, 'later_retry_matches': 0,
    }
    start = time.monotonic()
    with mp.Pool(ns.workers) as pool:
        for cube, terminal, states, counts, hits in pool.imap_unordered(source_job, tasks, chunksize=1):
            # Escrow a verified result BEFORE sealing a producer cache record.
            escrow_hits(escrow, hits)
            row = {
                'schema': SCHEMA, 'source_sha256': SRC_SHA, 'layout': layout,
                'anchor_positions': ANCHOR, 'bucket': cube, 'terminal': terminal,
                'timeout_ms': ns.retry_timeout_ms, 'max_models': ns.max_models,
                'states': [f'{a:016x}{b:016x}' for a,b in sorted(states)],
            }
            append_private(ledger, row)
            tally['processed'] += 1
            tally['terminal_'+terminal] += 1
            tally['SAT_states'] += len(states)
            tally['full_coupon_checks'] += counts['candidates']
            tally['original_K04_matches'] += counts['commit_hits']
            tally['later_retry_matches'] += counts['replay_views']
            if tally['processed'] % 256 == 0 or tally['processed'] == len(queue):
                print('AGGREGATE_ONLY ' + json.dumps({
                    'layout':layout, 'source_or_candidate_values_exposed':False,
                    'elapsed_s':round(time.monotonic()-start,2),
                    'counts':tally},sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
