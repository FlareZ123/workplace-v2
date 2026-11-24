#!/usr/bin/env python3
"""Bounded L-29/N four-word donor test against the conditional 4-fresh MT model.

This adds only source-derived tab-order encodings from the retained L-29
reconciliation and print-fleet note. A hit would be a candidate only: the CSV
is not the native PrevERP ledger and the four-fresh emitter is not authenticated.
No copied PS-0417 ACK2 payload is decoded.
"""
from __future__ import annotations

import csv
import decimal
import hashlib
import inspect
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "agents" / "agent10"))
import k04_fourfresh_future_source_donor_sft as base  # noqa: E402

RESOURCES = REPO / "resources"
CSV_REL = "evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv"
NOTE_REL = "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt"
csv_path = RESOURCES / CSV_REL
note_path = RESOURCES / NOTE_REL
csv_bytes = csv_path.read_bytes()
note_text = note_path.read_text(encoding="utf-8")

# Pin the two additional source objects that define the cohort and tab order.
base.SOURCE_HASHES[CSV_REL] = hashlib.sha256(csv_bytes).hexdigest()
base.SOURCE_HASHES[NOTE_REL] = hashlib.sha256(note_path.read_bytes()).hexdigest()

# The print-fleet note preserves the L-29/N binder order. The explicit PS-0417
# relationship is set-level only; this is not a ticket-to-job foreign key.
tab_order = ["ST-094", "ST-081", "ST-106", "ST-099", "ST-112"]
cursor = -1
for ticket in tab_order:
    pos = note_text.find(ticket, cursor + 1)
    assert pos > cursor, f"Missing or reordered L-29/N tab reference: {ticket}"
    cursor = pos
assert "PS-261003-0417" in note_text and "L-29/N" in note_text

# Skip the three comment lines before the CSV header.
with csv_path.open(newline="", encoding="utf-8") as stream:
    while True:
        position = stream.tell()
        line = stream.readline()
        if not line or not line.startswith("#"):
            stream.seek(position)
            break
    records = {row["line_ref"]: row for row in csv.DictReader(stream)}

for ticket in tab_order:
    row = records[ticket]
    assert row["source"] == "L29"
    assert row["run"] == "R3" and row["posting"] == "POSTED"
    assert row["account"] == "FA-17"
    assert row["folio_or_jacket"] == "H17-POL-17/A3"

def add_forms(label: str, tickets: list[str]) -> None:
    selected = [records[t] for t in tickets]
    suffixes = [int(t.rsplit("-", 1)[1]) for t in tickets]
    cents = [int(decimal.Decimal(r["amount_eur"]) * 100) for r in selected]
    packed = [(suffix << 16) | amount for suffix, amount in zip(suffixes, cents)]
    for form, values in (
        ("suffixes", suffixes),
        ("amount_cents", cents),
        ("suffix_x16_plus_cents", packed),
    ):
        payload = b"".join(v.to_bytes(4, "big") for v in values)
        base.BLOCKS[f"L29N_{label}_{form}"] = payload.hex().upper()

# Primary binder tabs 01-04, plus the explicitly conditional R3-POSTED
# comparison that substitutes tab05/ST-112 for tab04.
add_forms("tabs01_04", tab_order[:4])
add_forms("tabs01_02_03_05_conditional", [tab_order[0], tab_order[1], tab_order[2], tab_order[4]])

# Run the existing source-pinned model unchanged except for reporting:
# (1) the additional donor blocks, (2) any commitment hit without raw bytes,
# and (3) overlap/count diagnostics rather than assumptions about old totals.
source = inspect.getsource(base.main)
source = source.replace(
    'assert total == len(seen) == 2112',
    'print("CANDIDATE_COUNT", total, "DISTINCT", len(seen))',
)
source = source.replace(
    'originals.append((label, q, order, endian, already_native, component.hex().upper()))',
    'originals.append((label, q, order, endian, already_native))',
)
source = source.replace(
    'assert not originals, "Original K04 hit requires independent exact verification"',
    'print("K04_ACCEPTANCE_HITS", json.dumps(originals))',
)
source = source.replace(
    'assert len(old) == 748 and len(seen & old) == 0',
    'print("OVERLAP_WITH_PREVIOUS_748", len(seen & old))',
)
assert "K04_ACCEPTANCE_HITS" in source and "component.hex().upper()))" not in source
exec(compile(source, inspect.getsourcefile(base), "exec"), base.__dict__)

captured = io.StringIO()
with redirect_stdout(captured):
    base.main()
output = captured.getvalue()
print(output, end="")
(REPO / "k04_l29n_fourfresh_result.txt").write_text(output, encoding="utf-8")
