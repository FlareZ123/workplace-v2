"""SFT: four 32-bit aligned K04 coupon lanes from any preserved spool row.

Read-only. From repository root: python agents/agent7/k04_all_spool_word_mosaic_sft.py
Uses the original source, mask and commitment without writing any files.
"""
import hashlib
import itertools
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources/evidence/print/spool-reconstruction.log"
SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex(
    "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
)

raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256
lines = [line for line in raw.splitlines() if b"PAYLOAD=" in line]
rows = [bytes.fromhex(re.search(rb"PAYLOAD=([0-9A-F]{32})", line).group(1).decode())
        for line in lines]
selected = [i for i, line in enumerate(lines)
            if b"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line]
assert len(rows) == 133 and selected == [129]
assert rows[129].hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"

# Each complete candidate is the source-word mosaic XOR the official route mask.
lanes = [
    [bytes(x ^ y for x, y in zip(row[4*k:4*k+4], MASK[4*k:4*k+4]))
     for row in rows]
    for k in range(4)
]

def search(target: bytes, first_lane_limit: int, label: str):
    count = 0
    matches = []
    start = time.monotonic()
    for a in range(first_lane_limit):
        prefix_a = lanes[0][a]
        for b in range(133):
            prefix_ab = prefix_a + lanes[1][b]
            for c in range(133):
                prefix_abc = prefix_ab + lanes[2][c]
                for d in range(133):
                    component = prefix_abc + lanes[3][d]
                    count += 1
                    if hashlib.sha256(component).digest() == target:
                        matches.append(((a, b, c, d), component.hex().upper()))
                        print(f"{label}: FOUND a,b,c,d={a},{b},{c},{d} K04={component.hex().upper()}", flush=True)
        if a % 10 == 0:
            print(f"{label}: first lane {a+1}/{first_lane_limit}, "
                  f"assignments={count:,}", flush=True)
    print(f"{label}: assignments={count:,}, matches={len(matches)}, "
          f"elapsed_s={time.monotonic()-start:.2f}", flush=True)
    return count, matches

# A synthetic planted original with four distinct donors must be found exactly once.
planted = lanes[0][2] + lanes[1][3] + lanes[2][5] + lanes[3][7]
synthetic = hashlib.sha256(planted).digest()
count, matches = search(synthetic, 3, "synthetic")
assert count == 3 * 133**3
assert matches == [((2, 3, 5, 7), planted.hex().upper())]
print("Synthetic positive PASS", flush=True)

count, matches = search(TARGET, 133, "original")
assert count == 133**4
assert not matches, "Original K04 commitment matched; investigate the recovered candidate"
print("Original complete word-mosaic family NO_MATCH", flush=True)
