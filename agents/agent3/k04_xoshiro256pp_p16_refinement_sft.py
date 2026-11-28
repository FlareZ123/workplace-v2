#!/usr/bin/env python3
"""Exact P16 refinement of unknown c0 cubes in the conditional LABEL-s0 xoshiro256++ K04 inverse.
Synthetic-only by default. Historical mode is local-only, source-private and resumable.
Never infer a PRNG/physical-coupon link from these conditional calculations.
"""
import argparse,collections,hashlib,json,os,pathlib,random,time
from k04_xoshiro256pp_samejob_label_sft import stream,pack,unpack,invert,RR,MASK
from k04_xoshiro256pp_label_s0_12bit_cubes_sft import solve_bucket,raw_inputs,P12,safe_local

def children(a,b,d,y4,y5,parent,ms=800,max_models=8):
 for child in range(16):
  extra=tuple((4+j,(child>>j)&1) for j in range(4))
  yield child,solve_bucket((a,b,d,y4,y5,parent,ms,max_models,None,extra))

def synthetic():
 states=0;closed=0;checks=0;t0=time.monotonic()
 for seed in range(601,609):
  rng=random.Random(seed);s=tuple(rng.getrandbits(64) for _ in range(4));output=stream(s)
  parent=sum(((s[2]>>j)&1)<<k for k,j in enumerate(P12))
  results=list(children(s[0],s[1],s[3],output[4],output[5],parent))
  assert len(results)==16
  got=[c for _,z in results for c in z['states']]
  assert got==[s[2]],(seed,'no exact complete state')
  assert all(z['status']=='unsat' for _,z in results),(seed,'nonterminal cube')
  for c in got:
   assert stream((s[0],s[1],c,s[3]))==output
   mask=rng.randbytes(16)
   for start in range(2,20):
    y=stream((s[0],s[1],c,s[3]))
    predicted=bytes(x^m for x,m in zip(pack(y[start:start+2],'big',False),mask))
    original=bytes(x^m for x,m in zip(pack(output[start:start+2],'big',False),mask))
    assert hashlib.sha256(predicted).digest()==hashlib.sha256(original).digest()
    checks+=1
  states+=1;closed+=sum(z['status']=='unsat' for _,z in results)
 print({'source_free':True,'planted_complete_states':states,
        'terminal_unsat_children':closed,'complete_coupon_commitments':checks,
        'elapsed_s':round(time.monotonic()-t0,3),'historical_key_recovered':False})

def original(args):
 if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
  raise RuntimeError('Original K04 solver forbidden in public CI')
 source_sha,label,first,later,mask,target=raw_inputs(args.original_root)
 endian,wordorder=args.view.split('-');swap=wordorder=='ba'
 a,_=unpack(label,endian,swap);y0,y1=unpack(first,endian,swap)
 y4,y5=unpack(later,endian,swap);d=(RR((y0-a)&MASK,23)-a)&MASK
 roots,terminal=invert(a,y1);assert terminal=='unsat'
 coarse=safe_local(args.coarse_ledger)
 rows=[json.loads(line) for line in coarse.read_text().splitlines()]
 expected={'source_sha':source_sha,'solver':'xoshiro256pp-label-a-only-v1',
           'view':args.view,'positions':list(P12),
           'timeout_ms':args.coarse_timeout_ms,'version':1}
 assert rows[0]['header']==expected,'Refusing incompatible source/solver ledger'
 latest={}
 for row in rows[1:]:latest[(row['root'],row['bucket'])]=row
 targets=[]
 for root_index in range(len(roots)):
  for parent in range(args.start,min(args.start+args.count,4096)):
   row=latest.get((root_index,parent))
   if row is not None and row['status']=='unsat':continue
   targets.append((root_index,parent))
 refinement=safe_local(args.refinement_ledger)
 header={'source_sha':source_sha,'view':args.view,
         'solver':'xoshiro256pp-label-c0-P16-refinement-v1',
         'extra_positions':[4,5,6,7],
         'coarse_timeout_ms':args.coarse_timeout_ms,
         'timeout_ms':args.timeout_ms,'max_models':args.max_models}
 child_done={}
 if refinement.exists():
  with refinement.open() as f:
   for line in f:
    row=json.loads(line)
    if 'header' in row:assert row['header']==header
    else:child_done[(row['root'],row['bucket'],row['child'])]=row
 else:
  fd=os.open(refinement,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'w') as f:
   f.write(json.dumps({'header':header})+'\n');f.flush();os.fsync(f.fileno())
 escrow=safe_local(args.escrow)
 dispositions=collections.Counter();checks=0;hits=0;closed=0;processed=0
 t0=time.monotonic()
 for root_index,parent in targets:
  b=d^roots[root_index];statuses=[]
  for child in range(16):
   key=(root_index,parent,child)
   if key in child_done and child_done[key]['status']=='unsat':
    statuses.append('unsat');continue
   extra=tuple((4+j,(child>>j)&1) for j in range(4))
   result=solve_bucket((a,b,d,y4,y5,parent,args.timeout_ms,args.max_models,None,extra))
   if result['status']=='unknown' and args.retry_timeout_ms>args.timeout_ms:
    retry=solve_bucket((a,b,d,y4,y5,parent,args.retry_timeout_ms,args.max_models,None,extra))
    if retry['status']=='unsat':
     # A complete model-blocked retry supersedes the shorter partial scan.
     result=retry
    else:
     result={'status':retry['status'] if retry['status']!='unsat' else 'unsat',
             'states':list(dict.fromkeys(result['states']+retry['states']))}
   for candidate in result['states']:
    generated=stream((a,b,candidate,d))
    for start in range(2,20):
     component=bytes(x^y for x,y in zip(pack(generated[start:start+2],endian,swap),mask))
     checks+=1
     if hashlib.sha256(component).hexdigest()==target:
      fd=os.open(escrow,os.O_WRONLY|os.O_APPEND|os.O_CREAT|os.O_NOFOLLOW,0o600)
      with os.fdopen(fd,'a') as w:
       w.write(component.hex().upper()+'\n');w.flush();os.fsync(w.fileno())
      hits+=1
   rec={'root':root_index,'bucket':parent,'child':child,
        'status':result['status'],'retry_timeout_ms':args.retry_timeout_ms,
        'states':[f'{c:016x}' for c in result['states']]}
   fd=os.open(refinement,os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW)
   with os.fdopen(fd,'a') as f:
    f.write(json.dumps(rec)+'\n');f.flush();os.fsync(f.fileno())
   child_done[key]=rec;dispositions[result['status']]+=1
   statuses.append(result['status'])
  processed+=1;closed+=int(all(z=='unsat' for z in statuses))
  if processed%10==0:
   print({'source_private':True,'processed_parents':processed,
      'fully_closed_parents':closed,'new_child_dispositions':dict(dispositions),
      'complete_coupon_checks':checks,'original_K04_hits_escrowed':hits,
      'elapsed_s':round(time.monotonic()-t0,1)},flush=True)
 print({'source_private':True,'view':args.view,
        'coarse_candidate_parent_cubes':len(targets),
        'processed_parent_cubes':processed,'fully_closed_parent_cubes':closed,
        'new_child_statuses':dict(dispositions),'complete_coupon_checks':checks,
        'original_K04_hits_escrowed':hits,'unknown_or_unvisited_remain_open':True})

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--original-root',type=pathlib.Path)
 p.add_argument('--view',choices=('big-ab','big-ba','little-ab','little-ba'),default='big-ab')
 p.add_argument('--coarse-ledger',default='/mnt/data/h17_s0_bigab_3s_ledger.jsonl')
 p.add_argument('--refinement-ledger',default='/mnt/data/h17_s0_bigab_p16_ledger.jsonl')
 p.add_argument('--escrow',default='/mnt/data/h17_s0_bigab_p16_hits.txt')
 p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=4096)
 p.add_argument('--timeout-ms',type=int,default=800)
 p.add_argument('--retry-timeout-ms',type=int,default=4500)
 p.add_argument('--coarse-timeout-ms',type=int,default=3000)
 p.add_argument('--max-models',type=int,default=8)
 args=p.parse_args()
 assert 0<=args.start<4096 and 1<=args.count<=4096 and 100<=args.timeout_ms<=args.retry_timeout_ms<=30000 and 1<=args.max_models<=100
 if args.original_root:original(args)
 else:synthetic()
