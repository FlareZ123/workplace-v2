#!/usr/bin/env python3
"""Test North L-29 predecessor seal tuples and per-bay deltas as K04 candidates."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def latest_signed_as_left(receipts: list[dict], permit: str, bay: str) -> bytes | None:
    rows = [
        row for row in receipts
        if row["permit"] == permit
        and row["bay"] == bay
        and row["state"] == "CLOSED"
        and row["fitment"] == "AS_LEFT"
        and row["signed"] is True
    ]
    if not rows:
        return None
    row = max(rows, key=lambda item: item["revision"])
    return bytes.fromhex(row["serial"].removeprefix("SG-"))


def main() -> None:
    root = (
        Path(sys.argv[1]).resolve()
        if len(sys.argv) == 2
        else Path(__file__).resolve().parents[2] / "resources"
    )
    if len(sys.argv) > 2:
        raise SystemExit("usage: python k04_north_ticket_serial_coupon_sft.py [resource-root]")

    acceptance = json.loads((root / "acceptance.json").read_text(encoding="utf-8"))
    routing = json.loads((root / "evidence/recovery-routing.json").read_text(encoding="utf-8"))
    receipts = [
        json.loads(line)
        for line in (root / "evidence/maintenance/seal-receipts.jsonl")
        .read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    # Tab order from print-fleet-retirement-note.txt.
    north_tickets = ("ST-094", "ST-081", "ST-106", "ST-099", "ST-112")
    bay_order = ("A", "B", "C", "D")
    field_order = ("B", "D", "A", "C")
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    current = {
        bay: latest_signed_as_left(receipts, "PTW-417", bay)
        for bay in bay_order
    }
    assert all(value is not None for value in current.values())
    current = {bay: value for bay, value in current.items() if value is not None}

    blocks: dict[str, bytes] = {}
    for offset in (300, 304):
        by_bay: dict[str, bytes] = {}
        ticket_serials: list[bytes] = []
        ticket_bays: list[str] = []
        missing: list[str] = []

        for ticket in north_tickets:
            permit = f"PTW-{int(ticket.split('-')[1]) + offset}"
            matches = [
                row for row in receipts
                if row["permit"] == permit
                and row["state"] == "CLOSED"
                and row["fitment"] == "AS_LEFT"
                and row["signed"] is True
            ]
            if not matches:
                missing.append(f"{ticket}->{permit}")
                continue
            assert len({row["bay"] for row in matches}) == 1
            bay = matches[0]["bay"]
            serial = latest_signed_as_left(receipts, permit, bay)
            assert serial is not None and bay not in by_bay
            by_bay[bay] = serial
            ticket_bays.append(bay)
            ticket_serials.append(serial)

        print(
            f"+{offset}: ticket-order bays={','.join(ticket_bays)}; "
            f"missing={','.join(missing) if missing else 'none'}"
        )
        if set(by_bay) != set(bay_order):
            continue

        blocks[f"+{offset} predecessor ticket order"] = b"".join(ticket_serials)
        blocks[f"+{offset} predecessor bay order A/B/C/D"] = b"".join(
            by_bay[bay] for bay in bay_order
        )
        blocks[f"+{offset} predecessor field order B/D/A/C"] = b"".join(
            by_bay[bay] for bay in field_order
        )

        delta = {
            bay: bytes(a ^ b for a, b in zip(by_bay[bay], current[bay]))
            for bay in bay_order
        }
        blocks[f"+{offset} predecessor/current delta A/B/C/D"] = b"".join(
            delta[bay] for bay in bay_order
        )
        blocks[f"+{offset} predecessor/current delta B/D/A/C"] = b"".join(
            delta[bay] for bay in field_order
        )

    unique: dict[bytes, list[str]] = {}
    for label, block in blocks.items():
        assert len(block) == 16, (label, len(block))
        unique.setdefault(block, []).append(label)

    print(f"K04_target_sha256={target}")
    print(f"K04_mask={mask.hex().upper()}")
    print(f"unique_source_blocks={len(unique)}")
    tested = hits = 0
    for block, labels in unique.items():
        for interpretation, candidate in (
            ("block-as-component", block),
            ("block-as-payload-XOR-mask", bytes(a ^ b for a, b in zip(block, mask))),
        ):
            digest = hashlib.sha256(candidate).hexdigest()
            matched = digest == target
            tested += 1
            hits += int(matched)
            print(
                f"{'HIT' if matched else 'MISS'} | {'; '.join(labels)} | "
                f"{interpretation} | block={block.hex().upper()} | "
                f"candidate={candidate.hex().upper()} | sha256={digest}"
            )
    print(f"tested_candidates={tested}")
    print(f"commitment_matches={hits}")


if __name__ == "__main__":
    main()
