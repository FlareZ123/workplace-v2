"""H-17 source-only AX future-state donor scan, fixed strides 1..16.

A single reproducible test. Original selected printer ACK row129, K04 mask,
target commitment and K08 caption are excluded. Reuses Agent49's
source-pinned exact MT19937 GF(2) printer model and extends its future horizon.
Run: python agents/agent2/k04_ax_global_strides_sft.py
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "h17_p951_model", ROOT / "agents/agent49/k04_p951_symbolic_basis.py"
)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)

# A fixed, openly declared extended generator-state horizon.
model.LAST = 5400
basis, vectors = model.source(ROOT / "resources")
assert basis.rank == 15365
assert len(vectors) == model.LAST - model.ORIGIN + 1

transfers = ROOT / "resources/evidence/transfers/transfer-audit.jsonl"
raw = transfers.read_bytes()
assert hashlib.sha256(raw).hexdigest() == (
    "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
)
records = [json.loads(line) for line in raw.decode().splitlines()]
groups = {}
for item in records:
    if item["kind"] == "CHUNK":
        groups.setdefault(item["transfer"], []).append(item)
assert sorted(groups) == ["AX-7778", "AX-7781", "AX-7782", "AX-7783"]
assert all(len(items) == 16 for items in groups.values())

# Project the upper sixteen tempered bits of every native word into the
# span of 132 authentic intact spool coupons, selected target row omitted.
source_bits = []
for vector in vectors:
    tempered = model.temper(vector)
    fixed_mask = fixed_value = 0
    for bit in range(16, 32):
        v = basis.predict(tempered[bit])
        if v is not None:
            fixed_mask |= 1 << (bit - 16)
            fixed_value |= v << (bit - 16)
    source_bits.append((fixed_mask, fixed_value))

def scan(checkpoints):
    """Find all source-compatible 16-checkpoint starts at fixed stride 1..16."""
    best = (0, None, None)
    strong = []
    for stride in range(1, 17):
        for offset in range(len(source_bits) - 15 * stride):
            determined = 0
            for index, value in enumerate(checkpoints):
                mask, fixed = source_bits[offset + index * stride]
                determined += mask.bit_count()
                if ((value ^ fixed) & mask) != 0:
                    break
            else:
                if determined > best[0]:
                    best = (determined, stride, offset + model.ORIGIN)
                if determined >= 40:
                    strong.append((determined, stride, offset + model.ORIGIN))
    return best, strong

expected = {
    ("AX-7778", "native"): (11, 1, 4571),
    ("AX-7778", "byteswap"): (122, 1, -157),
    ("AX-7781", "native"): (14, 4, 4528),
    ("AX-7781", "byteswap"): (16, 8, 4986),
    ("AX-7782", "native"): (10, 8, 3530),
    ("AX-7782", "byteswap"): (14, 7, 4571),
    ("AX-7783", "native"): (10, 7, 2932),
    ("AX-7783", "byteswap"): (10, 7, 3708),
}
for name, items in sorted(groups.items()):
    data = [
        int(x["checkpoint"], 16)
        for x in sorted(items, key=lambda x: (x["seq"], x["attempt"]))
    ]
    for orientation in ("native", "byteswap"):
        values = data if orientation == "native" else [
            ((x >> 8) | ((x & 255) << 8)) for x in data
        ]
        best, strong = scan(values)
        assert best == expected[(name, orientation)], (name, orientation, best)
        if name == "AX-7778" and orientation == "byteswap":
            assert strong == [(122, 1, -157)]
        else:
            assert strong == [], (name, orientation, strong)
        print(name, orientation, "best_fixed_bits/stride/start", best,
              "source_consistent_40bit_stages", len(strong))

# An original independent AX-7778 source positive is recovered;
# there is no similarly supported stage for other original transfers.
assert source_bits[-157 - model.ORIGIN][0].bit_count() > 0
print("SOURCE_ONLY_PASS rank=15365, one strong AX-7778 original alignment;")
print("no indexed K04 future donor from this 16-value, stride-1..16 class")
