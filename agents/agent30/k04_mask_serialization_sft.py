"""K04 mask serialization, retaining the selected copied ACK unchanged.

Tests the original mask in both 4x4 row-major and transposed column-major
geometries. Within each geometry, allow arbitrary four-lane order and
independent byte order within each four-byte lane. Read-only source SFT.
The analog of this search on the *payload*, not the mask, was performed
earlier by Agent31: agents/agent31/k04_lane_interleaver_sft.py.
"""
import hashlib
import itertools
import json
import re
import time
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "resources"
raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
row = next(x for x in raw.decode("ascii").splitlines() if
           x.startswith("2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER "))
payload = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", row).group(1))
mask = bytes.fromhex(json.loads((root / "evidence/recovery-routing.json").read_text())
                     ["K04"]["masked_component"])
target = bytes.fromhex(json.loads((root / "acceptance.json").read_text())
                       ["slot_sha256"]["K04"])
perms = tuple(itertools.permutations(range(4)))


def run(transpose):
    original = (
        bytes(mask[4*r+c] for c in range(4) for r in range(4))
        if transpose else mask
    )
    words = tuple(original[i:i+4] for i in range(0, 16, 4))
    order = (2, 0, 3, 1)
    indices = (13, 4, 17, 5)
    planted = b"".join(
        bytes(words[w][j] for j in perms[k])
        for w, k in zip(order, indices)
    )
    goal = hashlib.sha256(bytes(a ^ b for a, b in zip(payload, planted))).digest()
    count = original_hits = control_hits = 0
    started = time.perf_counter()
    for order in perms:
        options = [tuple(bytes(words[w][j] for j in p) for p in perms)
                   for w in order]
        for four in itertools.product(*options):
            candidate_mask = b"".join(four)
            value = bytes(a ^ b for a, b in zip(payload, candidate_mask))
            digest = hashlib.sha256(value).digest()
            original_hits += digest == target
            control_hits += digest == goal
            count += 1
    assert count == 24 ** 5
    assert control_hits == 1
    print(f"transpose={transpose} assignments={count} "
          f"original_hits={original_hits} synthetic_hits={control_hits} "
          f"seconds={time.perf_counter()-started:.3f}")
    return original_hits


if __name__ == "__main__":
    assert run(False) + run(True) == 0, "Original commitment hit: investigate!"
