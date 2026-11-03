"""K04: xorshift128 Marsaglia retry replay, with a different-job holdout.

SFT: run this file from a checkout; optionally set H17_ROOT to the extracted
archive directory. Does not modify original evidence or canonical candidate.
"""
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("H17_ROOT", Path(__file__).resolve().parents[2] / "resources"))
LOG = ROOT / "evidence/print/spool-reconstruction.log"
assert hashlib.sha256(LOG.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
target = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"]
mask = bytes.fromhex(route["K04"]["masked_component"])
rows = []
for line in LOG.read_text().splitlines():
    if "PAYLOAD=" not in line:
        continue
    row = dict(re.findall(r"([A-Z]+)=([^ ]+)", line))
    row["time"] = line.split()[0]
    rows.append(row)

def pick(job, attempt, clock):
    vals = [r for r in rows if r["JOB"].endswith(job)
            and int(r["ATTEMPT"]) == attempt and r["time"].startswith(clock)]
    assert len(vals) == 1
    return bytes.fromhex(vals[0]["PAYLOAD"])

def step(state):
    a,b,c,d = state
    t = (a ^ ((a << 11) & 0xffffffff)) & 0xffffffff
    return [b,c,d,(d ^ (d >> 19) ^ t ^ (t >> 8)) & 0xffffffff]

def decode(buf, order, backward):
    w = [int.from_bytes(buf[i:i+4], order) for i in range(0,16,4)]
    return w[::-1] if backward else w

def encode(w, order, backward):
    return b"".join(v.to_bytes(4,order) for v in (w[::-1] if backward else w))

def replay(a, b, width=8192):
    found = []
    for order in ("big","little"):
        for backward in (False,True):
            state = decode(a,order,backward)
            for delta in range(1,width+1):
                state = step(state)
                if encode(state,order,backward) == b:
                    found.append([order,backward,delta])
    return found

# Four independent positive controls, with a true 137-word state displacement.
seed = [0x12345678,0x9a7bcdef,0xa159b26c,0xdeadbeef]
for order in ("big","little"):
    for backward in (False,True):
        after = seed[:]
        for _ in range(137):
            after = step(after)
        assert [order,backward,137] in replay(
            encode(seed,order,backward),encode(after,order,backward),192)

spare1 = pick("0420",1,"2026-10-03T17:00:")
spare2 = pick("0420",2,"2026-10-03T18:25:")
old = pick("0417",1,"2026-10-03T16:45:")
req1 = pick("0417",1,"2026-10-03T18:01:")
req3 = pick("0417",3,"2026-10-03T18:03:")
holdout_matches = replay(spare1,spare2)
other_matches = replay(req1,req3)
checks = 0
hits = []
for source_name,first in (("early_ack",old),("request1",req1)):
    for order in ("big","little"):
        for backward in (False,True):
            state = decode(first,order,backward)
            for delta in range(1,8193):
                state = step(state)
                predicted = encode(state,order,backward)
                component = bytes(x^y for x,y in zip(predicted,mask))
                checks += 1
                if hashlib.sha256(component).hexdigest() == target:
                    hits.append([source_name,order,backward,delta,component.hex().upper()])
assert checks == 65536
print(json.dumps({"synthetic_controls":4,"spare_ack1_to_ack2":holdout_matches,
                  "selected_request1_to_request3":other_matches,
                  "complete_k04_checks":checks,"accepted_k04":hits},sort_keys=True))
