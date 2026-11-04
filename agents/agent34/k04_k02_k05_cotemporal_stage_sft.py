"""Original K02-to-K05 near-time MT donor falsifier. K04 selected ACK withheld.

Run: python agents/agent34/k04_k02_k05_cotemporal_stage_sft.py
Requires the original repository resources and Agent49's symbolic MT module.
"""
import hashlib
import itertools
import json
import struct
import sys
import zlib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

mt.LAST = 1500
RES = ROOT / "resources"
b, symbolic = mt.source(RES)
assert b.rank == 15365

telepath = RES / "evidence/telemetry/freeze-export.jsonl"
assert hashlib.sha256(telepath.read_bytes()).hexdigest() == "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
chosen = {}
for row in map(json.loads, telepath.read_text().splitlines()):
    if (row.get("tag") == "LT-204" and row.get("field") == "DIAG_WORD"
            and row.get("quality") == "GOOD" and row.get("state") == "HOLD"
            and row.get("seq") in range(8)
            and datetime.fromisoformat("2026-10-03T21:13:40+00:00") <= datetime.fromisoformat(row["ts"])
            < datetime.fromisoformat("2026-10-03T21:13:48+00:00")):
        idx = row["seq"]
        if idx not in chosen or row["revision"] > chosen[idx]["revision"]:
            chosen[idx] = row
assert sorted(chosen) == list(range(8))
halfwords = b"".join(int(chosen[i]["value"]).to_bytes(2, "big") for i in range(8))
assert halfwords.hex().upper() == "E1A5E474BAD7E853A2E8C71D3317D507"

recpath = RES / "evidence/recorder/trip-recorder.raw"
raw = recpath.read_bytes()
assert hashlib.sha256(raw).hexdigest() == "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
controls = {}
for i in range(88):
    r = raw[16 + 24*i:16 + 24*(i+1)]
    _, node, event, latch, seq = struct.unpack_from("<IHBBI", r)
    if node == 49 and event == 82 and 300 <= seq <= 303:
        assert zlib.crc32(r[:20]) == struct.unpack_from("<I", r, 20)[0]
        controls[latch] = r[12:16]
assert sorted(controls) == list(range(4))
selected = b"".join(controls[k] for k in range(4))
assert selected.hex().upper() == "FF8B78200A56E8586DCDA00EF01E4572"


def donor_modes():
    for endian in ("big", "little"):
        for reverse_words, reverse_halves, native in itertools.product((False, True), repeat=3):
            chunks = [halfwords[k:k+4] for k in (0, 4, 8, 12)]
            if reverse_halves:
                chunks = [c[2:]+c[:2] for c in chunks]
            if reverse_words:
                chunks.reverse()
            words = [int.from_bytes(c, endian) for c in chunks]
            yield (endian, reverse_words, reverse_halves, native), [w if native else mt.untemper(w) for w in words]


def source_basis(stage, native_words):
    ext = mt.Basis()
    ext.rows = b.rows.copy()
    ext.rank = b.rank
    for lane, word in enumerate(native_words):
        for bit, equation in enumerate(mt.get(symbolic, stage + lane)):
            ext.insert(equation, (word >> bit) & 1)
    assert ext.rank == 15493
    return ext


def compare(ext, stage, words, native):
    known = mismatches = 0
    for lane, word in enumerate(words):
        eqs = mt.get(symbolic, stage + lane)
        if not native:
            eqs = mt.temper(eqs)
        for bit, expr in enumerate(eqs):
            p = ext.predict(expr)
            if p is not None:
                known += 1
                mismatches += p != ((word >> bit) & 1)
    return known, mismatches


stats = {1178: {"tested": 0, "informative": 0, "passes": 0, "max_known": 0, "min_mismatch_when_96_known": 129},
         1405: {"tested": 0, "informative": 0, "passes": 0, "max_known": 0, "min_mismatch_when_96_known": 129}}

for donor_stage in (1178, 1405):
    for source_mode, source_words in donor_modes():
        ext = source_basis(donor_stage, source_words)
        for offset in range(4, 45):
            k05_stage = donor_stage + offset
            for endian, reverse, native in itertools.product(("big", "little"), (False, True), (False, True)):
                pieces = [selected[k:k+4] for k in (0, 4, 8, 12)]
                if reverse:
                    pieces.reverse()
                value_words = [int.from_bytes(p, endian) for p in pieces]
                known, differences = compare(ext, k05_stage, value_words, native)
                stats[donor_stage]["tested"] += 1
                stats[donor_stage]["max_known"] = max(stats[donor_stage]["max_known"], known)
                if known >= 16:
                    stats[donor_stage]["informative"] += 1
                    stats[donor_stage]["passes"] += differences == 0
                if known >= 96:
                    stats[donor_stage]["min_mismatch_when_96_known"] = min(
                        stats[donor_stage]["min_mismatch_when_96_known"], differences)

# Genuine source-constrained planted producer state, followed by an intentional one-bit corruption.
_, donor_words = next(donor_modes())
source = source_basis(1178, donor_words)
state = 0
for pivot, (eq, value) in sorted(source.rows.items()):
    if value ^ ((eq & state).bit_count() & 1):
        state |= 1 << pivot
stage = 1185
words = []
for lane in range(4):
    eqs = mt.temper(mt.get(symbolic, stage + lane))
    words.append(sum(((v & state).bit_count() & 1) << j for j, v in enumerate(eqs)))
assert compare(source, stage, words, native=False) == (128, 0)
mutated = words.copy()
mutated[0] ^= 1
assert compare(source, stage, mutated, native=False) == (128, 1)
for stage, item in stats.items():
    assert item["tested"] == 16 * 41 * 8
    assert item["max_known"] == 128
    assert item["informative"] == 4992 and item["passes"] == 0
    assert item["min_mismatch_when_96_known"] > 0
    print("K02_ST", stage, item)
print("PLANTED full-state positive PASS and single-bit negative detected; physical K04 withheld")
