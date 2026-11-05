"""H17: all 38 new low-dimensional K05 227-stride +/-1 staggered coupon inversions.

Run: python agents/agent25/k04_stage1406_k05_sparse227_jitter2_target_sft.py resources
Original source, verifier and acceptance are read-only. Hypothetical producer.
"""
from collections import Counter
from itertools import permutations, product
from pathlib import Path
import hashlib,importlib.util,json,sys
spec=importlib.util.spec_from_file_location('sft',Path(__file__).with_name('k04_stage1406_k05_target_rank_sft.py'))
sft=importlib.util.module_from_spec(spec);spec.loader.exec_module(sft)
sft.ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path('resources')
root=sft.ROOT; k02,k05=sft.selected();source,bank=sft.mt.source(root)
# Source-only scan of five originally low-dimensional 227-stride centers.
# Freeze all 78 fresh target-rank<=12 stage tuples before any original K05 RHS
# or K04 acceptance checks; omit every previously tested +/-1 timing geometry.
b0=None
for _,k02words in sft.views(k02):
 trial=sft.mt.Basis();trial.rows=source.rows.copy();trial.rank=source.rank
 try:
  for lane,word in enumerate(k02words):
   for bit,eq in enumerate(sft.mt.get(bank,1406+lane)):trial.insert(eq,(word>>bit)&1)
 except AssertionError:continue
 b0=trial;break
assert b0 and b0.rank==15492
tgt0=[sft.expr(b0.rows,v) for pos in range(951,955) for v in sft.mt.get(bank,pos)]
def geometry_dimension(stages):
 piv={}
 for pos in stages:
  for v in sft.mt.get(bank,pos):
   rem,_=sft.expr(b0.rows,v)
   while rem:
    p=rem.bit_length()-1
    if p in piv:rem^=piv[p]
    else:piv[p]=rem;break
 return sft.target_dimension(tgt0,{p:(v,0,0) for p,v in piv.items()})
prior={(q,q+227+d1,q+454+d2,q+681+d3) for center in (1120,1347,1516,1743,2139) for q in range(center-1,center+2) for d1,d2,d3 in product((-1,0,1),repeat=3)}
models={}
rank_counts=Counter()
for center in (1120,1347,1516,1743,2139):
 for q in range(center-2,center+3):
  for d1,d2,d3 in product((-2,-1,0,1,2),repeat=3):
   positions=(q,q+227+d1,q+454+d2,q+681+d3)
   dim=geometry_dimension(positions)
   rank_counts[dim]+=1
   if dim<=12 and positions not in prior:models[positions]=dim
assert len(models)==78 and rank_counts=={2:50,3:70,4:1,29:2,30:44,31:65,32:77,33:2816}
print("JITTER_3125_SOURCE_RANKS",dict(sorted(rank_counts.items())),"NEW_LOW_DIM",len(models),flush=True)
acc=json.loads((root/'acceptance.json').read_text())['slot_sha256']
mask=bytes.fromhex(json.loads((root/'evidence/recovery-routing.json').read_text())['K04']['masked_component'])
assert mask.hex().upper()=='8556C8CB6140A7F9A5123AC7571BEE1C'

def reduced_map(b,stages):
 independent={};conditions=[]
 for j in range(128):
  lane,bit=divmod(j,32)
  v,c=sft.expr(b.rows,sft.mt.get(bank,stages[lane])[bit]);tag=1<<j
  while v:
   p=v.bit_length()-1
   if p in independent:
    w,d,t=independent[p];v^=w;c^=d;tag^=t
   else: independent[p]=(v,c,tag);break
  if not v:conditions.append((tag,c))
 leftover_basis={};target=[];dim=0
 for stage in range(951,955):
  for v in sft.mt.get(bank,stage):
   v,c=sft.expr(b.rows,v);tag=0
   rem=0
   while v:
    p=v.bit_length()-1
    if p in independent:
     w,d,t=independent[p];v^=w;c^=d;tag^=t
    else:rem|=1<<p;v^=1<<p
   freetag=0
   while rem:
    p=rem.bit_length()-1
    if p in leftover_basis:
     w,t=leftover_basis[p];rem^=w;freetag^=t
    else:
     freetag^=1<<dim;leftover_basis[p]=(rem,1<<dim);dim+=1;break
   target.append((c,tag,freetag))
 assert len(target)==128
 return conditions,target,dim

def component(nat):
 def temper(x):
  x^=x>>11;x^=(x<<7)&0x9d2c5680;x^=(x<<15)&0xefc60000;x^=x>>18
  return x&0xffffffff
 coupon=b''.join(temper((nat>>(32*lane))&0xffffffff).to_bytes(4,'little') for lane in range(4))
 return bytes(v^w for v,w in zip(coupon,mask))

# Four K05 latches, each with independent big/little endian and native/tempered.
# Preserve each source word exactly while admitting 24 chronological assignments.
views=[]
for piece in [k05[i:i+4] for i in (0,4,8,12)]:
 vals=[]
 for endian in ('big','little'):
  w=int.from_bytes(piece,endian)
  vals.extend((w,sft.mt.untemper(w)))
 views.append(vals)
conditions_pass=Counter();mode_checks=Counter();real_hits=[];seen_coupon=set();synthetic=0;source_valid_modes=0
for source_mode,words in sft.views(k02):
 b=sft.mt.Basis();b.rows=source.rows.copy();b.rank=source.rank
 try:
  for lane,w in enumerate(words):
   for j,v in enumerate(sft.mt.get(bank,1406+lane)):b.insert(v,(w>>j)&1)
 except AssertionError:continue
 source_valid_modes+=1
 # Full-state synthetic producer: satisfy original intact printer and K02 RHS.
 x=0
 for p,(expr,c) in sorted(b.rows.items()):
  if c^((expr&x).bit_count()&1):x|=1<<p
 selected_native=sum(((v&x).bit_count()&1)<<j for j,v in enumerate(v for k in range(951,955) for v in sft.mt.get(bank,k)))
 selected_comp=component(selected_native)
 for stages,selected_dim in models.items():
  q=stages[0]
  conditions,target,dim=reduced_map(b,stages)
  assert dim==selected_dim
  planted=sum(((v&x).bit_count()&1)<<j for j,v in enumerate(v for stage in stages for v in sft.mt.get(bank,stage)))
  assert all((tag&planted).bit_count()%2==c for tag,c in conditions)
  cbase=sum((c^((tag&planted).bit_count()&1))<<j for j,(c,tag,t) in enumerate(target))
  fmask=[sum(((t>>i)&1)<<j for j,(_,_,t) in enumerate(target)) for i in range(dim)]
  assert any(component(cbase ^ sum(v for i,v in enumerate(fmask) if f>>i&1))==selected_comp for f in range(1<<dim))
  synthetic+=1
  # Precompute each original K05 word's full parity syndrome and its
  # contribution to the selected output. This preserves all 128-bit equations
  # while reducing repeated O(100)-parity tests over 2.33m assignments.
  want=sum(c<<i for i,(_,c) in enumerate(conditions))
  const=sum(c<<i for i,(c,_,_) in enumerate(target))
  small={}
  for lane in range(4):
   for latch in range(4):
    for codec in range(4):
     part=views[latch][codec]<<(lane*32)
     syndrome=sum(((tag&part).bit_count()&1)<<i for i,(tag,_) in enumerate(conditions))
     mapped=sum(((tag&part).bit_count()&1)<<j for j,(_,tag,_) in enumerate(target))
     small[lane,latch,codec]=(syndrome,mapped)
  for order in permutations(range(4)):
   for codec in product(range(4),repeat=4):
    mode_checks[stages]+=1
    u0,u1,u2,u3=(small[lane,order[lane],codec[lane]] for lane in range(4))
    if (u0[0]^u1[0]^u2[0]^u3[0])!=want:continue
    conditions_pass[stages]+=1
    native0=const^u0[1]^u1[1]^u2[1]^u3[1]
    for free in range(1<<dim):
     nat=native0
     for i,v in enumerate(fmask):
      if free>>i&1:nat^=v
     out=component(nat);seen_coupon.add(out)
     if hashlib.sha256(out).hexdigest()==acc['K04']:
      real_hits.append((source_mode,stages,order,codec,free,out.hex().upper()))
      print('ORIGINAL_K04_MATCH',real_hits[-1],flush=True)
assert source_valid_modes==10
assert mode_checks=={positions:61440 for positions in models}
assert synthetic==780 and sum(conditions_pass.values())==869900
assert len(seen_coupon)==11040 and not real_hits
print("SOURCE original printer rank",source.rank,"selected K02 modes",source_valid_modes)
print("ASSIGNMENTS_SUM",sum(mode_checks.values()),"SOURCE_COMPATIBLE_SUM",sum(conditions_pass.values()),"SYNTHETIC_FULL_COUPON",synthetic)
print("UNIQUE_COMPLETE_K04",len(seen_coupon),"ORIGINAL_K04_HITS",len(real_hits))

# Cross-geometry full-component set control: the +/-2 shell adds no coupon
# absent from the +/-1 shell, despite different compatible K05 assignments.
assert hashlib.sha256(b"".join(sorted(seen_coupon))).hexdigest()=="9b249a0536e05804cee16b33fb7b5d8c17a38ae9f328e3ca37313a6c483dbd47"
print("COMPLETE_K04_SET_SHA256",hashlib.sha256(b"".join(sorted(seen_coupon))).hexdigest())
