"""H-17 K04 source-only AX16 and crossarchive native-stage screen.

Run from repository: python agents/agent31/k04_crossarchive_exact160_sft.py
Uses Agent49's original MT source basis and untouched resources.
Selected printer ACK2 is excluded by source(); target hashes are not consulted.
Historical common printer source and phase are hypotheses, not authenticated.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import source, get, temper, STARTS, ORIGIN, LAST, Basis

E = ROOT / "resources" / "evidence"
SOURCE_HASHES = {
    "transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "recorder/trip-recorder.raw": "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
    "procedures/RC-17-scans.txt": "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d",
}
for path, expected in SOURCE_HASHES.items():
    assert hashlib.sha256((E / path).read_bytes()).hexdigest() == expected

spool_basis, syms = source(ROOT / "resources")
assert spool_basis.rank == 15365
assert STARTS[34] == 250 and STARTS[129] == 951

def copy_basis(b):
    result = Basis()
    result.rows = b.rows.copy()
    result.rank = b.rank
    return result

def projected_bits(vectors, basis):
    value = mask = 0
    for bit, vector in enumerate(vectors):
        v = basis.predict(vector)
        if v is not None:
            mask |= 1 << bit
            value |= v << bit
    return mask, value

transfers = [json.loads(line) for line in
             (E / "transfers/transfer-audit.jsonl").read_text().splitlines()]
def transfer_halves(name):
    records = sorted((x for x in transfers if x.get("kind") == "CHUNK"
                      and x.get("transfer") == name),
                     key=lambda x: (x["seq"], x["attempt"]))
    assert len(records) == 16
    return records

ax = transfer_halves("AX-7778")
ax_halves = [int.from_bytes(bytes.fromhex(x["checkpoint"]), "little") for x in ax]
assert ax_halves[11:15] == [0x35AE, 0x78FE, 0x42DD, 0xFD35]
ax_start = STARTS[34] - 396 - 11
assert ax_start == -157

augmented = copy_basis(spool_basis)
direct_agreements = 0
new_rank = 0
for i, half in enumerate(ax_halves):
    vectors = temper(get(syms, ax_start + i))[16:32]
    known_mask, known_value = projected_bits(vectors, spool_basis)
    assert ((known_value ^ half) & known_mask) == 0, ("AX disagreement", i)
    direct_agreements += known_mask.bit_count()
    for j, v in enumerate(vectors):
        before = augmented.rank
        augmented.insert(v, (half >> j) & 1)
        new_rank += augmented.rank > before
assert direct_agreements == 122 and new_rank == 130
assert augmented.rank == 15495
print("AX16_FULL_SOURCE_MATCH", ax_start, direct_agreements,
      "individually_predicted_bits", new_rank, "new_rank")

# Independent population: original CRC-good CONTROL/AUX and RC-17 footer fields.
original = (E / "recorder/trip-recorder.raw").read_bytes()
assert original[:8] == b"TRP2DUMP"
assert int.from_bytes(original[10:12], "little") == 24
fields = []
for i in range(int.from_bytes(original[12:16], "little")):
    p = original[16 + 24*i:16 + 24*(i+1)]
    assert len(p) == 24
    if zlib.crc32(p[:20]) != int.from_bytes(p[20:24], "little"):
        continue
    node = int.from_bytes(p[4:6], "little")
    seq = int.from_bytes(p[8:12], "little")
    for role, position in (("CONTROL", 12), ("AUX", 16)):
        fields.append((f"TRP2:{node}:{seq}:{role}", p[position:position+4]))

for page in (E / "procedures/RC-17-scans.txt").read_text().split("\f"):
    head = re.search(r"DOCUMENT RC-17 / REV ([^ /]+) / SECTION ([^\n]+)", page)
    foot = re.search(r"Footer control strip:\s*([0-9A-F]{8})", page)
    if head and foot:
        fields.append((f"RC17:{head[1]}:{head[2]}", bytes.fromhex(foot[1])))
assert len(fields) == 180

projected = {"native": [], "tempered": []}
for stage in range(ORIGIN, LAST + 1):
    base = get(syms, stage)
    projected["native"].append(projected_bits(base, spool_basis))
    projected["tempered"].append(projected_bits(temper(base), spool_basis))

expected_null_matches = len(fields) * 2 * sum(
    2.0 ** -mask.bit_count()
    for p in projected.values() for mask, _ in p if mask.bit_count() >= 24
)
matches = []
tests = 0
for label, packet in fields:
    for endian in ("little", "big"):
        number = int.from_bytes(packet, endian)
        for mode, positions in projected.items():
            for idx, (mask, known) in enumerate(positions):
                if mask.bit_count() < 24:
                    continue
                tests += 1
                if ((number ^ known) & mask) == 0:
                    matches.append((label, idx + ORIGIN, endian, mode,
                                    mask.bit_count(), packet))
assert tests == 804240 and len(matches) == 16, (tests, len(matches))
assert all(endian == "little" and mode == "tempered"
           for _, _, endian, mode, _, _ in matches)
assert { (label, stage) for label, stage, *_ in matches } == {
    ("TRP2:50:24:CONTROL", -683),
    ("TRP2:50:7:CONTROL", -810),
    ("TRP2:50:12:CONTROL", -775),
    ("TRP2:49:201:CONTROL", -321),
    ("TRP2:49:203:CONTROL", -315),
    ("TRP2:50:13:CONTROL", -769),
    ("TRP2:50:70:CONTROL", -339),
    ("TRP2:49:992:CONTROL", -316),
    ("TRP2:50:44:CONTROL", -545),
    ("TRP2:50:45:CONTROL", -540),
    ("TRP2:49:990:CONTROL", -322),
    ("TRP2:50:41:CONTROL", -568),
    ("TRP2:49:993:CONTROL", -313),
    ("TRP2:50:25:CONTROL", -677),
    ("RC17:B:PURGE", -185),
    ("RC17:B:VERIFY", -186),
}
assert abs(expected_null_matches - 0.0008631683886051178) < 1e-12
print("FULL32_SCAN_FIELDS", len(fields), "TESTS", tests,
      "MATCHES", len(matches), "INDEPENDENT_UNIFORM_NULL_EXPECTATION",
      round(expected_null_matches, 9))
for label, stage, endian, mode, known_bits, data in matches:
    print("MATCH", label, stage, "source_known_bits", known_bits)

# Add the observed complete, stage-matched original 32-bit fields, then compute
# whether any selected-original native bit is actually constrained.
before = augmented.rank
for label, stage, endian, mode, known_bits, data in matches:
    vectors = temper(get(syms, stage)) if mode == "tempered" else get(syms, stage)
    value = int.from_bytes(data, endian)
    for bit, vector in enumerate(vectors):
        augmented.insert(vector, (value >> bit) & 1)
assert augmented.rank - before == 3
before_target = augmented.rank
for lane in range(4):
    for vector in get(syms, STARTS[129] + lane):
        # The true selected coupon is unknown; only vector rank is measured.
        augmented.insert(vector, 0)
assert augmented.rank - before_target == 128
print("ALL_AX16_PLUS_16_CROSSARCHIVE_NEW_RANK", augmented.rank - before_target,
      "K04_FREE_NATIVE_BITS", 128,
      "ORIGINAL_K04_RECOVERY", "MISSING")
