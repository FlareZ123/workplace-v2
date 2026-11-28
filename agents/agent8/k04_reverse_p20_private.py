#!/usr/bin/env python3
"""K04 exact later-first little/BA P20 rescue of unresolved P16 children.

Source-independent full exact solver; only original REQUESTED3 pair fitted.
Every SAT state separately predicts 177 complete 16-byte earlier byte-slip coupon
windows and checks full unchanged original K04 SHA256 first. Original REQUESTED1
is not a veto. Source input is SHA-pinned non-PDF text; historical mode is CI
denied; source-derived models and matching component stay in owner-private 0600
files in a 0700 directory outside GitHub. Synthetic mode loads no original.
"""
from __future__ import annotations
import argparse, hashlib, json, os, random, time
from pathlib import Path
import k04_reverse_littleba_private as r

P20=r.P16+(8,9,10,11)

def read_child(folder,parent,child):
    cube=parent|(child<<12)
    path=folder/f'cube_{cube:05d}.json'
    if not path.exists(): return None
    if path.is_symlink() or path.stat().st_mode&0o077:
        raise ValueError('Unsafe parent P16 state ledger')
    rec=json.loads(path.read_text())
    if rec.get('stamp')!=r.stamp('little','ba',r.P16) or rec.get('cube')!=cube:
        raise ValueError('Original P16 source/circuit/geometry mismatch')
    return rec

def source_run(lo,count,folder,timeout_ms,retry_ms):
    if not(0<=lo<4096 and 1<=count<=4096-lo and 100<=timeout_ms<=retry_ms<=30000):
        raise ValueError('Invalid parent range and budget')
    folder=r.private_directory(folder)
    later,earlier,mask,target=r.source()
    obs={0:later[0],1:later[1]}
    stamp=r.stamp('little','ba',P20)
    counts={'p12_parents':0,'p16_open_selected':0,'p16_closed_skipped':0,'p16_unvisited_skipped':0,
            'p20_children':0,'p20_reused':0,'p20_terminal_unsat_empty':0,'p20_terminal_unsat_with_states':0,
            'p20_open_unknown':0,'p20_sat_states':0,'coupon_windows_tested':0,'original_commitment_hits':0,
            'original_p12_parents_closed':0,'original_p12_parents_open':0}
    start=time.monotonic()
    for parent in range(lo,lo+count):
        counts['p12_parents']+=1
        parent_closed=True
        for child in range(16):
            old=read_child(folder,parent,child)
            if old is None:
                parent_closed=False;counts['p16_unvisited_skipped']+=1;continue
            if old['terminal']=='unsat':
                counts['p16_closed_skipped']+=1;continue
            counts['p16_open_selected']+=1
            sub_closed=True
            for sub in range(16):
                idx=parent|(child<<12)|(sub<<16)
                path=folder/f'p20_cube_{idx:07d}.json'
                rec=None
                if path.exists():
                    if path.is_symlink() or path.stat().st_mode&0o077:raise ValueError('Unsafe cached P20')
                    rec=json.loads(path.read_text())
                    if rec.get('cube')!=idx or rec.get('stamp')!=stamp:raise ValueError('Cache version mismatch')
                    if rec['terminal']=='unsat':counts['p20_reused']+=1
                if rec is None or rec['terminal']=='unknown':
                    fixed=sum(((idx>>j)&1)<<bit for j,bit in enumerate(P20))
                    states,status=r.e.solve(obs,fixed,P20,timeout_ms,True)
                    if status=='unknown' and retry_ms>timeout_ms:
                        more,status2=r.e.solve(obs,fixed,P20,retry_ms,True)
                        states=list(set(states).union(more));status=status2
                    old_states=[(int(a,16),int(b,16)) for a,b in rec['states']] if rec else []
                    states=sorted(set(states).union(old_states))
                    for state in states:
                        for offset,value in r.full_hits(state,mask,target,'little','ba'):
                            r.private_coupon(folder/'K04_ORIGINAL_HASH_HIT.json',offset,value,'K04')
                            counts['original_commitment_hits']+=1
                        counts['coupon_windows_tested']+=177
                    rec={'cube':idx,'stamp':stamp,'terminal':status,
                         'states':[[f'{a:016X}',f'{b:016X}'] for a,b in states]}
                    r.atomic(path,rec)
                counts['p20_children']+=1
                counts['p20_sat_states']+=len(rec['states'])
                if rec['terminal']=='unknown':
                    sub_closed=False;counts['p20_open_unknown']+=1
                elif rec['states']:
                    counts['p20_terminal_unsat_with_states']+=1
                else:
                    counts['p20_terminal_unsat_empty']+=1
            if not sub_closed:parent_closed=False
        counts['original_p12_parents_closed' if parent_closed else 'original_p12_parents_open']+=1
        if counts['p12_parents']%1==0:
            print('SOURCE_SAFE_AGGREGATE',json.dumps({'p12_parent_range':[lo,parent+1],
                  'elapsed_seconds':round(time.monotonic()-start,1),
                  'original_source_or_candidates_printed':False,'counts':counts},sort_keys=True),flush=True)
    return counts

def synthetic():
    count=0
    for seed in range(98420,98436):
        rng=random.Random(seed)
        state=(rng.getrandbits(64),rng.getrandbits(64))
        obs=dict(enumerate(r.e.stream(*state,2)))
        fixed=r.P12+r.P16[len(r.P12):]+(8,9,10,11)
        anchor=sum(((state[0]>>i)&1)<<i for i in fixed)
        states,status=r.e.solve(obs,anchor,fixed,350,True)
        if status=='unknown' and state not in states:
            more,status2=r.e.solve(obs,anchor,fixed,700,True)
            states=list(set(states).union(more));status=status2
        assert state in states,('Correct P20 planted state not recovered',seed,status)
        mask=rng.randbytes(16)
        raw=r.earlier_bytes(state)
        at=rng.randrange(len(raw)-15)
        expected=bytes(x^y for x,y in zip(raw[at:at+16],mask))
        assert (at,expected) in r.full_hits(state,mask,hashlib.sha256(expected).hexdigest())
        count+=1
    print(json.dumps({'source_free':True,'complete_state_and_177window_reducer_positives':count,
                      'original_source_loaded':False,'historical_K04_recovered':False},sort_keys=True))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--synthetic',action='store_true')
    ap.add_argument('--parent-start',type=int,default=0)
    ap.add_argument('--parent-count',type=int,default=4)
    ap.add_argument('--private-dir',type=Path)
    ap.add_argument('--timeout-ms',type=int,default=350)
    ap.add_argument('--retry-ms',type=int,default=700)
    args=ap.parse_args()
    if args.synthetic:synthetic()
    else:
        if args.private_dir is None:ap.error('--private-dir required')
        source_run(args.parent_start,args.parent_count,args.private_dir,args.timeout_ms,args.retry_ms)
