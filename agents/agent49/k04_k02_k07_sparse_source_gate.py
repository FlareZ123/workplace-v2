"""K04 K02+K07 sparse 227-stage selected checkpoint donor compatibility test.

Uses original six-slot source, conditional Agent49 p951 MT printer model,
and the selected AX-7782 eight checkpoint halfwords. Target digest is not
used for choosing geometry or for evaluating incompatible writers.
"""
import hashlib, itertools, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent49"))
import k04_p951_symbolic_basis as mt
mt.LAST=3300
SOURCE=ROOT/"resources"
PINS={
 "telemetry/freeze-export.jsonl":"3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
 "transfers/transfer-audit.jsonl":"32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
}
for name,sha in PINS.items():
 assert hashlib.sha256((SOURCE/"evidence"/name).read_bytes()).hexdigest()==sha
k02=bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
lines=[json.loads(x) for x in (SOURCE/"evidence/transfers/transfer-audit.jsonl").read_text().splitlines()]
chunks={}
for row in lines:
 if row.get("kind")=="CHUNK" and row.get("transfer")=="AX-7782":
  i=row["seq"]
  if i not in chunks or chunks[i]["attempt"]<row["attempt"]:chunks[i]=row
assert set(chunks)==set(range(8))
k07=b"".join(bytes.fromhex(chunks[i]["checkpoint"]) for i in range(8))
assert k07.hex().upper()=="8947CEDCB9CC73BAB7E87BE63302C5C9"
accepted=json.loads((SOURCE/"acceptance.json").read_text())["slot_sha256"]
assert hashlib.sha256(hashlib.sha256(k02).digest()[:16]).hexdigest()==accepted["K02"]
assert hashlib.sha256(hashlib.sha256(k07).digest()[:16]).hexdigest()==accepted["K07"]
printer,symbolic=mt.source(SOURCE)
selected=[e for i in range(951,955) for e in mt.get(symbolic,i)]

def donor_modes():
 for endian in ("big","little"):
  for reverse,swap_halves,native in itertools.product((False,True),repeat=3):
   parts=[k02[j:j+4] for j in range(0,16,4)]
   if swap_halves:parts=[x[2:]+x[:2] for x in parts]
   if reverse:parts.reverse()
   values=[int.from_bytes(x,endian) for x in parts]
   yield (endian,reverse,swap_halves,native),[v if native else mt.untemper(v) for v in values]

def extend(base,words):
 b=mt.Basis();b.rows=base.rows.copy();b.rank=base.rank
 for stage,w in words:
  for j,v in enumerate(mt.get(symbolic,stage)):b.insert(v,(w>>j)&1)
 return b

def parity_constraints(base,stages,hi):
 pivots={};checks=[]
 for lane,stage in enumerate(stages):
  bits=mt.temper(mt.get(symbolic,stage))
  for j,v in enumerate(bits[16:] if hi else bits[:16]):
   residual=0;constant=0
   while v:
    p=v.bit_length()-1
    if p in base.rows:
     w,c=base.rows[p];v^=w;constant^=c
    else:residual^=1<<p;v^=1<<p
   marker=1<<(16*lane+j)
   while residual:
    p=residual.bit_length()-1
    if p not in pivots:
     pivots[p]=(residual,marker,constant)
     break
    q,t,c=pivots[p]
    residual^=q;marker^=t;constant^=c
   if not residual:checks.append((marker,constant))
 assert len(checks)+len(pivots)==128
 def target_remainder(v):
  r=0
  while v:
   p=v.bit_length()-1
   if p in base.rows:v^=base.rows[p][0]
   else:r^=1<<p;v^=1<<p
  while r:
   p=r.bit_length()-1
   if p not in pivots:break
   r^=pivots[p][0]
  return r
 dimension=rank(target_remainder(v) for v in selected)
 return checks,len(pivots),dimension

def rank(expressions):
 pivots={}
 for v in expressions:
  while v:
   p=v.bit_length()-1
   if p not in pivots:pivots[p]=v;break
   v^=pivots[p]
 return len(pivots)

def residual_rank(base):
 def reduce(v):
  out=0
  while v:
   p=v.bit_length()-1
   if p in base.rows:v^=base.rows[p][0]
   else:out^=1<<p;v^=1<<p
  return out
 return rank(reduce(v) for v in selected)

starts=[1062,1120,1289,1347,1516]
orders={"forward":list(range(8)),"reverse":list(reversed(range(8))),
        "evens_odds":[0,2,4,6,1,3,5,7]}
count=0;compatible=[]
for mode,values in donor_modes():
 base=extend(printer,zip(range(1178,1182),values))
 assert base.rank==15493
 assert residual_rank(base)==33
 for start in starts:
  stages=[start+227*i for i in range(8)]
  for high in (False,True):
   checks,rank_donor,freedom=parity_constraints(base,stages,high)
   assert freedom==18
   assert len(checks)>=30
   for order_name,order in orders.items():
    for flips in range(256):
     word=0
     for lane,index in enumerate(order):
      p=k07[index*2:index*2+2]
      v=int.from_bytes(p,"little" if (flips>>lane)&1 else "big")
      word|=v<<(16*lane)
     count+=1
     if all(((word&tag).bit_count()&1)==rhs for tag,rhs in checks):
      compatible.append((mode,start,high,order_name,flips,rank_donor))
print("K02 33-bit conditional quotient; selected K07 sparse 227-word source gate:")
print("STAGE_GEOMETRIES",starts,"TARGET_BITS_REMAINING",18)
print("COMPLETE_SOURCE_ASSIGNMENTS",count,"SOURCE_COMPATIBLE",len(compatible))
assert count==16*5*2*3*256==122880
assert not compatible
