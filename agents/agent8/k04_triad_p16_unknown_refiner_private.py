#!/usr/bin/env python3
"""Exact P16 refinement ONLY for terminal-UNKNOWN K04 reverse-triad P12 parents.

Partition each 12-bit source-state parent into 16 disjoint child cubes
by fixing four additional 64-bit state-a bits 4,5,6,7. Source-dependent:
conditional copied PS-0417 ACK2 tail-eight intact + later REQUESTED3.
Every complete state is checked against the whole original masked K04 SHA
BEFORE earlier REQUESTED1 holdout. UNKNOWN is never exclusion; original
states, historical candidate bytes and true hits stay in owner-private cache.
"""
import argparse,hashlib,json,os,random
from pathlib import Path
import k04_pruned_native as e
import k04_triad_p12_source_private as tri

P16=tri.P12+(4,5,6,7)

def anchor_of(mask, positions):
    return sum(((mask>>i)&1)<<bit for i,bit in enumerate(positions))

def exhaustive_child(triad,mask,timeout,retry):
    state_anchor=anchor_of(mask,P16)
    models,status=e.solve(triad,state_anchor,P16,timeout,True)
    if status=='unknown' and retry>timeout:
        extra,status=e.solve(triad,state_anchor,P16,retry,True)
        models=sorted(set(models)|set(extra))
    return models,status

def synthetic():
    for seed in range(202611281230,202611281234):
        rng=random.Random(seed)
        state=(rng.getrandbits(64),rng.getrandbits(64))
        obs=dict(enumerate(e.stream(*state,3)))
        full_mask=sum(((state[0]>>bit)&1)<<j for j,bit in enumerate(P16))
        parent=full_mask&4095
        models=[];statuses=[]
        for child in range(16):
            found,status=exhaustive_child(obs,parent|(child<<12),350,700)
            models.extend(found);statuses.append(status)
        assert models==[state] and statuses==['unsat']*16
    print({'synthetic_source_free':True,'planted_128bit_states_recovered':4,
           'complete_disjoint_child_cubes':64,'terminal_UNSAT':64,
           'historical_data_read':False})

def original(start,count,endian,folder,timeout,retry):
    if os.environ.get('GITHUB_ACTIONS') or os.environ.get('GITHUB_REPOSITORY'):
        raise RuntimeError('Historical inputs forbidden in GitHub Actions')
    if folder.is_symlink() or not folder.is_dir() or folder.stat().st_mode&0o077:
        raise ValueError('Owner-private nonsymlink 0700 output directory required')
    folder=folder.resolve()
    if folder==tri.ROOT or tri.ROOT in folder.parents:
        raise ValueError('Private cache cannot be inside Git repository')
    obs,first,mask,target=tri.source(endian)
    out={'original_P12_unknown_selected':0,'visited_P12':0,
         'P16_full_child_checks':0,'P16_terminal_UNSAT':0,'P16_terminal_UNKNOWN':0,
         'source_compatible_states':0,'original_K04_hits':0,
         'REQUESTED1_replays':0,'fully_closed_empty_parents':0,'still_open_parents':0}
    for parent in range(start,start+count):
        p12=folder/f'triad_{endian}_p12_{parent:04d}.json'
        if not p12.is_file() or p12.is_symlink() or p12.stat().st_mode&0o077:
            raise ValueError('P12 cache missing/insecure; run P12 first')
        base=json.loads(p12.read_text())
        if base['parent']!=parent or base['tag']!='tail8-v1' or base['view']!=endian:
            raise ValueError('P12 incompatible original source checkpoint')
        if base['status']=='unsat':continue
        out['original_P12_unknown_selected']+=1
        all_unsat=True;all_empty=True
        for child in range(16):
            cube=parent|(child<<12)
            p16=folder/f'triad_{endian}_p16_{cube:05d}.json'
            if p16.exists():
                if p16.is_symlink() or p16.stat().st_mode&0o077:
                    raise ValueError('Insecure P16 checkpoint')
                rec=json.loads(p16.read_text())
                if rec['cube']!=cube or rec['tag']!='triad-p16-v1' or rec['view']!=endian:
                    raise ValueError('P16 cache mismatch')
            else:
                states,status=exhaustive_child(obs,cube,timeout,retry)
                hits=0;replays=0
                for state in states:
                    sequence=tri.whole_stream(state)
                    assert sequence[3:6]==[obs[k] for k in range(3)]
                    coupon=sequence[2].to_bytes(8,endian)+sequence[3].to_bytes(8,endian)
                    component=bytes(a^b for a,b in zip(coupon,mask))
                    good=hashlib.sha256(component).hexdigest()==target
                    hits+=int(good)
                    replays+=int(sequence[:2]==first)
                    if good:
                        tri.atomic(folder/f'K04_ORIGINAL_HASH_HIT_P16_{endian}_{cube:05d}.json',
                            {'K04':component.hex().upper(),'source_hypothesis':'ACK2 last-eight intact'})
                rec={'cube':cube,'view':endian,'tag':'triad-p16-v1','status':status,
                     'states':[[f'{a:016X}',f'{b:016X}'] for a,b in states],
                     'original_hits':hits,'earlier_holdout_replays':replays}
                tri.atomic(p16,rec)
            out['P16_full_child_checks']+=1
            out['P16_terminal_UNSAT' if rec['status']=='unsat' else 'P16_terminal_UNKNOWN']+=1
            out['source_compatible_states']+=len(rec['states'])
            out['original_K04_hits']+=rec['original_hits']
            out['REQUESTED1_replays']+=rec['earlier_holdout_replays']
            all_unsat &= rec['status']=='unsat'
            all_empty &= not rec['states']
        out['visited_P12']+=1
        if all_unsat and all_empty:out['fully_closed_empty_parents']+=1
        else:out['still_open_parents']+=1
        print('SOURCE_SAFE_AGGREGATE',
            json.dumps({'view':endian,'source_data_printed':False,'totals':out},sort_keys=True),
            flush=True)
    print('FINAL_SOURCE_SAFE_AGGREGATE',json.dumps(out,sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--synthetic',action='store_true')
    p.add_argument('--endian',choices=('big','little'),default='big')
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=64)
    p.add_argument('--timeout-ms',type=int,default=350)
    p.add_argument('--retry-ms',type=int,default=700)
    p.add_argument('--private-dir',type=Path)
    a=p.parse_args()
    if a.synthetic:synthetic()
    else:
        if not a.private_dir or not(0<=a.start and a.count>0 and a.start+a.count<=4096):
            p.error('Original P12 range and private-dir required')
        original(a.start,a.count,a.endian,a.private_dir,a.timeout_ms,a.retry_ms)
