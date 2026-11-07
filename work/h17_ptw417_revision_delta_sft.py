#!/usr/bin/env python3
"""Bounded PTW-417 per-bay revision-delta screen against the K04 commitment.

Run from the repository root:
    python work/h17_ptw417_revision_delta_sft.py

The script reads only preserved source files under resources/ and performs no
password, device, or external-service access.
"""
from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


BAYS = ("B", "D", "A", "C")
REVISION_PAIRS = ((1, 2), (2, 4), (1, 4))


def xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def add_bytes(left: bytes, right: bytes) -> bytes:
    return bytes((a + b) & 0xFF for a, b in zip(left, right))


def sub_bytes(left: bytes, right: bytes) -> bytes:
    return bytes((a - b) & 0xFF for a, b in zip(left, right))


def as_u32(raw: bytes) -> int:
    return int.from_bytes(raw, "big", signed=False)


def u32_bytes(value: int) -> bytes:
    return (value & 0xFFFFFFFF).to_bytes(4, "big", signed=False)


def add_u32(left: bytes, right: bytes) -> bytes:
    return u32_bytes(as_u32(left) + as_u32(right))


def sub_u32(left: bytes, right: bytes) -> bytes:
    return u32_bytes(as_u32(left) - as_u32(right))


def parse_spool_line(line: str) -> dict[str, Any] | None:
    tokens = line.strip().split()
    if len(tokens) < 2 or not tokens[0].startswith("2026-"):
        return None
    fields: dict[str, str] = {}
    for token in tokens[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    required = {"JOB", "ATTEMPT", "STATE", "CLASS", "PAYLOAD", "DEST"}
    if not required.issubset(fields):
        return None
    stamp = tokens[0].replace("Z", "+00:00")
    return {
        "timestamp": datetime.fromisoformat(stamp),
        "job": fields["JOB"],
        "attempt": int(fields["ATTEMPT"]),
        "state": fields["STATE"],
        "class": fields["CLASS"],
        "payload": bytes.fromhex(fields["PAYLOAD"]),
        "dest": fields["DEST"],
    }


def read_sources(resources: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]], str, int]:
    acceptance = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    routing = json.loads((resources / "evidence" / "recovery-routing.json").read_text(encoding="utf-8"))

    ini = configparser.ConfigParser(interpolation=None)
    ini.optionxform = str
    ini.read(resources / "evidence" / "archive-labels.ini", encoding="utf-8")
    route_section = next(
        section for section in ini.sections()
        if section.startswith("printer_routes_2026-09-01_to_2026-10-03")
    )
    route_job = ini[route_section]["ESC-N"]

    spool_rows = []
    for line in (resources / "evidence" / "print" / "spool-reconstruction.log").read_text(encoding="utf-8").splitlines():
        row = parse_spool_line(line)
        if row is not None and row["job"] == route_job:
            spool_rows.append(row)
    ack_rows = [row for row in spool_rows if row["state"] == "ACK"]
    if not ack_rows:
        raise RuntimeError(f"No ACK rows found for ESC-N job {route_job}")
    selected_ack = max(ack_rows, key=lambda row: (row["timestamp"], row["attempt"]))
    if len(selected_ack["payload"]) != 16:
        raise RuntimeError("Selected ACK payload is not 16 bytes")

    receipts = [
        json.loads(line)
        for line in (resources / "evidence" / "maintenance" / "seal-receipts.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ptw_all = [row for row in receipts if row.get("permit") == "PTW-417"]
    ptw = [
        row for row in ptw_all
        if row.get("signed") is True
        and row.get("state") == "CLOSED"
        and row.get("revision") in (1, 2, 4)
    ]
    open_revision3_count = sum(
        row.get("revision") == 3 and row.get("state") == "OPEN" and row.get("signed") is False
        for row in ptw_all
    )

    closeout_mail = (resources / "evidence" / "mail" / "04.eml").read_text(encoding="utf-8")
    match = re.search(r"The witness walk\s+was\s+([A-D](?:,\s*[A-D]){3})\.", closeout_mail)
    if not match:
        raise RuntimeError("Could not recover signed B,D,A,C bay order from MAIL-04")
    bay_order = tuple(part.strip() for part in match.group(1).split(","))
    if bay_order != BAYS:
        raise RuntimeError(f"Unexpected bay order {bay_order}; expected {BAYS}")

    return acceptance, routing, selected_ack, ptw, route_job, open_revision3_count


def serial_bytes(row: dict[str, Any]) -> bytes:
    value = row["serial"]
    if not value.startswith("SG-"):
        raise RuntimeError(f"Unexpected seal serial format: {value}")
    raw = bytes.fromhex(value[3:])
    if len(raw) != 4:
        raise RuntimeError(f"Seal serial is not four bytes: {value}")
    return raw


def build_candidate_vectors(ptw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_bay_revision: dict[str, dict[int, list[dict[str, Any]]]] = {
        bay: {revision: [] for revision in (1, 2, 4)}
        for bay in BAYS
    }
    for row in ptw:
        bay = row["bay"]
        revision = row["revision"]
        if bay in by_bay_revision and revision in by_bay_revision[bay]:
            by_bay_revision[bay][revision].append(row)

    # Keep both signed CLOSED revision-1 A records. One is unannotated; the
    # other has asset/inspector fields. Neither is silently preferred here.
    for bay in ("B", "D", "C"):
        if len(by_bay_revision[bay][1]) != 1:
            raise RuntimeError(f"Expected one signed revision-1 record for bay {bay}")
    if len(by_bay_revision["A"][1]) != 2:
        raise RuntimeError("Expected both signed revision-1 A alternatives")
    for bay in BAYS:
        for revision in (2, 4):
            if len(by_bay_revision[bay][revision]) != 1:
                raise RuntimeError(f"Expected one signed revision-{revision} record for bay {bay}")
    for bay in BAYS:
        for row in by_bay_revision[bay][1]:
            if row.get("fitment") != "AS_LEFT":
                raise RuntimeError(f"Unexpected revision-1 fitment for bay {bay}")
        if by_bay_revision[bay][2][0].get("fitment") != "AS_LEFT":
            raise RuntimeError(f"Unexpected revision-2 fitment for bay {bay}")
        if by_bay_revision[bay][4][0].get("fitment") != "REMOVED":
            raise RuntimeError(f"Unexpected revision-4 fitment for bay {bay}")

    a_options = sorted(
        by_bay_revision["A"][1],
        key=lambda row: (bool(row.get("asset")), bool(row.get("inspector")), row["serial"]),
    )
    vectors: list[dict[str, Any]] = []

    operations = []
    for left_rev, right_rev in REVISION_PAIRS:
        operations.extend([
            (f"xor_{left_rev}_{right_rev}", xor_bytes),
            (f"byte_add_{left_rev}_{right_rev}", add_bytes),
        ])
    for left_rev, right_rev in ((2, 1), (1, 2), (4, 2), (2, 4), (4, 1), (1, 4)):
        operations.append((f"byte_sub_{left_rev}_{right_rev}", sub_bytes))

    # The serial suffixes are 32-bit values. In addition to the exact
    # bytewise screen above, test the same pairwise add/sub relations with
    # ordinary modulo-2^32 arithmetic, preserving big-endian serial notation.
    for left_rev, right_rev in REVISION_PAIRS:
        operations.append((f"u32_add_{left_rev}_{right_rev}", add_u32))
    for left_rev, right_rev in ((2, 1), (1, 2), (4, 2), (2, 4), (4, 1), (1, 4)):
        operations.append((f"u32_sub_{left_rev}_{right_rev}", sub_u32))

    for a_option in a_options:
        a_label = "asset-annotated" if a_option.get("asset") and a_option.get("inspector") else "unannotated"
        selected_rows: dict[str, dict[int, dict[str, Any]]] = {}
        for bay in BAYS:
            selected_rows[bay] = {}
            for revision in (1, 2, 4):
                rows = by_bay_revision[bay][revision]
                selected_rows[bay][revision] = a_option if bay == "A" and revision == 1 else rows[0]

        for name, operation in operations:
            # Operation applies independently to each four-byte bay serial,
            # then the results are concatenated in the signed B,D,A,C order.
            pair_match = re.fullmatch(r"(?:xor|byte_add|byte_sub|u32_add|u32_sub)_(\d)_(\d)", name)
            if not pair_match:
                raise RuntimeError(f"Unexpected operation name {name}")
            left_rev, right_rev = map(int, pair_match.groups())
            parts = [
                operation(
                    serial_bytes(selected_rows[bay][left_rev]),
                    serial_bytes(selected_rows[bay][right_rev]),
                )
                for bay in BAYS
            ]
            candidate = b"".join(parts)
            if len(candidate) != 16:
                raise RuntimeError("Revision candidate is not 16 bytes")
            vectors.append({
                "a_rev1_source": a_label,
                "operation": name,
                "vector": candidate,
            })

    return vectors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_resources = Path(__file__).resolve().parents[1] / "resources"
    parser.add_argument("--resources-dir", type=Path, default=default_resources)
    args = parser.parse_args()
    resources = args.resources_dir.resolve()

    acceptance, routing, selected_ack, ptw, route_job, open_revision3_count = read_sources(resources)
    if selected_ack["attempt"] != 2 or selected_ack["class"] != "RECOVER" or selected_ack["dest"] != "bench":
        raise RuntimeError("Selected ESC-N ACK does not match the documented PS-0417 RECOVER/bench attempt-2 row")
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    if len(mask) != 16:
        raise RuntimeError("K04 mask is not 16 bytes")
    target = acceptance["slot_sha256"]["K04"]
    payload = selected_ack["payload"]
    component_candidate = xor_bytes(payload, mask)
    vectors = build_candidate_vectors(ptw)

    results = []
    for item in vectors:
        candidate = item["vector"]
        candidate_xor_mask = xor_bytes(candidate, mask)
        results.append({
            "a_rev1_source": item["a_rev1_source"],
            "operation": item["operation"],
            "vector_hex": candidate.hex().upper(),
            "sha256": hashlib.sha256(candidate).hexdigest(),
            "direct_component_commitment_match": hashlib.sha256(candidate).hexdigest() == target,
            "masked_component_commitment_match": hashlib.sha256(candidate_xor_mask).hexdigest() == target,
            "equals_reconstructed_component": candidate == component_candidate,
            "equals_selected_payload": candidate == payload,
            "xor_mask_equals_selected_payload": candidate_xor_mask == payload,
        })

    output = {
        "route_job": route_job,
        "selected_ack": {
            "timestamp": selected_ack["timestamp"].isoformat(),
            "attempt": selected_ack["attempt"],
            "state": selected_ack["state"],
            "class": selected_ack["class"],
            "destination": selected_ack["dest"],
            "payload_hex": payload.hex().upper(),
        },
        "mask_hex": mask.hex().upper(),
        "reconstructed_component_candidate_hex": component_candidate.hex().upper(),
        "reconstructed_component_candidate_sha256": hashlib.sha256(component_candidate).hexdigest(),
        "k04_commitment": target,
        "ptw417_signed_closed_revision_rows": len(ptw),
        "ptw417_unsigned_open_revision3_rows_excluded": open_revision3_count,
        "ptw417_revision1_a_options": [
            {
                "serial": row["serial"],
                "asset_annotated": bool(row.get("asset")),
                "inspector_annotated": bool(row.get("inspector")),
            }
            for row in sorted(
                [r for r in ptw if r["bay"] == "A" and r["revision"] == 1],
                key=lambda r: (bool(r.get("asset")), r["serial"]),
            )
        ],
        "candidate_count": len(results),
        "direct_component_commitment_hits": sum(row["direct_component_commitment_match"] for row in results),
        "masked_component_commitment_hits": sum(row["masked_component_commitment_match"] for row in results),
        "reconstructed_component_identity_hits": sum(row["equals_reconstructed_component"] for row in results),
        "selected_payload_identity_hits": sum(row["equals_selected_payload"] for row in results),
        "rows": results,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
