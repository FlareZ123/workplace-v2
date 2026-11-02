"""H17 K04 two-layer 32-bit lane/endianness copier reinterpretation.

Original late-Z selected ACK and transcribed mask, each independently
permuted at a 4x32 lane stage, with optional byte-reversal in each lane.
Original evidence is read-only. Synthetic nonidentity positive control.
Run: python agents/agent48/k04_dual_lane_serializer_sft.py
"""
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = bytes.fromhex(accept["slot_sha256"]["K04"])
selected = [line for line in spool.decode().splitlines()
            if "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line]
assert len(selected) == 1 and selected[0].startswith("2026-10-03T18:02:00Z")
payload = bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})", selected[0]).group(1))
assert payload.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"


def stage(value):
    words = [value[i:i + 4] for i in range(0, 16, 4)]
    for order in itertools.permutations(range(4)):
        for flips in itertools.product((False, True), repeat=4):
            yield b"".join(
                words[order[i]][::-1] if flips[i] else words[order[i]]
                for i in range(4)
            )


def digest(left, right):
    return hashlib.sha256(bytes(x ^ y for x, y in zip(left, right))).digest()


def main():
    a, b = list(stage(payload)), list(stage(mask))
    assert len(a) == len(b) == len(set(a)) == len(set(b)) == 384
    planted = digest(a[197], b[316])
    planted_count = 0
    matches = []
    distinct = set()
    for i, p in enumerate(a):
        for j, m in enumerate(b):
            component = bytes(x ^ y for x, y in zip(p, m))
            distinct.add(component)
            candidate = hashlib.sha256(component).digest()
            if candidate == planted:
                planted_count += 1
            if candidate == target:
                matches.append((i, j, component.hex().upper()))
    assert len(distinct) == 147456 and planted_count == 1
    print("original K04 matches", matches)
    print("two-layer assignments and unique candidates:", len(distinct))
    print("nonidentity planted stage positive:", planted_count)
    assert matches == []  # Original target still unrecovered.


if __name__ == "__main__":
    main()
