#!/usr/bin/env python3
"""Exact P20 child refinement of an unresolved K04 P16 xoroshiro128++ state cell.

A firstpacket output fixes 128 original bits. A P16 state partition may end
UNKNOWN under a bounded SMT budget. This module splits EXACTLY that P16 cell
into all 16 assignments to a0 positions 8,9,10,11 (P20), model-blocks every
SAT state, and retains UNKNOWN when any child remains unresolved. No historical
bit is supplied as a witness. Every recovered state is checked against a
complete unaltered K04 slot SHA256 after masked-coupon reconstruction.

--synthetic is source-independent and CI safe. Historical source mode is
CI-denied, only named hash-pinned non-PDF inputs, aggregate-only public output,
and any hit must be escrowed outside the GitHub tree with chmod0600.
"""
from __future__ import annotations
import argparse,ctypes,hashlib,json,os,random,re,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from agents.agent7.k04_xoropp_p16_subcube_source_local import P16
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import circuit,stream,ror
from agents.agent7.k04_xoropp_byte_slip_reducer import (
    assess_state,escrow_hits,serialized_bytes)
P20=P16+(8,9,10,11)
M=(1<<64)-1
assert len(P20)==20 and len(set(P20))==20

def exact_models(first,cube20,timeout_ms=350,cap=32):
    assert 0<=cube20<(1<<20)
    anchor=sum(((cube20>>j)&1)<<p for j,p in enumerate(P20))
    script=circuit({0:first[0],1:first[1]},anchor,P20,timeout_ms)
    lib=ctypes.CDLL('libz3.so.4');P=ctypes.c_void_p
    lib.Z3_mk_config.restype=P
    lib.Z3_mk_context.argtypes=[P];lib.Z3_mk_context.restype=P
    lib.Z3_del_config.argtypes=[P];lib.Z3_del_context.argtypes=[P]
    lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
    cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
    def run(command):
        return (lib.Z3_eval_smtlib2_string(ctx,command.encode()) or b'').decode().strip()
    try:
        status=run(script);states=[]
        while status=='sat':
            raw=run('(get-value ('+' '.join(f'a0_{j}' for j in range(64))+'))')
            bits={int(j):int(v=='true') for j,v in
                  re.findall(r'\(a0_(\d+)\s+(true|false)\)',raw)}
            if len(bits)!=64:raise AssertionError('Incomplete solver model')
            a=sum(bits[j]<<j for j in range(64))
            b=(ror((first[0]-a)&M,17)-a)&M
            assert stream(a,b,2)==list(first)
            assert all((a>>pos&1)==(cube20>>j&1)
                       for j,pos in enumerate(P20))
            states.append((a,b))
            if len(states)>=cap:return states,'unknown'
            clause=' '.join(f'(not a0_{j})' if bits[j] else f'a0_{j}'
                            for j in range(64))
            run('(assert (or '+clause+'))')
            status=run('(check-sat)')
        if status not in ('unsat','unknown'):
            raise AssertionError('Unexpected SMT disposition')
        return states,status
    finally:
        lib.Z3_del_context(ctx)

def refine_p16(first,cube16,short_ms=350,retry_ms=3000,model_cap=32):
    assert 0<=cube16<65536 and 100<=short_ms<=retry_ms<=30000
    totals={'children':0,'first_unknown':0,'unsat':0,
            'unknown':0,'models':0}
    all_states=set()
    for extra in range(16):
        cube20=cube16+(extra<<16)
        states,status=exact_models(first,cube20,short_ms,model_cap)
        totals['first_unknown']+=int(status=='unknown')
        if status=='unknown' and retry_ms>short_ms:
            more,status=exact_models(first,cube20,retry_ms,model_cap)
            states=list(set(states).union(more))
        totals[status]+=1
        totals['children']+=1
        totals['models']+=len(states)
        all_states.update(states)
    assert totals['children']==16
    return list(all_states),totals

def synthetic():
    # True P16 parent is disclosed for a SOURCE-FREE planted solver benchmark,
    # never selected from the original printer record or K04 target.
    rng=random.Random(80904)
    state=(rng.getrandbits(64),rng.getrandbits(64))
    outputs=stream(*state,2)
    parent=sum(((state[0]>>p)&1)<<j for j,p in enumerate(P16))
    t=time.monotonic()
    states,count=refine_p16(outputs,parent)
    assert count['unsat']==16 and count['unknown']==0
    assert state in states and len(states)==1
    m=rng.randbytes(16)
    payload=serialized_bytes(state,17,'big','ab')
    at=16*(3+1)+7
    expected=bytes(x^y for x,y in zip(payload[at:at+16],m))
    digest=hashlib.sha256(expected).hexdigest()
    checked=0;hits=[]
    for candidate in states:
        got,found=assess_state(candidate,m,digest,'big','ab',8,8)
        checked+=got['candidates']
        hits.extend(found)
    assert hits==[expected.hex().upper()] and checked==144
    print(json.dumps({'synthetic_only':True,'original_source_loaded':False,
        'true_P16_partition_used_for_calibration_only':True,
        'child_subcubes_exhausted':count['children'],
        'terminal_unsat_child_subcubes':count['unsat'],
        'all_full_state_models':count['models'],
        'complete_128bit_true_state_recovered':True,
        'whole_16byte_SHA256_commitment_positive':True,
        'elapsed_s':round(time.monotonic()-t,2)},sort_keys=True))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--synthetic',action='store_true')
    ap.add_argument('--p16-cube',type=int)
    ap.add_argument('--fit',choices=('first','later'),default='first')
    ap.add_argument('--endian',choices=('big','little'),default='big')
    ap.add_argument('--order',choices=('ab','ba'),default='ba')
    ap.add_argument('--timeout-ms',type=int,default=350)
    ap.add_argument('--retry-timeout-ms',type=int,default=3000)
    ap.add_argument('--max-models',type=int,default=32)
    ap.add_argument('--local-hit-escrow',type=Path)
    ap.add_argument('--summary-json',type=Path)
    a=ap.parse_args()
    if a.synthetic:return synthetic()
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        ap.error('Original H17 source processing forbidden in public CI')
    if a.p16_cube is None or not 0<=a.p16_cube<65536:
        ap.error('One explicit P16 UNKNOWN cell is required')
    if not 100<=a.timeout_ms<=a.retry_timeout_ms<=30000:
        ap.error('Invalid timeout')
    if not 1<=a.max_models<=1024:
        ap.error('Invalid model cap')
    if a.local_hit_escrow is None:
        ap.error('Historical source mode needs external private escrow')
    escrow=a.local_hit_escrow.resolve()
    if escrow==ROOT or ROOT in escrow.parents or not escrow.parent.is_dir():
        ap.error('Escrow must be outside repository')
    if a.summary_json and a.summary_json.resolve()==escrow:
        ap.error('Summary cannot overwrite component escrow')
    source_root=ROOT/'resources'
    pins={
      'evidence/print/spool-reconstruction.log':'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
      'evidence/recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
      'acceptance.json':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'}
    for rel,digest in pins.items():
        fn=source_root/rel
        if fn.suffix.lower()=='.pdf' or hashlib.sha256(fn.read_bytes()).hexdigest()!=digest:
            ap.error('Original input checksum mismatch or quarantined file')
    from agents.agent37.k04_xoropp_acceptance_first_source_local import read_named_sources
    first,later,mask,target=read_named_sources(source_root,a.endian,a.order)
    fitted=first if a.fit=='first' else later
    independent=later if a.fit=='first' else first
    t=time.monotonic()
    states,totals=refine_p16(fitted,a.p16_cube,a.timeout_ms,
                             a.retry_timeout_ms,a.max_models)
    count={'states_examined':len(states),'complete_coupons':0,
           'original_K04_full_SHA256_hits':0,'independent_replay_views':0}
    accepted=[]
    for candidate in states:
        if a.fit=='first':
            c,h=assess_state(candidate,mask,target,a.endian,a.order,8,8,independent)
            count['complete_coupons']+=c['candidates']
            count['original_K04_full_SHA256_hits']+=c['commit_hits']
            count['independent_replay_views']+=c['replay_views']
        else:
            from agents.agent7.k04_xoropp_laterfirst_p16_byte_slip import full_coupon_scan
            c,h=full_coupon_scan(candidate,mask,target,a.endian,a.order,independent)
            count['complete_coupons']+=c['complete_coupons']
            count['original_K04_full_SHA256_hits']+=c['accepts']
            count['independent_replay_views']+=c['earlier_replays']
        accepted.extend(h)
    escrow_hits(escrow,accepted)
    report={'original_source_local_only':True,
            'model_conditional':'xoroshiro128++','fitted_request':a.fit,
            'layout':a.endian+'/'+a.order,
            'single_explicit_P16_cell':True,
            'all_P20_children_decided':totals['unknown']==0,
            'source_or_candidate_bytes_exposed':False,
            'elapsed_s':round(time.monotonic()-t,2),
            'subcube_dispositions':totals,'commitment_counts':count}
    print('AGGREGATE_ONLY',json.dumps(report,sort_keys=True),flush=True)
    if a.summary_json:
        a.summary_json.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':
    main()
