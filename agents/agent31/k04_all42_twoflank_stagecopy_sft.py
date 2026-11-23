"""H-17 K04 two-flank stage-copy original-source complete coupon producer.

Under the source-consistent all42 MT stage model, shift only original
source-connected producer groups containing the two preserved PS-0417
RECOVER REQUESTED records. The selected ACK2 (row129) is withheld
*before reading its copied PAYLOAD*. Find complete raw four-word coupons
which are independently fixed by other original packets at a selected
intermediate native stage. Hash through unchanged original K04 mask.

Run: python agents/agent31/k04_all42_twoflank_stagecopy_sft.py
Pure Python standard library, uses Agent1's source-pinned row parser/stages.
"""
import collections
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents/agent1"))
import k04_all42_cpython_n98_extended_sft as base

U=0xffffffff
MAG=0x9908b0df
GROUP12={12,43,66,96,128}
GROUP13={13,44,67,97,130,131}
BASE=tuple(base.S)
assert len(BASE)==133 and BASE[128:133]==(951,952,957,961,966)

def temper(x):
 x^=x>>11
 x^=(x<<7)&0x9d2c5680
 x^=(x<<15)&0xefc60000
 x^=x>>18
 return x&U

def native_expressions():
 words=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
 for k in range(624,624+970):
  x,y,z=words[k-624],words[k-623],words[k-227]
  words.append([z[j]^(x[31] if j==30 else y[j+1] if j<30 else 0)
                ^(y[0] if MAG&(1<<j) else 0) for j in range(32)])
 return words

def make_basis(words,stages,packets):
 basis={}
 def add(v,rhs):
  while v:
   p=v.bit_length()-1
   if p not in basis:basis[p]=(v,rhs);return
   w,c=basis[p];v^=w;rhs^=c
  if rhs:raise ValueError("original packet GF2 contradiction")
 for r,payload in enumerate(packets):
  if payload is None:continue
  for q in range(4):
   native=base.untemper(int.from_bytes(payload[4*q:4*q+4],"little"))
   for j,expr in enumerate(words[624+stages[r]+q]):
    add(expr,(native>>j)&1)
 return basis

def predict(words,basis,stage):
 def known(v):
  rhs=0
  while v:
   p=v.bit_length()-1
   if p not in basis:return None
   w,c=basis[p];v^=w;rhs^=c
  return rhs
 masks=[];values=[]
 for q in range(4):
  native=mask=0
  for j,expr in enumerate(words[624+stage+q]):
   x=known(expr)
   if x is not None:mask|=1<<j;native|=x<<j
  masks.append(mask.bit_count())
  values.append(native)
 if sum(masks)==128:
  return masks,b"".join(temper(v).to_bytes(4,"little") for v in values)
 return masks,None

def main():
 raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
 assert hashlib.sha256(raw).hexdigest()==base.SOURCE_SHA
 packets=base.source()
 assert len(packets)==133 and packets[129] is None
 # No reference to the selected copied buffer or its mask until after every
 # source-only chronology and complete native-coupon prediction is frozen.
 words=native_expressions()
 route=json.loads((ROOT/"resources/evidence/recovery-routing.json").read_text())
 acceptance=json.loads((ROOT/"resources/acceptance.json").read_text())
 mask=bytes.fromhex(route["K04"]["masked_component"])
 target=acceptance["slot_sha256"]["K04"]
 assert mask.hex().upper()=="8556C8CB6140A7F9A5123AC7571BEE1C"
 assert target=="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
 counts=collections.Counter()
 observed=[]
 original_hits=[]
 synthetic_hits=0
 synthetic=hashlib.sha256(bytes(a^b for a,b in zip(
   bytes.fromhex("6ADB2FB180DA2AA90B33F7A444D53DFC"),mask))).hexdigest()
 for d12 in range(-4,2):
  for d13 in range(-5,4):
   stages=[s+(d12 if i in GROUP12 else d13 if i in GROUP13 else 0)
           for i,s in enumerate(BASE)]
   if stages[128]>stages[129] or stages[130]<stages[129]:
    counts["causal_reject"]+=1;continue
   if any(stages[i+1]<stages[i] for i in range(132)):
    counts["monotone_reject"]+=1;continue
   counts["monotone_pass"]+=1
   try:basis=make_basis(words,stages,packets)
   except ValueError:
    counts["source_contradiction"]+=1
    continue
   assert len(basis)==15434,(d12,d13,len(basis))
   counts["source_fit"]+=1
   for q in range(stages[128],stages[130]+1):
    bits,raw_coupon=predict(words,basis,q)
    counts["selected_stages"]+=1
    if raw_coupon is None:continue
    counts["complete_assignments"]+=1
    comp=bytes(a^b for a,b in zip(raw_coupon,mask))
    if hashlib.sha256(comp).hexdigest()==target:
     original_hits.append((d12,d13,q,comp.hex().upper()))
    if hashlib.sha256(comp).hexdigest()==synthetic:
     synthetic_hits+=1
    observed.append((d12,d13,q,raw_coupon.hex().upper(),comp.hex().upper()))
 assert counts["monotone_pass"]==54,counts
 assert counts["source_contradiction"]==47,counts
 assert counts["source_fit"]==7,counts
 assert counts["selected_stages"]==44,counts
 assert counts["complete_assignments"]==20,counts
 distinct={a[3]:a[4] for a in observed}
 assert len(distinct)==5,distinct
 assert synthetic_hits==2,(synthetic_hits,observed)
 assert not original_hits,original_hits
 assert distinct=={
  "CD3E4F216ADB2FB180DA2AA90B33F7A4":"486887EA0B9B884825C8106E5C2819B8",
  "6ADB2FB180DA2AA90B33F7A444D53DFC":"EF8DE77AE19A8D50AE21CD6313CED3E0",
  "80DA2AA90B33F7A444D53DFC29D7943A":"058CE2626A73505DE1C7073B7ECC7A26",
  "0B33F7A444D53DFC29D7943A95D89371":"8E653F6F25959A058CC5AEFDC2C37D6D",
  "44D53DFC29D7943A95D89371DA58EC64":"C183F537489733C330CAA9B68D430278",
 },distinct
 print("ORIGINAL_RESULT",json.dumps({
  "source_sha":base.SOURCE_SHA,"original_rows":132,
  "selected_ACK2_payload_decoded":False,
  "model": "all42 2-root REQUESTED1/3 stage-copy, source-consistent",
  "monotone_source_placements":counts["monotone_pass"],
  "source_compatible_placements":counts["source_fit"],
  "selected_phases":counts["selected_stages"],
  "complete_candidate_assignments":counts["complete_assignments"],
  "distinct_source_coupons":distinct,
  "synthetic_full_component_hits":synthetic_hits,
  "original_K04_hits":len(original_hits),
  "combined_rec8_complete":False
 },sort_keys=True))

if __name__=="__main__":main()
