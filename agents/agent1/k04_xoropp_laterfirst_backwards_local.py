#!/usr/bin/env python3
"""LOCAL ONLY: exact later-first xoroshiro128++ backward whole-coupon recovery.

Fit ONLY the intact REQUESTED3 first two 64-bit output words, enumerate all
first-pair-compatible initial states in each of 4096 P12 cubes with exact
model blocking, invert the PRNG transition to predict 18 complete candidate
coupons before that later request, and check the unchanged original K04 SHA256
for EVERY complete predicted 16-byte component. Earlier REQUESTED1 whole-pair
replay is an INDEPENDENT diagnostic, never an acceptance veto.

The selected ACK2 copied payload is never loaded. The source model and coupon
serializations are HYPOTHESES, not authenticated paper production. Historical
source mode is CI-denied, non-PDF, aggregate-only and requires private chmod0600
escrow OUTSIDE the repository for any genuine full-hash hit.
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

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from agents.agent4.k04_xoropp_zero_witness_synthetic import POSITIONS
from agents.agent4.k04_xoropp_zero_witness_source_local import requested_packet,unpack,pack
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import stream
from agents.agent37.k04_xoropp_samebucket_collision_sft import query_models
from agents.agent1.k04_xoropp_halfdraw_local import securely_escrow, SAFE_SHA

M=(1<<64)-1
def rol(v,n):
    return ((v<<n)|(v>>(64-n)))&M
def ror(v,n):
    return ((v>>n)|(v<<(64-n)))&M
def output(a,b):
    return (rol((a+b)&M,17)+a)&M
def prev_state(a1,b1):
    """Exact inverse of xoroshiro128++ 1.0 state transition."""
    t=ror(b1,28)
    a0=ror(a1^t^((t<<21)&M),49)
    return a0,a0^t
def forward_state(a,b):
    t=a^b
    return rol(a,49)^t^((t<<21)&M),rol(t,28)

def predicted_prehistory(state, max_gap=17, max_before=8):
    """Index distance i means 64-bit generator state i outputs before REQUESTED3."""
    n=4+max_gap+max_before
    states=[state]
    for _ in range(n):
        states.append(prev_state(*states[-1]))
    assert all(forward_state(*states[i+1])==states[i] for i in range(n))
    return [output(*s) for s in states]

def scan_state(state,first,later,mask,target,endian,order,
               max_gap=17,max_before=8):
    assert tuple(stream(*state,2))==tuple(later)
    backward=predicted_prehistory(state,max_gap,max_before)
    counts={'candidate_windows':0,'unfiltered_commitment_hits':0,
            'even_pre_gap_commitment_hits':0,'odd_pre_gap_commitment_hits':0,
            'earlier_whole_pair_replays':0,'joint':0}
    accepted=[]
    for gap in range(max_gap+1):
        # later starts at output0. Coupon is two consecutive outputs
        # at negative offsets -gap-2 and -gap-1 (oldest first).
        coupon=pack((backward[gap+2],backward[gap+1]),endian,order)
        component=bytes(x^y for x,y in zip(coupon,mask))
        committed=hashlib.sha256(component).hexdigest()==target
        counts['candidate_windows']+=1
        counts['unfiltered_commitment_hits']+=int(committed)
        counts['even_pre_gap_commitment_hits']+=int(committed and gap%2==0)
        counts['odd_pre_gap_commitment_hits']+=int(committed and gap%2==1)
        if committed:accepted.append(component.hex().upper())
        # Optional independent earlier REQUESTED1, before selected coupon.
        for unknown_between in range(max_before+1):
            k=gap+4+unknown_between
            if (backward[k],backward[k-1])==tuple(first):
                counts['earlier_whole_pair_replays']+=1
                counts['joint']+=int(committed)
    return counts,accepted

def branch(job):
    bucket,first,later,mask,target,endian,order,timeout_ms,max_gap,max_before=job
    anchor=sum(((bucket>>j)&1)<<p for j,p in enumerate(POSITIONS))
    states,terminal=query_models(list(later),anchor,timeout_ms)
    if terminal not in ('unsat','unknown'):
        raise AssertionError('In-cube state enumeration did not close')
    all_count={'candidate_windows':0,'unfiltered_commitment_hits':0,
               'even_pre_gap_commitment_hits':0,'odd_pre_gap_commitment_hits':0,
               'earlier_whole_pair_replays':0,'joint':0}
    accepted=[]
    for state in states:
        got,hits=scan_state(state,first,later,mask,target,endian,order,max_gap,max_before)
        for k,v in got.items():all_count[k]+=v
        accepted.extend(hits)
    assert len(accepted)==all_count['unfiltered_commitment_hits']
    return terminal,len(states),all_count,accepted

def synthetic_test():
    import random,stat,tempfile
    rng=random.Random(20261129)
    for _ in range(100000):
        state=(rng.getrandbits(64),rng.getrandbits(64))
        assert prev_state(*forward_state(*state))==state
    # Withhold the complete selected coupon and exact early req from the SAT fit.
    seed=(rng.getrandbits(64),rng.getrandbits(64))
    ss=stream(*seed,26)
    later_state=seed
    for _ in range(24):later_state=forward_state(*later_state)
    later=ss[24:26]
    idx=sum(((later_state[0]>>p)&1)<<j for j,p in enumerate(POSITIONS))
    mask=bytes(rng.getrandbits(8) for _ in range(16))
    for endian in ('big','little'):
        for order in ('ab','ba'):
            later_visible=unpack(pack(later,endian,order),endian,order)
            first=unpack(pack(ss[2:4],endian,order),endian,order)
            # Positive coupon is at y5/y6. Distance to later = 24-7=17
            # => gap = 17; fits the declared 0..17 stage family.
            positive=pack((ss[5],ss[6]),endian,order)
            component=bytes(x^y for x,y in zip(positive,mask))
            target=hashlib.sha256(component).hexdigest()
            terminal,n,c,hits=branch((idx,first,later_visible,mask,target,endian,order,
                                      30000,17,8))
            assert terminal=='unsat' and n>=1
            assert c['candidate_windows']>=18
            assert c['unfiltered_commitment_hits']==1 and hits==[component.hex().upper()]
            poisoned_first=[first[0]^1,first[1]]
            t2,n2,poison,poison_hits=branch((idx,poisoned_first,later_visible,mask,target,
                                            endian,order,30000,17,8))
            assert t2=='unsat' and n2>=1 and poison_hits==hits
            assert poison['joint']==0 and poison['unfiltered_commitment_hits']==1
            # Every prescribed previous stage is recoverable as a complete
            # component with no additional SAT when its target is planted.
            for gap in range(18):
                prior=predicted_prehistory(later_state,17,8)
                raw=pack((prior[gap+2],prior[gap+1]),endian,order)
                goal=hashlib.sha256(bytes(x^y for x,y in zip(raw,mask))).hexdigest()
                one,accepted=scan_state(later_state,first,later_visible,mask,goal,
                                        endian,order,17,8)
                assert one['unfiltered_commitment_hits']==1 and len(accepted)==1
    with tempfile.TemporaryDirectory(prefix='h17-reverse-synthetic-') as folder:
        file=Path(folder)/'verified'
        securely_escrow(file,[component.hex().upper()])
        assert stat.S_IMODE(file.stat().st_mode)==0o600
    print({'synthetic_only':True,'transition_inverse_exact':100000,
           'four_layouts_complete_middle_from_later_only':True,
           'earlier_request_poison_does_not_veto_commitment':True,
           'every_backward_coupon_window_passing':72,
           'private_hit_escrow_0600':True})

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--synthetic',action='store_true')
    p.add_argument('--resources-root',type=Path,default=ROOT/'resources')
    p.add_argument('--endian',choices=('big','little'),default='big')
    p.add_argument('--order',choices=('ab','ba'),default='ab')
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=512)
    p.add_argument('--timeout-ms',type=int,default=5000)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--max-preselected-gap-words',type=int,default=17)
    p.add_argument('--max-before-selected-gap-words',type=int,default=8)
    p.add_argument('--local-hit-escrow',type=Path)
    p.add_argument('--summary-json',type=Path)
    a=p.parse_args()
    if a.synthetic:
        synthetic_test()
        return
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        p.error('Historical source forbidden in CI')
    if not 0<=a.start<4096 or not 1<=a.count<=4096-a.start:
        p.error('Invalid P12 interval')
    if not 100<=a.timeout_ms<=30000 or not 1<=a.workers<=4:
        p.error('Invalid solver budget')
    if not 0<=a.max_preselected_gap_words<=17 or not 0<=a.max_before_selected_gap_words<=8:
        p.error('Invalid bounded phase hypothesis')
    if a.local_hit_escrow is None:
        p.error('Historical mode requires out-of-repository --local-hit-escrow')
    escrow=a.local_hit_escrow.expanduser().resolve()
    if escrow==ROOT or ROOT in escrow.parents or not escrow.parent.is_dir():
        p.error('Confidential hit escrow path must be outside repository')
    for name,digest in SAFE_SHA.items():
        file=a.resources_root/name
        if file.suffix.lower()=='.pdf':
            p.error('PDF forbidden')
        if hashlib.sha256(file.read_bytes()).hexdigest()!=digest:
            p.error('Safe source checksum mismatch')
    spool=a.resources_root/'evidence/print/spool-reconstruction.log'
    first=unpack(requested_packet(spool,1),a.endian,a.order)
    later=unpack(requested_packet(spool,3),a.endian,a.order)
    route=json.loads((a.resources_root/'evidence/recovery-routing.json').read_text())
    acceptance=json.loads((a.resources_root/'acceptance.json').read_text())
    mask=bytes.fromhex(route['K04']['masked_component'])
    target=acceptance['slot_sha256']['K04']
    assert len(mask)==16 and re.fullmatch('[0-9a-f]{64}',target)
    stats={'completed':0,'sat_cubes':0,'unsat_cubes':0,'open_unknown_cubes':0,
           'models_examined':0,'candidate_windows':0,
           'unfiltered_commitment_hits':0,'even_pre_gap_commitment_hits':0,
           'odd_pre_gap_commitment_hits':0,'earlier_whole_pair_replays':0,'joint':0}
    started=time.monotonic()
    jobs=((i,first,later,mask,target,a.endian,a.order,a.timeout_ms,
           a.max_preselected_gap_words,a.max_before_selected_gap_words)
          for i in range(a.start,a.start+a.count))
    with mp.Pool(a.workers) as pool:
        for terminal,n,c,hits in pool.imap_unordered(branch,jobs,chunksize=1):
            stats['completed']+=1
            stats['sat_cubes']+=int(n>0)
            stats['unsat_cubes']+=int(terminal=='unsat' and n==0)
            stats['open_unknown_cubes']+=int(terminal=='unknown')
            stats['models_examined']+=n
            for k,v in c.items():stats[k]+=v
            if hits:securely_escrow(escrow,hits)
            if stats['completed']%100==0:
                print('AGGREGATE',{'completed':stats['completed'],
                       'sat':stats['sat_cubes'],'unsat':stats['unsat_cubes'],
                       'unknown':stats['open_unknown_cubes'],
                       'complete_coupon_windows':stats['candidate_windows'],
                       'full_original_acceptances':stats['unfiltered_commitment_hits']},flush=True)
    result={'conditional_model':'xoroshiro128pp_last_request_first',
            'layout':a.endian+'/'+a.order,'fit_only':'REQUESTED3 full 16-byte',
            'selected_ACK2_withheld':True,'earlier_REQUESTED1':'blind diagnostic only',
            'preselected_gap_word_values':[0,a.max_preselected_gap_words],
            'cube_range':[a.start,a.start+a.count],
            'all_buckets_decided':stats['open_unknown_cubes']==0,
            'historical_coupon_authenticated':False,
            'source_or_candidate_bytes_emitted':False,
            'elapsed_seconds':round(time.monotonic()-started,1),**stats}
    print('AGGREGATE_ONLY',json.dumps(result,sort_keys=True),flush=True)
    if a.summary_json:
        a.summary_json.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':
    main()
