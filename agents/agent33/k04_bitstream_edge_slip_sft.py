"""Selected H-17 ACK2 bitstream-edge displacement recovery test.

Hypothetical copy-stage bit slip, not historically authenticated. All evidence and
the original acceptance commitment remain read-only. Run as a single file from
the shared repository: python agents/agent33/k04_bitstream_edge_slip_sft.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "resources"
spool = (SOURCE / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
matches = [
    line for line in spool.decode("ascii").splitlines()
    if "JOB=PS-261003-0417" in line and "ATTEMPT=2" in line
    and "STATE=ACK" in line and "CLASS=RECOVER" in line
]
assert len(matches) == 1
payload = bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})", matches[0]).group(1))
assert payload.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
routing = json.loads((SOURCE / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((SOURCE / "acceptance.json").read_text())
mask = int.from_bytes(bytes.fromhex(routing["K04"]["masked_component"]), "big")
target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
assert target.hex() == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

copied = int.from_bytes(payload, "big")
planted = {("prefix", 3): 5, ("suffix", 19): 304570}
planted_hashes = {}
for (direction, bits), missing in planted.items():
    reconstructed = (
        (missing << (128 - bits)) | (copied >> bits)
        if direction == "prefix"
        else ((copied & ((1 << (128 - bits)) - 1)) << bits) | missing
    )
    planted_hashes[(direction, bits)] = hashlib.sha256(
        (reconstructed ^ mask).to_bytes(16, "big")
    ).digest()
    assert planted_hashes[(direction, bits)] != target

checks = 0
non_nibble_checks = 0
authentic = []
synthetic = []
for bits in range(1, 21):
    for direction in ("prefix", "suffix"):
        fixed = (
            copied >> bits if direction == "prefix"
            else (copied & ((1 << (128 - bits)) - 1)) << bits
        )
        for unknown in range(1 << bits):
            reconstructed = (
                (unknown << (128 - bits)) | fixed
                if direction == "prefix" else fixed | unknown
            )
            component = (reconstructed ^ mask).to_bytes(16, "big")
            digest = hashlib.sha256(component).digest()
            if digest == target:
                authentic.append([direction, bits, unknown, component.hex().upper()])
            if digest == planted_hashes.get((direction, bits)):
                synthetic.append([direction, bits, unknown])
        checks += 1 << bits
        if bits % 4:
            non_nibble_checks += 1 << bits

assert checks == 4194300
assert non_nibble_checks == 1957340
assert sorted(synthetic) == sorted(
    [[direction, bits, unknown] for (direction, bits), unknown in planted.items()]
)
print(json.dumps({
    "complete_original_sha256_checks": checks,
    "non_nibble_bitshift_checks": non_nibble_checks,
    "original_matches": authentic,
    "synthetic_positives": synthetic,
}, sort_keys=True))
