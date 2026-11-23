#!/usr/bin/env python3
"""All42 four-fresh conditional MT future-word carrier census.

Read-only source-pinned SFT. From repository root:
    python agents/agent1/k04_fourfresh_future_word_carriers_sft.py

Selected PS-0417 ACK2 bytes are withheld. Original model provenance unverified.
This tests exact full tempered MT words, not partial words or shifted encodings.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent10"))
from k04_all42_wholewindow_sft import (
    ALT_STAGES, SPOOL_SHA, build_basis, project, symbolic_words, temper, untemper
)
from k04_all42_fourfresh_countermodel_sft import GAP_DELTAS

RESOURCES = ROOT / "resources"
SPOOL = RESOURCES / "evidence/print/spool-reconstruction.log"
HEX_RUN = re.compile(rb"(?<![0-9A-Fa-f])[0-9A-Fa-f]{8,}(?![0-9A-Fa-f])")


def main() -> None:
    source = SPOOL.read_bytes()
    assert hashlib.sha256(source).hexdigest() == SPOOL_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        source, re.M,
    )
    assert len(rows) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417",
        b"2", b"ACK", b"RECOVER",
    )
    # Withhold the selected copied ACK2 PAYLOAD before any decoding.
    native = [
        None if i == 129 else tuple(
            untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4*j:4*j+4], "little"))
            for j in range(4)
        )
        for i, row in enumerate(rows)
    ]
    gaps = [b - a for a, b in zip(ALT_STAGES, ALT_STAGES[1:])]
    for index, delta in GAP_DELTAS.items():
        gaps[index] += delta
    assert min(gaps) >= 4 and max(gaps) <= 16
    stages = [0]
    for delta in gaps:
        stages.append(stages[-1] + delta)
    assert stages[129] == 955

    symbols = symbolic_words(0, 2101)
    basis = build_basis(native, tuple(stages), symbols, 0)
    assert len(basis) == 15434

    # Future stages are omitted from all original printer training equations.
    # A full 32-bit tempered word is projected only when all its native bits
    # reduce to constants of the intact printer source basis.
    predictions: dict[int, list[int]] = {}
    for stage in range(1041, 2101):
        known = [project(form, basis) for form in symbols[stage]]
        if any(free for free, value in known):
            continue
        native_word = sum(value << bit for bit, (free, value) in enumerate(known))
        predictions.setdefault(temper(native_word), []).append(stage)
    assert len(predictions) == 279

    original_files = [
        RESOURCES / name for name in (
            "START_HERE.md", "verify.py", "acceptance.json",
            "candidate.template.json"
        )
    ]
    original_files += sorted(
        p for p in (RESOURCES / "evidence").rglob("*")
        if p.is_file() and p != SPOOL
    )
    assert len(original_files) == 45
    raw_count = hex_count = 0
    hits = []
    for path in original_files:
        content = path.read_bytes()
        for offset in range(max(0, len(content) - 3)):
            fragment = content[offset:offset+4]
            raw_count += 1
            for endian in ("little", "big"):
                word = int.from_bytes(fragment, endian)
                if word in predictions:
                    hits.append((str(path.relative_to(RESOURCES)), "raw", offset, endian, predictions[word]))
        for match in HEX_RUN.finditer(content):
            sequence = match.group()
            for offset in range(len(sequence) - 7):
                fragment = bytes.fromhex(sequence[offset:offset+8].decode("ascii"))
                hex_count += 1
                for endian in ("little", "big"):
                    word = int.from_bytes(fragment, endian)
                    if word in predictions:
                        hits.append((str(path.relative_to(RESOURCES)), "hex8", match.start()+offset, endian, predictions[word]))

    assert raw_count == 100830, raw_count
    assert hex_count == 1440, hex_count
    assert hits == [], hits
    # Planted controls for both raw and decoded-hex word recognition.
    planted_word, planted_stages = next(iter(predictions.items()))
    planted = planted_word.to_bytes(4, "little")
    assert int.from_bytes(planted, "little") in predictions
    assert int.from_bytes(bytes.fromhex(planted.hex()), "little") in predictions
    print({
        "original_spool_sha256": SPOOL_SHA,
        "original_source_rank": len(basis),
        "selected_payload_decoded": False,
        "future_stage_range_inclusive": [1041, 2100],
        "fully_predicted_future_tempered_words": len(predictions),
        "original_files_scanned_except_selected_printer_spool": len(original_files),
        "raw_fourbyte_windows": raw_count,
        "hex8_windows": hex_count,
        "exact_original_future_word_matches": len(hits),
        "synthetic_raw_hex_recognition": True,
        "synthetic_stages": planted_stages,
        "original_K04_recovered": False,
    })


if __name__ == "__main__":
    main()
