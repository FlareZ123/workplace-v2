#!/usr/bin/env python3
"""Exact P20 rescue of K04 copied-tail8 reverse-triad P16 UNKNOWN cubes.

P12+[4..7]+[8..11] forms 20 fixed initial-state bits, each P16 cube
partitioned into exactly sixteen disjoint P20 children. A terminal UNKNOWN
at P20 remains OPEN. Source mode is local-only, original bytes/complete states
remain chmod-0600 outside GitHub. Every recovered complete 16-byte coupon
is checked against unchanged full original K04 SHA256 BEFORE replay holdout.
"""
from __future__ import annotations
import argparse, hashlib, json, os, random
from pathlib import Path
import k04_pruned_native as e
import k04_triad_p12_source_private as base

P20=base.P12+(4,5,6,7,8,9,10,11)
def anchor(cube):
    return sum(((cube>>i)&1)<<bit for i,bit in enumerate(P20))

def solve_child(observations,cube,timeout,retry):
    states,status=e.solve(observations,anchor(cube),P20,timeout,True)
    if status=='unknown' and retry>timeout:
        extra,status=e.solve(observations,anchor(cube),P20,retry,True)
        states=sorted(set(states).union(extra))
    return states,status

def synthetic():
    for seed in range(202611281230,202611281234):
        rng=random.Random(seed)
        state=(rng.getrandbits(64),rng.getrandbits(64))
        observations=dict(enumerate(e.stream(*state,3)))
        cube=sum(((state[0]>>bit)&1)<<i for i,bit in enumerate(P20))
        states,status=solve_child(observations,cube,1000,1000)
        assert states==[state] and status=='unsat'
    print(json.dumps({'source_free_planted_full128bit_states':4,
                      'source_free_exact_final_model_blocks':4,
                      'original_source_read':False},sort_keys=True))

def run(view,folder,start,count,timeout,retry):
    if os.environ.get('GITHUB_ACTIONS') or os.environ.get('GITHUB_REPOSITORY'):
        raise RuntimeError('Original archive computation forbidden in public GitHub CI')
    if not folder.is_dir() or folder.is_symlink() or folder.stat().st_mode&0o077:
        raise ValueError('Owner-private nonsymlink 0700 directory required')
    folder=folder.resolve()
    if folder==base.ROOT or base.ROOT in folder.parents:
        raise ValueError('Private archive state cannot live in repo')
    observations,first,mask,target=base.source(view)
    parents=[]
    for file in folder.glob(f'triad_{view}_p16_*.json'):
        if file.is_symlink() or file.stat().st_mode&0o077:
            raise ValueError('Unsafe private P16 source-state file')
        rec=json.loads(file.read_text())
        cube=rec['cube']
        if rec['tag']!='triad-p16-v1' or rec['view']!=view:
            raise ValueError('Incompatible P16 original-source record')
        if rec['status']=='unknown' and start <= (cube&4095) < start+count:
            parents.append(cube)
    counts={'P16_unknown_selected':len(parents),'P16_processed':0,
            'P20_children':0,'P20_terminal_UNSAT':0,'P20_terminal_UNKNOWN':0,
            'state_models':0,'original_K04_hits':0,'earlier_request_holdouts':0,
            'P16_refined_closed':0,'P16_still_open':0}
    for parent in sorted(parents):
        terminal=True
        for extra in range(16):
            cube=parent|(extra<<16)
            file=folder/f'triad_{view}_p20_{cube:06d}.json'
            if file.exists():
                if file.is_symlink() or file.stat().st_mode&0o077:
                    raise ValueError('Unsafe cached P20 child')
                rec=json.loads(file.read_text())
                if rec['cube']!=cube or rec['tag']!='triad-p20-v1' or rec['view']!=view:
                    raise ValueError('Incompatible cached original-source P20 subcube')
            else:
                states,status=solve_child(observations,cube,timeout,retry)
                hits=0;holdouts=0
                for state in states:
                    seq=base.whole_stream(state)
                    assert seq[3:6]==[observations[k] for k in range(3)]
                    coupon=seq[2].to_bytes(8,view)+seq[3].to_bytes(8,view)
                    component=bytes(a^b for a,b in zip(coupon,mask))
                    correct=hashlib.sha256(component).hexdigest()==target
                    hits+=int(correct)
                    holdouts+=int(seq[:2]==first)
                    if correct:
                        base.atomic(folder/f'K04_ORIGINAL_HIT_P20_{view}_{cube:06d}.json',
                            {'K04':component.hex().upper(),'conditional_model':'ACK2 copied-tail8 intact'})
                rec={'cube':cube,'view':view,'tag':'triad-p20-v1',
                     'status':status,'states':[[f'{a:016X}',f'{b:016X}'] for a,b in states],
                     'original_hits':hits,'holdout':holdouts}
                base.atomic(file,rec)
            counts['P20_children']+=1
            counts['P20_terminal_UNSAT' if rec['status']=='unsat' else 'P20_terminal_UNKNOWN']+=1
            counts['state_models']+=len(rec['states'])
            counts['original_K04_hits']+=rec['original_hits']
            counts['earlier_request_holdouts']+=rec['holdout']
            if rec['status']=='unknown':terminal=False
        counts['P16_processed']+=1
        counts['P16_refined_closed' if terminal else 'P16_still_open']+=1
        print('SOURCE_SAFE_AGGREGATE',json.dumps({'view':view,'counts':counts,
               'source_state_or_candidate_bytes_printed':False},sort_keys=True),flush=True)
    print('FINAL_SOURCE_SAFE_AGGREGATE',json.dumps(counts,sort_keys=True),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--synthetic',action='store_true')
    p.add_argument('--private-dir',type=Path)
    p.add_argument('--endian',choices=('big','little'),default='big')
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=4096)
    p.add_argument('--timeout-ms',type=int,default=350)
    p.add_argument('--retry-ms',type=int,default=700)
    args=p.parse_args()
    synthetic()
    if not args.synthetic:
        if args.private_dir is None or not(0<=args.start and args.count>0 and args.start+args.count<=4096):
            p.error('Original mode requires valid P12 parent range and private directory')
        run(args.endian,args.private_dir,args.start,args.count,args.timeout_ms,args.retry_ms)
