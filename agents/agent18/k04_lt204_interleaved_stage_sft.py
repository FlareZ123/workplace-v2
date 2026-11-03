"""Source-only p951 search for LT204 diagnostics interleaved by seq/revision.

Different from the existing p955 revision-major fixed-pad probe: retain all
32 historical revisions and test six explicitly source-defined orders of 32
direct 16-bit values at fixed per-reading MT draw strides (1..12).
Never use the untrusted selected row129, K04 mask/hash or K08 commitment.
Run from repo root: python agents/agent18/k04_lt204_interleaved_stage_sft.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
MOD = Path(__file__).resolve().parents[1] / "agent2/20261102_k04_multicarrier_p951_sft.py"
spec = importlib.util.spec_from_file_location("agent2_source_mt", MOD)
source_model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source_model)
values, masks, offset = source_model.source_closure(ROOT)
assert sum(m == 0xffffffff for m in masks) == 968
assert all(masks[offset + 951 + i] == 0 for i in range(4))
full = {i - offset: v for i, (v, m) in enumerate(zip(values, masks))
        if m == 0xffffffff}

tele = (ROOT / "evidence/telemetry/freeze-export.jsonl").read_bytes()
assert hashlib.sha256(tele).hexdigest() == (
    "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
)
records = [json.loads(line) for line in tele.decode().splitlines()]
diag = [(i, r) for i, r in enumerate(records)
        if r["tag"] == "LT-204" and r["field"] == "DIAG_WORD"
        and 0 <= r["seq"] < 8 and 1 <= r["revision"] <= 4]
assert len(diag) == 32
assert len({(r["seq"], r["revision"]) for _, r in diag}) == 32

def utc(r):
    return datetime.fromisoformat(r["ts"]).timestamp()

orders = {
    "seq_major": sorted(diag, key=lambda x: (x[1]["seq"], x[1]["revision"])),
    "revision_major": sorted(diag, key=lambda x: (x[1]["revision"], x[1]["seq"])),
    "time": sorted(diag, key=lambda x: (utc(x[1]), x[1]["revision"], x[1]["seq"])),
    "export_order": diag,
    "seq_reverse_revision": sorted(diag, key=lambda x: (x[1]["seq"], -x[1]["revision"])),
    "revision_reverse_seq": sorted(diag, key=lambda x: (x[1]["revision"], -x[1]["seq"])),
}
feature_views = {
    "native_hi": {i: (v >> 16) for i, v in full.items()},
    "native_lo": {i: (v & 0xffff) for i, v in full.items()},
    "tempered_hi": {i: (source_model.temper(v) >> 16) for i, v in full.items()},
    "tempered_lo": {i: (source_model.temper(v) & 0xffff) for i, v in full.items()},
}

def swap16(x):
    return ((x & 255) << 8) | (x >> 8)

# Independent planted source-stage witness. Some 32word positions are
# unobserved; leave arbitrary placeholders there. The selected stage is
# not consulted. The original source pins all 25 control halfwords.
view = feature_views["tempered_hi"]
planted = [view.get(q, (q * 4093 + 5) & 65535) for q in range(32)]
training = [(q, view[q]) for q in range(16) if q in view]
heldout = [(q, view[q]) for q in range(16, 32) if q in view]
assert (len(training), len(heldout)) == (10, 15)
assert all(planted[q] == v for q, v in training + heldout)
mutant = planted.copy()
mutant[training[0][0]] ^= 1
assert mutant[training[0][0]] != training[0][1]

informative = 0
maximum_fixed = 0
for stride in range(1, 13):
    for start in range(-2000, 4000 - 31 * stride):
        count = sum(start + stride*q in full for q in range(16))
        informative += count >= 3
        maximum_fixed = max(maximum_fixed, count)
assert (informative, maximum_fixed) == (22183, 16)

trials = 0
good_calibrations = []
best_matched = 0
for label, order in orders.items():
    observed = [r["value"] for _, r in order]
    for name, feature in feature_views.items():
        for orientation in ("direct", "swapped"):
            target = observed if orientation == "direct" else [swap16(x) for x in observed]
            for stride in range(1, 13):
                for start in range(-2000, 4000 - 31 * stride):
                    trials += 1
                    train = [(q, feature[start + stride*q]) for q in range(16)
                             if start + stride*q in feature]
                    agreeing = sum(p == target[q] for q,p in train)
                    best_matched = max(agreeing, best_matched)
                    if len(train) < 3 or agreeing != len(train):
                        continue
                    hold = [(q, feature[start + stride*q]) for q in range(16, 32)
                            if start + stride*q in feature]
                    disagreements = sum(p != target[q] for q,p in hold)
                    good_calibrations.append((label, name, orientation,
                                              stride, start, len(train),
                                              len(hold), disagreements))

assert trials == 3339936 and best_matched == 1 and not good_calibrations
print(json.dumps({
    "source":"32 original LT204 diagnostic u16 observations, six orders",
    "source_full_MT_words":len(full),
    "source_informative_stage_stride_layouts":informative,
    "tested_order_orientation_stage_stride":trials,
    "highest_original_agreeing_first16":best_matched,
    "original_calibrations_matching_3_or_more":len(good_calibrations),
    "original_independently_indexed_target_bits":0,
    "planted_source_stage_positive":{"first16_matches":len(training),
                                      "last16_matches":len(heldout),
                                      "mutated_negative":"PASS"}
},indent=2))
