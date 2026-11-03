"""Source-only two-footer adjacency sweep in original RC17 documents.

Run: python agents/agent4/k04_rc17_b_pair_adjacency_sft.py
The selected original spool row129 is withheld by the shared source model.
"""
import hashlib
import importlib.util
import itertools
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "p951_source", ROOT / "agents/agent49/k04_p951_symbolic_basis.py"
)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
basis, states = model.source(ROOT / "resources")
assert basis.rank == 15365
raw = (ROOT / "resources/evidence/procedures/RC-17-scans.txt").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"
regex = r"DOCUMENT RC-17 / REV (B|C|D-draft) / SECTION (\w+).*?Footer control strip: ([0-9A-F]{8})"
rows = [(m.group(1), m.group(2), m.group(3))
        for m in re.finditer(regex, raw.decode(), re.S)]
assert len(rows) == 12
views = {}
for representation in ("native", "tempered"):
    pred = []
    for stage in range(model.ORIGIN, model.LAST + 1):
        bits = model.get(states, stage)
        if representation == "tempered":
            bits = model.temper(bits)
        known_mask = known_value = 0
        for bit, symbol in enumerate(bits):
            value = basis.predict(symbol)
            if value is not None:
                known_mask |= 1 << bit
                known_value |= value << bit
        pred.append((known_mask, known_value))
    views[representation] = pred

for endian in ("little", "big"):
    for representation, pred in views.items():
        candidates = {rev: [(section, h, int.from_bytes(bytes.fromhex(h), endian))
                            for r, section, h in rows if r == rev]
                      for rev in ("B", "C", "D-draft")}
        checked = 0
        matches = []
        for revision, fields in candidates.items():
            for a, z in itertools.permutations(fields, 2):
                for stage in range(model.ORIGIN, model.LAST):
                    m1, v1 = pred[stage - model.ORIGIN]
                    m2, v2 = pred[stage + 1 - model.ORIGIN]
                    count1, count2 = m1.bit_count(), m2.bit_count()
                    if count1 < 8 or count2 < 8 or count1 + count2 < 26:
                        continue
                    checked += 1
                    if not (((a[2] ^ v1) & m1) or ((z[2] ^ v2) & m2)):
                        matches.append((revision, a[0], z[0], stage, count1, count2))
        assert checked == (33336 if representation == "tempered" else 33516)
        expected = [("B", "VERIFY", "PURGE", -186, 32, 26)] if (
            endian, representation) == ("little", "tempered") else []
        assert matches == expected, (endian, representation, matches)
        print(endian, representation, "INFORMATIVE_PAIRS", checked,
              "MATCHES", matches)
print("TOTAL_INFORMATIVE_PAIRS", 133704)
print("ORIGINAL_SELECTED_K04_REMOVED_BEFORE_SOURCE_FIT; NO_RECOVERY_CLAIM")
