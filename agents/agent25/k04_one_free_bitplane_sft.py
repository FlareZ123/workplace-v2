"""H-17 complete-candidate K04 copy-wire bitplane test.

Run: python agents/agent25/k04_one_free_bitplane_sft.py
Source checksum pinned. Verifier, evidence and canonical candidate are read-only.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
payloads = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
assert len(payloads) == 133
selected = bytes.fromhex(payloads[129].decode("ascii"))
assert selected.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(routing["K04"]["masked_component"])
reduced = bytes(x ^ y for x,y in zip(selected,mask))
target = bytes.fromhex(accept["slot_sha256"]["K04"])
for plane in range(8):
    flag = 1<<plane
    fixed = bytes(value & ~flag for value in reduced)
    control_pattern = 0xA35C
    control = bytes(value|(((control_pattern>>position)&1)<<plane)
                    for position,value in enumerate(fixed))
    positive = 0
    original = 0
    for assignment in range(1<<16):
        candidate = bytes(value|(((assignment>>position)&1)<<plane)
                          for position,value in enumerate(fixed))
        digest = hashlib.sha256(candidate).digest()
        positive += digest == hashlib.sha256(control).digest()
        original += digest == target
    assert positive == 1 and original == 0, (plane,positive,original)
    print("bitplane",plane,"assignments",65536,
          "synthetic control PASS","original K04 hits",original)
print("PASS 524288 complete components; no accepted K04")
