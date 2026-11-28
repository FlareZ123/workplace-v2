#!/usr/bin/env python3
"""Local-only firstpacket xoroshiro128++ inversion allowing hidden 64-bit draws.

Distinct from even-packet-only later holdout: fit only REQUESTED1 y0/y1,
predict selected erased ACK2 y2/y3, and hold out whole REQUESTED3 pair
at each phase 4..21 (both even and odd phases). The odd phases allow a
single hidden 64-bit producer draw; they are exploratory, not attested.

Original-source mode is CI-denied and aggregate-only. Never emits source
bytes, state, missing packet, coupon, component, or candidate wording.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import multiprocessing as mp
import os
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent4.k04_xoropp_zero_witness_synthetic import POSITIONS
from agents.agent4.k04_xoropp_zero_witness_source_local import requested_packet, unpack, pack
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import stream
from agents.agent37.k04_xoropp_samebucket_collision_sft import query_models

SAFE_SHA = {
    'evidence/print/spool-reconstruction.log': '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
    'evidence/recovery-routing.json': 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
    'acceptance.json': '681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f',
}

def branch(job):
    idx, first, later, timeout_ms, skips, endian, order, mask, target = job
    anchor = sum(((idx >> j) & 1) << pos for j,pos in enumerate(POSITIONS))
    states,terminal = query_models(first,anchor,timeout_ms)
    if terminal not in ('unsat','unknown'):
        raise AssertionError('Source branch not closed: '+str(terminal))
    even = odd = even_hits = odd_hits = 0
    for state in states:
        ys = stream(*state, 7 + 2*skips)  # y22 for phase21/y22 holdout
        coupon = pack(tuple(ys[2:4]),endian,order)
        candidate = bytes(v ^ m for v,m in zip(coupon,mask))
        commitment_hit = hashlib.sha256(candidate).hexdigest() == target
        for phase in range(4,6 + 2*skips):
            if tuple(ys[phase:phase+2]) == tuple(later):
                if phase % 2:
                    odd += 1
                    odd_hits += int(commitment_hit)
                else:
                    even += 1
                    even_hits += int(commitment_hit)
    return bool(states),terminal,len(states),even,odd,even_hits,odd_hits

def synthetic_control():
    rng = random.Random(20261128)
    state = (rng.getrandbits(64),rng.getrandbits(64))
    ys = stream(*state,23)
    idx = sum(((state[0] >> pos)&1) << j for j,pos in enumerate(POSITIONS))
    mask = bytes(rng.getrandbits(8) for _ in range(16))
    for endian,order in (('big','ab'),('big','ba'),('little','ab'),('little','ba')):
        first = unpack(pack(ys[:2],endian,order),endian,order)
        later = unpack(pack(ys[5:7],endian,order),endian,order)
        middle = pack(ys[2:4],endian,order)
        target = hashlib.sha256(bytes(v^m for v,m in zip(middle,mask))).hexdigest()
        _,terminal,n,eh,oh,ea,oa = branch(
            (idx,first,later,30000,8,endian,order,mask,target))
        assert terminal == 'unsat' and n >= 1 and eh == 0 and oh == 1
        assert ea == 0 and oa == 1
    print({'synthetic_only':True,'odd_phase_five_tested':True,
           'four_layouts_full_middle_and_later_replay':True,
           'four_layouts_full_sha256_commitment_positive':True})

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--synthetic',action='store_true')
    p.add_argument('--resources-root',type=Path,default=ROOT/'resources')
    p.add_argument('--endian',choices=('big','little'),default='big')
    p.add_argument('--order',choices=('ab','ba'),default='ba')
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=1024)
    p.add_argument('--timeout-ms',type=int,default=5000)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--max-later-skipped-packets',type=int,default=8)
    p.add_argument('--summary-json',type=Path)
    a = p.parse_args()
    if a.synthetic:
        synthetic_control()
        return
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        raise SystemExit('Historical source forbidden in public CI')
    if not (0 <= a.start < 4096 and 1 <= a.count <= 4096-a.start):
        p.error('Anchor partition must be within 0..4095')
    if not (100 <= a.timeout_ms <= 30000 and 1 <= a.workers <= 4
            and 0 <= a.max_later_skipped_packets <= 8):
        p.error('Invalid solver/phase budget')
    for relative,digest in SAFE_SHA.items():
        file = a.resources_root/relative
        if file.suffix.lower() == '.pdf':
            raise SystemExit('PDF prohibited')
        if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
            raise SystemExit('Source pin mismatch')
    spool = a.resources_root/'evidence/print/spool-reconstruction.log'
    first = unpack(requested_packet(spool,1),a.endian,a.order)
    later = unpack(requested_packet(spool,3),a.endian,a.order)
    route = json.loads((a.resources_root/'evidence/recovery-routing.json').read_text())
    acceptance = json.loads((a.resources_root/'acceptance.json').read_text())
    mask = bytes.fromhex(route['K04']['masked_component'])
    target = acceptance['slot_sha256']['K04']
    assert len(mask)==16 and re.fullmatch('[0-9a-f]{64}',target)
    counts = dict(done=0,sat_buckets=0,unsat_buckets=0,open_unknown=0,
                  models_examined=0,even_holdout=0,odd_holdout=0,
                  even_commitment_hits=0,odd_commitment_hits=0)
    jobs = ((idx,first,later,a.timeout_ms,a.max_later_skipped_packets,
             a.endian,a.order,mask,target) for idx in range(a.start,a.start+a.count))
    started = time.monotonic()
    with mp.Pool(a.workers) as pool:
        for sat,terminal,n,eh,oh,ea,oa in pool.imap_unordered(branch,jobs,chunksize=1):
            counts['done'] += 1
            counts['sat_buckets'] += int(sat)
            counts['unsat_buckets'] += int(not sat and terminal=='unsat')
            counts['open_unknown'] += int(terminal=='unknown')
            counts['models_examined'] += n
            counts['even_holdout'] += eh
            counts['odd_holdout'] += oh
            counts['even_commitment_hits'] += ea
            counts['odd_commitment_hits'] += oa
            if counts['done'] % 100 == 0:
                print('AGGREGATE_PROGRESS',{'completed':counts['done'],
                      'sat':counts['sat_buckets'],'unsat':counts['unsat_buckets'],
                      'unknown':counts['open_unknown'],
                      'full_even_replays':counts['even_holdout'],
                      'full_odd_replays':counts['odd_holdout']},flush=True)
    summary = {
        'conditional_model':'xoroshiro128pp_1.0',
        'layout':a.endian+'/'+a.order,
        'source_data_emitted':False,
        'selected_ACK2_withheld_from_fit':True,
        'fit_outputs':'first intact REQUESTED packet only',
        'independent_later_pair_phases':list(range(4,6+2*a.max_later_skipped_packets)),
        'start_inclusive':a.start,'end_exclusive':a.start+a.count,
        'max_solver_ms_per_query':a.timeout_ms,
        'all_examined_branches_decided':counts['open_unknown']==0,
        'historical_coupon_authenticated':False,
        'elapsed_seconds':round(time.monotonic()-started,1),
        **counts,
    }
    print('AGGREGATE_ONLY',json.dumps(summary,sort_keys=True),flush=True)
    if a.summary_json:
        a.summary_json.write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')

if __name__ == '__main__':
    main()
