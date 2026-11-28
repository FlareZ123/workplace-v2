#!/usr/bin/env python3
"""Count exactly proved empty K04 xoroshiro P16/P18 subcubes from private caches.

Do not count UNKNOWN, unvisited or any cube containing a SAT state as empty.
A P16 UNKNOWN cube is resolved only if ALL FOUR P18 children terminate
UNSAT with no recovered state. The original P16 cache is immutable; each
P18 cohort is joined to its frozen SHA256-matched P16 input snapshot.
No source states, commitments, candidate bytes or hit components are printed.
Source-private audit is forbidden on public CI. --synthetic is source-free.
"""
from __future__ import annotations
import argparse,hashlib,json,os,stat
from pathlib import Path
PIN='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
ROOT=Path(__file__).resolve().parents[2]

def private_bytes(name):
    p=Path(name).expanduser().absolute()
    if p.is_symlink() or ROOT==p or ROOT in p.parents or not p.is_file():
        raise ValueError('Private source must be regular outside the repo')
    if (p.stat().st_mode&0o077) or (p.parent.stat().st_mode&0o077):
        raise ValueError('Private source and parent cannot allow group/other access')
    return p.read_bytes()

def source_rows(raw):
    rows={}
    for line in raw.splitlines():
        r=json.loads(line)
        b=r.get('bucket')
        valid_circuit = (r.get('circuit')=='firstpair-minimal-p16-v1' or
                         (r.get('schema')=='p16-agent7-firstpair-v1' and
                          r.get('anchor_positions')==
                          [0,1,2,3,22,23,24,25,45,46,47,48,4,5,6,7]))
        if (r.get('source_sha256')!=PIN or r.get('layout')!='big/ab' or
            not valid_circuit or
            r.get('terminal') not in ('unsat','unknown') or
            not isinstance(b,int) or not 0<=b<65536 or
            not isinstance(r.get('states'),list) or b in rows):
            raise ValueError('Original P16 cache fingerprint or duplicate invalid')
        rows[b]=r
    return rows

def refined_rows(frozen_pairs,source):
    out={}
    for input_file,output_file in frozen_pairs:
        raw=private_bytes(input_file)
        digest=hashlib.sha256(raw).hexdigest()
        frozen=source_rows(raw)
        if any(b not in source or source[b]!=row for b,row in frozen.items()):
            raise ValueError('Frozen source cohort differs from original P16 cache')
        for line in private_bytes(output_file).splitlines():
            r=json.loads(line);b=r.get('bucket')
            statuses=r.get('child_statuses',[])
            if (r.get('method',r.get('schema')) not in
                ('p18-two-bit-8-9-firstpair-v1','p18-agent50-refine-firstpair-v1') or
                r.get('source_sha256')!=PIN or r.get('layout')!='big/ab' or
                r.get('first_stage_sha256',r.get('p16_cache_sha256'))!=digest or
                r.get('child_positions')!=[8,9] or
                b not in frozen or frozen[b]['terminal']!='unknown' or
                b in out or len(statuses)!=4 or
                any(x not in ('unsat','unknown') for x in statuses) or
                not isinstance(r.get('states'),list)):
                raise ValueError('Invalid P18 source join / child terminality')
            out[b]=r
    return out

def classify(source,refined,max_parent=4096):
    empty=set();stateful=set();p16_excluded=p18_excluded=0
    for b,row in source.items():
        if row['states']:
            stateful.add(b)
        elif row['terminal']=='unsat':
            empty.add(b);p16_excluded+=1
        elif b in refined:
            r=refined[b]
            if r['states']:
                stateful.add(b)
            elif all(t=='unsat' for t in r['child_statuses']):
                empty.add(b);p18_excluded+=1
    closed=[p for p in range(max_parent)
            if all(p+(sub<<12) in empty for sub in range(16))]
    prefix=0
    while prefix<len(closed) and closed[prefix]==prefix:prefix+=1
    intervals=[]
    for p in closed:
        if intervals and p==intervals[-1][1]+1:intervals[-1][1]=p
        else:intervals.append([p,p])
    return {
        'original_source_or_state_exposed':False,
        'source_hypothesis':'xoroshiro128++ original PS-0417 first packet big/AB',
        'full_P16_partition':65536,
        'P16_source_cubes_visited':len(source),
        'P16_unvisited':65536-len(source),
        'P16_direct_terminal_EMPTY':p16_excluded,
        'P16_OPEN_resolved_by_all_P18_terminal_EMPTY':p18_excluded,
        'P16_TOTAL_proved_EMPTY':len(empty),
        'P16_stateful_NOT_EXCLUDED':len(stateful),
        'P16_not_proved_empty':65536-len(empty),
        'P18_source_cubes_tested':len(refined),
        'P12_parents_fully_proved_empty':len(closed),
        'P12_contiguous_closed_prefix_end_exclusive':prefix,
        'P12_closed_intervals':intervals,
    }

def synthetic_controls():
    source={}
    for parent in range(5):
        for child in range(16):
            cube=parent+(child<<12)
            source[cube]={'states':[],'terminal':'unsat'}
    a=1+(2<<12);b=2+(2<<12);c=3+(2<<12)
    source[a]['terminal']='unknown'
    source[b]['terminal']='unknown'
    source[c]['states']=['0'*32]
    del source[4+(2<<12)]
    refs={a:{'states':[],'child_statuses':['unsat']*4},
          b:{'states':[],'child_statuses':['unsat']*3+['unknown']}}
    report=classify(source,refs,5)
    assert report['P12_parents_fully_proved_empty']==2
    assert report['P12_contiguous_closed_prefix_end_exclusive']==2
    assert report['P16_stateful_NOT_EXCLUDED']==1
    print(json.dumps({'synthetic_only':True,'five_source_parent_controls':'PASS',
          'exact_closed_parents':2,'open_unknown_stateful_unvisited':3},sort_keys=True))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--synthetic',action='store_true')
    ap.add_argument('--p16-ledger')
    ap.add_argument('--p18-cohort',nargs=2,action='append',default=[],metavar=('FROZEN_P16','P18_LEDGER'))
    ns=ap.parse_args()
    if ns.synthetic:
        synthetic_controls()
        return
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        ap.error('Source-private audit prohibited in public CI')
    if not ns.p16_ledger:ap.error('Requires original source-private P16 ledger')
    source=source_rows(private_bytes(ns.p16_ledger))
    refined=refined_rows(ns.p18_cohort,source)
    print('AGGREGATE_ONLY '+json.dumps(classify(source,refined),sort_keys=True))

if __name__=='__main__':
    main()
