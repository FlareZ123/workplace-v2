"""Original K04 mask-serialization hypothesis: byte order within each 32-bit lane,
then four-word order, with fixed selected ACK bytes. Read-only SFT.
"""
import hashlib
import itertools
import json
import re
import time
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "resources"
spool = (root / "evidence/print/spool-reconstruction.log").read_text()
row = next(x for x in spool.splitlines() if
           x.startswith("2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER "))
payload = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", row).group(1))
mask = bytes.fromhex(json.loads((root / "evidence/recovery-routing.json").read_text())
                     ["K04"]["masked_component"])
target = bytes.fromhex(json.loads((root / "acceptance.json").read_text())
                       ["slot_sha256"]["K04"])
perms = tuple(itertools.permutations(range(4)))
words = tuple(mask[i:i+4] for i in range(0, 16, 4))

# Plant an independently specified valid member of the exact mask permutation class.
planted_order = (2, 0, 3, 1)
planted_indices = (13, 4, 17, 5)
planted_mask = b"".join(
    bytes(words[w][j] for j in perms[k])
    for w, k in zip(planted_order, planted_indices)
)
planted_digest = hashlib.sha256(bytes(a ^ b for a, b in
                                       zip(payload, planted_mask))).digest()
count = original_hits = control_hits = 0
started = time.perf_counter()
for order in perms:
    options = [tuple(bytes(words[w][j] for j in p) for p in perms)
               for w in order]
    for four in itertools.product(*options):
        permuted_mask = b"".join(four)
        value = bytes(a ^ b for a, b in zip(payload, permuted_mask))
        digest = hashlib.sha256(value).digest()
        original_hits += digest == target
        control_hits += digest == planted_digest
        count += 1

assert count == 24 ** 5, count
assert control_hits == 1, control_hits
print(f"assignments={count} original_hits={original_hits} "
      f"synthetic_hits={control_hits} seconds={time.perf_counter()-started:.3f}")
