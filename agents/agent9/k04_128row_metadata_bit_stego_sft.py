"""K04 one-bit-per-row metadata-indexed complete coupon test."""
import hashlib, itertools, json, re, sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else "resources")
spool=(root/"evidence/print/spool-reconstruction.log").read_bytes()
route=(root/"evidence/recovery-routing.json").read_bytes()
assert hashlib.sha256(spool).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(route).hexdigest()=="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
mask=bytes.fromhex(json.loads(route)["K04"]["masked_component"])
target="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
lines=[s for s in spool.decode().splitlines() if "PAYLOAD=" in s]
rows=[];cls=[];dest=[]
for job in range(300,428):
    matches=[s for s in lines if f"JOB=PS-261003-{job:04d} " in s and "STATE=ACK" in s and "ATTEMPT=1" in s]
    assert len(matches)==1
    line=matches[0]
    rows.append(bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})",line).group(1)))
    cls.append(("LABEL","STORES","RECOVER").index(re.search(r"CLASS=(\w+)",line).group(1)))
    dest.append(("bench","desk","store").index(re.search(r"DEST=(\w+)",line).group(1)))
assert len(rows)==128 and set(cls)=={0,1,2} and set(dest)=={0,1,2}
def emit(a,b,cp,dp,sv,reverse):
    value=0
    for i in range(128):
        j=127-i if reverse else i
        pos=(a*i+b+16*cp[cls[j]]+32*dp[dest[j]])&127
        if sv&1:pos^=7
        if sv&2:pos=127-pos
        value|=((rows[j][pos>>3]>>(pos&7))&1)<<i
    return value
def sha(value,packing):
    coupon=value.to_bytes(16,"little" if packing==0 else "big")
    return hashlib.sha256(bytes(x^y for x,y in zip(coupon,mask))).hexdigest()
plant=sha(emit(5,39,(1,2,0),(2,0,1),1,1),1)
checks=0;authentic=[];positives=0
for a,b,cp,dp,sv,rev in itertools.product((1,3,5,7,15,31,63,127),range(128),itertools.permutations(range(3)),itertools.permutations(range(3)),range(4),range(2)):
    v=emit(a,b,cp,dp,sv,rev)
    for packing in range(2):
        digest=sha(v,packing);checks+=1
        if digest==target:authentic.append((a,b,cp,dp,sv,rev,packing))
        if digest==plant:positives+=1
assert checks==589824 and positives==1 and not authentic
print(json.dumps({"complete_K04_checks":checks,"real_matches":authentic,"planted_matches":positives}))
