#!/usr/bin/env python3
"""Local-only exact P18 repair for P16 original first-packet UNKNOWN cubes.

Consumes a PRIVATE replayable P16 ledger from Agent50's producer wrapper.
For every P16 UNKNOWN, try all four values of fresh a0 bits 8 and 9.
Never infer UNSAT from a timeout. Every SAT state is screened against the
unchanged COMPLETE 16-byte K04 commitment BEFORE REQUESTED3 replay.
Derived states and passing components stay in 0600 out-of-repository files;
the original-source path is strictly forbidden on public CI.
"""
from __future__ import annotations
import argparse,hashlib,json,os,time
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agents.agent50.k04_xoropp_p16_private_ledger import (
    SRC_SHA, ANCHOR, SCHEMA as P16_SCHEMA, private_path, append_private, read_ledger)
from agents.agent50.k04_xoropp_p18_adaptive_synthetic import refine_parent
from agents.agent7.k04_xoropp_p16_subcube_source_local import read_original
from agents.agent7.k04_xoropp_byte_slip_reducer import assess_state, escrow_hits

SCHEMA = 'p18-agent50-refine-firstpair-v1'


def read_refinement(path,layout,source_sha):
    latest={}
    if not path.exists():return latest
    for line in path.read_text().splitlines():
        row=json.loads(line)
        if (row.get('schema')!=SCHEMA or row.get('source_sha256')!=SRC_SHA or
            row.get('layout')!=layout or row.get('p16_cache_sha256')!=source_sha or
            row.get('child_positions')!=[8,9] or
            not isinstance(row.get('p16_bucket'),int) or
            row['p16_bucket'] not in range(65536)):
            raise ValueError('P18 cache fingerprint mismatch')
        bucket=row['p16_bucket']
        if bucket in latest:
            old=latest[bucket]
            if 'unknown' not in old['child_statuses']:
                raise ValueError('Already closed P18 parent must not rerun')
            if row['retry_ms']<=old['retry_ms']:
                raise ValueError('P18 retry timeout must strictly increase')
            row['states']=sorted(set(old['states']) | set(row['states']))
        latest[bucket]=row
    return latest


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--p16-ledger',required=True)
    ap.add_argument('--p18-ledger',required=True)
    ap.add_argument('--hit-escrow',required=True)
    ap.add_argument('--endian',choices=('big','little'),default='big')
    ap.add_argument('--order',choices=('ab','ba'),default='ab')
    ap.add_argument('--limit',type=int,default=256)
    ap.add_argument('--timeout-ms',type=int,default=350)
    ap.add_argument('--retry-ms',type=int,default=700)
    ap.add_argument('--max-pre-packets',type=int,default=8)
    ap.add_argument('--max-later-packets',type=int,default=8)
    ns=ap.parse_args()
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        ap.error('Historical-source operation forbidden in public CI')
    if not (1<=ns.limit<=65536 and 100<=ns.timeout_ms<=ns.retry_ms<=30000 and
            0<=ns.max_pre_packets<=16 and 0<=ns.max_later_packets<=16):
        ap.error('Invalid search/reducer bounds')
    root=Path(__file__).resolve().parents[2]
    src=private_path(ns.p16_ledger,root,False)
    out=private_path(ns.p18_ledger,root,True)
    hit=private_path(ns.hit_escrow,root,True)
    if len({src,out,hit})!=3:
        ap.error('Private input/output/verified escrow paths must differ')
    layout=ns.endian+'/'+ns.order
    p16=read_ledger(src,layout)
    input_sha=hashlib.sha256(src.read_bytes()).hexdigest()
    p18=read_refinement(out,layout,input_sha)
    unknown=[cube for cube,row in p16.items() if row['terminal']=='unknown']
    invalid=[cube for cube in unknown if cube in p18 and
             'unknown' in p18[cube]['child_statuses'] and
             ns.retry_ms<=p18[cube]['retry_ms']]
    if invalid:
        ap.error('Open P18 results need higher retry budget; never repeat same budget')
    tasks=[cube for cube in unknown if cube not in p18 or
           'unknown' in p18[cube]['child_statuses']]
    first,later,mask,target=read_original(ns.endian,ns.order)
    totals={
        'p16_input_cubes':len(p16),'p16_unknown_cubes':len(unknown),
        'p18_prior_completed':len(p18),
        'selected_for_refinement':min(len(tasks),ns.limit),
        'processed':0,'parent_exactly_closed':0,'child_unsat':0,
        'child_unknown':0,'sat_states':0,'complete_coupon_checks':0,
        'commitment_hits':0,'later_replay_hits':0,
    }
    t0=time.monotonic()
    for cube in tasks[:ns.limit]:
        states,terms=refine_parent(first,cube,ns.timeout_ms,ns.retry_ms)
        if cube in p18:
            # Previously recovered states survive an incomplete earlier pass.
            states.update((int(s[:16],16),int(s[16:],16))
                          for s in p18[cube]['states'])
        totals['processed']+=1
        totals['parent_exactly_closed']+=int('unknown' not in terms)
        totals['child_unsat']+=terms.count('unsat')
        totals['child_unknown']+=terms.count('unknown')
        totals['sat_states']+=len(states)
        found=[]
        for state in states:
            counts,hits=assess_state(state,mask,target,ns.endian,ns.order,
                                      ns.max_pre_packets,ns.max_later_packets,later)
            totals['complete_coupon_checks']+=counts['candidates']
            totals['commitment_hits']+=counts['commit_hits']
            totals['later_replay_hits']+=counts['replay_views']
            found.extend(hits)
        # Original accepted components must be escrowed BEFORE sealing the cube.
        escrow_hits(hit,found)
        row={
            'schema':SCHEMA,'source_sha256':SRC_SHA,
            'p16_cache_sha256':input_sha,'layout':layout,
            'p16_bucket':cube,'child_positions':[8,9],
            'child_statuses':terms,'timeout_ms':ns.timeout_ms,
            'retry_ms':ns.retry_ms,
            'states':[f'{a:016x}{b:016x}' for a,b in sorted(states)],
            'commit_hits':len(found),
            'reducer_max_pre_packets':ns.max_pre_packets,
            'reducer_max_later_packets':ns.max_later_packets,
        }
        append_private(out,row)
    print('AGGREGATE_ONLY '+json.dumps({
        'method':SCHEMA,'original_source_or_state_exposed':False,
        'layout':layout,'p16_whole_domain_coverage':len(p16)==65536,
        'all_open_P16_addressed':len(tasks)<=ns.limit,
        'elapsed_s':round(time.monotonic()-t0,2),
        'counts':totals},sort_keys=True),flush=True)


if __name__=='__main__':
    main()
