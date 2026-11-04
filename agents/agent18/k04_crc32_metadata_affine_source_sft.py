"""Source-only CRC32-IEEE metadata-to-printer 32-bit lane producer pilot."""
import datetime
import hashlib
import json
import sys
import zlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = []
for line in raw.decode().splitlines():
    if "+00:00 JOB=" not in line:
        continue
    words = line.split()
    r = dict(x.split("=",1) for x in words[1:])
    r["TS"],r["LINE"] = words[0],line
    rows.append(r)
assert len(rows) == 128

def fields(r):
    job=r["JOB"]
    number=int(job.rsplit("-",1)[-1])
    ts=r["TS"]
    unixt=int(datetime.datetime.fromisoformat(ts).timestamp())
    fmt=f"{job}|{r['ATTEMPT']}|{r['STATE']}|{r['CLASS']}|{r['DEST']}"
    return {
        "job_ascii":job.encode(),"job_lower":job.lower().encode(),
        "job_numeric_ascii":str(number).encode(),
        "job_suffix_4char":f"{number:04d}".encode(),
        "job_u16be":number.to_bytes(2,"big"),
        "job_u16le":number.to_bytes(2,"little"),
        "job_u32be":number.to_bytes(4,"big"),
        "job_u32le":number.to_bytes(4,"little"),
        "timestamp_ascii":ts.encode(),"datetime_utc":ts[:-6].encode(),
        "unix_u32be":unixt.to_bytes(4,"big"),
        "unix_u32le":unixt.to_bytes(4,"little"),
        "unix_u64be":unixt.to_bytes(8,"big"),
        "unix_u64le":unixt.to_bytes(8,"little"),
        "minute_u32be":(unixt//60).to_bytes(4,"big"),
        "minute_u32le":(unixt//60).to_bytes(4,"little"),
        "job_class":f"{job}|{r['CLASS']}".encode(),
        "job_dest":f"{job}|{r['DEST']}".encode(),
        "job_attempt":f"{job}|{r['ATTEMPT']}".encode(),
        "metadata_pipe":fmt.encode(),
        "metadata_concat":fmt.replace("|","").encode(),
        "metadata_spacing":f"JOB={job} ATTEMPT={r['ATTEMPT']} STATE={r['STATE']} CLASS={r['CLASS']} DEST={r['DEST']}".encode(),
        "line_before_payload":r["LINE"].split(" PAYLOAD=")[0].encode(),
    }

forms=[fields(r) for r in rows]
assert len(set(tuple(f) for f in forms)) == 1
views={order:[[int.from_bytes(bytes.fromhex(r["PAYLOAD"])[4*i:4*i+4],order)
               for i in range(4)] for r in rows] for order in ("big","little")}
def groups(kind):
    result=defaultdict(list)
    for i,r in enumerate(rows):
        key={"all":"all","class":r["CLASS"],"class-dest":r["CLASS"]+"|"+r["DEST"]}[kind]
        result[key].append(i)
    return [indices for indices in result.values() if len(indices)>=2]

summary={}
for group_type in ("all","class","class-dest"):
    tested=0
    matches=[]
    for indices in groups(group_type):
        a=indices[0]
        for name in forms[0]:
            crc0=zlib.crc32(forms[a][name])
            for endian in ("big","little"):
                for lane in range(4):
                    pad=crc0^views[endian][a][lane]
                    for index in indices[1:]:
                        tested+=1
                        if zlib.crc32(forms[index][name])^pad == views[endian][index][lane]:
                            matches.append((group_type,name,endian,lane,a,index))
    summary[group_type]={"heldout_32bit_word_checks":tested,"matches":matches}
# Independent synthetic fixed-lane-pad producer recovers all 128 packets.
pads=(0xA5A5AC17,0x4F1AB62C,0x5D081717,0xD3C88F01)
tokens=[[zlib.crc32(f["job_ascii"])^pad for pad in pads] for f in forms]
for lane,key in enumerate(pads):
    recovered=zlib.crc32(forms[0]["job_ascii"])^tokens[0][lane]
    assert recovered==key
    assert all((zlib.crc32(f["job_ascii"])^recovered)==obs[lane]
               for f,obs in zip(forms,tokens))
print(json.dumps({"ordinary_rows":len(rows),"metadata_forms":len(forms[0]),
                  "source":summary,"synthetic_all128_all4_lanes":"PASS"},indent=2))
