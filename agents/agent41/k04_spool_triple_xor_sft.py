"""Agent41 original K04 three-spool-packet whole-block parity experiment.

Source-pinned read-only single-file test with a genuine planted triple positive.
Python 3 standard library. No changes to original evidence or commitments.
"""
import hashlib
import itertools
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
lines = [line for line in raw.decode().splitlines() if "PAYLOAD=" in line]
assert len(lines) == 133
selected = [i for i, line in enumerate(lines) if all(x in line for x in (
    "JOB=PS-261003-0417", "ATTEMPT=2", "CLASS=RECOVER", "STATE=ACK"
))]
assert selected == [129]
readings = [int(x, 16) for i, line in enumerate(lines) if i != 129
            for x in re.findall(r"PAYLOAD=([A-F0-9]{32})", line)]
assert len(readings) == 132
mask = int("8556C8CB6140A7F9A5123AC7571BEE1C", 16)
target = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
def digest(coupon):
    return hashlib.sha256((coupon ^ mask).to_bytes(16, "big")).digest()

plant = digest(readings[3] ^ readings[27] ^ readings[111])
count = planted = original = 0
all_values = set()
for a, b, c in itertools.combinations(range(132), 3):
    coupon = readings[a] ^ readings[b] ^ readings[c]
    all_values.add(coupon)
    hashed = digest(coupon)
    original += hashed == target
    planted += hashed == plant
    count += 1
assert count == len(all_values) == 374660
assert original == 0 and planted == 1
fingerprint = hashlib.sha256(b"".join(v.to_bytes(16, "big")
                                   for v in sorted(all_values))).hexdigest()
assert fingerprint == "b0ac45ae735f530e0da4f46d6a7d761320241182d6ba0cadc75e8ba23060728d"
pairs = {}
parity_four = 0
for a, b in itertools.combinations(range(132), 2):
    key = readings[a] ^ readings[b]
    if key in pairs and len({a,b,*pairs[key]}) == 4:
        parity_four += 1
    else:
        pairs.setdefault(key, (a,b))
assert parity_four == 0
selected_job = [int(re.search(r"PAYLOAD=([A-F0-9]{32})", line).group(1), 16)
                for k, line in enumerate(lines) if k != 129
                and "JOB=PS-261003-0417" in line]
assert len(selected_job) == 3
selected_job_coupon = selected_job[0] ^ selected_job[1] ^ selected_job[2]
assert digest(selected_job_coupon) != target
print(f"ORIGINAL_SOURCE_PIN=PASS count={count} distinct={len(all_values)} "
      f"original_K04_hits={original} planted_full_positive={planted}")
print(f"FOUR_BLOCK_PARITY=0 same_job_coupon={selected_job_coupon:032X} "
      f"set_SHA256={fingerprint}")
