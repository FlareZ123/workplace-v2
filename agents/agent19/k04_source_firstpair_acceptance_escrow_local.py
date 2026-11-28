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

M=(1<<64)-1
P=ctypes.c_void_p
SPOOL_SHA256='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'

def rotr(x,n):return ((x>>n)|(x<<(64-n)))&M

def all_firstpair_states(first,anchor,timeout_ms,max_states):
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
        status=ev(circuit({0:first[0],1:first[1]},anchor,POSITIONS,timeout_ms))
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
    bucket,first,later,mask,target,endian,order,timeout_ms,later_skips,max_states=task
    anchor=sum(((bucket>>j)&1)<<p for j,p in enumerate(POSITIONS))
    models,terminal=all_firstpair_states(first,anchor,timeout_ms,max_states)
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
    return (terminal,len(models),matches_any,matches_later,matches_joint,accepted_components)

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
    p.add_argument('--max-later-skipped-packets',type=int,default=8)
    p.add_argument('--summary-json',type=Path)
    p.add_argument('--local-hit-escrow',type=Path,required=True,
                   help='Full path to confidential chmod0600 results outside Git repository')
    a=p.parse_args()
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        p.error('Real original K04 source prohibited in public CI')
    if not(0<=a.start<4096 and 1<=a.count<=4096-a.start):p.error('Bad partition')
    if not(1<=a.workers<=4 and 100<=a.timeout_ms<=30000):p.error('Bad solver budget')
    if not(1<=a.max_models_per_cube<=65536 and 0<=a.max_later_skipped_packets<=8):
        p.error('Bad model or gap budget')
    path=a.local_hit_escrow.resolve()
    if path==ROOT or ROOT in path.parents:
        p.error('Confidential hit escrow MUST be outside the Git repository')
    if not path.parent.is_dir():p.error('Confidential escrow parent must exist')
    first,later,mask,target=read_sources(a.resources_root,a.endian,a.order)
    tasks=((i,first,later,mask,target,a.endian,a.order,a.timeout_ms,
            a.max_later_skipped_packets,a.max_models_per_cube)
           for i in range(a.start,a.start+a.count))
    t0=time.monotonic();done=states=sat_cubes=hits=replays=joints=stored=0
    terminal_count={'unsat':0,'unknown':0}
    with mp.Pool(a.workers) as pool:
        for terminal,n,h,r,j,components in pool.imap_unordered(evaluate,tasks,chunksize=1):
            done+=1;states+=n;sat_cubes+=(n>0);hits+=h;replays+=r;joints+=j
            terminal_count[terminal]+=1
            if components:
                securely_escrow(path,components)
                stored+=len(components)
            if done%50==0 or done==a.count:
                status={'branch_interval':[a.start,a.start+a.count],
                        'layout':a.endian+'/'+a.order,
                        'branches_completed':done,'total_branches':a.count,
                        'firstpacket_states_enumerated':states,'sat_cubes':sat_cubes,
                        'terminal_counts':terminal_count.copy(),
                        'original_K04_hits_any_state':hits,
                        'later_full_packet_replays':replays,
                        'joint_hits':joints,
                        'verified_hits_securely_escrowed':stored==hits,
                        'original_ACK2_not_read':True,
                        'unknown_cubes_unresolved':terminal_count['unknown'],
                        'endian_order_historical_hypothesis':True,
                        'elapsed_seconds':round(time.monotonic()-t0,2)}
                print('AGGREGATE_ONLY',json.dumps(status,sort_keys=True),flush=True)
                if a.summary_json:
                    a.summary_json.write_text(json.dumps(status,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':main()
