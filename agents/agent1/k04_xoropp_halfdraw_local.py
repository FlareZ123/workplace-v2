#!/usr/bin/env python3
"""Local-only firstpacket xoroshiro128++ inversion allowing hidden 64-bit draws.

Distinct from even-packet-only later holdout: fit only REQUESTED1 y0/y1,
predict all 18 complete erased ACK2 candidates at word starts2..19, and hold out whole REQUESTED3 pair
at each phase following the candidate by 2..19 words. Odd starts and phases allow a
bounded hidden 64-bit producer draws; exploratory, not source-authenticated.

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

def securely_escrow(path: Path,components: list[str]) -> None:
    """Commitment-passing 16-byte values only; no raw source/state/diagnostics."""
    if not components:return
    flags=os.O_WRONLY|os.O_CREAT|os.O_APPEND|getattr(os,'O_NOFOLLOW',0)
    fd=os.open(path,flags,0o600)
    with os.fdopen(fd,'a',encoding='ascii') as f:
        os.fchmod(f.fileno(),0o600)
        for item in components:
            if not re.fullmatch(r'[0-9A-F]{32}',item):
                raise ValueError('Invalid escrow component')
            f.write(json.dumps({'verified_K04_component':item},sort_keys=True)+'\n')
        f.flush()
        os.fsync(f.fileno())

def scan_states(states,later,skips,pre_gap,endian,order,mask,target):
    """Every complete shifted coupon is checked BEFORE independent retry replay."""
    counts = {'window_assignments':0,'all_accept':0,
              'even_coupon_accept':0,'odd_coupon_accept':0,
              'even_retry':0,'odd_retry':0,'joint':0}
    verified_hits = []
    total = 7 + pre_gap + 2*skips  # 40 outputs for pre_gap17/skips8
    for state in states:
        ys = stream(*state,total)
        for begin in range(2,3+pre_gap):
            coupon = pack(tuple(ys[begin:begin+2]),endian,order)
            candidate = bytes(v^m for v,m in zip(coupon,mask))
            committed = hashlib.sha256(candidate).hexdigest()==target
            counts['window_assignments'] += 1
            counts['all_accept'] += int(committed)
            if committed: verified_hits.append(candidate.hex().upper())
            counts['even_coupon_accept'] += int(committed and begin%2==0)
            counts['odd_coupon_accept'] += int(committed and begin%2==1)
            for phase in range(begin+2,begin+4+2*skips):
                if tuple(ys[phase:phase+2])==tuple(later):
                    counts['odd_retry' if phase%2 else 'even_retry'] += 1
                    counts['joint'] += int(committed)
    assert len(verified_hits) == counts['all_accept']
    return counts, verified_hits

def branch(job):
    bucket,first,later,timeout_ms,skips,pre_gap,endian,order,mask,target = job
    anchor=sum(((bucket>>j)&1)<<pos for j,pos in enumerate(POSITIONS))
    states,terminal=query_models(first,anchor,timeout_ms)
    if terminal not in ('unsat','unknown'):
        raise AssertionError('Incomplete in-cube model blocking')
    counts,verified_hits = scan_states(states,later,skips,pre_gap,endian,order,mask,target)
    return bool(states),terminal,len(states),counts,verified_hits

def synthetic_control():
    rng=random.Random(20261128)
    state=(rng.getrandbits(64),rng.getrandbits(64))
    ys=stream(*state,42)
    bucket=sum(((state[0]>>pos)&1)<<j for j,pos in enumerate(POSITIONS))
    mask=bytes(rng.getrandbits(8) for _ in range(16))
    for endian,order in (('big','ab'),('big','ba'),('little','ab'),('little','ba')):
        first=unpack(pack(ys[:2],endian,order),endian,order)
        later=unpack(pack(ys[23:25],endian,order),endian,order)
        raw=pack(ys[19:21],endian,order)  # farthest odd coupon offset
        target=hashlib.sha256(bytes(v^m for v,m in zip(raw,mask))).hexdigest()
        _,terminal,n,c,hits=branch((bucket,first,later,30000,8,17,endian,order,mask,target))
        assert terminal=='unsat' and n>=1
        assert c['all_accept']==1 and hits==[bytes(v^m for v,m in zip(raw,mask)).hex().upper()]
        assert c['odd_coupon_accept']==1
        assert c['even_coupon_accept']==0 and c['joint']==1
        assert c['odd_retry']>=1
        poison=(later[0]^1,later[1])
        _,term2,n2,p,poison_hits=branch((bucket,first,poison,30000,8,17,endian,order,mask,target))
        assert term2=='unsat' and n2>=1 and p['all_accept']==1 and poison_hits==hits
        assert p['joint']==0 and p['even_retry']==0 and p['odd_retry']==0
        for begin in range(2,20):
            raw=pack(ys[begin:begin+2],endian,order)
            t=hashlib.sha256(bytes(v^m for v,m in zip(raw,mask))).hexdigest()
            c2,one_hit=scan_states([state],later,8,17,endian,order,mask,t)
            assert c2['window_assignments']==18 and c2['all_accept']==1
            assert one_hit == [bytes(v^m for v,m in zip(raw,mask)).hex().upper()]
    print({'synthetic_only':True,'four_layouts':4,
           'verified_components_returned_for_private_escrow':True,
           'odd_coupon_start19_and_odd_retry_phase23_pass':True,
           'poisoned_retry_does_not_veto_committed_coupon':True,
           '72_shifted_full_coupon_checks_pass':True})

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
    p.add_argument('--max-preselected-skipped-words',type=int,default=17)
    p.add_argument('--summary-json',type=Path)
    p.add_argument('--local-hit-escrow',type=Path,
                   help='Required in historical mode: chmod0600 outside repository')
    a = p.parse_args()
    if a.synthetic:
        synthetic_control()
        return
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        raise SystemExit('Historical source forbidden in public CI')
    if a.local_hit_escrow is None:
        p.error('Historical source requires secure out-of-repository --local-hit-escrow')
    hit_path = a.local_hit_escrow.expanduser().resolve()
    if hit_path == ROOT or ROOT in hit_path.parents or not hit_path.parent.is_dir():
        p.error('Local hit escrow must be in an existing directory outside repository')
    if a.summary_json and (a.summary_json.resolve()==hit_path):
        p.error('Never send escrow contents to aggregate JSON')
    if not (0 <= a.start < 4096 and 1 <= a.count <= 4096-a.start):
        p.error('Anchor partition must be within 0..4095')
    if not (100 <= a.timeout_ms <= 30000 and 1 <= a.workers <= 4
            and 0 <= a.max_later_skipped_packets <= 8
            and 0 <= a.max_preselected_skipped_words <= 17):
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
                  models_examined=0,coupon_window_assignments=0,
                  even_holdout=0,odd_holdout=0,
                  even_coupon_accepts=0,odd_coupon_accepts=0,
                  joint_later_accepts=0,unfiltered_commitment_hits=0)
    jobs = ((idx,first,later,a.timeout_ms,a.max_later_skipped_packets,
             a.max_preselected_skipped_words,a.endian,a.order,mask,target)
             for idx in range(a.start,a.start+a.count))
    started = time.monotonic()
    with mp.Pool(a.workers) as pool:
        for sat,terminal,n,c,hits in pool.imap_unordered(branch,jobs,chunksize=1):
            counts['done'] += 1
            counts['sat_buckets'] += int(sat)
            counts['unsat_buckets'] += int(not sat and terminal=='unsat')
            counts['open_unknown'] += int(terminal=='unknown')
            counts['models_examined'] += n
            counts['coupon_window_assignments'] += c['window_assignments']
            counts['even_holdout'] += c['even_retry']
            counts['odd_holdout'] += c['odd_retry']
            counts['even_coupon_accepts'] += c['even_coupon_accept']
            counts['odd_coupon_accepts'] += c['odd_coupon_accept']
            counts['joint_later_accepts'] += c['joint']
            counts['unfiltered_commitment_hits'] += c['all_accept']
            if hits:
                securely_escrow(hit_path,hits)  # only fully committed bytes
            if counts['done'] % 100 == 0:
                print('AGGREGATE_PROGRESS',{'completed':counts['done'],
                      'sat':counts['sat_buckets'],'unsat':counts['unsat_buckets'],
                      'unknown':counts['open_unknown'],
                      'full_even_replays':counts['even_holdout'],
                      'full_odd_replays':counts['odd_holdout'],
                      'unfiltered_commitments':counts['unfiltered_commitment_hits']},flush=True)
    summary = {
        'conditional_model':'xoroshiro128pp_1.0',
        'layout':a.endian+'/'+a.order,
        'source_data_emitted':False,
        'selected_ACK2_withheld_from_fit':True,
        'fit_outputs':'first intact REQUESTED packet only',
        'coupon_output_word_starts':[2,2+a.max_preselected_skipped_words],
        'independent_later_pair_phases':'coupon_start+2 through coupon_start+'+str(3+2*a.max_later_skipped_packets),
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
