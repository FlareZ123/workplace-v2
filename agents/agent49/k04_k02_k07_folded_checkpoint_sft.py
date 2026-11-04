"""K04 K02+K07 fold16 checkpoint emitter, source-first original-data test."""
import hashlib, itertools, json
from pathlib import Path
import k04_p951_symbolic_basis as mt
mt.LAST=3300
ROOT=Path(__file__).resolve().parents[2]/'resources'
assert hashlib.sha256((ROOT/'evidence/transfers/transfer-audit.jsonl').read_bytes()).hexdigest()=='32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf'
k02=bytes.fromhex('E1A5E474BAD7E853A2E8C71D3317D507')
k07=bytes.fromhex('8947CEDCB9CC73BAB7E87BE63302C5C9')
accept=json.loads((ROOT/'acceptance.json').read_text())['slot_sha256']
assert hashlib.sha256(hashlib.sha256(k02).digest()[:16]).hexdigest()==accept['K02']
assert hashlib.sha256(hashlib.sha256(k07).digest()[:16]).hexdigest()==accept['K07']
printer,symbolic=mt.source(ROOT)
sel=[e for t in range(951,955) for e in mt.get(symbolic,t)]

def donor_modes():
 for endian in ('big','little'):
  for reverse,swap_halves,native in itertools.product((False,True),repeat=3):
   p=[k02[k:k+4] for k in (0,4,8,12)]
   if swap_halves:p=[x[2:]+x[:2] for x in p]
   if reverse:p.reverse()
   values=[int.from_bytes(x,endian) for x in p]
   yield (endian,reverse,swap_halves,native),[v if native else mt.untemper(v) for v in values]

def extend(base,stages,values):
 out=mt.Basis();out.rows=base.rows.copy();out.rank=base.rank
 for stage,value in zip(stages,values):
  for j,eq in enumerate(mt.get(symbolic,stage)):out.insert(eq,(value>>j)&1)
 return out

def syndrome(base,stages,view):
 pivots={};checks=[]
 for lane,stage in enumerate(stages):
  native=mt.get(symbolic,stage)
  src=mt.temper(native) if view=='tempered' else native
  bits=[src[j]^src[j+16] for j in range(16)]
  for j,v in enumerate(bits):
   residual=constant=0
   while v:
    p=v.bit_length()-1
    if p in base.rows:
     x,c=base.rows[p];v^=x;constant^=c
    else:residual^=1<<p;v^=1<<p
   tag=1<<(16*lane+j)
   while residual:
    p=residual.bit_length()-1
    if p not in pivots:
     pivots[p]=(residual,tag,constant);break
    x,t,c=pivots[p];residual^=x;tag^=t;constant^=c
   if not residual:checks.append((tag,constant))
 assert len(pivots)+len(checks)==128
 return checks,len(pivots),pivots

starts=[1062,1120,1289,1347,1516]
orders={'forward':list(range(8)),'reverse':list(reversed(range(8))),
        'evens_odds':[0,2,4,6,1,3,5,7]}
def state_from_basis(base):
 state=0
 for pivot,(expression,bit) in sorted(base.rows.items()):
  if bit ^ ((expression&state).bit_count()&1):state|=1<<pivot
 return state

def rank(vectors):
 rows={}
 for v in vectors:
  while v:
   p=v.bit_length()-1
   if p not in rows:rows[p]=v;break
   v^=rows[p]
 return len(rows)

def selected_dimension(base,pivots):
 def residue(v):
  out=0
  while v:
   p=v.bit_length()-1
   if p in base.rows:v^=base.rows[p][0]
   else:out^=1<<p;v^=1<<p
  v=out;out=0
  while v:
   p=v.bit_length()-1
   if p in pivots:v^=pivots[p][0]
   else:out^=1<<p;v^=1<<p
  return out
 return rank(residue(e) for e in sel)

stats={};matched=[];planted_checks=0
for k02mode,words in donor_modes():
 base=extend(printer,range(1178,1182),words)
 assert base.rank==15493
 for start in starts:
  stages=[start+227*j for j in range(8)]
  for view in ('native','tempered'):
   checks,rank_donor,pivots=syndrome(base,stages,view)
   if k02mode==next(donor_modes())[0]:
    assert selected_dimension(base,pivots)==17
    state=state_from_basis(base)
    planted=0
    for lane,stage in enumerate(stages):
     raw=mt.get(symbolic,stage)
     bits=mt.temper(raw) if view=='tempered' else raw
     folded=sum(((((bits[j]^bits[j+16])&state).bit_count()&1)<<j) for j in range(16))
     planted|=folded<<(16*lane)
    assert all(((planted&tag).bit_count()&1)==rhs for tag,rhs in checks)
    bad_bit=checks[0][0]&-checks[0][0]
    assert any((((planted^bad_bit)&tag).bit_count()&1)!=rhs for tag,rhs in checks)
    planted_checks+=1
   key=(start,view)
   if key not in stats:stats[key]={'parity_checks':len(checks),'donor_rank':rank_donor,'assignments':0,'compatible':0}
   stat=stats[key]
   assert stat['parity_checks']==len(checks) and stat['donor_rank']==rank_donor
   for name,order in orders.items():
    for flips in range(256):
     packed=sum(int.from_bytes(k07[2*i:2*i+2],'little' if flips>>j&1 else 'big')<<(16*j) for j,i in enumerate(order))
     stat['assignments']+=1
     if all(((packed&tag).bit_count()&1)==rhs for tag,rhs in checks):
      stat['compatible']+=1;matched.append((k02mode,start,view,name,flips))
assert sum(x['assignments'] for x in stats.values())==16*5*2*3*256
assert planted_checks==10 and not matched
print('ORIGINAL_SOURCE_ASSIGNS',sum(x['assignments'] for x in stats.values()),'MATCHES',len(matched),'PLANTED',planted_checks,'TARGET_FREE_BITS',17)
print('GEOMETRIES',json.dumps({str(k):v for k,v in stats.items()}))
