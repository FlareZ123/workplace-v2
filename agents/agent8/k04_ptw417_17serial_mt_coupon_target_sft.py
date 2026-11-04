"""Target-reaching candidate: PTW417 complete 17-serial generator run around selected p951 coupon.
Source printed origin is held fixed; selected copier ACK withheld.
"""
import sys,json,collections,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'agent49'))
import k04_p951_symbolic_basis as M
ROOT=Path(__file__).resolve().parents[2]/'resources'
basis,states=M.source(ROOT)
orig={k:v[0] for k,v in basis.rows.items()}
seal=(ROOT/'evidence/maintenance/seal-receipts.jsonl')
assert hashlib.sha256(seal.read_bytes()).hexdigest()=='c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32'
rows=[json.loads(x) for x in seal.read_text().splitlines()]
items=[r for r in rows if r['permit']=='PTW-417'];assert len(items)==17
views={
 'revision_bay':sorted(items,key=lambda x:(x['revision'],x['bay'])),
 'bay_revision':sorted(items,key=lambda x:(x['bay'],x['revision'])),
}
T=[w for p in range(951,955) for w in M.get(states,p)]
def addeq(d,v):
 while v:
  p=v.bit_length()-1
  if p in d:v^=d[p]
  else:d[p]=v;return 1
 return 0

def structural(start,stride):
 b=orig.copy()
 for k in range(17):
  for x in M.get(states,start+k*stride):addeq(b,x)
 return sum(addeq(b,w) for w in T)

starttime=time.monotonic()
interesting=[]
for stride in (1,2,3,4,5,6,7,8):
 for start in range(650,951):
  if start+16*stride>M.LAST:continue
  q=structural(start,stride)
  if q<128:interesting.append((q,start,stride))
nonoverlap=[(q,s,d) for q,s,d in interesting if not {s+i*d for i in range(17)}.intersection(range(951,955))]
assert len(interesting)==499 and len(nonoverlap)==117 and all(q==127 for q,_,_ in nonoverlap)
print('REDUCING_STAGE_GEOMETRIES',len(interesting),'NO_DIRECT_TARGET_OVERLAP',len(nonoverlap),'ALL_NONOVERLAP_QUOTIENT',127,'BEST',sorted(interesting)[:20],flush=True)

survivors=[];inspected=0;direct_fixed_conflict=0
for q,start,stride in sorted(interesting):
 for order,seq in views.items():
  for reverse in (False,True):
   actual=seq[::-1] if reverse else seq
   for endian in ('little','big'):
    for serializer in ('tempered','native'):
     inspected+=1
     new=M.Basis();new.rows=basis.rows.copy();new.rank=basis.rank
     contradictions=0;insertions=0
     for i,rec in enumerate(actual):
      h=rec['serial'][3:];x=int.from_bytes(bytes.fromhex(h),endian)
      x=M.untemper(x) if serializer=='tempered' else x
      p=start+stride*i
      before=new.rank
      for j,expr in enumerate(M.get(states,p)):
       try:new.insert(expr,(x>>j)&1)
       except AssertionError:contradictions+=1;break
      if contradictions:break
      insertions+=new.rank-before
     if not contradictions:survivors.append((q,start,stride,order,reverse,endian,serializer,insertions))
     else:direct_fixed_conflict+=1
print('ORIGINAL_SERIAL_SOURCE_MODELS',inspected,'FIXED_CONTRADICTIONS',direct_fixed_conflict,'FULL_SURVIVORS',len(survivors),'SAMPLES',survivors[:15],flush=True)
print('ELAPSED_SEC',round(time.monotonic()-starttime,2))
assert not survivors
# Real original printer equations supply an affine state solution; planted PTW-stage
# outputs from that solution must reconstruct all four synthetic selected words.
assigned=0
for p,(coeff,rhs) in sorted(basis.rows.items()):
 bit=rhs^((coeff&assigned).bit_count()&1)
 assigned|=bit<<p
assert all(((v&assigned).bit_count()&1)==rhs for v,rhs in basis.rows.values())
def evaluated(wordbits):
 return sum(((v&assigned).bit_count()&1)<<j for j,v in enumerate(wordbits))
state=M.Basis();state.rows=basis.rows.copy();state.rank=basis.rank
for p in range(938,955):
 original_tempered=evaluated(M.temper(M.get(states,p)))
 source_raw=original_tempered.to_bytes(4,'little')
 encoded=M.untemper(int.from_bytes(source_raw,'little'))
 for bit,expr in enumerate(M.get(states,p)):
  state.insert(expr,(encoded>>bit)&1)
assert state.rank>=basis.rank
expected=[evaluated(M.get(states,p)) for p in range(951,955)]
predicted=[]
for p in range(951,955):
 w=0
 for j,expr in enumerate(M.get(states,p)):
  result=state.predict(expr)
  assert result is not None
  w|=result<<j
 predicted.append(w)
assert predicted==expected
print('POSITIVE SYNTHETIC_SOURCE_COMPATIBLE_17WORD_STAGES=938..954 FULL_K04_128BIT_RECONSTRUCTION_PASS; target_solution', [hex(w) for w in predicted])
