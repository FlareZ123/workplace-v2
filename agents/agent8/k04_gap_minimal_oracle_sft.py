"""Find inclusion-minimal sets of original routine printer gaps whose hypothetically
full native MT outputs determine the selected 16-byte K04 coupon under p951.
No actual gap output data is supplied. This is algebraic observability only.
"""
import importlib.util
import sys
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
 basis, stream = m.source(ROOT)
 base={p:v for p,(v,_) in basis.rows.items()}
 target=[v for i in range(951,955) for v in m.get(stream,i)]
 groups=[]
 for i in range(127):
  gap=list(range(m.STARTS[i]+4,m.STARTS[i+1]))
  groups.append((gap,[v for p in gap for v in m.get(stream,p)]))
 assert sum(len(x[0]) for x in groups)==434
 def dimension(keep):
  rows=base.copy()
  for index in sorted(keep):
   for vector in groups[index][1]:put(rows,vector)
  test=rows.copy()
  return sum(put(test,v) for v in target),len(rows)-len(base)
 assert dimension(set(range(127)))[0]==0
 assert dimension(set())[0]==128
 for order in (list(range(127)),list(reversed(range(127)))):
  keep=set(range(127))
  for i in order:
   trial=keep-{i}
   d,_=dimension(trial)
   if d==0:keep=trial
  assert dimension(keep)[0]==0
  essential={i:dimension(keep-{i})[0] for i in sorted(keep)}
  assert all(v>0 for v in essential.values())
  print('MINIMAL', 'ascending' if order[0]==0 else 'descending',
        'gaps',sorted(keep),'native_words',sum(len(groups[i][0]) for i in keep),
        'rank_gain',dimension(keep)[1],'remove_one_free_dims',essential,flush=True)
  for i in sorted(keep):
   print('GAP',i,'pos',groups[i][0][0],groups[i][0][-1],
        'routine_print_jobs',f'PS-261003-{300+i:04d}',f'PS-261003-{301+i:04d}',flush=True)

if __name__=='__main__':main()
