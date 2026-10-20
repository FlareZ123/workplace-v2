"""Reconstruct six verified H17 archive slots; keep unverified slots null."""
import datetime as dt
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "resources"
E = R / "evidence"
A = json.loads((R / "acceptance.json").read_text())["slot_sha256"]
C = {f"K{i:02d}": None for i in range(1, 9)}

def check(slot, raw):
    value = raw.hex().upper()
    assert hashlib.sha256(raw).hexdigest() == A[slot], (slot, value)
    C[slot] = value
    print(slot, "PASS", value)

def short_hash(raw):
    return hashlib.sha256(raw).digest()[:16]

def read_rows(path):
    return [json.loads(row) for row in path.read_text().splitlines() if row.strip()]

check("K01", bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"))
start = dt.datetime.fromisoformat("2026-10-03T21:13:40+00:00")
end = dt.datetime.fromisoformat("2026-10-03T21:13:48+00:00")
t = {}
for r in read_rows(E / "telemetry/freeze-export.jsonl"):
    if (r.get("tag"),r.get("field"),r.get("quality"),r.get("state")) != ("LT-204","DIAG_WORD","GOOD","HOLD"):
        continue
    if not start <= dt.datetime.fromisoformat(r["ts"]) < end:
        continue
    s = r["seq"]
    if s not in t or r["revision"] > t[s]["revision"]:
        t[s] = r
check("K02", short_hash(b"".join(int(t[i]["value"]).to_bytes(2,"big") for i in range(8))))
seals = {}
for r in read_rows(E / "maintenance/seal-receipts.jsonl"):
    if r.get("permit") != "PTW-417" or r.get("state") != "CLOSED" or r.get("fitment") != "AS_LEFT" or r.get("signed") is not True:
        continue
    b = r["bay"]
    if b not in seals or r["revision"] > seals[b]["revision"]:
        seals[b] = r
check("K03", short_hash("|".join(seals[b]["serial"] for b in "BDAC").encode("ascii")))
mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
spool = (E / "print/spool-reconstruction.log").read_text()
entries = []
for line in spool.splitlines():
    match = re.search(r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32})", line)
    if match and match.group(1) == "PS-261003-0417" and match.group(3) == "ACK" and match.group(4) == "RECOVER":
        entries.append((int(match.group(2)), bytes.fromhex(match.group(5))))
assert entries
payload = max(entries)[1]
wrong = bytes(a ^ b for a,b in zip(payload,mask))
assert hashlib.sha256(wrong).hexdigest() != A["K04"]
print("K04 NO_MATCH", wrong.hex().upper(), "(excluded)")
recorder = (E / "recorder/trip-recorder.raw").read_bytes()
magic,version,size,count = struct.unpack_from("<8sHHI",recorder)
assert (magic,version,size,len(recorder)) == (b"TRP2DUMP",2,24,16+count*24)
latches = {}
for i in range(count):
    record = recorder[16+i*24:16+(i+1)*24]
    ts,node,event,latch,seq,word,aux,crc = struct.unpack("<IHBBI4sII",record)
    if zlib.crc32(record[:20]) != crc or (node,event) != (49,82) or not 1791062040 <= ts < 1791062048:
        continue
    if latch not in latches or seq > latches[latch][0]:
        latches[latch] = (seq,word)
check("K05", b"".join(latches[i][1] for i in range(4)))
pages = {}
for page in (E / "procedures/RC-17-scans.txt").read_text().split("\f"):
    heading = re.search(r"DOCUMENT RC-17 / REV (\S+) / SECTION (\S+)", page)
    strip = re.search(r"Footer control strip: ([0-9A-F]{8})", page)
    if heading and strip:
        pages[(heading.group(1),heading.group(2))] = strip.group(1)
check("K06", bytes.fromhex("".join(pages[("C",section)] for section in ("DRAIN","ISOLATE","PURGE","VERIFY"))))
rows = read_rows(E / "transfers/transfer-audit.jsonl")
assert any(r.get("kind")=="COMMIT" and r.get("transfer")=="AX-7782" and r.get("dry_run") is False for r in rows)
chunks = {}
for r in rows:
    if r.get("kind")!="CHUNK" or r.get("transfer")!="AX-7782": continue
    s=r["seq"]
    if s not in chunks or r["attempt"] > chunks[s]["attempt"]:
        chunks[s] = r
check("K07", short_hash(b"".join(bytes.fromhex(chunks[i]["checkpoint"]) for i in range(8))))
(R.parent / "candidate.json").write_text(json.dumps(C,indent=2)+"\n")
