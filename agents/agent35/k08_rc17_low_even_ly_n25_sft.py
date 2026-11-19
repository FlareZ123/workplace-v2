#!/usr/bin/env python3
"""Target-blind RC-17 LOW-IF-EVEN side-channel locator probe.

This does NOT implement the official K06 reducer (which uses authorized Rev C),
and does NOT recover a K08 phrase. It tests whether the already-derived
LOW-IF-EVEN selector, applied to the lower/upper RC-17 revision pair in the
explicit service order, yields a reproducible locator worth adversarial review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED = {
    "procedures/RC-17-scans.txt": "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d",
    "procedures/document-register.log": "20d8dc63a28bab7084b6919207c50fb5bf957054f30b71c3ced0b3b5507e7f2c",
    "archive-labels.ini": "146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad",
    "crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
}


def pack_first_bit_as_lsb(data: bytes) -> bytes:
    bits = [byte & 1 for byte in data]
    out = bytearray()
    for start in range(0, len(bits), 8):
        chunk = bits[start:start + 8]
        out.append(sum(bit << i for i, bit in enumerate(chunk)))
    return bytes(out)


def parse_service_order(text: str) -> list[str]:
    m = re.search(r"(?m)^service_order=([A-Z,]+)$", text)
    if not m:
        raise ValueError("service_order not found")
    return m.group(1).split(",")


def parse_footer_strips(text: str) -> dict[tuple[str, str], bytes]:
    strips: dict[tuple[str, str], bytes] = {}
    for page in text.split("\\f"):
        m = re.search(r"DOCUMENT RC-17 / REV (B|C|D-draft) / SECTION (DRAIN|ISOLATE|PURGE|VERIFY)", page)
        f = re.search(r"Footer control strip: ([A-F0-9]{8})", page)
        if not m or not f:
            continue
        revision, stage = m.groups()
        revision = "D" if revision == "D-draft" else revision
        strips[(stage, revision)] = bytes.fromhex(f.group(1))
    return strips


def pack_for_pattern(order: list[str], strips: dict[tuple[str, str], bytes], pattern: str) -> dict:
    raw = b"".join(strips[(stage, revision)] for stage, revision in zip(order, pattern))
    packed = pack_first_bit_as_lsb(raw)
    try:
        ascii_text = packed.decode("ascii")
    except UnicodeDecodeError:
        ascii_text = None
    return {"pattern": pattern, "raw_hex": raw.hex().upper(), "packed_hex": packed.hex().upper(), "ascii": ascii_text}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, default=Path("resources/evidence"))
    args = parser.parse_args()
    root = args.evidence_root

    pins = {}
    for rel, expected in EXPECTED.items():
        data = (root / rel).read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise SystemExit(f"source pin mismatch: {rel}: {actual} != {expected}")
        pins[rel] = actual

    labels = (root / "archive-labels.ini").read_text(encoding="utf-8")
    order = parse_service_order(labels)
    if order != ["DRAIN", "ISOLATE", "PURGE", "VERIFY"]:
        raise SystemExit(f"unexpected service order: {order}")

    strips = parse_footer_strips((root / "procedures/RC-17-scans.txt").read_text(encoding="utf-8"))
    required = {(stage, revision) for stage in order for revision in ("B", "C", "D")}
    if set(strips) != required:
        raise SystemExit(f"unexpected RC-17 strip inventory: {sorted(strips)}")

    # Zero-based service-order ordinal: lower revision B on even positions,
    # higher revision D-draft on odd positions. This is exploratory only.
    low_if_even = "".join("B" if i % 2 == 0 else "D" for i in range(len(order)))
    results = {
        "low_if_even_zero_based": pack_for_pattern(order, strips, low_if_even),
        "one_based_alternative": pack_for_pattern(order, strips, "DBDB"),
        "official_rev_c_control": pack_for_pattern(order, strips, "CCCC"),
        "all_rev_b_control": pack_for_pattern(order, strips, "BBBB"),
        "all_rev_d_draft_control": pack_for_pattern(order, strips, "DDDD"),
    }

    note_text = (root / "crew/noticeboard-and-desk-notes.txt").read_text(encoding="utf-8")
    note_ids = sorted(int(x) for x in re.findall(r"(?m)^N(\\d{2}) /", note_text))
    output = results["low_if_even_zero_based"]["ascii"]
    if output and re.fullmatch(r"[A-Z]{2}", output):
        a1z26 = [ord(c) - 64 for c in output]
        a0z25 = [ord(c) - 65 for c in output]
    else:
        a1z26 = None
        a0z25 = None

    spool_text = (root / "print/spool-reconstruction.log").read_text(encoding="utf-8")
    p0325 = [line for line in spool_text.splitlines() if "JOB=PS-261003-0325 " in line]

    print(json.dumps({
        "source_pins": pins,
        "service_order": order,
        "revision_status": {
            "B": "issued then withdrawn 2026-09-30",
            "C": "issued and retained 2026-10-03; official K06 revision",
            "D": "D-draft; review copy only, no issue authority",
        },
        "results": results,
        "a1z26_locator_hypothesis": a1z26,
        "a0z25_alternative": a0z25,
        "note_ids_present": note_ids,
        "N11_present": 11 in note_ids,
        "N12_present": 12 in note_ids,
        "N24_present": 24 in note_ids,
        "N25_absent": 25 not in note_ids,
        "PS0325_rows": p0325,
        "interpretation": "LY -> N12/N25 is a conditional A1Z26 locator hypothesis only; no K08 phrase or component recovered.",
    }, indent=2))


if __name__ == "__main__":
    main()
