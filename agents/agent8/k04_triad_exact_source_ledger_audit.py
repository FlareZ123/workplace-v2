#!/usr/bin/env python3
"""Read-only, fail-closed source-private K04 reverse-triad P12/P16/P20 proof auditor.

Audits all 4096 disjoint P12 parent cubes, P16 refinements of P12 UNKNOWN,
and P20 refinements of P16 UNKNOWN. A branch is closed only if every
disjoint descendant reaches terminal UNSAT after all SAT states are blocked.
UNKNOWN/missing child is OPEN; an accepted full SHA256 candidate is counted,
escrowed elsewhere by the runner, and never printed. Validates every cached
state against original three 64-bit source words, original unmodified K04
full-component hash, and earlier REQUESTED1 holdout. Supports both the
Agent8 original local cache convention and public reusable runner naming.
Do not run historical original source in GitHub Actions or commit the cache.
"""
from __future__ import annotations
import argparse,hashlib,json,os,random,re
from pathlib import Path
P12=(0,1,2,3,22,23,24,25,45,46,47,48)
P16=P12+(4,5,6,7)
P20=P16+(8,9,10,11)
MASK=(1<<64)-1
PINS={'evidence/print/spool-reconstruction.log':'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
'evidence/recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
'acceptance.json':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'}
def rol(x,n):return ((x<<n)|(x>>(64-n)))&MASK
def ror(x,n):return ((x>>n)|(x<<(64-n)))&MASK
def step(s):
 a,b=s;t=a^b
 return rol(a,49)^t^((t<<21)&MASK),rol(t,28)
def inverse(s):
 a,b=s;t=ror(b,28);v=ror(a^t^((t<<21)&MASK),49)
 return v,v^t
def stream(state,n):
 outputs=[]
 for _ in range(n):
  a,b=state;outputs.append((rol((a+b)&MASK,17)+a)&MASK)
  state=step(state)
 return outputs
def state_word(x):return int(x,16) if isinstance(x,str) else int(x)
def anchor(s,positions):return sum(((s>>bit)&1)<<i for i,bit in enumerate(positions))
def load_source(root,endian):
 for rel,dig in PINS.items():
  if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=dig:
   raise ValueError('Original source integrity pin failed '+rel)
 lines=(root/'evidence/print/spool-reconstruction.log').read_text().splitlines()
 found=[line for line in lines if 'JOB=PS-261003-0417 ' in line and 'CLASS=RECOVER ' in line]
 if len(found)!=3:raise ValueError('Selected job no longer uniquely three RECOVER records')
 rows={}
 for line in found:
  att=int(re.search(r'ATTEMPT=(\d+)',line)[1])
  rows[att]=bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})',line)[1])
 if set(rows)!={1,2,3}:raise ValueError('Incomplete source attempts')
 word=lambda block:[int.from_bytes(block[j:j+8],endian) for j in (0,8)]
 obs=[int.from_bytes(rows[2][8:],endian)]+word(rows[3])
 first=word(rows[1])
 mask=bytes.fromhex(json.loads((root/'evidence/recovery-routing.json').read_text())['K04']['masked_component'])
 target=json.loads((root/'acceptance.json').read_text())['slot_sha256']['K04']
 assert len(mask)==16 and len(target)==64
 return obs,first,mask,target
def readrec(folder,endian,level,index):
 suffix=(f'{index:04d}' if level==12 else f'{index:05d}' if level==16 else f'{index:06d}')
 candidates=(folder/f'{endian}_triad_p{level}_{suffix}.json',
             folder/f'triad_{endian}_p{level}_{suffix}.json')
 present=[p for p in candidates if p.exists()]
 if len(present)>1:raise ValueError('Duplicate competing original-state records')
 if not present:return None
 p=present[0]
 if not p.is_file() or p.is_symlink() or p.stat().st_mode&0o077:
  raise ValueError('Insecure source-state record')
 r=json.loads(p.read_text())
 recorded_id=r.get('parent',r.get('index',r.get('cube',r.get('id'))))
 recorded_view=r.get('view',r.get('endian'))
 recorded_tag=r.get('tag',r.get('source_tag'))
 expected_tag='tail8-v1' if level==12 else f'triad-p{level}-v1'
 if recorded_id!=index or recorded_view!=endian or recorded_tag!=expected_tag:
  raise ValueError('Wrong source, parent ID or solver-depth checkpoint')
 if r['status'] not in ('unsat','unknown'):
  raise ValueError('Unsound solver terminal status')
 return r
def check_states(r,index,positions,obs,first,mask,target,endian):
 states=[tuple(state_word(v) for v in pair) for pair in r['states']]
 hits=0;holdout=0
 for state in states:
  if len(state)!=2 or any(v<0 or v>MASK for v in state):
   raise ValueError('Non-width-128 state')
  if anchor(state[0],positions)!=index:
   raise ValueError('Source-state model outside declared exact disjoint subcube')
  if stream(state,3)!=obs:
   raise ValueError('Stored original-compatible state does not replay source')
  start=state
  for _ in range(3):start=inverse(start)
  seq=stream(start,6)
  if seq[3:]!=obs:raise ValueError('Reverse transition replay failed')
  coupon=seq[2].to_bytes(8,endian)+seq[3].to_bytes(8,endian)
  component=bytes(a^b for a,b in zip(coupon,mask))
  hits+=int(hashlib.sha256(component).hexdigest()==target)
  holdout+=int(seq[:2]==first)
 if hits!=r.get('original_hits',r.get('original_hit',0)):
  raise ValueError('Full historical original K04 hit count mismatch')
 if holdout!=r.get('earlier_holdout_replays',
                  r.get('firstpair_replay',r.get('holdout',0))):
  raise ValueError('Independent original REQUESTED1 replay count mismatch')
 return len(states),hits,holdout
def audit(root,folder,view,start,count):
 if os.environ.get('GITHUB_ACTIONS') or os.environ.get('GITHUB_REPOSITORY'):
  raise RuntimeError('Original-source audit is local-only; no GitHub Actions')
 if not folder.is_dir() or folder.is_symlink() or folder.stat().st_mode&0o077:
  raise ValueError('Private cache directory must be nonsymlink mode0700')
 if folder.resolve()==root.resolve() or root.resolve() in folder.resolve().parents:
  raise ValueError('Private source-state caches forbidden inside repository')
 obs,first,mask,target=load_source(root,view)
 c={x:0 for x in ('P12_requested','P12_recorded','P12_terminal_UNSAT','P12_terminal_UNKNOWN',
   'P16_recorded','P16_terminal_UNSAT','P16_terminal_UNKNOWN','P16_missing',
   'P20_recorded','P20_terminal_UNSAT','P20_terminal_UNKNOWN','P20_missing',
   'P16_unknown_fully_refined','P12_closed_empty','P12_closed_with_state',
   'P12_still_open','P12_missing','source_states','original_K04_hits',
   'earlier_REQUESTED1_replays')}
 c['P12_requested']=count
 for parent in range(start,start+count):
  p=readrec(folder,view,12,parent)
  if p is None:c['P12_missing']+=1;continue
  c['P12_recorded']+=1
  size,hits,holdout=check_states(p,parent,P12,obs,first,mask,target,view)
  c['source_states']+=size;c['original_K04_hits']+=hits;c['earlier_REQUESTED1_replays']+=holdout
  c['P12_terminal_UNSAT' if p['status']=='unsat' else 'P12_terminal_UNKNOWN']+=1
  if p['status']=='unsat':
   c['P12_closed_with_state' if size else 'P12_closed_empty']+=1;continue
  open_parent=False;fitted_states=size
  for child in range(16):
   cube=parent|(child<<12);r=readrec(folder,view,16,cube)
   if r is None:c['P16_missing']+=1;open_parent=True;continue
   c['P16_recorded']+=1
   size,hits,holdout=check_states(r,cube,P16,obs,first,mask,target,view)
   fitted_states+=size;c['source_states']+=size
   c['original_K04_hits']+=hits;c['earlier_REQUESTED1_replays']+=holdout
   c['P16_terminal_UNSAT' if r['status']=='unsat' else 'P16_terminal_UNKNOWN']+=1
   if r['status']=='unknown':
    child_complete=True
    for ext in range(16):
     grand=cube|(ext<<16);g=readrec(folder,view,20,grand)
     if g is None:c['P20_missing']+=1;child_complete=False;continue
     c['P20_recorded']+=1
     size,hits,holdout=check_states(g,grand,P20,obs,first,mask,target,view)
     fitted_states+=size;c['source_states']+=size
     c['original_K04_hits']+=hits;c['earlier_REQUESTED1_replays']+=holdout
     c['P20_terminal_UNSAT' if g['status']=='unsat' else 'P20_terminal_UNKNOWN']+=1
     if g['status']=='unknown':child_complete=False
    if child_complete:c['P16_unknown_fully_refined']+=1
    else:open_parent=True
  if open_parent:c['P12_still_open']+=1
  else:c['P12_closed_with_state' if fitted_states else 'P12_closed_empty']+=1
 assert c['P12_closed_empty']+c['P12_closed_with_state']+c['P12_still_open']+c['P12_missing']==count
 return c
def synthetic():
 r=random.Random(202611281238)
 for _ in range(32):
  s=(r.getrandbits(64),r.getrandbits(64))
  assert inverse(step(s))==s
  assert step(inverse(s))==s
  assert stream(s,3)==stream(inverse(step(s)),3)
  for pos in (P12,P16,P20):
   assert anchor(s[0],pos)==sum(((s[0]>>j)&1)<<i for i,j in enumerate(pos))
 print({'source_free':True,'roundtrip_state_positive_controls':32,
        'all_partition_depth_membership_controls':96},flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--synthetic',action='store_true')
 p.add_argument('--resources-root',type=Path)
 p.add_argument('--private-dir',type=Path)
 p.add_argument('--endian',choices=('big','little'),default='big')
 p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=4096)
 a=p.parse_args()
 synthetic()
 if not a.synthetic:
  if not a.resources_root or not a.private_dir or not (0<=a.start and a.count>0 and a.start+a.count<=4096):
   p.error('Original audit requires resources, private-dir and valid P12 interval')
  print('SOURCE_SAFE_EXACT_PROOF_LEDGER',json.dumps(
       {'source_view':a.endian,'original_source_or_state_values_printed':False,
        'range':[a.start,a.start+a.count],
        'counts':audit(a.resources_root,a.private_dir,a.endian,a.start,a.count)},
       sort_keys=True),flush=True)
