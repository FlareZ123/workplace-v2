"""Read-only H-17 source-parity coupon test, 1..4 intact printer rows."""
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = []
selected = []
for line in raw.decode().splitlines():
    if "PAYLOAD=" not in line:
        continue
    data = dict(piece.split("=", 1) for piece in line.split()[1:])
    value = int(data["PAYLOAD"], 16)
    if line.startswith("2026-10-03T18:02:00Z") and data["JOB"] == "PS-261003-0417" and data["ATTEMPT"] == "2":
        selected.append(value)
    else:
        rows.append((data["JOB"], data["CLASS"], value))
assert len(selected) == 1 and len(rows) == 132
mask = int("8556C8CB6140A7F9A5123AC7571BEE1C", 16)
target = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
planted = rows[10][2] ^ rows[33][2] ^ rows[78][2] ^ rows[102][2]
control = hashlib.sha256((planted ^ mask).to_bytes(16, "big")).digest()
cases = {"1":0, "2":0, "3":0, "4":0}
original_hits = []
planted_hits = []
for n in range(1, 5):
    for indices in itertools.combinations(range(132), n):
        coupon = 0
        for i in indices:
            coupon ^= rows[i][2]
        masked = hashlib.sha256((coupon ^ mask).to_bytes(16, "big")).digest()
        unmasked = hashlib.sha256(coupon.to_bytes(16, "big")).digest()
        cases[str(n)] += 2
        if masked == target:
            original_hits.append(("route_xor", indices, (coupon ^ mask).to_bytes(16, "big").hex()))
        if unmasked == target:
            original_hits.append(("direct", indices, coupon.to_bytes(16, "big").hex()))
        if masked == control:
            planted_hits.append(indices)
    assert cases[str(n)] == math.comb(132, n) * 2
assert planted_hits == [(10, 33, 78, 102)]
print(json.dumps({"source_rows":132, "excluded_untrusted_ack2":True,
                  "orders":cases, "total_checks":sum(cases.values()),
                  "real_hits":original_hits,
                  "planted_exact_four_source_positive":planted_hits}, indent=2))
