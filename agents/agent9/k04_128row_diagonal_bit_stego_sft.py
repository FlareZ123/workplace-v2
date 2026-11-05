"""K04 source-only 128-row indexed bit carrier; original target read only."""
import hashlib, itertools, json, re, sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else "resources")
spool=(root/"evidence/print/spool-reconstruction.log").read_bytes()
route=(root/"evidence/recovery-routing.json").read_bytes()
assert hashlib.sha256(spool).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(route).hexdigest()=="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
mask=bytes.fromhex(json.loads(route)["K04"]["masked_component"])
target="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
lines=[line for line in spool.decode().splitlines() if "PAYLOAD=" in line]
rows=[]
for job in range(300,428):
 matches=[line for line in lines if f"JOB=PS-261003-{job:04d} " in line and "STATE=ACK" in line and "ATTEMPT=1" in line]
 assert len(matches)==1
 rows.append(bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})",matches[0]).group(1)))
assert len(rows)==128
def coupon(pattern,source,reverse,pack):
 value=0
 for i in range(128):
  pos=pattern(i)&127
  if source&1: pos^=7
  if source&2: pos=127-pos
  data=rows[127-i if reverse else i]
  value|=((data[pos>>3]>>(pos&7))&1)<<i
 return value.to_bytes(16,"little" if pack==0 else "big")
def sha(c):return hashlib.sha256(bytes(x^y for x,y in zip(c,mask))).hexdigest()
plant_a=sha(coupon(lambda i:(37*i+53)&127,1,1,1))
plant_g=sha(coupon(lambda i:8*((5*(i%16)+7)%16)+((3*(i//16)+4)%8),2,0,0))
counts=[0,0];hits=[];plants=[0,0]
views=list(itertools.product(range(4),range(2),range(2)))
for a,b in itertools.product(range(128),repeat=2):
 pattern=lambda i,a=a,b=b:(a*i+b)&127
 for v in views:
  h=sha(coupon(pattern,*v));counts[0]+=1
  if h==target:hits.append(("affine",a,b,v))
  if h==plant_a:plants[0]+=1
for mb,mt,bb,bt in itertools.product((1,3,5,7,9,11,13,15),(1,3,5,7),range(16),range(8)):
 pattern=lambda i,mb=mb,mt=mt,bb=bb,bt=bt:8*((mb*(i%16)+bb)%16)+((mt*(i//16)+bt)%8)
 for v in views:
  h=sha(coupon(pattern,*v));counts[1]+=1
  if h==target:hits.append(("grid",mb,mt,bb,bt,v))
  if h==plant_g:plants[1]+=1
assert counts==[262144,65536] and plants==[2,4] and not hits
print(json.dumps({"checks":counts,"original_hits":hits,"planted_hits":plants}))
