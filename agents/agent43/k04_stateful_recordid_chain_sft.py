#!/usr/bin/env python3
"""Read-only H-17 SFT: stateful PTW/PS record-ID reducer hypotheses.

Run from the workplace-v2 repository root. Python standard library only.
No source, candidate, route, acceptance, or verifier file is modified.
"""
from collections import Counter
from pathlib import Path
import hashlib
import hmac
import itertools
import json
import re

ROOT = Path("resources")
E = ROOT / "evidence"
PINS = {
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "maintenance/seal-receipts.jsonl": "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    "mail/04.eml": "c9e83a610f9240c3abd4b4d435588bd9056de34edf6fa3e6d7aca88d8a21f439",
    "recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
}
for name, expected in PINS.items():
    assert hashlib.sha256((E / name).read_bytes()).hexdigest() == expected, name
ACCEPTANCE_PIN = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
assert hashlib.sha256((ROOT / "acceptance.json").read_bytes()).hexdigest() == ACCEPTANCE_PIN

receipts = [json.loads(x) for x in (E / "maintenance/seal-receipts.jsonl").read_text().splitlines()]
legacy = {}
for r in receipts:
    if r["permit"] != "PTW-417":
        n = int(r["permit"].split("-")[-1])
        if 390 <= n <= 416:
            assert n not in legacy, n
            legacy[n] = r
assert set(legacy) == set(range(390, 417))

packets = {}
for line in (E / "print/spool-reconstruction.log").read_text().splitlines():
    m = re.search(r"^(\S+) JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$", line)
    if not m:
        continue
    ts, job, attempt, state, cls, payload, dest = m.groups()
    n = int(job[-4:])
    if 390 <= n <= 416 and state == "ACK":
        assert n not in packets, n
        packets[n] = {"ts": ts, "job": job, "att": attempt, "state": state,
                      "class": cls, "payload": bytes.fromhex(payload), "dest": dest}
assert set(packets) == set(range(390, 417))

# Hold out PS-0417; use the selected ACK/RECOVER row only for reporting.
target_row = None
for line in (E / "print/spool-reconstruction.log").read_text().splitlines():
    m = re.search(r"^(\S+) JOB=PS-261003-0417 ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$", line)
    if m:
        ts, attempt, state, cls, payload, dest = m.groups()
        if state == "ACK" and cls == "RECOVER":
            target_row = {"ts": ts, "job": "PS-261003-0417", "att": attempt,
                          "state": state, "class": cls, "payload": bytes.fromhex(payload), "dest": dest}
assert target_row is not None

# Highest signed CLOSED/AS_LEFT PTW-417 revision per bay, in MAIL-04 order B,D,A,C.
by_bay = {}
for r in receipts:
    if r["permit"] == "PTW-417" and r["state"] == "CLOSED" and r["fitment"] == "AS_LEFT" and r["signed"] is True:
        bay = r["bay"]
        if bay not in by_bay or int(r["revision"]) > int(by_bay[bay]["revision"]):
            by_bay[bay] = r
bays = ("B", "D", "A", "C")
assert set(by_bay) == set(bays)
target_serials = [by_bay[b]["serial"] for b in bays]
target_raw = b"".join(bytes.fromhex(s.split("-")[-1]) for s in target_serials)

route = json.loads((E / "recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
k04_commitment = acceptance["slot_sha256"]["K04"]

REPS = ("raw", "rawle", "hex", "serial")
LAYOUTS = ("serial", "job", "ptw", "job-class-dest", "ptw-bay",
           "ts-job-class-dest", "job-att-state-class-dest-ts", "json")
ORDERS = ("prev-msg", "msg-prev")
TRANSFORMS = ("direct", "xor-pad", "add-pad")

HASHES = {
    "md5": lambda p, m, j: hashlib.md5(j).digest(),
    "sha1-first16": lambda p, m, j: hashlib.sha1(j).digest()[:16],
    "sha256-first16": lambda p, m, j: hashlib.sha256(j).digest()[:16],
    "sha256-last16": lambda p, m, j: hashlib.sha256(j).digest()[-16:],
    "sha512-first16": lambda p, m, j: hashlib.sha512(j).digest()[:16],
    "sha512-last16": lambda p, m, j: hashlib.sha512(j).digest()[-16:],
    "sha3-first16": lambda p, m, j: hashlib.sha3_256(j).digest()[:16],
    "sha3-last16": lambda p, m, j: hashlib.sha3_256(j).digest()[-16:],
    "blake2s-128": lambda p, m, j: hashlib.blake2s(j, digest_size=16).digest(),
    "blake2b-128": lambda p, m, j: hashlib.blake2b(j, digest_size=16).digest(),
    "shake128-128": lambda p, m, j: hashlib.shake_128(j).digest(16),
    "shake256-128": lambda p, m, j: hashlib.shake_256(j).digest(16),
    "hmac-sha256-prevkey": lambda p, m, j: hmac.new(p, j, hashlib.sha256).digest()[:16],
    "hmac-sha256-msgkey": lambda p, m, j: hmac.new(m, j, hashlib.sha256).digest()[:16],
    "hmac-sha3-prevkey": lambda p, m, j: hmac.new(p, j, hashlib.sha3_256).digest()[:16],
    "hmac-sha3-msgkey": lambda p, m, j: hmac.new(m, j, hashlib.sha3_256).digest()[:16],
    "blake2s-prevkey": lambda p, m, j: hashlib.blake2s(j, key=p, digest_size=16).digest(),
    "blake2b-prevkey": lambda p, m, j: hashlib.blake2b(j, key=p, digest_size=16).digest(),
}

def source_bytes(n, rep):
    serial = legacy[n]["serial"]
    raw = bytes.fromhex(serial.split("-")[-1])
    return {"raw": raw, "rawle": raw[::-1], "hex": serial.split("-")[-1].encode(),
            "serial": serial.encode()}[rep]

def message_for(n, rep, layout):
    r, s = packets[n], legacy[n]
    src = source_bytes(n, rep)
    contexts = {
        "serial": b"",
        "job": r["job"].encode(),
        "ptw": s["permit"].encode(),
        "job-class-dest": (r["job"] + "|" + r["class"] + "|" + r["dest"]).encode(),
        "ptw-bay": (s["permit"] + "|" + s["bay"]).encode(),
        "ts-job-class-dest": "|".join((r["ts"], r["job"], r["class"], r["dest"])).encode(),
        "job-att-state-class-dest-ts": "|".join((r["job"], r["att"], r["state"], r["class"], r["dest"], r["ts"])).encode(),
        "json": json.dumps({"permit": s["permit"], "bay": s["bay"], "serial": s["serial"],
            "ts": r["ts"], "job": r["job"], "att": r["att"], "state": r["state"],
            "class": r["class"], "dest": r["dest"]}, sort_keys=True, separators=(",", ":")).encode(),
    }
    ctx = contexts[layout]
    return src if layout == "serial" else (ctx + b"|" + src if layout == "json" else src + b"|" + ctx)

def apply(value, transform, pad=None):
    if transform == "direct":
        return value
    if transform == "xor-pad":
        return bytes(a ^ b for a, b in zip(value, pad))
    return ((int.from_bytes(value, "big") + pad) & ((1 << 128) - 1)).to_bytes(16, "big")

scores = Counter()
full_models = []
max_score = 0
for rep, layout, order, hash_name, transform in itertools.product(REPS, LAYOUTS, ORDERS, HASHES, TRANSFORMS):
    transitions = []
    for n in range(391, 417):
        prev, msg = packets[n - 1]["payload"], message_for(n, rep, layout)
        joined = prev + msg if order == "prev-msg" else msg + prev
        transitions.append((HASHES[hash_name](prev, msg, joined), packets[n]["payload"]))
    if transform == "direct":
        score, denominator = sum(a == b for a, b in transitions), 26
    else:
        pad = (bytes(a ^ b for a, b in zip(*transitions[0]))
               if transform == "xor-pad"
               else (int.from_bytes(transitions[0][1], "big") - int.from_bytes(transitions[0][0], "big")) & ((1 << 128) - 1))
        holdouts = [(apply(a, transform, pad), b) for a, b in transitions[1:]]
        score, denominator = sum(a == b for a, b in holdouts), 25
    scores[f"{score}/{denominator}"] += 1
    max_score = max(max_score, score)
    if score == denominator:
        full_models.append((rep, layout, order, hash_name, transform))

# Synthetic positive: planted previous-state HMAC-SHA256 chain with one XOR pad.
prev = bytes(range(16))
pad = bytes.fromhex("1234567890ABCDEF1234567890ABCDEF")
srcs = [bytes((i, i ^ 0x55, i ^ 0xAA, 255 - i)) for i in range(27)]
synthetic = [prev]
for src in srcs[1:]:
    raw = hmac.new(prev, prev + src, hashlib.sha256).digest()[:16]
    nxt = bytes(a ^ b for a, b in zip(raw, pad))
    synthetic.append(nxt)
    prev = nxt
fit = hmac.new(synthetic[0], synthetic[0] + srcs[1], hashlib.sha256).digest()[:16]
recovered_pad = bytes(a ^ b for a, b in zip(fit, synthetic[1]))
synthetic_holdouts = 0
for i in range(2, 27):
    raw = hmac.new(synthetic[i - 1], synthetic[i - 1] + srcs[i], hashlib.sha256).digest()[:16]
    synthetic_holdouts += bytes(a ^ b for a, b in zip(raw, recovered_pad)) == synthetic[i]
assert recovered_pad == pad and synthetic_holdouts == 25

print(json.dumps({
    "source_pins": {**PINS, "acceptance.json": ACCEPTANCE_PIN},
    "historical_pairs": len(packets),
    "direct_transitions": 26,
    "padded_holdouts": 25,
    "models": len(REPS) * len(LAYOUTS) * len(ORDERS) * len(HASHES) * len(TRANSFORMS),
    "max_exact_holdouts": max_score,
    "score_histogram": dict(sorted(scores.items())),
    "full_holdout_models": full_models,
    "synthetic_positive": {"holdouts": synthetic_holdouts, "passed": True},
    "held_out_target": {
        "job": target_row["job"], "attempt": target_row["att"], "state": target_row["state"],
        "class": target_row["class"], "destination": target_row["dest"],
        "payload": target_row["payload"].hex().upper(),
        "source_bay_order": list(bays), "source_serials": target_serials,
        "source_block": target_raw.hex().upper(),
    },
    "k04_commitment": k04_commitment,
    "target_candidate": None if not full_models else "requires independent review",
}, indent=2))
