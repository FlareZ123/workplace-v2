"""H-17 K04: source-first AES-GCM tag + shared XOR pad with south/watch controls.

Read-only; optional first argument is extracted original archive's resources directory.
Requires cryptography. The copied selected north ACK2 is excluded from model fitting.
"""
from datetime import datetime
from pathlib import Path
from itertools import product
import hashlib
import json
import re
import struct
import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

root = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources"
e = root/"evidence"
raw = (e/"print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
route = json.loads((e/"recovery-routing.json").read_text())
acceptance = json.loads((root/"acceptance.json").read_text())
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
mask = bytes.fromhex(route["K04"]["masked_component"])
target = acceptance["slot_sha256"]["K04"]
known = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
}
assert all(hashlib.sha256(bytes.fromhex(v)).hexdigest() == acceptance["slot_sha256"][k] for k,v in known.items())
keys = {k:bytes.fromhex(v) for k,v in known.items()}
keys.update({"desk_nonce":nonce, "K01+K06":keys["K01"]+keys["K06"],
             "K02+K07":keys["K02"]+keys["K07"], "K03+K05":keys["K03"]+keys["K05"],
             "K04_mask":mask})
assert len(keys)==11

# Only original ACK RECOVER events: north selected, south calibration, watch holdout.
records = {}
for line in raw.decode().splitlines():
    if not line or line.startswith("#"):
        continue
    m = re.fullmatch(r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)",line)
    assert m is not None,line
    stamp,job,attempt,state,kind,payload,dest = m.groups()
    if state=="ACK" and kind=="RECOVER" and job in ("PS-261003-0417","PS-261003-0448","PS-261003-0420"):
        records[job] = dict(stamp=stamp,job=job,attempt=int(attempt),kind=kind,
                            dest=dest,payload=bytes.fromhex(payload))
assert len(records)==3
north,south,watch=(records[x] for x in ("PS-261003-0417","PS-261003-0448","PS-261003-0420"))
assert (north["stamp"],north["attempt"],north["dest"]) == ("2026-10-03T18:02:00Z",2,"bench")
assert south["attempt"]==1 and watch["attempt"]==2
assert south["payload"].hex().upper()=="234BE186E97EE05830909790E336109E"
assert watch["payload"].hex().upper()=="432475F72A62DB39F3D5693E2C937FA4"
lane={"PS-261003-0417":"ESC-N","PS-261003-0448":"ESC-S","PS-261003-0420":"WATCH-SPARE"}
cassette={"PS-261003-0417":"L-29/N","PS-261003-0448":"L-29/S","PS-261003-0420":"L-29/W"}

def message(r,n):
    job=r["job"];stamp=r["stamp"];attempt=r["attempt"]
    choices=(b"",job.encode(),lane[job].encode(),cassette[job].encode(),
             f"{job}|{attempt}".encode(),
             f"{job}|{r['kind']}|{r['dest']}".encode(),
             f"{lane[job]}|{job}|{r['kind']}|{r['dest']}|{attempt}".encode(),
             stamp.encode(),f"{stamp}|{job}|{attempt}".encode())
    return choices[n]

def iv_for(r,n):
    job=r["job"];stamp=r["stamp"];attempt=r["attempt"]
    ts=int(datetime.fromisoformat(stamp.replace("Z","+00:00")).timestamp())
    choices=(hashlib.sha256(job.encode()).digest()[:12],
             hashlib.sha256(f"{job}|{attempt}".encode()).digest()[:12],
             hashlib.sha256(f"{lane[job]}|{job}|{attempt}".encode()).digest()[:12],
             hashlib.sha256(f"{stamp}|{job}|{attempt}".encode()).digest()[:12],
             struct.pack(">QI",ts,attempt),struct.pack("<QI",ts,attempt),
             job.encode()[:12],job.encode()[-12:],nonce[:12],nonce[-12:])
    return choices[n]

def tag(k,r,i,a,t):
    return AESGCM(k).encrypt(iv_for(r,i),message(r,t),message(r,a))[-16:]

def models():
    for name,k in keys.items():
        for i,a,t in product(range(10),range(9),range(9)):
            yield name,k,i,a,t

def bxor(a,b):
    return bytes(x^y for x,y in zip(a,b))

# Synthetic whole-value calibration/withholding positive, with independently
# manufactured same-format original-event data and an unknown common copy pad.
planted=next(m for m in models() if m[0]=="K06" and m[2:]==(1,6,2))
_,pk,pi,pa,pt=planted
synthetic_pad=bytes.fromhex("66A1C63A47D4B539410D64DAE78CA0FE")
synthetic_south=bxor(tag(pk,south,pi,pa,pt),synthetic_pad)
synthetic_watch=bxor(tag(pk,watch,pi,pa,pt),synthetic_pad)
recovered_pad=bxor(tag(pk,south,pi,pa,pt),synthetic_south)
assert recovered_pad==synthetic_pad
assert bxor(tag(pk,watch,pi,pa,pt),recovered_pad)==synthetic_watch
print("synthetic_complete_south_watch_pad_positive=PASS")

seen=0;watch_matches=[];authentic_hits=[]
for name,key,i,a,t in models():
    seen+=1
    pad=bxor(tag(key,south,i,a,t),south["payload"])
    if bxor(tag(key,watch,i,a,t),pad)!=watch["payload"]:
        continue
    watch_matches.append((name,i,a,t))
    coupon=bxor(tag(key,north,i,a,t),pad)
    component=bxor(coupon,mask)
    if hashlib.sha256(component).hexdigest()==target:
        authentic_hits.append((name,i,a,t,component.hex().upper()))
assert seen==8910
print(f"original_complete_source_models={seen} exact_watch_control_matches={len(watch_matches)} original_K04_ACCEPTED={len(authentic_hits)}")
if watch_matches: print("source_models=",watch_matches)
if authentic_hits: print("accepted_components=",authentic_hits)
