"""H-17 K04 speculative serial-link LFSR scrambler, original commitment test.

Read-only. The source does not attest serial scrambling.
From repository root: python agents/agent18/k04_lfsr_scrambler_sft.py
"""
import hashlib
import json
import re
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
selected = [line for line in raw.decode().splitlines()
            if "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line]
assert len(selected) == 1 and selected[0].startswith("2026-10-03T18:02:00Z")
ack = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", selected[0]).group(1))
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT / "acceptance.json").read_text())
base = int.from_bytes(ack, "big") ^ int(route["K04"]["masked_component"], 16)
target = bytes.fromhex(accept["slot_sha256"]["K04"])
assert hashlib.sha256(base.to_bytes(16, "big")).digest() != target
POLY = (0x1021, 0x8005, 0x3D65, 0x8BB7, 0xC867)

def rev16(x):
    return int(f"{x:016b}"[::-1], 2)

def stream(seed, poly, reverse_clock, lsb_bit_first, reverse_bytes):
    feedback = rev16(poly) if reverse_clock else poly
    state = seed
    out = 0
    for i in range(128):
        bit = (state & 1) if reverse_clock else (state >> 15)
        if reverse_clock:
            state = (state >> 1) ^ (feedback if bit else 0)
        else:
            state = ((state << 1) & 65535) ^ (feedback if bit else 0)
        index = 15 - i // 8 if reverse_bytes else i // 8
        shift = i % 8 if lsb_bit_first else (7 - i % 8)
        out |= bit << (8 * (15 - index) + shift)
    return out

seed_planted = 0xA53D
model_planted = (0x1021, False, False, False)
fake_target = hashlib.sha256(
    (base ^ stream(seed_planted, *model_planted)).to_bytes(16, "big")
).digest()
assert fake_target != target

# GF2 linearity reduces every 65536-seed scan to a 16-base stream XOR walk.
count = 0
real = []
planted = []
started = perf_counter()
for poly in POLY:
    for clock in (False, True):
        for lsb in (False, True):
            for revbytes in (False, True):
                basis = [stream(1 << i, poly, clock, lsb, revbytes)
                         for i in range(16)]
                statecode = 0
                lastgray = 0
                for i in range(65536):
                    gray = i ^ (i >> 1)
                    diff = gray ^ lastgray
                    if diff:
                        statecode ^= basis[diff.bit_length() - 1]
                    lastgray = gray
                    coupon = (base ^ statecode).to_bytes(16, "big")
                    digest = hashlib.sha256(coupon).digest()
                    count += 1
                    if digest == target:
                        real.append((hex(poly), clock, lsb, revbytes,
                                     gray, coupon.hex().upper()))
                    if digest == fake_target and (
                        poly, clock, lsb, revbytes
                    ) == model_planted:
                        planted.append(gray)
assert planted == [seed_planted], planted
assert count == len(POLY) * 2 * 2 * 2 * 65536 and not real
print(json.dumps({
    "original_spool_SHA256": "PASS",
    "feedback_polynomials": [f"{p:04X}" for p in POLY],
    "shift_directions": 2,
    "bit_packings": 2,
    "byte_orders": 2,
    "complete_K04_candidate_checks": count,
    "planted_seed_control_hits": planted,
    "authentic_K04_commitment_matches": real,
    "elapsed_seconds": round(perf_counter() - started, 3)
}, indent=2))
