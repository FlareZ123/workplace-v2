#!/usr/bin/env python3
"""K04: source-independent 128-bit prior-packet holdout on one complete REQUESTED1 fit.

Read only original non-PDF sources in local mode; never run original work on CI.
Do not interpret or fit selected RECOVER/ACK2. Never publish actual source state,
original coupon, component or payload: these are checked only in process.
Source-free planted arithmetic, full SHA and poisoning controls can run in CI.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent50.k04_xoropp_p16_incremental_synthetic import solve_parent

MASK = (1 << 64) - 1
SPOOL_PIN = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'

def rol(x,k): return ((x << k)|(x >> (64-k))) & MASK
def ror(x,k): return ((x >> k)|(x << (64-k))) & MASK

def step(state):
    a,b=state
    t=a^b
    return ((rol(a,49)^t^((t << 21)&MASK))&MASK, rol(t,28))

def reverse_step(state):
    nxt_a,nxt_b=state
    t=ror(nxt_b,28)
    a=ror(nxt_a^t^((t << 21)&MASK),49)
    return a,a^t

def rewind(state,n):
    for _ in range(n): state=reverse_step(state)
    return state

def outputs(state,n):
    vals=[]
    for _ in range(n):
        a,b=state
        vals.append((rol((a+b)&MASK,17)+a)&MASK)
        state=step(state)
    return vals

def serialize(words):
    assert len(words)%2==0
    return b''.join(b''.join(w.to_bytes(8,'big') for w in reversed(words[j:j+2]))
                    for j in range(0,len(words),2))

def controls():
    rng=random.Random(20261128)
    for _ in range(10000):
        state=(rng.getrandbits(64),rng.getrandbits(64))
        assert step(reverse_step(state))==state
        assert reverse_step(step(state))==state
        assert rewind(step(step(state)),2)==state
    planted=0
    for n in range(32):
        state=(rng.getrandbits(64),rng.getrandbits(64))
        earlier=serialize(outputs(rewind(state,22),2))
        assert earlier!=serialize(outputs(rewind(state,2),2))
        stream=serialize(outputs(state,40))
        route=bytes(rng.getrandbits(8) for _ in range(16))
        start=16*(1+n%9)+n%16
        comp=bytes(x^y for x,y in zip(stream[start:start+16],route))
        target=hashlib.sha256(comp).digest()
        successes=0
        for gap in range(9):
            for slip in range(16):
                i=16*(1+gap)+slip
                cand=bytes(x^y for x,y in zip(stream[i:i+16],route))
                successes+=int(hashlib.sha256(cand).digest()==target)
        assert successes==1
        planted+=1
    print('SYNTHETIC_PASS '+json.dumps({'inverse_roundtrips':10000,
        'complete_coupon_positive_controls':planted,'negative_wrong_prior_gap':True},sort_keys=True))

def source(root):
    spool=root/'evidence/print/spool-reconstruction.log'
    data=spool.read_bytes()
    assert hashlib.sha256(data).hexdigest()==SPOOL_PIN
    rows=[]
    for line in data.decode('utf-8').splitlines():
        m=re.search(r'\bJOB=(PS-261003-\d+) ATTEMPT=(\d+) STATE=([A-Z]+) CLASS=([A-Z]+) PAYLOAD=([0-9A-F]{32})\b',line)
        if m:
            rows.append({'job':m[1], 'attempt':int(m[2]), 'state':m[3],
                         'class':m[4], 'payload':bytes.fromhex(m[5])})
    assert len(rows)==133
    idcs=[i for i,row in enumerate(rows) if row['job']=='PS-261003-0417' and
          row['attempt']==1 and row['state']=='REQUESTED' and row['class']=='RECOVER']
    assert idcs==[128]
    earlier=[i for i,row in enumerate(rows) if i<128 and row['job']=='PS-261003-0417' and
             row['state']=='ACK' and row['class']=='LABEL']
    assert earlier==[117]
    assert rows[127]['job']!=rows[128]['job'] and rows[127]['state']=='ACK'
    route=json.loads((root/'evidence/recovery-routing.json').read_text())
    accepted=json.loads((root/'acceptance.json').read_text())
    mask=bytes.fromhex(route['K04']['masked_component'])
    sha=bytes.fromhex(accepted['slot_sha256']['K04'])
    assert len(mask)==16 and len(sha)==32
    first=tuple(int.from_bytes(rows[128]['payload'][i:i+8],'big') for i in (8,0))
    later=tuple(int.from_bytes(rows[130]['payload'][i:i+8],'big') for i in (8,0))
    assert rows[130]['job']=='PS-261003-0417' and rows[130]['state']=='REQUESTED'
    return rows, first,later,mask,sha

def original_run(root,ms,retry_ms,escrow):
    rows,first,later,mask,sha=source(root)
    # Parent was discovered by prior source-only first-packet scan; it is
    # NOT selected by matching any heldout source record or K04 target.
    results=solve_parent(first,1371,ms,retry_ms,64)
    states=[s for _,_,group,_ in results for s in group]
    status=[s for _,s,_,_ in results]
    if any(s!='unsat' for s in status):
        print('UNRESOLVED: model blocker did not close all P16 branches')
        return
    totals=dict(complete_P16_branches=len(results),source_compatible_states=len(states),
      actual_K04_commitment_hits=0,complete_K04_coupon_checks=0,
      earlier_samejob_onepacket_matches=0,earlier_samejob_rowgap_matches=0,
      preceding_global_row_matches=0,following_REQUESTED3_matches=0)
    for state in states:
        totals['earlier_samejob_onepacket_matches']+=int(
            serialize(outputs(rewind(state,2),2))==rows[117]['payload'])
        totals['earlier_samejob_rowgap_matches']+=int(
            serialize(outputs(rewind(state,22),2))==rows[117]['payload'])
        totals['preceding_global_row_matches']+=int(
            serialize(outputs(rewind(state,2),2))==rows[127]['payload'])
        totals['following_REQUESTED3_matches']+=int(
            serialize(outputs(step(step(step(step(state)))),2))==serialize(later))
        data=serialize(outputs(state,40))
        for gap in range(9):
            for slip in range(16):
                start=16*(1+gap)+slip
                coupon=data[start:start+16]
                comp=bytes(x^y for x,y in zip(coupon,mask))
                totals['complete_K04_coupon_checks']+=1
                accepted=hashlib.sha256(comp).digest()==sha
                totals['actual_K04_commitment_hits']+=int(accepted)
                if accepted:
                    flags=os.O_WRONLY|os.O_CREAT|os.O_APPEND|getattr(os,'O_NOFOLLOW',0)
                    fd=os.open(escrow,flags,0o600)
                    with os.fdopen(fd,'a',encoding='ascii') as f:
                        f.write(json.dumps({'verified_original_K04':comp.hex().upper()})+'\n')
                        f.flush();os.fsync(f.fileno())
    print('ORIGINAL_AGGREGATE_ONLY '+json.dumps({**totals,
      'status':'conditional xoroshiro128++ big/BA producer holdout',
      'old_label_to_request_global_row_gap':11,
      'selected_ACK2_not_used':True,'no_source_or_candidate_bytes_emitted':True},sort_keys=True))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--original',action='store_true')
    p.add_argument('--root',type=Path,default=ROOT/'resources')
    p.add_argument('--ms',type=int,default=350)
    p.add_argument('--retry-ms',type=int,default=2500)
    p.add_argument('--escrow',type=Path,default=Path('/tmp/h17-agent9-k04-private-verified.jsonl'))
    a=p.parse_args()
    controls()
    if a.original:
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            p.error('local original data cannot run in public CI')
        if not a.escrow.is_absolute() or a.escrow.resolve().is_relative_to(ROOT):
            p.error('Escrow must be absolute and outside repository')
        os.umask(0o077)
        original_run(a.root,a.ms,a.retry_ms,a.escrow)
if __name__=='__main__': main()
