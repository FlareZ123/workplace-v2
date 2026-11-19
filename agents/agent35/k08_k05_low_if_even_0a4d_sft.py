#!/usr/bin/env python3
"""Target-blind K08 source test: apply LOW IF EVEN to the K05 retry stratum.

This does not read acceptance.json or any K08 target. It only uses the original
TRP2 recorder export plus the published K05 route metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path

RECORDER_SHA256 = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
EXPECTED_MIXED = bytes.fromhex("42BFD0530A56E8586FC2B743F01E4572")
EXPECTED_PACKED = bytes([10, ord("M")])


def pack_lsb(bits: list[int]) -> int:
    return sum(bit << index for index, bit in enumerate(bits))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "resources",
    )
    args = parser.parse_args()
    root = args.root

    recorder_path = root / "evidence/recorder/trip-recorder.raw"
    route_path = root / "evidence/recovery-routing.json"

    recorder = recorder_path.read_bytes()
    assert hashlib.sha256(recorder).hexdigest() == RECORDER_SHA256
    route = json.loads(route_path.read_text(encoding="utf-8"))["K05"]

    magic, version, record_size, record_count = struct.unpack_from("<8sHHI", recorder, 0)
    assert (magic, version, record_size, record_count) == (b"TRP2DUMP", 2, 24, 88)

    start = datetime.fromisoformat(route["start_utc"])
    end = datetime.fromisoformat(route["end_utc_exclusive"])
    matching: dict[int, list[tuple[int, bytes]]] = {latch: [] for latch in range(4)}

    for index in range(record_count):
        offset = 16 + index * record_size
        row = recorder[offset : offset + record_size]
        stored_crc = struct.unpack_from("<I", row, 20)[0]
        if zlib.crc32(row[:20]) & 0xFFFFFFFF != stored_crc:
            continue

        timestamp, node, event, latch, sequence = struct.unpack_from("<IHBBI", row, 0)
        when = datetime.fromtimestamp(timestamp, timezone.utc)
        if (
            node == route["node"]
            and event == route["event"]
            and start <= when < end
            and latch in matching
        ):
            matching[latch].append((sequence, row[12:16]))

    expected = {
        0: [(200, "42BFD053"), (300, "FF8B7820")],
        1: [(201, "8052760C"), (301, "0A56E858")],
        2: [(202, "6FC2B743"), (302, "6DCDA00E")],
        3: [(203, "BFB00270"), (303, "F01E4572")],
    }
    normalized = {
        latch: [(seq, word.hex().upper()) for seq, word in sorted(rows)]
        for latch, rows in matching.items()
    }
    assert normalized == expected

    # Source-derived instruction already established independently of K05:
    # LOW IF EVEN. On even latch ordinals select the lower sequence; on odd
    # latch ordinals select the higher sequence.
    chosen: list[tuple[int, int, bytes]] = []
    for latch in range(4):
        rows = sorted(matching[latch])
        sequence, control = rows[0] if latch % 2 == 0 else rows[-1]
        chosen.append((latch, sequence, control))

    mixed = b"".join(control for _, _, control in chosen)
    assert mixed == EXPECTED_MIXED

    low_bits = [byte & 1 for byte in mixed]
    packed = bytes(pack_lsb(low_bits[offset : offset + 8]) for offset in (0, 8))
    assert low_bits == [
        0, 1, 0, 1, 0, 0, 0, 0,
        1, 0, 1, 1, 0, 0, 1, 0,
    ]
    assert packed == EXPECTED_PACKED

    print("RECORDER_SHA256", RECORDER_SHA256)
    print(
        "MATCHING",
        ";".join(
            f"latch{latch}:"
            + ",".join(f"seq{seq}={word}" for seq, word in expected[latch])
            for latch in range(4)
        ),
    )
    print(
        "RULE",
        "LOW IF EVEN: even latch -> lower sequence; odd latch -> higher sequence",
    )
    print(
        "CHOSEN",
        ";".join(
            f"latch{latch}:seq{seq}={control.hex().upper()}"
            for latch, seq, control in chosen
        ),
    )
    print("MIXED", mixed.hex().upper())
    print("LOW_BITS", "".join(map(str, low_bits)))
    print("PACKED", packed.hex().upper())
    print("DECODE", packed[0], chr(packed[1]))
    print("PASS", "K05 retry stratum independently reproduces N10 + M")


if __name__ == "__main__":
    main()
