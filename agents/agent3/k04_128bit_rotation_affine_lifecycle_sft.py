#!/usr/bin/env python3
"""Bounded 128-bit rotation-plus-constant PS-0417 lifecycle test."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"
ROUTE = ROOT / "resources/evidence/recovery-routing.json"
ACCEPTANCE = ROOT / "resources/acceptance.json"
PINS = {
    SPOOL: "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    ROUTE: "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    ACCEPTANCE: "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
for path, expected in PINS.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == expected, (path, actual, expected)

routing = json.loads(ROUTE.read_text(encoding="utf-8"))
acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
mask = bytes.fromhex(routing["K04"]["masked_component"])
target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
assert len(mask) == len(target[:16]) == 16

def job_record(job: str, attempt: int, state: str, klass: str) -> dict[str, str]:
    for line in SPOOL.read_text(encoding="utf-8").splitlines():
        fields = dict(re.findall(r"(\\w+)=([^\\s]+)", line))
        if (
            fields.get("JOB") == job
            and fields.get("ATTEMPT") == str(attempt)
            and fields.get("STATE") == state
            and fields.get("CLASS") == klass
        ):
            return fields
    raise AssertionError((job, attempt, state, klass))

train_in = bytes.fromhex(job_record("PS-261003-0420", 1, "ACK", "STORES")["PAYLOAD"])
train_out = bytes.fromhex(job_record("PS-261003-0420", 2, "ACK", "RECOVER")["PAYLOAD"])
predecessors = {
    "PS-0417 prior ACK/LABEL attempt 1": bytes.fromhex(job_record("PS-261003-0417", 1, "ACK", "LABEL")["PAYLOAD"]),
    "PS-0417 RECOVER REQUESTED attempt 1": bytes.fromhex(job_record("PS-261003-0417", 1, "REQUESTED", "RECOVER")["PAYLOAD"]),
    "PS-0417 RECOVER REQUESTED attempt 3": bytes.fromhex(job_record("PS-261003-0417", 3, "REQUESTED", "RECOVER")["PAYLOAD"]),
}
selected_ack = bytes.fromhex(job_record("PS-261003-0417", 2, "ACK", "RECOVER")["PAYLOAD"])
assert train_in.hex().upper() == "31C9714DD36DB2677BB9006670A9DFFD"
assert train_out.hex().upper() == "432475F72A62DB39F3D5693E2C937FA4"
assert selected_ack.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
assert all(len(x) == 16 for x in [train_in, train_out, selected_ack, *predecessors.values()])

MOD = (1 << 128) - 1

def rotl128(x: int, r: int) -> int:
    r %= 128
    return x if r == 0 else ((x << r) | (x >> (128 - r))) & MOD

def as_int(b: bytes) -> int:
    return int.from_bytes(b, "big")

def as_bytes(x: int) -> bytes:
    return (x & MOD).to_bytes(16, "big")

# Synthetic positive controls exercise both fit/predict paths independently.
syn_train_x = int("1234567890ABCDEF0011223344556677", 16)
syn_test_x = int("FEDCBA0987654321FFEEDDCCBBAA9988", 16)
syn_r = 37
syn_c = int("A55A0123456789ABCDEF9876543210FF", 16)
syn_train_y_xor = rotl128(syn_train_x, syn_r) ^ syn_c
fit_c_xor = syn_train_y_xor ^ rotl128(syn_train_x, syn_r)
assert (rotl128(syn_test_x, syn_r) ^ fit_c_xor) == (rotl128(syn_test_x, syn_r) ^ syn_c)
syn_train_y_add = (rotl128(syn_train_x, syn_r) + syn_c) & MOD
fit_c_add = (syn_train_y_add - rotl128(syn_train_x, syn_r)) & MOD
assert (rotl128(syn_test_x, syn_r) + fit_c_add) & MOD == (rotl128(syn_test_x, syn_r) + syn_c) & MOD

hits = []
exact_payload_matches = []
predictions = 0
for r in range(128):
    rotated_train = rotl128(as_int(train_in), r)
    c_xor = as_int(train_out) ^ rotated_train
    c_add = (as_int(train_out) - rotated_train) & MOD
    for name, predecessor in predecessors.items():
        x = as_int(predecessor)
        predicted = {
            "ROTL128-XOR-constant": as_bytes(rotl128(x, r) ^ c_xor),
            "ROTL128-add-constant": as_bytes((rotl128(x, r) + c_add) & MOD),
        }
        for model, payload in predicted.items():
            predictions += 1
            component = bytes(a ^ b for a, b in zip(payload, mask))
            if payload == selected_ack:
                exact_payload_matches.append((r, name, model))
            if hashlib.sha256(component).digest() == target:
                hits.append((r, name, model, payload.hex().upper(), component.hex().upper()))

print(f"predictions={predictions}")
print("synthetic_positive_controls=2/2")
print(f"exact_selected_ACK2_payload_matches={len(exact_payload_matches)}")
print(f"K04_commitment_hits={len(hits)}")
print("RESULT=NO_MATCH" if not hits else "RESULT=MATCH")
assert predictions == 128 * 3 * 2
assert not exact_payload_matches
assert not hits
