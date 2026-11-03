"""Extract original H17 16-byte source-derived MT donor carrier groups.
Usage: python agents/agent11/build_donor_corpus.py h17-archive-dump.zip output.tsv
This reads the historical ZIP and writes only a freshly generated TSV.
"""
import json
import re
import struct
import hashlib
import sys
from zipfile import ZipFile

assert len(sys.argv)==3,"specify original zip and output TSV"
z=ZipFile(sys.argv[1])
assert hashlib.sha256(z.read("evidence/print/spool-reconstruction.log")).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
source={}
def add(label,b):
    if isinstance(b,str):b=bytes.fromhex(b)
    if len(b)==16:source.setdefault(b,label)

for name in z.namelist():
    if name.endswith("/") or name in ("acceptance.json","verify.py","candidate.template.json"):continue
    data=z.read(name)
    for m in re.finditer(rb"(?<![0-9a-fA-F])([0-9a-fA-F]{32})(?![0-9a-fA-F])",data):
        add(f"HEX32:{name}:{m.start()}",bytes.fromhex(m.group(1).decode()))
sp=z.read("evidence/print/spool-reconstruction.log")
for i,m in enumerate(re.finditer(rb"PAYLOAD=([0-9A-F]{32})",sp)):
    add(f"PRINTER:row{i}",bytes.fromhex(m.group(1).decode()))

tr=z.read("evidence/recorder/trip-recorder.raw")
seq=[];recs=[]
for i in range(88):
    off=16+i*24
    ts,node,event,latch,n,control,aux,crc=struct.unpack_from("<IHBBI4sII",tr,off)
    recs.append((node,event,latch,n,control))
    seq.append(control)
for i in range(len(seq)-3):
    add(f"TRP2:physical:window{i}",b"".join(seq[i:i+4]))
ordered=sorted(recs,key=lambda x:(x[0],x[1],x[3],x[2]))
for i in range(len(ordered)-3):
    add(f"TRP2:sorted:window{i}",b"".join(x[4] for x in ordered[i:i+4]))
for (node,event) in sorted({(r[0],r[1]) for r in recs}):
    arr=sorted([x for x in recs if x[0]==node and x[1]==event],key=lambda x:x[3])
    for i in range(len(arr)-3):
        add(f"TRP2:node{node}-event{event}:window{i}",b"".join(x[4] for x in arr[i:i+4]))

trans=[json.loads(line) for line in z.read("evidence/transfers/transfer-audit.jsonl").splitlines()]
for name in ["AX-7778","AX-7781","AX-7782","AX-7783"]:
    rows=sorted([x for x in trans if x["kind"]=="CHUNK" and x["transfer"]==name],key=lambda x:(x["seq"],x["attempt"]))
    cp=[bytes.fromhex(x["checkpoint"]) for x in rows]
    for i in range(9):add(f"{name}:sorted8:offset{i}",b"".join(cp[i:i+8]))
    for retry in (1,2):
        vals=[bytes.fromhex(x["checkpoint"]) for x in rows if x["attempt"]==retry]
        add(f"{name}:attempt{retry}",b"".join(vals))
    vals=[bytes.fromhex(max((x for x in rows if x["seq"]==j),key=lambda x:x["attempt"])["checkpoint"]) for j in range(8)]
    add(f"{name}:greatest-retry",b"".join(vals))

pages=z.read("evidence/procedures/RC-17-scans.txt").decode().split("\f")
foot=[]
for p in pages:
    m=re.search(r"Footer control strip:\s*([0-9A-F]{8})",p)
    if m:
        rev=re.search(r"DOCUMENT RC-17 / REV ([^/]+) / SECTION ([^\n]+)",p)
        foot.append((rev.group(1).strip(),rev.group(2).strip(),bytes.fromhex(m.group(1))))
for i in range(len(foot)-3):
    add(f"RC17:scanwindow{i}",b"".join(t[2] for t in foot[i:i+4]))
for rev in sorted(set(t[0] for t in foot)):
    groups={section:b for r,section,b in foot if r==rev}
    if len(groups)==4:
        add(f"RC17:REV{rev}:serviceorder",b"".join(groups[x] for x in ("DRAIN","ISOLATE","PURGE","VERIFY")))
        add(f"RC17:REV{rev}:sectionorder",b"".join(groups[x] for x in sorted(groups)))

tele=[json.loads(x) for x in z.read("evidence/telemetry/freeze-export.jsonl").splitlines()]
for key,subset in {
    "ALL":[x for x in tele if x["field"]=="DIAG_WORD"],
    "LT204":[x for x in tele if x["tag"]=="LT-204" and x["field"]=="DIAG_WORD"],
    "GOOD_HOLD":[x for x in tele if x["tag"]=="LT-204" and x["field"]=="DIAG_WORD" and x["quality"]=="GOOD" and x["state"]=="HOLD"],
}.items():
    for order,arr in [
        ("source",subset),
        ("seq",sorted(subset,key=lambda x:(x["seq"],x["revision"]))),
        ("time",sorted(subset,key=lambda x:x["ts"]))
    ]:
        words=[int(x["value"]).to_bytes(2,"big") for x in arr if isinstance(x["value"],int) and 0<=x["value"]<=65535]
        for i in range(len(words)-7):
            add(f"TELEMETRY:{key}:{order}:offset{i}",b"".join(words[i:i+8]))

receipts=[json.loads(x) for x in z.read("evidence/maintenance/seal-receipts.jsonl").splitlines()]
serial=[(x["permit"],x["bay"],x["serial"].split("-")[-1]) for x in receipts]
for i in range(len(serial)-3):
    add(f"SEAL:sourceoffset{i}",b"".join(bytes.fromhex(s) for _,_,s in serial[i:i+4]))
for permit in sorted(set(x[0] for x in serial)):
    vals=sorted([x for x in serial if x[0]==permit],key=lambda x:x[1])
    for i in range(len(vals)-3):
        add(f"SEAL:{permit}:offset{i}",b"".join(bytes.fromhex(s) for _,_,s in vals[i:i+4]))

verified={
    "K01":"049AAB2E1CDE7A82CD7C60234303C91A",
    "K02":"0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03":"1384AF96E25D6ADA666209CB55E062FA",
    "K05":"FF8B78200A56E8586DCDA00EF01E4572",
    "K06":"5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07":"93495F5E425AB8E592123DABAEB68545"
}
for k,h in verified.items():add("DERIVED:"+k,h)
assert bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C") in source
assert bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497") in source
assert len(source)==531
with open(sys.argv[2],"w",encoding="utf-8",newline="\n") as f:
    for b,label in sorted(source.items(),key=lambda kv:kv[1]):
        f.write(b.hex().upper()+"\t"+label+"\n")
with open(sys.argv[2],"rb") as f:
    digest=hashlib.sha256(f.read()).hexdigest()
assert digest=="f63f248fd90e9a592c0e760df4743965930a0f7cfa677809329c381b472ebffc",digest
print(json.dumps({"donors":len(source),"tsv_sha256":digest,"output":sys.argv[2]},indent=2))
