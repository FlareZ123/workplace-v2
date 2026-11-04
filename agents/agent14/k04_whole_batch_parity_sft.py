"""One-file source-only K04 whole-batch checksum probe; Python 3.11+."""
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "resources"
raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = {}
for line in raw.decode().splitlines():
    match = re.search(r"JOB=PS-261003-(\\d{4}) .*?PAYLOAD=([0-9A-F]{32})", line)
    if match and "ATTEMPT=1 STATE=ACK " in line:
        job = int(match[1])
        if 300 <= job <= 427:
            rows[job] = bytes.fromhex(match[2])
assert list(rows) == list(range(300, 428))
packets = list(rows.values())
routing = json.loads((root / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((root / "acceptance.json").read_text())
mask = bytes.fromhex(routing["K04"]["masked_component"])
target = acceptance["slot_sha256"]["K04"]

def combine(group):
    result = bytearray(16)
    for packet in group:
        for i, b in enumerate(packet):
            result[i] ^= b
    return bytes(result)

def slot_digest(coupon):
    component = bytes(a ^ b for a, b in zip(coupon, mask))
    return hashlib.sha256(component).hexdigest()

predictions = {}
for p in range(128):
    for bit in range(2):
        label = f"walsh_{p}_{bit}"
        coupon = combine(packets[i] for i in range(128)
                         if ((i & p).bit_count() & 1) == bit)
        predictions.setdefault(coupon, []).append(label)
for n in range(1, 129):
    predictions.setdefault(combine(packets[:n]), []).append(f"prefix_{n}")
    predictions.setdefault(combine(packets[-n:]), []).append(f"suffix_{n}")
hits = [labels for coupon, labels in predictions.items() if slot_digest(coupon) == target]
known = next(iter(predictions))
assert [value for value in predictions if slot_digest(value) == slot_digest(known)] == [known]
print(json.dumps({"predictions": 512, "unique": len(predictions),
                  "original_matches": hits, "planted_control": True}, indent=2))
