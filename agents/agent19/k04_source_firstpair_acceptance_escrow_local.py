#!/usr/bin/env python3
"""LOCAL ONLY: recover K04 from every complete xoroshiro128++ firstpair model.

A single original PS-0417 REQUESTED1 pair is fit as the first two consecutive
64-bit xoroshiro128++ 1.0 outputs. The selected ACK2 is NEVER read. For each
exact initial state, predict a full 16-byte missing middle packet, XOR the
unchanged routing mask and check the original full K04 SHA256. Independently
replay REQUESTED3 over optional later packet gaps: the speculative third-retry
stage does NOT filter candidate acceptance.

All firstpair-compatible states are enumerated in each twelve-anchor cube until
UNSAT, UNKNOWN, or an explicit model-budget limit (then UNKNOWN). A passing
component is privately escrowed into a chmod0600 file OUTSIDE the repository,
not merely counted and discarded. No source-bearing material is printed or
put in public CI/results. Requires libz3.so.4 and original local non-PDF
resources. This producer/chronology is a hypothesis, not an authenticated
historical printer implementation.
"""
from __future__ import annotations
import argparse
import ctypes
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
from agents.agent4.k04_xoropp_zero_witness_source_local import requested_packet, unpack, pack
from agents.agent4.k04_xoropp_zero_witness_synthetic import POSITIONS
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import circuit, stream
from agents.agent19.k04_source_retry_ledger import (
    MODEL_ID, validate_private_path, append_record, unknown_buckets,
)

M=(1<<64)-1
P=ctypes.c_void_p
SPOOL_SHA256='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'

def rotr(x,n):return ((x>>n)|(x<<(64-n)))&M

def all_firstpair_states(first,anchor,timeout_ms,max_states,positions=POSITIONS):
    """Return observed models and an honest terminal UNSAT or UNKNOWN."""
    lib=ctypes.CDLL('libz3.so.4')
    lib.Z3_mk_config.restype=P
    lib.Z3_mk_context.argtypes=[P]
    lib.Z3_mk_context.restype=P
    lib.Z3_del_config.argtypes=[P]
    lib.Z3_del_context.argtypes=[P]
    lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
    cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
    def ev(v):return (lib.Z3_eval_smtlib2_string(ctx,v.encode()) or b'').decode().strip()
    try:
        status=ev(circuit({0:first[0],1:first[1]},anchor,positions,timeout_ms))
        models=[]
        while status=='sat':
            raw=ev('(get-value ('+' '.join(f'a0_{j}' for j in range(64))+'))')
            bits={int(i):int(v=='true') for i,v in re.findall(r'\(a0_(\d+)\s+(true|false)\)',raw)}
            if len(bits)!=64:raise ValueError('Incomplete solver model')
            a=sum(bits[j]<<j for j in range(64))
            b=(rotr((first[0]-a)&M,17)-a)&M
            if tuple(stream(a,b,2))!=tuple(first):raise ValueError('Invalid solver state replay')
            models.append((a,b))
            if len(models)>=max_states:
                # Model budget is NOT a logical exclusion, even if last model
                # happened to be the last one; report UNKNOWN conservatively.
                return models,'unknown'
            blocking=' '.join(f'(not a0_{j})' if bits[j] else f'a0_{j}' for j in range(64))
            ev(f'(assert (or {blocking}))')
            status=ev('(check-sat)')
        if status not in ('unsat','unknown'):raise RuntimeError('Solver returned '+status)
        return models,status
    finally:lib.Z3_del_context(ctx)

def evaluate(task):
    bucket,first,later,mask,target,endian,order,timeout_ms,later_skips,max_states,split_bit=task
    anchor=sum(((bucket>>j)&1)<<p for j,p in enumerate(POSITIONS))
    models,terminal=all_firstpair_states(first,anchor,timeout_ms,max_states)
    rescued=split_attempted=False
    if terminal=='unknown' and split_bit is not None:
        # The two P13 children are a disjoint, exhaustive partition of
        # the unresolved P12 a0 cube. This is source-free exact inference,
        # NOT an approximation or a claim that one SAT state is unique.
        split_attempted=True
        complete_children=[]
        all_seen=set(models)
        for side in (0,1):
            child_anchor=anchor|(side<<split_bit)
            child_states,child_terminal=all_firstpair_states(
                first,child_anchor,timeout_ms,max_states,POSITIONS+(split_bit,))
            if any((state[0]>>split_bit)&1!=side for state in child_states):
                raise AssertionError('P13 child escaped its source-state partition')
            all_seen.update(child_states)
            complete_children.append(child_terminal=='unsat')
        models=list(all_seen)
        rescued=all(complete_children)
        terminal='unsat' if rescued else 'unknown'
    matches_any=matches_later=matches_joint=0
    accepted_components=[]
    for state in models:
        outputs=stream(*state,6+2*later_skips)
        assert tuple(outputs[:2])==tuple(first)
        coupon=pack(tuple(outputs[2:4]),endian,order)
        component=bytes(x^y for x,y in zip(coupon,mask))
        committed=hashlib.sha256(component).hexdigest()==target
        replay=any(tuple(outputs[k:k+2])==tuple(later)
                   for k in range(4,6+2*later_skips,2))
        matches_any+=committed
        matches_later+=replay
        matches_joint+=(committed and replay)
        if committed:accepted_components.append(component.hex().upper())
    assert matches_any==len(accepted_components)
    return (bucket,terminal,len(models),matches_any,matches_later,matches_joint,
            accepted_components,split_attempted,rescued)

def read_sources(root,endian,order):
    spool=root/'evidence/print/spool-reconstruction.log'
    if hashlib.sha256(spool.read_bytes()).hexdigest()!=SPOOL_SHA256:
        raise ValueError('Unexpected original spool SHA256')
    first=unpack(requested_packet(spool,1),endian,order)
    later=unpack(requested_packet(spool,3),endian,order)
    route=json.loads((root/'evidence/recovery-routing.json').read_text(encoding='utf-8'))
    checks=json.loads((root/'acceptance.json').read_text(encoding='utf-8'))
    mask=bytes.fromhex(route['K04']['masked_component'])
    target=checks['slot_sha256']['K04']
    if len(mask)!=16 or not re.fullmatch('[0-9a-f]{64}',target):
        raise ValueError('Bad routing or target format')
    return first,later,mask,target

def securely_escrow(path,components):
    if not components:return
    # No original source bytes reach standard output or public repository.
    flag=os.O_CREAT|os.O_WRONLY|os.O_APPEND|getattr(os,'O_NOFOLLOW',0)
    fd=os.open(path,flag,0o600)
    with os.fdopen(fd,'a',encoding='utf-8') as f:
        os.fchmod(f.fileno(),0o600)
        for component in components:
            f.write(json.dumps({'K04_verified_component':component},sort_keys=True)+'\n')
        f.flush();os.fsync(f.fileno())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--resources-root',type=Path,default=ROOT/'resources')
    p.add_argument('--endian',choices=('big','little'),default='big')
    p.add_argument('--order',choices=('ab','ba'),default='ab')
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=4096)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--timeout-ms',type=int,default=5000)
    p.add_argument('--max-models-per-cube',type=int,default=64)
    p.add_argument('--split-unknown-bit',type=int,
                   help='Optionally split an unresolved P12 cube into both exhaustive P13 children, e.g. 4')
    p.add_argument('--max-later-skipped-packets',type=int,default=8)
    p.add_argument('--summary-json',type=Path)
    p.add_argument('--local-status-ledger',type=Path,
                   help='Optional confidential chmod0600 per-bucket dispositions outside the Git repository')
    p.add_argument('--retry-unknown-from',type=Path,
                   help='Schedule only previously UNKNOWN cubes in a same-source/same-layout private ledger')
    p.add_argument('--local-hit-escrow',type=Path,required=True,
                   help='Full path to confidential chmod0600 results outside Git repository')
    a=p.parse_args()
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        p.error('Real original K04 source prohibited in public CI')
    if not(0<=a.start<4096 and 1<=a.count<=4096-a.start):p.error('Bad partition')
    if not(1<=a.workers<=4 and 100<=a.timeout_ms<=30000):p.error('Bad solver budget')
    if not(1<=a.max_models_per_cube<=65536 and 0<=a.max_later_skipped_packets<=8):
        p.error('Bad model or gap budget')
    if a.split_unknown_bit is not None and (
            not 0<=a.split_unknown_bit<64 or a.split_unknown_bit in POSITIONS):
        p.error('The split bit must be one of the 52 free initial-a positions')
    path=validate_private_path(a.local_hit_escrow,ROOT)
    ledger_path=(validate_private_path(a.local_status_ledger,ROOT)
                 if a.local_status_ledger else None)
    first,later,mask,target=read_sources(a.resources_root,a.endian,a.order)
    if a.retry_unknown_from:
        retry_path=validate_private_path(a.retry_unknown_from,ROOT,must_exist=True)
        bucket_ids=unknown_buckets(retry_path,SPOOL_SHA256,a.endian+'/'+a.order,
                                   a.start,a.start+a.count)
    else:
        bucket_ids=list(range(a.start,a.start+a.count))
    num_jobs=len(bucket_ids)
    if not num_jobs:
        print('AGGREGATE_ONLY',json.dumps({
            'reference_interval':[a.start,a.start+a.count],
            'retry_unknown_only':bool(a.retry_unknown_from),
            'jobs_selected':0,'source_bytes_in_output':False,
            'original_K04_hits_any_state':0},sort_keys=True),flush=True)
        return
    tasks=((i,first,later,mask,target,a.endian,a.order,a.timeout_ms,
            a.max_later_skipped_packets,a.max_models_per_cube,a.split_unknown_bit)
           for i in bucket_ids)
    t0=time.monotonic();done=states=sat_cubes=hits=replays=joints=stored=0
    rescue_attempts=rescue_proofs=0
    terminal_count={'unsat':0,'unknown':0}
    with mp.Pool(a.workers) as pool:
        for bucket,terminal,n,h,r,j,components,split_attempted,rescued in pool.imap_unordered(
                evaluate,tasks,chunksize=1):
            done+=1;states+=n;sat_cubes+=(n>0);hits+=h;replays+=r;joints+=j
            rescue_attempts+=int(split_attempted)
            rescue_proofs+=int(rescued)
            terminal_count[terminal]+=1
            if ledger_path:
                append_record(ledger_path,{
                    'model_id':MODEL_ID,'source_sha256':SPOOL_SHA256,
                    'layout':a.endian+'/'+a.order,'bucket':bucket,
                    'terminal':terminal,'states_examined':n,
                    'timeout_ms':a.timeout_ms,
                    'max_models_per_cube':a.max_models_per_cube,
                    'split_unknown_bit':a.split_unknown_bit,
                    'rescue_attempted':bool(split_attempted),
                    'rescue_exact_closure':bool(rescued),
                })
            if components:
                securely_escrow(path,components)
                stored+=len(components)
            if done%50==0 or done==num_jobs:
                status={'reference_interval':[a.start,a.start+a.count],
                        'layout':a.endian+'/'+a.order,
                        'retry_unknown_only':bool(a.retry_unknown_from),
                        'branches_completed':done,'total_branches':num_jobs,
                        'original_interval_size':a.count,
                        'firstpacket_states_enumerated':states,'sat_cubes':sat_cubes,
                        'terminal_counts':terminal_count.copy(),
                        'original_K04_hits_any_state':hits,
                        'later_full_packet_replays':replays,
                        'joint_hits':joints,
                        'verified_hits_securely_escrowed':stored==hits,
                        'original_ACK2_not_read':True,
                        'unknown_cubes_unresolved':terminal_count['unknown'],
                        'split_unknown_bit':a.split_unknown_bit,
                        'split_rescue_attempts':rescue_attempts,
                        'split_rescue_exact_closures':rescue_proofs,
                        'endian_order_historical_hypothesis':True,
                        'elapsed_seconds':round(time.monotonic()-t0,2)}
                print('AGGREGATE_ONLY',json.dumps(status,sort_keys=True),flush=True)
                if a.summary_json:
                    a.summary_json.write_text(json.dumps(status,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':main()
