"""Conditional oracle: even 44 genuine PTW signed and unsigned serials staged in early MT region."""
import sys, time, json, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'agent49'))
import k04_p951_symbolic_basis as M
ROOT=Path(__file__).resolve().parents[2]/'resources'
raw=(ROOT/'evidence/maintenance/seal-receipts.jsonl').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32'
assert len([json.loads(x) for x in raw.splitlines()])==44
basis,states=M.source(ROOT)
orig={p:v[0] for p,v in basis.rows.items()}
target=[v for p in range(951,955) for v in M.get(states,p)]
def add(d,x):
 while x:
  k=x.bit_length()-1
  if k in d:x^=d[k]
  else:d[k]=x;return 1
 return 0
starttime=time.monotonic();count=0;reduced=[];addmin=10**6;addmax=0
for pos in range(-1070,-799):
 for stride in range(1,9):
  if pos+43*stride>-400:continue
  d=orig.copy();n=0
  for stage in (pos+i*stride for i in range(44)):
   for w in M.get(states,stage):n+=add(d,w)
  q=sum(add(d,x) for x in target)
  count+=1;addmin=min(n,addmin);addmax=max(n,addmax)
  if q<128:reduced.append((q,pos,stride,n))
print('ORIGINAL_PRINTER_RANK',basis.rank,'44_SERIALLIKE_OBSERVED_EARLY_REGULAR_ORDERS',count,'GROWN_RANK_RANGE',(addmin,addmax),'K04_QUOTIENT_REDUCING_GEOMETRIES',len(reduced),'TOP',sorted(reduced)[:12]);assert count==2168 and len(reduced)==13 and {q for q,_,_,_ in reduced}=={127}
print('SECONDS',round(time.monotonic()-starttime,3))

planted=orig.copy()
for stage in range(951,955):
 for expr in M.get(states,stage):add(planted,expr)
assert sum(add(planted,x) for x in target)==0
print('PLANTED_DIRECT_STAGE_128BIT_RANK_POSITIVE_PASS')
