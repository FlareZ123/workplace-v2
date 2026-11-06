"""Source-only H-17 K04 donor probe: all 32 genuine K02 telemetry revisions.
Do not use selected printer buffer, K04 hash, or recovery mask in fitting.
Run: python agents/agent3/k04_k02_allrevisions_mt_source_sft.py
"""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from agents.agent49.k04_p951_symbolic_basis import source, get, temper, ORIGIN, LAST

ROOT = REPO / "resources"
TELEMETRY = ROOT / "evidence/telemetry/freeze-export.jsonl"
AX = ROOT / "evidence/transfers/transfer-audit.jsonl"
assert hashlib.sha256(TELEMETRY.read_bytes()).hexdigest() == (
    "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
)
basis, symbolic = source(ROOT)
assert basis.rank == 15365

records = [json.loads(line) for line in TELEMETRY.read_text().splitlines()]
diag = {(r["seq"], r["revision"]): r["value"] for r in records
        if r["field"] == "DIAG_WORD" and 0 <= r["seq"] <= 7
        and 1 <= r["revision"] <= 4}
assert len(diag) == 32
orders = {
    "seq_rev": [diag[s, r] for s in range(8) for r in range(1, 5)],
    "rev_seq": [diag[s, r] for r in range(1, 5) for s in range(8)],
}
selected = []
for seq in range(8):
    eligible = [r for r in records if r["field"] == "DIAG_WORD"
                and r["seq"] == seq and r["quality"] == "GOOD"
                and r["state"] == "HOLD" and 1 <= r["revision"] <= 4]
    selected.append(max(eligible, key=lambda r: r["revision"])["value"])
groups = {f"rev{revision}": [diag[s, revision] for s in range(8)]
          for revision in range(1, 5)}
groups["selected"] = selected

# Source determined bits are computed only from the other 132 spool packets.
predictions = {}
for view in ("native", "tempered"):
    predicted = []
    for pos in range(ORIGIN, LAST + 1):
        bits = get(symbolic, pos)
        if view == "tempered":
            bits = temper(bits)
        mask = value = 0
        for bit, expression in enumerate(bits):
            fixed = basis.predict(expression)
            if fixed is not None:
                mask |= 1 << bit
                value |= fixed << bit
        predicted.append((mask, value))
    predictions[view] = predicted

def swap16(n):
    return ((n & 255) << 8) | (n >> 8)

def scan(cases, maximum_stride, minimum_fixed):
    tested = found = 0
    for values in cases.values():
        for prediction in predictions.values():
            for shift in (0, 16):
                for swap in (False, True):
                    observations = [swap16(x) if swap else x for x in values]
                    for stride in range(1, maximum_stride + 1):
                        for start in range(ORIGIN, LAST - (len(values)-1)*stride + 1):
                            tested += 1
                            fixed_bits = mismatches = 0
                            for index, word in enumerate(observations):
                                known, expected = prediction[start+index*stride-ORIGIN]
                                mask = (known >> shift) & 65535
                                fixed_bits += mask.bit_count()
                                mismatches += (((expected >> shift) ^ word) & mask).bit_count()
                                if mismatches > 1:
                                    break
                            if mismatches == 0 and fixed_bits >= minimum_fixed:
                                found += 1
    return tested, found

full = scan(orders, 8, 24)
eight = scan(groups, 64, 48)
assert full == (256192, 0), full
assert eight == (4898560, 0), eight

# Genuine independent source-positive: all 16 AX-7778 halfwords at -157
# match the conditional printer MT source, 122 individually fixed bits.
transfers = [json.loads(x) for x in AX.read_text().splitlines()]
ax = sorted((r for r in transfers if r["kind"] == "CHUNK"
             and r["transfer"] == "AX-7778"),
            key=lambda r: (r["seq"], r["attempt"]))
assert len(ax) == 16
total_fixed = 0
for i, r in enumerate(ax):
    observed = int.from_bytes(bytes.fromhex(r["checkpoint"]), "little")
    mask, word = predictions["tempered"][-157+i-ORIGIN]
    mask = (mask >> 16) & 65535
    assert (((word >> 16) ^ observed) & mask) == 0
    total_fixed += mask.bit_count()
assert total_fixed == 122, total_fixed
print("K02_ALL_REVISIONS_SFT PASS: 32-record contiguous/stride models", full,
      "8-record channel models", eight, "AX7778 positive source bits", total_fixed)
