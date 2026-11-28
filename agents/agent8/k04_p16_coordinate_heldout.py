#!/usr/bin/env python3
"""Source-free positive-recovery liveness control for alternative exact P16 anchors."""
import importlib.util,random,time,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('e',Path(__file__).with_name('k04_pruned_native.py'))
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
P12=(0,1,2,3,22,23,24,25,45,46,47,48)
GROUPS=((4,5,6,7),(26,27,28,29))
base_seeds=list(range(50000,50128))
result=[]
for group in GROUPS:
 stats={'seeded':0,'exact_true_states':0,'SAT_states':0,'terminal_unsat_with_models':0,'terminal_unsat_empty':0,'terminal_unknown':0,'timeouts_ms':[350,700]}
 start=time.monotonic()
 for seed in base_seeds:
  rng=random.Random(seed);a,b=rng.getrandbits(64),rng.getrandbits(64)
  y=dict(enumerate(e.stream(a,b,2)))
  pos=P12+group
  st=None
  for ms in (350,700):
   states,st=e.solve(y,a,pos,ms,True)
   if st!='unknown' or states:break
  stats['seeded']+=1;stats['SAT_states']+=len(states)
  stats['exact_true_states']+=int((a,b) in states)
  stats['terminal_unsat_with_models' if st=='unsat' and states else 'terminal_unsat_empty' if st=='unsat' else 'terminal_unknown']+=1
 assert not stats['terminal_unsat_empty'], 'True planted anchor cannot be exhausted UNSAT without its state'
 stats['elapsed_s']=round(time.monotonic()-start,2)
 result.append((group,stats))
 print(json.dumps({'extra_bits':group,'source_free':True,'stats':stats},sort_keys=True),flush=True)
