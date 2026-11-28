#!/usr/bin/env python3
"""Conditional K04 later-first little/BA exact P20 UNKNOWN -> P22/P24/P26 rescue.

The initial-source view is intact REQUESTED3 only. Correctly closure-preserving
refinement partitions each open P20 state cube by two further initial-a bits,
recursively through P26. Every SAT state is evaluated through all 177 complete
original-style K04 commitment windows before any earlier holdout. All historical
state/hits live only in owner-private atomic files; public output is aggregate.
No public CI / PDFs / ACK2 source fit. Mechanism adapted from Agent4's P22 work.
"""
import argparse,hashlib,json,os,random,time
from pathlib import Path
import k04_reverse_littleba_private as r
P20=r.P16+(8,9,10,11)
LAYERS=((12,13),(14,15),(16,17))

def source_run(lo,count,folder,ms=350,retry_ms=700):
 if not (0<=lo<4096 and 1<=count<=4096-lo and 100<=ms<=retry_ms<=30000):raise ValueError('bad arguments')
 folder=r.private_directory(folder)
 later,_,mask,target=r.source();obs={0:later[0],1:later[1]}
 counts={'P20_unknown_selected':0,'P22_unsat':0,'P22_unknown':0,'P24_unsat':0,'P24_unknown':0,
         'P26_unsat':0,'P26_unknown':0,'sat_states':0,'coupon_windows':0,'original_K04_hits':0,
         'P20_unknown_fully_rescued':0,'P20_unknown_still_open':0}
 def refine(cube,positions,depth=0):
  bits=LAYERS[depth]; ps=positions+bits
  label='P'+str(len(ps)); closed=True
  for branch in range(4):
   idx=cube|(branch<<len(positions))
   path=folder/f'deep_{label}_cube_{idx:08d}.json'
   rec=None
   if path.exists():
    if path.is_symlink() or path.stat().st_mode&0o077:raise ValueError('Unsafe deep ledger')
    rec=json.loads(path.read_text())
    if rec['cube']!=idx or rec['stamp']!=r.stamp('little','ba',ps):raise ValueError('Incompatible deep cache')
   if rec is None or rec['terminal']=='unknown':
    anchor=sum(((idx>>j)&1)<<bit for j,bit in enumerate(ps))
    states,status=r.e.solve(obs,anchor,ps,ms,True)
    if status=='unknown' and retry_ms>ms:
     more,status=r.e.solve(obs,anchor,ps,retry_ms,True)
     states=list(set(states).union(more))
    oldstates=[(int(a,16),int(b,16)) for a,b in rec.get('states',[])] if rec else []
    states=sorted(set(states).union(oldstates))
    for state in states:
     for offset,component in r.full_hits(state,mask,target,'little','ba'):
      r.private_coupon(folder/'K04_ORIGINAL_HASH_HIT.json',offset,component,'K04')
      counts['original_K04_hits']+=1
     counts['coupon_windows']+=177
    rec={'cube':idx,'stamp':r.stamp('little','ba',ps),'terminal':status,
         'states':[[f'{a:016X}',f'{b:016X}'] for a,b in states]}
    r.atomic(path,rec)
   counts['sat_states']+=len(rec['states'])
   counts[label+'_'+rec['terminal']]+=1
   if rec['terminal']=='unknown':
    if depth+1<len(LAYERS):
     if not refine(idx,ps,depth+1):closed=False
    else:closed=False
  return closed
 start=time.monotonic()
 for parent in range(lo,lo+count):
  for child in range(16):
   for sub in range(16):
    idx=parent|(child<<12)|(sub<<16)
    p=folder/f'p20_cube_{idx:07d}.json'
    if not p.exists():continue
    if p.is_symlink() or p.stat().st_mode&0o077:raise ValueError('Unsafe P20 input')
    rec=json.loads(p.read_text())
    if rec['cube']!=idx or rec['stamp']!=r.stamp('little','ba',P20):raise ValueError('Incorrect P20 source/geometry')
    if rec['terminal']=='unknown':
     counts['P20_unknown_selected']+=1
     if refine(idx,P20):counts['P20_unknown_fully_rescued']+=1
     else:counts['P20_unknown_still_open']+=1
  print('SOURCE_SAFE_AGGREGATE',json.dumps({'parents':[lo,parent+1],
        'elapsed_s':round(time.monotonic()-start,1),'values_printed':False,'counts':counts},sort_keys=True),flush=True)
 return counts

def synthetic():
 for seed in range(86200,86208):
  rng=random.Random(seed);s=(rng.getrandbits(64),rng.getrandbits(64))
  p=P20+LAYERS[0]
  fixed=sum(((s[0]>>bit)&1)<<bit for bit in p)
  states,status=r.e.solve(dict(enumerate(r.e.stream(*s,2))),fixed,p,3000,True)
  assert s in states and status in ('unsat','unknown')
 print({'synthetic_only':True,'P22_exact_planted_complete_states':8})

if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__)
 a.add_argument('--synthetic',action='store_true');a.add_argument('--private-dir',type=Path)
 a.add_argument('--parent-start',type=int,default=0);a.add_argument('--parent-count',type=int,default=16)
 a.add_argument('--timeout-ms',type=int,default=350);a.add_argument('--retry-ms',type=int,default=700)
 p=a.parse_args()
 if p.synthetic:synthetic()
 else:
  if not p.private_dir:a.error('Private directory required')
  source_run(p.parent_start,p.parent_count,p.private_dir,p.timeout_ms,p.retry_ms)
