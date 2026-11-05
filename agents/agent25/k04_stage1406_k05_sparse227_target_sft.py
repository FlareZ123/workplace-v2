"""H17 novel stage1406 K02 and 227-strided selected K05 full K04 reconstruction.

Run: python agents/agent25/k04_stage1406_k05_sparse227_target_sft.py resources
The original source, acceptance and verifier are never written.
"""
from collections import Counter
from itertools import permutations, product
from pathlib import Path
import hashlib,importlib.util,json,sys
spec=importlib.util.spec_from_file_location('sft',Path(__file__).with_name('k04_stage1406_k05_target_rank_sft.py'))
sft=importlib.util.module_from_spec(spec);spec.loader.exec_module(sft)
sft.ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path('resources')
root=sft.ROOT; k02,k05=sft.selected();source,bank=sft.mt.source(root)
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
 for q in (1120,1347,1516,1743,2139):
  stages=tuple(q+227*j for j in range(4))
  conditions,target,dim=reduced_map(b,stages)
  assert dim=={1120:2,1347:2,1516:3,1743:3,2139:4}[q]
  planted=sum(((v&x).bit_count()&1)<<j for j,v in enumerate(v for stage in stages for v in sft.mt.get(bank,stage)))
  assert all((tag&planted).bit_count()%2==c for tag,c in conditions)
  cbase=sum((c^((tag&planted).bit_count()&1))<<j for j,(c,tag,t) in enumerate(target))
  fmask=[sum(((t>>i)&1)<<j for j,(_,_,t) in enumerate(target)) for i in range(dim)]
  assert any(component(cbase ^ sum(v for i,v in enumerate(fmask) if f>>i&1))==selected_comp for f in range(1<<dim))
  synthetic+=1
  for order in permutations(range(4)):
   for codec in product(range(4),repeat=4):
    packed=sum(views[order[lane]][codec[lane]]<<(32*lane) for lane in range(4))
    mode_checks[q]+=1
    if not all((tag&packed).bit_count()%2==c for tag,c in conditions):continue
    conditions_pass[q]+=1
    native0=sum((c^((tag&packed).bit_count()&1))<<j for j,(c,tag,t) in enumerate(target))
    for free in range(1<<dim):
     nat=native0
     for i,v in enumerate(fmask):
      if free>>i&1:nat^=v
     out=component(nat);seen_coupon.add(out)
     if hashlib.sha256(out).hexdigest()==acc['K04']:
      real_hits.append((source_mode,q,order,codec,free,out.hex().upper()))
      print('ORIGINAL_K04_MATCH',real_hits[-1],flush=True)
assert source_valid_modes==10
assert mode_checks=={q:61440 for q in (1120,1347,1516,1743,2139)}
assert conditions_pass=={1120:6080,1516:1520,1743:14720,2139:3700}
assert synthetic==50 and len(seen_coupon)==8800 and not real_hits
print('SOURCE original printer rank',source.rank,'selected K02 modes',source_valid_modes)
print('ASSIGNMENTS',dict(mode_checks),'SOURCE_COMPATIBLE',dict(conditions_pass),'SYNTHETIC_FULL_COUPON',synthetic)
print('UNIQUE_COMPLETE_K04',len(seen_coupon),'ORIGINAL_K04_HITS',len(real_hits))
