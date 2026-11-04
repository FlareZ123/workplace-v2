#!/usr/bin/env python3
"""Original-source SHA-pinned five-stream GF128 selected-version postprocessor SFT."""
from pathlib import Path
from itertools import combinations, product
from hashlib import sha256
import json,sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources"
e=root/"evidence"
pins={
"print/spool-reconstruction.log":"7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
"telemetry/freeze-export.jsonl":"3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
"maintenance/seal-receipts.jsonl":"c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
"recorder/trip-recorder.raw":"5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
"procedures/RC-17-scans.txt":"a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d",
"transfers/transfer-audit.jsonl":"32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
"recovery-routing.json":"f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
}
for p,v in pins.items():assert sha256((e/p).read_bytes()).hexdigest()==v,p
assert sha256((root/"acceptance.json").read_bytes()).hexdigest()=="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
route=json.loads((e/"recovery-routing.json").read_text());accept=json.loads((root/"acceptance.json").read_text())
mask=bytes.fromhex(route["K04"]["masked_component"]);target=bytes.fromhex(accept["slot_sha256"]["K04"])
# Authentic original full 16-byte older -> selected pairs.
# K02 GOOD DIAG_WORD earlier/latest, K03 PTW417 signed earlier/latest B,D,A,C;
# K05 CONTROL seq200/seq300, K06 RC17 B/C service strips,
# K07 transfer AX7778 drill/AX7782 final attempt2 checkpoints.
rows=[
("K02","BB1E82F3BFB3479E5358255316967CAA","E1A5E474BAD7E853A2E8C71D3317D507"),
("K03","AD1D814B64B2EE4A574A92325CB72EE5","D7DAD6BC9714519B7DAD0AD4BE8E87FD"),
("K05","42BFD0538052760C6FC2B743BFB00270","FF8B78200A56E8586DCDA00EF01E4572"),
("K06","D82A73E9E1DB4379759E0027C130C9BB","5DBF40EE52FAAED9A536D3326CF0D95A"),
("K07","AC5FBCDD1CB5C98CA234AE35DD42B16A","8947CEDCB9CC73BAB7E87BE63302C5C9"),
]
assert sha256(bytes.fromhex(rows[0][2])).digest()[:16].hex().upper()=="0D7E3AB56FB75DA3EB0E2E06786D239E"
assert sha256(bytes.fromhex(rows[4][2])).digest()[:16].hex().upper()=="93495F5E425AB8E592123DABAEB68545"
spool=(e/"print/spool-reconstruction.log").read_text()
original=["CD3E4F216ADB2FB180DA2AA90B33F7A4","44D53DFC29D7943A95D89371DA58EC64","E1E60D5F6B6DD2225FA6D5A2A63AD932"]
for x in original:assert "PAYLOAD="+x in spool
inputs=list(map(bytes.fromhex,original))
F=(1<<128)-1
def mul(a,b):
 out=0
 while b:
  if b&1:out^=a
  b>>=1;a=((a<<1)&F)^(0x87 if a>>127 else 0)
 return out
def inv(a):
 assert a
 n=(1<<128)-2;out=1
 while n:
  if n&1:out=mul(out,a)
  a=mul(a,a);n>>=1
 return out
def div(a,b):return mul(a,inv(b))
def rbyte(x):return int(f"{x:08b}"[::-1],2)
def enc(raw,wr,lr,br):
 words=[raw[i:i+4] for i in range(0,16,4)]
 if wr:words=words[::-1]
 if lr:words=[w[::-1] for w in words]
 a=b"".join(words)
 if br:a=bytes(map(rbyte,a))
 return int.from_bytes(a,"big")
def dec(n,wr,lr,br):
 a=n.to_bytes(16,"big")
 if br:a=bytes(map(rbyte,a))
 words=[a[i:i+4] for i in range(0,16,4)]
 if lr:words=[w[::-1] for w in words]
 if wr:words=words[::-1]
 return b"".join(words)
def quadratic(p):
 (x,y),(u,v),(w,z)=p
 first=div(y^v,x^u);other=div(y^z,x^w)
 A=div(first^other,u^w);B=first^mul(A,x^u)
 C=y^mul(A,mul(x,x))^mul(B,x)
 return lambda q:mul(A,mul(q,q))^mul(B,q)^C
# Synthetic original-shaped five-record publisher must be predicted exactly.
co=(0xAF03812B3212368713,0x012312ABCEDA8899EF,0xAABBCCDDEEFF)
xs=[1,5,11,32,77]
ys=[mul(co[0],mul(x,x))^mul(co[1],x)^co[2] for x in xs]
for idx in combinations(range(5),3):
 fn=quadratic([(xs[i],ys[i]) for i in idx])
 assert all(fn(x)==y for x,y in zip(xs,ys))
stats={"affine":0,"quadratic":0,"historical_complete_heldouts":0,"full_original_K04_checks":0,"original_K04_matches":[]}
# Actual signed K03 A-bay revision 1 has two distinct original values.
for alt_a in ("574A9232","7E73B4CC"):
 data=[(n,bytes.fromhex(old.replace("574A9232",alt_a)),bytes.fromhex(new)) for n,old,new in rows]
 for wr,lr,br in product((0,1),repeat=3):
  points=[(enc(old,wr,lr,br),enc(new,wr,lr,br)) for _,old,new in data]
  for kind,k in (("affine",2),("quadratic",3)):
   for training in combinations(range(5),k):
    pp=[points[i] for i in training]
    if kind=="affine":
     (x,y),(u,v)=pp;A=div(y^v,x^u);B=y^mul(A,x)
     func=lambda q,A=A,B=B:mul(A,q)^B
    else:func=quadratic(pp)
    stats[kind]+=1
    stats["historical_complete_heldouts"]+=sum(func(points[i][0])==points[i][1] for i in range(5) if i not in training)
    for source in inputs:
     coupon=dec(func(enc(source,wr,lr,br)),wr,lr,br)
     candidate=bytes(x^y for x,y in zip(coupon,mask))
     stats["full_original_K04_checks"]+=1
     if sha256(candidate).digest()==target:
      stats["original_K04_matches"].append({"kind":kind,"K03_A_old":alt_a,"training":training,"layout":(wr,lr,br),"K04":candidate.hex()})
assert stats=={"affine":160,"quadratic":160,"historical_complete_heldouts":0,"full_original_K04_checks":960,"original_K04_matches":[]},stats
print("PASS synthetic five-record GF128 publisher all ten training triples")
print(json.dumps(stats,indent=2))
