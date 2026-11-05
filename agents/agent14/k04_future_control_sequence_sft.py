"""Future-stage crossarchive source scan. Run from repository root:
python agents/agent14/k04_future_control_sequence_sft.py
Read-only. Selected printer row129 is excluded by the imported source basis.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "resources" / "evidence"
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

mt.LAST = 4015
basis, state = mt.source(ROOT / "resources")
assert basis.rank == 15365
seals = E / "maintenance/seal-receipts.jsonl"
recorder = E / "recorder/trip-recorder.raw"
procedure = E / "procedures/RC-17-scans.txt"
transfers = E / "transfers/transfer-audit.jsonl"
expected = {
    seals: "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    recorder: "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
    procedure: "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d",
    transfers: "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
}
for path, digest in expected.items():
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest

def projected(vectors):
    mask = value = 0
    for bit, v in enumerate(vectors):
        p = basis.predict(v)
        if p is not None:
            mask |= 1 << bit
            value |= p << bit
    return mask, value

# All 44 genuine seal serials (2 32-bit byte orders).
seal_data = [json.loads(line) for line in seals.read_text().splitlines()]
assert len(seal_data) == 44
seal_values = [
    int.from_bytes(bytes.fromhex(row["serial"][3:]), endian)
    for row in seal_data for endian in ("little", "big")
]

# 168 CRC-valid recorder CONTROL/AUX words plus 12 RC-17 footer controls.
raw = recorder.read_bytes()
fields = []
for idx in range(int.from_bytes(raw[12:16], "little")):
    p = raw[16 + 24 * idx:16 + 24 * (idx+1)]
    if zlib.crc32(p[:20]) != int.from_bytes(p[20:24], "little"):
        continue
    fields.extend([p[12:16], p[16:20]])
for page in procedure.read_text().split("\f"):
    h = re.search(r"DOCUMENT RC-17 / REV ([^ /]+) / SECTION ([^\n]+)", page)
    f = re.search(r"Footer control strip:\s*([0-9A-F]{8})", page)
    if h and f:
        fields.append(bytes.fromhex(f[1]))
assert len(fields) == 180
control_values = [int.from_bytes(x, endian) for x in fields for endian in ("little", "big")]

# All four 16-element transfer checkpoint chronologies, including revisions.
transfer_rows = [json.loads(line) for line in transfers.read_text().splitlines()]
ax = {}
for transfer in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
    records = sorted(
        (r for r in transfer_rows
         if r.get("kind") == "CHUNK" and r.get("transfer") == transfer),
        key=lambda r: (r["seq"], r["attempt"]),
    )
    assert len(records) == 16
    for endian in ("little", "big"):
        ax[transfer, endian] = [
            int.from_bytes(bytes.fromhex(r["checkpoint"]), endian)
            for r in records
        ]

# Build the once-only source projector for all stage indices.
mode_series = {"native": [], "tempered": []}
for stage in range(mt.ORIGIN, 4016):
    native = mt.get(state, stage)
    mode_series["native"].append(projected(native))
    mode_series["tempered"].append(projected(mt.temper(native)))

seal_checks = control_checks = 0
seal_hits = control_hits = 0
seal_null = control_null = 0.0
for stage in range(1041, 4001):
    # Full serials are expected to be conventional tempered outputs.
    seal_mask, seal_value = mode_series["tempered"][stage-mt.ORIGIN]
    k = seal_mask.bit_count()
    if k >= 24:
        seal_null += len(seal_values) * 2.0 ** -k
        for word in seal_values:
            seal_checks += 1
            seal_hits += (word ^ seal_value) & seal_mask == 0
    for mode in ("native", "tempered"):
        control_mask, control_value = mode_series[mode][stage-mt.ORIGIN]
        k = control_mask.bit_count()
        if k >= 24:
            control_null += len(control_values) * 2.0 ** -k
            for word in control_values:
                control_checks += 1
                control_hits += (word ^ control_value) & control_mask == 0

assert seal_checks == 43120 and seal_hits == 0
assert control_checks == 437760 and control_hits == 0

# Original historical positive anchor retained at native -157.
series = mode_series["tempered"]
known = wrong = 0
for i, expected_half in enumerate(ax["AX-7778", "little"]):
    mask, value = series[-157 - mt.ORIGIN + i]
    mask >>= 16
    value >>= 16
    known += mask.bit_count()
    wrong += ((expected_half ^ value) & mask).bit_count()
assert (known, wrong) == (122, 0)

candidate_matches = []
tested_starts = 0
for transfer in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
    for endian in ("little", "big"):
        values = ax[transfer, endian]
        for mode in ("native", "tempered"):
            source = mode_series[mode]
            for half in ("low16", "high16"):
                shift = 16 if half == "high16" else 0
                for start in range(1041, 4001):
                    predicted = [
                        source[start-mt.ORIGIN+i] for i in range(16)
                    ]
                    masks = [((m >> shift) & 65535) for m, _ in predicted]
                    expected_values = [(v >> shift) & 65535 for _, v in predicted]
                    nbits = sum(m.bit_count() for m in masks)
                    if nbits >= 48 and all(
                        ((a ^ b) & mask) == 0
                        for a, b, mask in zip(values, expected_values, masks)
                    ):
                        candidate_matches.append((transfer, endian, mode, half, start))
                    tested_starts += 1

assert tested_starts == 94720 and candidate_matches == []
print("SOURCE_RANK", basis.rank, "SELECTED_ROW_129_WITHHELD", True)
print("POSTTARGET_STAGES", "1041..4000", "SEAL_TESTS", seal_checks,
      "SEAL_HITS", seal_hits, "SEAL_NULL", seal_null)
print("CONTROL_TESTS", control_checks, "CONTROL_HITS", control_hits,
      "CONTROL_NULL", control_null)
print("AX_SEQUENCE_STARTS", tested_starts, "AX_MATCHES_GE48BITS",
      len(candidate_matches), "HISTORICAL_AX_ANCHOR", known, wrong)
print("K04_RECOVERY", "MISSING")
