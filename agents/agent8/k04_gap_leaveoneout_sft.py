"""Optimistic fullword gap donor sensitivity: leave-one-routine-gap-out controls.

Requires the exact Agent49 p951 model. Source-only, physical row129 withheld.
"""
import importlib.util
import sys
import time
from pathlib import Path
ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'
spec=importlib.util.spec_from_file_location('h17p951',Path(__file__).resolve().parents[1]/'agent49'/'k04_p951_symbolic_basis.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def put(r,v):
 while v:
  k=v.bit_length()-1
  if k not in r:r[k]=v;return 1
  v^=r[k]
 return 0

def main():
 b,s=m.source(ROOT)
 basis={k:v for k,(v,_) in b.rows.items()}
 targets=[x for i in range(951,955) for x in m.get(s,i)]
 intervals=[list(range(m.STARTS[i]+4,m.STARTS[i+1])) for i in range(127)]
 assert sum(map(len,intervals))==434
 vectors={p:m.temper(m.get(s,p)) for interval in intervals for p in interval}
 start=int(sys.argv[2]) if len(sys.argv)>2 else 0
 stop=int(sys.argv[3]) if len(sys.argv)>3 else 127
 timer=time.perf_counter()
 for missing in range(start,stop):
  r=basis.copy()
  for i,interval in enumerate(intervals):
   if i==missing:continue
   for p in interval:
    for bit in vectors[p]:put(r,bit)
  joint=r.copy()
  remain=sum(put(joint,v) for v in targets)
  print('DROP_GAP',missing,'words',len(intervals[missing]),'selected_remaining',remain,'source_gain',len(r)-len(basis),flush=True)
 print('PERF',stop-start,time.perf_counter()-timer,flush=True)

if __name__=='__main__':main()
