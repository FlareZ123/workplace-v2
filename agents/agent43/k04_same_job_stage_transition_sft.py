#!/usr/bin/env python3
"""Read-only H-17 same-job prior-stage -> RECOVER transition SFT.

Run from the workplace-v2 repository root. Requires Python's cryptography package
for AES-CMAC. No source, candidate, route, acceptance, or verifier file is changed.
"""
from pathlib import Path
from datetime import datetime
import hashlib
import hmac
import json
import re
from cryptography.hazmat.primitives.cmac import CMAC
from cryptography.hazmat.primitives.ciphers import algorithms

ROOT = Path("resources")
E = ROOT / "evidence"
PINS = {
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
}
for name, expected in PINS.items():
    assert hashlib.sha256((E / name).read_bytes()).hexdigest() == expected, name
ACCEPTANCE_PIN = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
assert hashlib.sha256((ROOT / "acceptance.json").read_bytes()).hexdigest() == ACCEPTANCE_PIN

route = json.loads((E / "recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
target_commitment = acceptance["slot_sha256"]["K04"]

by_job = {}
for line in (E / "print/spool-reconstruction.log").read_text().splitlines():
    m = re.search(r"^(\S+) JOB=(PS-261003-(\d{4})) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$", line)
    if m:
        ts, job, suffix, attempt, state, cls, payload, dest = m.groups()
        by_job.setdefault(suffix, []).append({
            "ts": ts, "job": job, "att": attempt, "state": state, "class": cls,
            "payload": bytes.fromhex(payload), "dest": dest, "line": line.encode(),
        })

transitions = {}
for suffix in ("0417", "0420"):
    rows = by_job[suffix]
    prior = [r for r in rows if r["att"] == "1" and r["state"] == "ACK"][0]
    final = [r for r in rows if r["att"] == "2" and r["state"] == "ACK" and r["class"] == "RECOVER"][0]
    transitions[suffix] = (prior, final)
prior_control, final_control = transitions["0420"]
prior_target, final_target = transitions["0417"]

def metadata(prior, final, layout):
    delta = int((datetime.fromisoformat(final["ts"].replace("Z", "+00:00")) -
                 datetime.fromisoformat(prior["ts"].replace("Z", "+00:00"))).total_seconds())
    fields = {
        "job": final["job"].encode(),
        "job-classes": (final["job"] + "|" + prior["class"] + "|" + final["class"]).encode(),
        "job-class-dest": (final["job"] + "|" + prior["class"] + "|" + prior["dest"] +
                           "|" + final["class"] + "|" + final["dest"]).encode(),
        "timestamps": (prior["ts"] + "|" + final["ts"]).encode(),
        "delta": str(delta).encode(),
        "stages": "|".join((final["job"], prior["att"], prior["state"], prior["class"],
            prior["dest"], final["att"], final["state"], final["class"], final["dest"])).encode(),
        "full-lines": prior["line"] + b"\n" + final["line"],
        "json": json.dumps({
            "previous": {k: (v.hex().upper() if k == "payload" else v)
                         for k, v in prior.items() if k != "line"},
            "final": {k: (v.hex().upper() if k == "payload" else v)
                      for k, v in final.items() if k != "line"},
        }, sort_keys=True, separators=(",", ":")).encode(),
    }
    return fields[layout]

def cmac(key, message):
    c = CMAC(algorithms.AES(key))
    c.update(message)
    return c.finalize()

FUNCS = {
    "md5": lambda prev, msg, joined: hashlib.md5(joined).digest(),
    "sha1-first16": lambda prev, msg, joined: hashlib.sha1(joined).digest()[:16],
    "sha256-first16": lambda prev, msg, joined: hashlib.sha256(joined).digest()[:16],
    "sha256-last16": lambda prev, msg, joined: hashlib.sha256(joined).digest()[-16:],
    "sha512-first16": lambda prev, msg, joined: hashlib.sha512(joined).digest()[:16],
    "sha512-last16": lambda prev, msg, joined: hashlib.sha512(joined).digest()[-16:],
    "sha3-first16": lambda prev, msg, joined: hashlib.sha3_256(joined).digest()[:16],
    "sha3-last16": lambda prev, msg, joined: hashlib.sha3_256(joined).digest()[-16:],
    "blake2s": lambda prev, msg, joined: hashlib.blake2s(joined, digest_size=16).digest(),
    "blake2b": lambda prev, msg, joined: hashlib.blake2b(joined, digest_size=16).digest(),
    "shake128": lambda prev, msg, joined: hashlib.shake_128(joined).digest(16),
    "shake256": lambda prev, msg, joined: hashlib.shake_256(joined).digest(16),
    "hmac256-prevkey": lambda prev, msg, joined: hmac.new(prev, joined, hashlib.sha256).digest()[:16],
    "hmac256-msgkey": lambda prev, msg, joined: hmac.new(msg, joined, hashlib.sha256).digest()[:16],
    "hmac3-prevkey": lambda prev, msg, joined: hmac.new(prev, joined, hashlib.sha3_256).digest()[:16],
    "hmac3-msgkey": lambda prev, msg, joined: hmac.new(msg, joined, hashlib.sha3_256).digest()[:16],
    "blake2s-prevkey": lambda prev, msg, joined: hashlib.blake2s(joined, key=prev, digest_size=16).digest(),
    "blake2b-prevkey": lambda prev, msg, joined: hashlib.blake2b(joined, key=prev, digest_size=16).digest(),
    "cmac-prevkey": lambda prev, msg, joined: cmac(prev, joined),
    "cmac-maskkey": lambda prev, msg, joined: cmac(mask, joined),
    "cmac-noncekey": lambda prev, msg, joined: cmac(nonce, joined),
}
LAYOUTS = ("job", "job-classes", "job-class-dest", "timestamps", "delta", "stages", "full-lines", "json")
ORDERS = ("prev-msg", "msg-prev")
TRANSFORMS = ("direct", "xor-pad", "add-pad")

def raw_output(prior, final, layout, order, function):
    msg = metadata(prior, final, layout)
    joined = prior["payload"] + msg if order == "prev-msg" else msg + prior["payload"]
    return FUNCS[function](prior["payload"], msg, joined)

target_full_payload_predictions = []
k04_commitment_hits = []
direct_control_matches = 0
models = 0
for layout in LAYOUTS:
    for order in ORDERS:
        for function in FUNCS:
            control_raw = raw_output(prior_control, final_control, layout, order, function)
            target_raw = raw_output(prior_target, final_target, layout, order, function)
            direct_control_matches += control_raw == final_control["payload"]
            for transform in TRANSFORMS:
                models += 1
                if transform == "direct":
                    candidate = target_raw
                    if control_raw != final_control["payload"]:
                        continue
                elif transform == "xor-pad":
                    pad = bytes(a ^ b for a, b in zip(control_raw, final_control["payload"]))
                    candidate = bytes(a ^ b for a, b in zip(target_raw, pad))
                else:
                    pad = (int.from_bytes(final_control["payload"], "big") -
                           int.from_bytes(control_raw, "big")) & ((1 << 128) - 1)
                    candidate = ((int.from_bytes(target_raw, "big") + pad) &
                                 ((1 << 128) - 1)).to_bytes(16, "big")
                if candidate == final_target["payload"]:
                    target_full_payload_predictions.append((layout, order, function, transform))
                component = bytes(a ^ b for a, b in zip(candidate, mask))
                if hashlib.sha256(component).hexdigest() == target_commitment:
                    k04_commitment_hits.append((layout, order, function, transform, component.hex().upper()))

# Synthetic positive: a previous-payload HMAC transition with a global XOR pad.
synthetic_pad = bytes.fromhex("1234567890ABCDEF1234567890ABCDEF")
synthetic = []
for i in (1, 2):
    previous = bytes([i]) * 16
    message = f"PS-TEST-{i}|ACK|RECOVER|bench".encode()
    raw = hmac.new(previous, previous + message, hashlib.sha256).digest()[:16]
    output = bytes(a ^ b for a, b in zip(raw, synthetic_pad))
    synthetic.append((previous, message, output))
control = synthetic[0]
target = synthetic[1]
control_raw = hmac.new(control[0], control[0] + control[1], hashlib.sha256).digest()[:16]
fitted_pad = bytes(a ^ b for a, b in zip(control_raw, control[2]))
target_raw = hmac.new(target[0], target[0] + target[1], hashlib.sha256).digest()[:16]
synthetic_prediction = bytes(a ^ b for a, b in zip(target_raw, fitted_pad))
assert fitted_pad == synthetic_pad and synthetic_prediction == target[2]

print(json.dumps({
    "source_pins": {**PINS, "acceptance.json": ACCEPTANCE_PIN},
    "transitions": {
        suffix: {
            "prior_class": pair[0]["class"], "prior_payload": pair[0]["payload"].hex().upper(),
            "final_class": pair[1]["class"], "final_payload": pair[1]["payload"].hex().upper(),
        } for suffix, pair in transitions.items()
    },
    "metadata_layouts": list(LAYOUTS),
    "functions": list(FUNCS),
    "models": models,
    "direct_control_matches": direct_control_matches,
    "target_full_payload_predictions": target_full_payload_predictions,
    "K04_acceptance_hits": k04_commitment_hits,
    "synthetic_positive_passed": True,
}, indent=2))
