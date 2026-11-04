#!/usr/bin/env python3
"""Source-trained spool AES128 counter block emitter with a shared XOR pad.
Eight genuine archive keys, ten event-counter encodings, original intact
spool packet holdouts, and full missing K04 commitment. Historical use of AES
is an exploratory hypothesis; no selected ACK2 copy is fitted or used.
Requires cryptography. No original records are modified.
"""
from pathlib import Path
from hashlib import sha256, md5
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import json
import re

p = Path(__file__).resolve().parents[2] / "resources"
spool = p / "evidence/print/spool-reconstruction.log"
route = p / "evidence/recovery-routing.json"
accept = p / "acceptance.json"
assert sha256(spool.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert sha256(route.read_bytes()).hexdigest() == "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
assert sha256(accept.read_bytes()).hexdigest() == "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
a = json.loads(accept.read_text())
rr = json.loads(route.read_text())
rows = []
for line in spool.read_text().splitlines():
    m = re.match(r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)", line)
    if m:
        rows.append(dict(time=m[1], job=m[2], attempt=int(m[3]), state=m[4], cls=m[5], dest=m[7], payload=bytes.fromhex(m[6])))
assert len(rows) == 133
keys = {k: bytes.fromhex(s) for k, s in {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
    "route_mask": rr["K04"]["masked_component"],
    "desk_nonce": rr["K08"]["desk_nonce"]
}.items()}
assert all(sha256(v).hexdigest() == a["slot_sha256"][k] for k, v in keys.items() if k in ("K01","K02","K03","K05","K06","K07"))
assert all(len(k) == 16 for k in keys.values())

def vectors(r):
    suffix = int(r["job"][-4:])
    t = int(datetime.fromisoformat(r["time"].replace("Z", "+00:00")).timestamp())
    n = r["attempt"]
    label = f"{r['job']}:{n}:{r['state']}:{r['cls']}:{r['dest']}".encode()
    return {
        "jobbig": suffix.to_bytes(16, "big"),
        "joblittle": suffix.to_bytes(16, "little"),
        "timebig": t.to_bytes(16, "big"),
        "timelittle": t.to_bytes(16, "little"),
        "jobattemptbig": (suffix * 4 + n).to_bytes(16, "big"),
        "jobattemptlittle": (suffix * 4 + n).to_bytes(16, "little"),
        "md5job": md5(r["job"].encode()).digest(),
        "sha16job": sha256(r["job"].encode()).digest()[:16],
        "md5state": md5(label).digest(),
        "sha16state": sha256(label).digest()[:16],
    }

def aes(key, block):
    ctx = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return ctx.update(block) + ctx.finalize()

def xor(a, b):
    return bytes(i ^ j for i, j in zip(a, b))

selected = next(r for r in rows if r["job"].endswith("0417") and r["attempt"] == 2 and r["state"] == "ACK")
controls = rows[:128]
assert all(r is not selected for r in controls)
passes = checks = target_hits = 0
mask = keys["route_mask"]
for name, key in keys.items():
    for fmt in vectors(controls[0]):
        pad = xor(controls[0]["payload"], aes(key, vectors(controls[0])[fmt]))
        control_hits = sum(xor(aes(key, vectors(r)[fmt]), pad) == r["payload"] for r in controls[1:])
        passes += control_hits
        checks += 127
        candidate = xor(xor(aes(key, vectors(selected)[fmt]), pad), mask)
        target_hits += sha256(candidate).hexdigest() == a["slot_sha256"]["K04"]

# Genuinely recover withheld 16-byte synthetic packets from only first donor.
synthetic_key = bytes(range(16))
synthetic_pad = bytes(range(16, 32))
synthetic = [xor(aes(synthetic_key, vectors(r)["jobattemptlittle"]), synthetic_pad) for r in rows]
learned = xor(synthetic[0], aes(synthetic_key, vectors(rows[0])["jobattemptlittle"]))
assert all(xor(aes(synthetic_key, vectors(r)["jobattemptlittle"]), learned) == item for r, item in zip(rows[1:], synthetic[1:]))
assert (len(keys) * len(vectors(rows[0])), checks, passes, target_hits) == (80, 10160, 0, 0)
print({"AES_counter_emitter_models": 80, "genuine_original_spool_heldout_checks": checks,
       "exact_16byte_spool_heldout_matches": passes, "original_K04_commitment_checks": 80,
       "original_K04_hits": target_hits, "synthetic_source_holdouts": 132})
