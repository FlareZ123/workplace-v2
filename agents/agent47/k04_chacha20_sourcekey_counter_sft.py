"""Test a source-derived ChaCha20 event-coupon emitter on original H-17 evidence.

Python 3, cryptography >=46.0 (ChaCha20 uses 4-byte little-endian counter
and 12-byte nonce). Read-only reproducible single-file test.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

root = Path(__file__).resolve().parents[2] / "resources"
spool = root / "evidence/print/spool-reconstruction.log"
assert sha256(spool.read_bytes()).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)

rows = []
for line in spool.read_text().splitlines():
    if not line.startswith("2026-"):
        continue
    ts, *fields = line.split()
    row = {"ts": ts}
    row.update(dict(part.split("=", 1) for part in fields))
    row["PAYLOAD"] = bytes.fromhex(row["PAYLOAD"])
    rows.append(row)
assert len(rows) == 133
selected = 129
assert (rows[selected]["JOB"], rows[selected]["ATTEMPT"],
        rows[selected]["STATE"], rows[selected]["PAYLOAD"].hex().upper()) == (
            "PS-261003-0417", "2", "ACK", "A9A9DC5731A5E2AE879C47215C2559D5"
        )

accepted = json.loads((root / "candidate.json").read_text())
route = json.loads((root / "evidence/recovery-routing.json").read_text())
commitment = bytes.fromhex(json.loads((root / "acceptance.json").read_text())
                           ["slot_sha256"]["K04"])
names = ["K01", "K02", "K03", "K05", "K06", "K07"]
blocks = [bytes.fromhex(accepted[n]) for n in names]
mask = bytes.fromhex(route["K04"]["masked_component"])
desk = bytes.fromhex(route["K08"]["desk_nonce"])
blocks += [mask, desk]
keys = [sha256(b).digest() for b in blocks]
keys += [a + b for a in blocks for b in blocks]
assert len(keys) == 72 and all(len(key) == 32 for key in keys)


def coupon(key: bytes, row: dict, i: int, ni: int, ci: int, layout: int) -> bytes:
    """Construct an entire 16-byte packet before the original K04 reduction."""
    job = row["JOB"]
    attempt = int(row["ATTEMPT"])
    epoch = int(datetime.fromisoformat(row["ts"]).timestamp())
    nonce_forms = (
        bytes(12), mask[:12], desk[:12],
        sha256(job.encode("ascii")).digest()[:12],
        sha256(f"{job}|{attempt}|{row['CLASS']}|{row['DEST']}".encode("ascii")).digest()[:12],
        epoch.to_bytes(8, "little") + attempt.to_bytes(4, "little"),
    )
    counter_forms = (0, 1, i, int(job.rsplit("-", 1)[1]), epoch & 0xFFFFFFFF)
    initial = counter_forms[ci].to_bytes(4, "little") + nonce_forms[ni]
    stream = Cipher(algorithms.ChaCha20(key, initial), mode=None).encryptor()
    output = stream.update(bytes(64))
    chunk = output[(layout // 3) * 16 : (layout // 3 + 1) * 16]
    if layout % 3 == 1:
        return b"".join(chunk[j:j+4] for j in (12, 8, 4, 0))
    if layout % 3 == 2:
        return b"".join(chunk[j:j+4][::-1] for j in (0, 4, 8, 12))
    return chunk


def component(block: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(block, mask))


controls = (0, 3, 43, 84, 127)
configurations = ((ki, ni, ci, li)
                  for ki in range(len(keys))
                  for ni in range(6)
                  for ci in range(5)
                  for li in range(12))
source_fits = 0
max_control_hits = 0
target_hits = []
count = 0
planted = (3, 4, 2, 7)
planted_controls = [coupon(keys[planted[0]], rows[i], i, *planted[1:])
                    for i in controls]
planted_target = sha256(component(
    coupon(keys[planted[0]], rows[selected], selected, *planted[1:]))).digest()
planted_source_fits = 0
planted_target_hits = 0

for ki, ni, ci, li in configurations:
    count += 1
    key = keys[ki]
    generated_controls = [coupon(key, rows[i], i, ni, ci, li)
                          for i in controls]
    n = sum(a == rows[i]["PAYLOAD"]
            for i, a in zip(controls, generated_controls))
    max_control_hits = max(max_control_hits, n)
    source_fits += n == len(controls)
    planted_source_fits += generated_controls == planted_controls
    selected_packet = coupon(key, rows[selected], selected, ni, ci, li)
    digest = sha256(component(selected_packet)).digest()
    if digest == commitment:
        target_hits.append((ki, ni, ci, li))
    planted_target_hits += digest == planted_target

print("original_source_sha256=PASS rows=133 selected=129")
print(f"keys={len(keys)} nonces=6 counters=5 layouts=12 tested={count}")
print(f"original_control_fits={source_fits} max_controls={max_control_hits}/5")
print(f"original_K04_commitment_hits={len(target_hits)} {target_hits}")
print(f"synthetic_control_fits={planted_source_fits} synthetic_target_hits={planted_target_hits}")
assert (count, source_fits, max_control_hits, len(target_hits),
        planted_source_fits, planted_target_hits) == (25920, 0, 0, 0, 1, 1)
