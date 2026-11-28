#!/usr/bin/env python3
"""Source-private incremental P16 producer with complete original commitment gate.

Push/pop 16 child cubes of each P12 parent in ONE exact solver context.
Store all recovered SAT states, terminal UNSAT and UNKNOWN in private 0600
out-of-repo cache. For every SAT state test complete unchanged K04 commitment
BEFORE optional REQUESTED3 replay. Selected ACK2 is never a fitting input.
CI is explicitly forbidden for original-source mode. Supports focusing
previously inconclusive 16-child parent groups and durable resume.
"""
from __future__ import annotations
import argparse,json,multiprocessing as mp,os,time
from pathlib import Path
from agents.agent50.k04_xoropp_p16_incremental_synthetic import solve_parent
from agents.agent50.k04_xoropp_p16_private_ledger import (
    private_path,append_private,read_ledger,SRC_SHA,ANCHOR)
from agents.agent7.k04_xoropp_p16_subcube_source_local import read_original
from agents.agent7.k04_xoropp_byte_slip_reducer import assess_state,escrow_hits

SCHEMA='p16-shared-context-parent-v1'


def load_saved(path,layout):
    saved={}
    if not path.exists():return saved
    for line in path.read_text().splitlines():
        row=json.loads(line)
        if (row.get('schema')!=SCHEMA or row.get('source_sha256')!=SRC_SHA or
            row.get('layout')!=layout or row.get('anchor_positions')!=ANCHOR or
            not isinstance(row.get('parent'),int) or row['parent'] not in range(4096)):
            raise ValueError('Incremental source cache fingerprint mismatch')
        parent=row['parent']
        if parent in saved:
            old=saved[parent]
            if old['terminal_unknown']==0:
                raise ValueError('Decided parent must never be re-run')
            if row['retry_ms']<=old['retry_ms']:
                raise ValueError('Retry budget must strictly increase')
        saved[parent]=row
    return saved


def source_job(job):
    parent,first,later,mask,target,endian,order,ms,retry_ms,cap,pre,lag=job
    results=solve_parent(first,parent,ms,retry_ms,cap)
    rows=[]
    counters={'states':0,'coupon_checks':0,'commit_hits':0,
              'later_replay_matches':0}
    verified=[]
    for sub,status,states,retried in results:
        hits=[]
        for state in states:
            counts,found=assess_state(state,mask,target,endian,order,
                                      pre,lag,later)
            counters['states']+=1
            counters['coupon_checks']+=counts['candidates']
            counters['commit_hits']+=counts['commit_hits']
            counters['later_replay_matches']+=counts['replay_views']
            hits.extend(found)
        verified.extend(hits)
        rows.append({'subcube':sub,'terminal':status,'retried':bool(retried),
                     'states':[f'{a:016x}{b:016x}' for a,b in sorted(states)]})
    return parent,rows,counters,verified


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--start-parent',type=int,default=0)
    ap.add_argument('--parent-count',type=int,default=16)
    ap.add_argument('--focus-unknown-ledger')
    ap.add_argument('--min-unknown',type=int,default=1)
    ap.add_argument('--endian',choices=('big','little'),default='big')
    ap.add_argument('--order',choices=('ab','ba'),default='ab')
    ap.add_argument('--timeout-ms',type=int,default=350)
    ap.add_argument('--retry-ms',type=int,default=700)
    ap.add_argument('--max-models',type=int,default=32)
    ap.add_argument('--max-pre-packets',type=int,default=8)
    ap.add_argument('--max-later-packets',type=int,default=8)
    ap.add_argument('--workers',type=int,default=2)
    ap.add_argument('--private-ledger',required=True)
    ap.add_argument('--hit-escrow',required=True)
    ns=ap.parse_args()
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        ap.error('Historical original-source work forbidden on public CI')
    if not (0<=ns.start_parent<4096 and
            1<=ns.parent_count<=4096-ns.start_parent and
            100<=ns.timeout_ms<=ns.retry_ms<=30000 and
            1<=ns.workers<=4 and 1<=ns.max_models<=1024 and
            0<=ns.max_pre_packets<=16 and
            0<=ns.max_later_packets<=16 and 1<=ns.min_unknown<=16):
        ap.error('Invalid bounded settings')
    root=Path(__file__).resolve().parents[2]
    output=private_path(ns.private_ledger,root,True)
    escrow=private_path(ns.hit_escrow,root,True)
    if output==escrow:ap.error('Cache and verified escrow must differ')
    layout=ns.endian+'/'+ns.order
    saved=load_saved(output,layout)
    parents=list(range(ns.start_parent,ns.start_parent+ns.parent_count))
    if ns.focus_unknown_ledger:
        focus=private_path(ns.focus_unknown_ledger,root,False)
        prior=read_ledger(focus,layout)
        unresolved={p:0 for p in parents}
        finished={p:0 for p in parents}
        for cube,row in prior.items():
            p=cube&4095
            if p in unresolved:
                finished[p]+=1
                unresolved[p]+=int(row['terminal']=='unknown')
        parents=[p for p in parents
                 if finished[p]==16 and unresolved[p]>=ns.min_unknown]
    active=[p for p in parents
            if p not in saved or saved[p]['terminal_unknown']>0]
    if any(p in saved and ns.retry_ms<=saved[p]['retry_ms']
           for p in active):
        ap.error('Previously UNKNOWN parent requires strictly higher retry budget')
    first,later,mask,target=read_original(ns.endian,ns.order)
    tasks=((p,first,later,mask,target,ns.endian,ns.order,
             ns.timeout_ms,ns.retry_ms,ns.max_models,
             ns.max_pre_packets,ns.max_later_packets) for p in active)
    tally={'eligible_parents':len(parents),
           'already_closed':len(parents)-len(active),
           'processed':0,'P16_terminal_UNSAT':0,
           'P16_terminal_UNKNOWN':0,'SAT_states':0,
           'original_full_coupon_checks':0,'commitment_hits':0,
           'later_retry_matches':0}
    start=time.monotonic()
    with mp.Pool(ns.workers) as pool:
        for parent,rows,counters,hits in pool.imap_unordered(source_job,tasks,chunksize=1):
            # Verified complete original components are escrowed before cache seal.
            escrow_hits(escrow,hits)
            statuses=[r['terminal'] for r in rows]
            row={'schema':SCHEMA,'source_sha256':SRC_SHA,'layout':layout,
                 'anchor_positions':ANCHOR,'parent':parent,
                 'first_timeout_ms':ns.timeout_ms,'retry_ms':ns.retry_ms,
                 'terminal_unsat':statuses.count('unsat'),
                 'terminal_unknown':statuses.count('unknown'),
                 'children':rows}
            append_private(output,row)
            tally['processed']+=1
            tally['P16_terminal_UNSAT']+=row['terminal_unsat']
            tally['P16_terminal_UNKNOWN']+=row['terminal_unknown']
            tally['SAT_states']+=counters['states']
            tally['original_full_coupon_checks']+=counters['coupon_checks']
            tally['commitment_hits']+=counters['commit_hits']
            tally['later_retry_matches']+=counters['later_replay_matches']
            if tally['processed']%8==0 or tally['processed']==len(active):
                print('AGGREGATE_ONLY '+json.dumps({
                    'method':SCHEMA,'layout':layout,
                    'original_source_or_state_exposed':False,
                    'elapsed_s':round(time.monotonic()-start,2),
                    'counts':tally},sort_keys=True),flush=True)


if __name__=='__main__':main()
