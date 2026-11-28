#!/usr/bin/env python3
"""Source-private exact adaptive xoroshiro128++ later-first P12 -> P16 -> P20 -> P24 -> P28.

Original REQUESTED3 intact packet is the only fitted source; copied ACK2 is
never loaded. Exhaustively enumerate every child of a timed-out subcube.
Every SAT model is reduced to ALL 18 complete backward coupon windows and
checked against unchanged K04 acceptance before any optional chronology test.
No SAT model or candidate is printed. UNKNOWN is never misreported UNSAT.
Historical mode disallowed in public CI; accepted candidates escrow 0600.
"""
from __future__ import annotations
import argparse,hashlib,multiprocessing as mp,os,random,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from agents.agent15 import k04_laterfirst_p16_p20_source_local as k

P24=k.P20+(12,13,14,15)
P28=P24+(16,17,18,19)

def child(job):
 parent,c,first,mask,target,endian,order,ms=job
 cube=parent|(c<<12)
 states,status=k.exact_states(first,cube,ms,positions=k.P16)
 totals=dict(p16=1,p20=0,p24=0,p28=0,unresolved=0,
             p20_unknown=0,p24_unknown=0,p28_unknown=0,
             models=0,checks=0,hits=0)
 if status=='unknown':
  allmodels=set(states);p20status=[]
  for j in range(16):
   c20=cube|(j<<16)
   more,terminal=k.exact_states(first,c20,ms,positions=k.P20)
   totals['p20']+=1;allmodels.update(more)
   if terminal=='unknown':
    submodels=set(more);statuses=[]
    for sub in range(16):
     c24=c20|(sub<<20)
     got,st=k.exact_states(first,c24,ms,positions=P24)
     totals['p24']+=1;submodels.update(got)
     if st=='unknown':
      deepmodels=set(got);deepstatuses=[]
      for branch in range(16):
       extra,deep=k.exact_states(first,c24|(branch<<24),ms,positions=P28)
       totals['p28']+=1;totals['p28_unknown']+=int(deep=='unknown')
       deepmodels.update(extra);deepstatuses.append(deep)
      submodels.update(deepmodels)
      st='unsat' if all(x=='unsat' for x in deepstatuses) else 'unknown'
     totals['p24_unknown']+=int(st=='unknown')
     statuses.append(st)
    allmodels.update(submodels)
    terminal='unsat' if all(x=='unsat' for x in statuses) else 'unknown'
   totals['p20_unknown']+=int(terminal=='unknown')
   p20status.append(terminal)
  states=list(allmodels)
  status='unsat' if all(x=='unsat' for x in p20status) else 'unknown'
 totals['unresolved']=int(status=='unknown')
 totals['models']=len(states)
 accepted=[]
 for state in states:
  checks,hits=k.check_state(state,mask,target,endian,order)
  totals['checks']+=checks;totals['hits']+=len(hits)
  accepted.extend(hits)
 return c,totals,accepted

def scan_parent(parent,first,mask,target,endian,order,ms,workers,escrow):
 total=dict(children=0,closed=0,unknown=0,models=0,p16=0,p20=0,p24=0,p28=0,
            p20_unknown=0,p24_unknown=0,p28_unknown=0,checks=0,hits=0)
 with mp.Pool(workers) as pool:
  jobs=((parent,c,first,mask,target,endian,order,ms) for c in range(16))
  for c,s,hits in pool.imap_unordered(child,jobs,chunksize=1):
   total['children']+=1;total['closed']+=int(s['unresolved']==0)
   total['unknown']+=s['unresolved']
   for attr in ('models','p16','p20','p24','p28',
                'p20_unknown','p24_unknown','p28_unknown','checks','hits'):
    total[attr]+=s[attr]
   if hits and escrow is not None:
    fd=os.open(escrow,os.O_WRONLY|os.O_APPEND|os.O_CREAT|getattr(os,'O_NOFOLLOW',0),0o600)
    with os.fdopen(fd,'a') as f:
     os.fchmod(f.fileno(),0o600)
     for v in hits:f.write(v.hex().upper()+'\n')
     f.flush();os.fsync(f.fileno())
 return total

def synthetic(ms=350):
 rng=random.Random(20261128)
 original=rng.getrandbits(64),rng.getrandbits(64)
 first=k.firstpair(*original);mask=rng.randbytes(16)
 parent=sum(((original[0]>>p)&1)<<j for j,p in enumerate(k.P12))
 earlier=k.earlier_words(*original)
 coupon=k.pack((earlier[7],earlier[6]),'big','ab')
 target=hashlib.sha256(bytes(x^y for x,y in zip(coupon,mask))).hexdigest()
 for positions in (k.P20,P24,P28):
  cube=sum(((original[0]>>p)&1)<<j for j,p in enumerate(positions))
  states,status=k.exact_states(first,cube,1000,positions=positions)
  assert original in states and status=='unsat'
 totals=scan_parent(parent,first,mask,target,'big','ab',ms,4,None)
 assert totals['hits']==1 and totals['models']>=1
 print({'synthetic_only':True,'planted_complete_commitment_hit':True,
        'P20_P24_P28_planted_exact':True,
        'children_exhausted':totals['closed'],
        'open_children':totals['unknown']},flush=True)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--synthetic',action='store_true')
 p.add_argument('--resources-root',type=Path,default=ROOT/'resources')
 p.add_argument('--parent',type=int,default=1026)
 p.add_argument('--endian',choices=('big','little'),default='big')
 p.add_argument('--order',choices=('ab','ba'),default='ab')
 p.add_argument('--timeout-ms',type=int,default=350)
 p.add_argument('--workers',type=int,default=4)
 p.add_argument('--local-hit-escrow',type=Path)
 args=p.parse_args()
 assert 0<=args.parent<4096 and 100<=args.timeout_ms<=10000 and 1<=args.workers<=4
 if args.synthetic:return synthetic(args.timeout_ms)
 if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
  p.error('Original-source mode forbidden in public CI')
 if args.local_hit_escrow is None:p.error('Private original-hit escrow required')
 escrow=args.local_hit_escrow.resolve()
 if escrow==ROOT or ROOT in escrow.parents or not escrow.parent.is_dir():
  p.error('Escrow must be in existing directory outside repository')
 first,mask,target=k.source(args.resources_root,args.endian,args.order)
 start=time.monotonic()
 t=scan_parent(args.parent,first,mask,target,args.endian,args.order,
               args.timeout_ms,args.workers,escrow)
 print({'aggregate_only':True,'source':'intact attempt3 only',
        'copied_ACK2_withheld':True,'model':'conditional xoroshiro128++ later-first',
        'view':args.endian+'/'+args.order,'parent':args.parent,
        'elapsed_s':round(time.monotonic()-start,2),**t},flush=True)
if __name__=='__main__':main()
