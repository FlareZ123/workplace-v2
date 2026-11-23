"""K04: original-source LOW IF EVEN cross-row coupon construction.

Explore 128 chronological pre-18:00 ACK1 packets as a 128-bit carrier.
Byte column may depend on source row index, class or destination; note
the LOW IF EVEN cue is not historically attested as a printer operation.
Never read the disputed selected ACK2 payload during candidate creation.

Run: python agents/agent33/h17_low_even_crossrow_coupon_sft.py resources
"""
import re, hashlib, itertools, collections, sys
from pathlib import Path

root=Path(sys.argv[1] if len(sys.argv)>1 else "resources")
spool=root/"evidence/print/spool-reconstruction.log"
assert hashlib.sha256(spool.read_bytes()).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows=[]
for ln in spool.read_text().splitlines():
    if "PAYLOAD=" not in ln:
        continue
    d=dict(re.findall(r"([A-Z]+)=([\w-]+)",ln))
    rows.append(d)
assert len(rows)==133
rr=rows[:128]
assert all(d["JOB"]==f"PS-261003-{i:04d}" and d["STATE"]=="ACK" and d["ATTEMPT"]=="1" for i,d in enumerate(rr,300))
data=[bytes.fromhex(d["PAYLOAD"]) for d in rr]
assert all(len(d)==16 for d in data)
route=(root/"evidence/recovery-routing.json").read_bytes()
assert hashlib.sha256(route).hexdigest()=="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
mask=bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
commit=bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")

def coupon(indices,evenbit,oddbit,reverse_rows,reverse_bits,reverse_bytes):
    bits=[(data[i][indices[i]]>>(evenbit if i%2==0 else oddbit))&1 for i in range(128)]
    if reverse_rows:
        bits.reverse()
    out=bytes(sum(bits[8*j+k]<<(7-k if reverse_bits else k) for k in range(8)) for j in range(16))
    return out[::-1] if reverse_bytes else out

def reduce_coupon(raw):
    return bytes(x^y for x,y in zip(raw,mask))

classes=sorted({d["CLASS"] for d in rr})
destinations=sorted({d["DEST"] for d in rr})
selectors=[]
for rule in ("row","block","interleave","constant","job-digit","class","dest"):
    for step in range(16 if rule in ("row","block","interleave") else 1):
        for off in range(16):
            if rule=="row":
                indexes=[(i*step+off)%16 for i in range(128)]
            elif rule=="block":
                indexes=[((i//8)*step+off)%16 for i in range(128)]
            elif rule=="interleave":
                indexes=[((i//16)*step+off)%16 for i in range(128)]
            elif rule=="constant":
                indexes=[off]*128
            elif rule=="job-digit":
                indexes=[((i+300)%10+off)%16 for i in range(128)]
            elif rule=="class":
                indexes=[(classes.index(d["CLASS"])+off)%16 for d in rr]
            else:
                indexes=[(destinations.index(d["DEST"])+off)%16 for d in rr]
            selectors.append((rule,step,off,indexes))
assert len(selectors)==832

plant=reduce_coupon(coupon([(i+7)%16 for i in range(128)],0,7,False,False,False))
plant_commit=hashlib.sha256(plant).digest()
seen=set()
hits=[]
plant_hits=0
for rule,step,off,indexes in selectors:
    for even,odd in ((0,7),(0,6),(0,5),(0,4),(0,3),(0,2),(0,1),(0,0),(7,0),(7,7)):
        for flip_rows,flip_bits,flip_bytes in itertools.product((False,True),repeat=3):
            component=reduce_coupon(coupon(indexes,even,odd,flip_rows,flip_bits,flip_bytes))
            if component in seen:
                continue
            seen.add(component)
            digest=hashlib.sha256(component).digest()
            if digest==commit:
                hits.append((rule,step,off,even,odd,flip_rows,flip_bits,flip_bytes,component.hex()))
            if digest==plant_commit:
                plant_hits+=1
print(f"selectors={len(selectors)} distinct_complete_original_K04_checks={len(seen)} original_hits={len(hits)} planted_hits={plant_hits}")
print("original_matches",hits)
assert len(seen)==31360 and len(hits)==0 and plant_hits==1
