#!/usr/bin/env python3
"""Audit exact disjoint P12→P16→P20→P22/P24/P26 private K04 source ledgers.

Does not load original archive, print source-derived states, or infer UNSAT from
timeouts/missing cache entries. Produces a method-only exhaustive-domain receipt
for given source/circuit/serializer fingerprints and expected cube counts.
"""
import argparse,json
from pathlib import Path
import k04_reverse_littleba_private as r
P20=r.P16+(8,9,10,11)
LAYERS=((12,13),(14,15),(16,17))

def audit(folder,start,count):
 folder=r.private_directory(folder)
 if not(0<=start<4096 and 1<=count<=4096-start):raise ValueError('Invalid parent scope')
 d={'parent_total':count,'source_empty_parents':0,'enumerated_with_models_parents':0,
    'unresolved_parents':0,'P16_visited':0,'P16_unsat':0,'P16_unknown':0,
    'P20_visited':0,'P20_unsat':0,'P20_unknown':0,
    'P22_visited':0,'P22_unsat':0,'P22_unknown':0,
    'P24_visited':0,'P24_unsat':0,'P24_unknown':0,
    'P26_visited':0,'P26_unsat':0,'P26_unknown':0,
    'fully_enumerated_source_states':0,'missing_subcubes':0,'unresolved_terminal_timeout':0}
 def validated(path,cube,positions):
  if not path.exists():d['missing_subcubes']+=1;return None
  if path.is_symlink() or path.stat().st_mode&0o077:raise ValueError('Unsafe ledger file')
  row=json.loads(path.read_text())
  if row.get('cube')!=cube or row.get('stamp')!=r.stamp('little','ba',positions):
   raise ValueError('Cache geometry/source/circuit mismatch: '+path.name)
  if row.get('terminal') not in ('unsat','unknown'):raise ValueError('Invalid terminal status')
  d['fully_enumerated_source_states']+=len(row['states'])
  return row
 def descendants(cube,positions,depth):
  ps=positions+LAYERS[depth]
  tag='P'+str(len(ps))
  complete=True
  for branch in range(4):
   idx=cube|(branch<<len(positions))
   row=validated(folder/f'deep_{tag}_cube_{idx:08d}.json',idx,ps)
   if row is None:complete=False;continue
   d[tag+'_visited']+=1;d[tag+'_'+row['terminal']]+=1
   if row['terminal']=='unknown':
    if depth==len(LAYERS)-1:
     d['unresolved_terminal_timeout']+=1;complete=False
    else:
     if not descendants(idx,ps,depth+1):complete=False
  return complete
 for parent in range(start,start+count):
  complete=True
  states_before=d['fully_enumerated_source_states']
  for child in range(16):
   idx=parent|(child<<12)
   row=validated(folder/f'cube_{idx:05d}.json',idx,r.P16)
   if row is None:complete=False;continue
   d['P16_visited']+=1;d['P16_'+row['terminal']]+=1
   if row['terminal']=='unknown':
    for sub in range(16):
     gidx=idx|(sub<<16)
     subrow=validated(folder/f'p20_cube_{gidx:07d}.json',gidx,P20)
     if subrow is None:complete=False;continue
     d['P20_visited']+=1;d['P20_'+subrow['terminal']]+=1
     if subrow['terminal']=='unknown':
      if not descendants(gidx,P20,0):complete=False
  if not complete:d['unresolved_parents']+=1
  elif d['fully_enumerated_source_states']>states_before:d['enumerated_with_models_parents']+=1
  else:d['source_empty_parents']+=1
 assert d['source_empty_parents']+d['enumerated_with_models_parents']+d['unresolved_parents']==count
 print(json.dumps({'method':'exact P12/P16/P20/P22-P26 source state-domain tree',
                   'view':'later-first little/BA',
                   'range':[start,start+count],
                   'source_or_state_values_printed':False,
                   'complete_original_K04_hit_escrow_exists':(folder/'K04_ORIGINAL_HASH_HIT.json').exists(),
                   'counts':d},sort_keys=True))
 return d

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--private-dir',type=Path,required=True)
 p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=16)
 a=p.parse_args();audit(a.private_dir,a.start,a.count)
