"""K04 all-printer misaligned one-burst copier source test.

Run from repo root: python agents/agent7/k04_one_shifted_burst_sft.py
Reads unmodified original export; writes nothing.
"""
from pathlib import Path
from hashlib import sha256
from itertools import product
import re

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources" / "evidence" / "print" / "spool-reconstruction.log"
raw = SPOOL.read_bytes()
assert sha256(raw).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
rows = [bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
assert len(rows) == 133
copied = rows[129]
assert copied.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
target = bytes.fromhex(
    "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
)

def digest(coupon):
    return sha256(bytes(a ^ b for a, b in zip(coupon, mask))).digest()

# Plant a complete positive with a non-aligned, reversed 10-byte donor burst.
planted = copied[:4] + rows[132][2:12][::-1] + copied[14:]
planted_digest = digest(planted)
plant_count = 0
checked = 0
original_hits = []
for source_idx, donor in enumerate(rows):
    for length in range(1, 17):
        for output_start in range(17-length):
            for donor_start in range(17-length):
                frag = donor[donor_start:donor_start+length]
                for piece in (frag, frag[::-1]):
                    candidate = (
                        copied[:output_start] + piece
                        + copied[output_start+length:]
                    )
                    checked += 1
                    d = digest(candidate)
                    plant_count += d == planted_digest
                    if d == target:
                        original_hits.append(("splice", source_idx, length, output_start, donor_start, candidate.hex()))
                    candidate = bytearray(copied)
                    for i, byte in enumerate(piece):
                        candidate[output_start+i] ^= byte
                    d = digest(candidate)
                    checked += 1
                    plant_count += d == planted_digest
                    if d == target:
                        original_hits.append(("xor-overlay", source_idx, length, output_start, donor_start, candidate.hex()))

assert plant_count >= 1
print("planted synthetic positive PASS", plant_count)
print("original complete original SHA256 checks:", checked)
print("original K04 matches:", original_hits)
assert not original_hits
