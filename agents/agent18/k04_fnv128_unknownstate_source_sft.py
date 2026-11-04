"""Read-only FNV-1/FNV-1a 128-bit unknown-initial-state printer source test."""
import datetime
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources"
raw = (ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows=[]
for line in raw.decode().splitlines():
    if "+00:00 JOB=" not in line: continue
    fields=line.split()
    r=dict(x.split("=",1) for x in fields[1:])
    r["TIME"],r["LINE"]=fields[0],line
    rows.append(r)
assert len(rows)==128
PRIME=int("0000000001000000000000000000013B",16)
M=(1<<128)-1
INV=pow(PRIME,-1,1<<128)
def fnv(state,data,variant):
    x=state
    for ch in data:
        x=(((x^ch)*PRIME)&M) if variant=="a" else (((x*PRIME)&M)^ch)
    return x
def invert(output,data,variant):
    x=output
    for ch in reversed(data):
        x=(((x*INV)&M)^ch) if variant=="a" else (((x^ch)*INV)&M)
    return x
def forms(r):
    n=int(r["JOB"].split("-")[-1])
    job=r["JOB"]
    time=r["TIME"]
    epoch=int(datetime.datetime.fromisoformat(time).timestamp())
    return {
        "job_ascii":job.encode(),"job_lower":job.lower().encode(),
        "job_suffix_ascii":f"{n:04d}".encode(),
        "job_u32be":n.to_bytes(4,"big"),"job_u32le":n.to_bytes(4,"little"),
        "unix_u32be":epoch.to_bytes(4,"big"),"unix_u32le":epoch.to_bytes(4,"little"),
        "unix_u64be":epoch.to_bytes(8,"big"),"unix_u64le":epoch.to_bytes(8,"little"),
        "timestamp":time.encode(),
        "job_class":f"{job}|{r['CLASS']}".encode(),
        "job_dest":f"{job}|{r['DEST']}".encode(),
        "job_attempt":f"{job}|{r['ATTEMPT']}".encode(),
        "job_class_dest":f"{job}|{r['CLASS']}|{r['DEST']}".encode(),
        "job_attempt_class":f"{job}|{r['ATTEMPT']}|{r['CLASS']}".encode(),
        "job_time":f"{job}|{time}".encode(),
        "metadata_pipe":f"{job}|{r['ATTEMPT']}|{r['STATE']}|{r['CLASS']}|{r['DEST']}".encode(),
        "line_prefix":r["LINE"].split(" PAYLOAD=")[0].encode(),
    }
messages=[forms(r) for r in rows]
def layout(hexpayload,method):
    data=bytes.fromhex(hexpayload)
    if method=="natural":return data
    if method=="reverse":return data[::-1]
    if method=="word_reverse":return b"".join(data[i:i+4][::-1] for i in range(0,16,4))
    return data[8:]+data[:8]
found=[]
comparisons=0
for kind in ("all","class","class_dest"):
    groups=defaultdict(list)
    for i,r in enumerate(rows):
        key={"all":"all","class":r["CLASS"],"class_dest":r["CLASS"]+"|"+r["DEST"]}[kind]
        groups[key].append(i)
    for name,indices in groups.items():
        if len(indices)<2:continue
        for variant in ("1","a"):
            for style in ("natural","reverse","word_reverse","swap_halves"):
                observed=[int.from_bytes(layout(rows[i]["PAYLOAD"],style),"big") for i in indices]
                for form in messages[0]:
                    seeds=[invert(v,messages[i][form],variant) for i,v in zip(indices,observed)]
                    comparisons+=len(seeds)-1
                    common=[j for j in range(1,len(seeds)) if seeds[j]==seeds[0]]
                    if common:found.append((kind,name,variant,style,form,common))
                    assert fnv(seeds[0],messages[indices[0]][form],variant)==observed[0]
seed=0xFE88995CA6E30001234566778899AABB
for variant in ("1","a"):
    produced=[fnv(seed,word["job_ascii"],variant) for word in messages]
    assert all(invert(value,msg["job_ascii"],variant)==seed for msg,value in zip(messages,produced))
print(json.dumps({"original_rows":len(rows),"forms":len(messages[0]),"layouts":4,
                  "hash_variants":2,"heldout_state_checks":comparisons,
                  "original_consistent_seed_matches":found,
                  "planted_128packet_positive":True},indent=2))
