#!/usr/bin/env python3
"""Independent, target-blind review of the K05 LOW-IF-EVEN retry proposal.

Run from a workplace-v2 checkout root. This deliberately separates:
  * the official K05 greatest-valid-sequence reducer; and
  * the exploratory LOW-IF-EVEN alternate-row selector.

It reads the K05 slot commitment only to verify the official reducer. It never
reads or tests the K08 commitment or any candidate phrase.
"""
from __future__ import annotations

import hashlib
import json
import struct
import zlib
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("resources") if Path("resources/evidence/recorder/trip-recorder.raw").exists() else Path(".")
RECORDER_SHA256 = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
FORMAT_SHA256 = "78ff213040de20f81bc582cdfc25a4d0930ceb2d3956dbcc944b775b88fd7b22"
MAIL10_SHA256 = "ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48"
ROUTE_SHA256 = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPTANCE_SHA256 = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
EXPECTED_PAIRS = {
    0: [(200, "42BFD053"), (300, "FF8B7820")],
    1: [(201, "8052760C"), (301, "0A56E858")],
    2: [(202, "6FC2B743"), (302, "6DCDA00E")],
    3: [(203, "BFB00270"), (303, "F01E4572")],
}
LOW_IF_EVEN_MASK = 0b1010  # latch 0 low, 1 high, 2 low, 3 high


def lowbit_pack(raw: bytes, first_bit_is_lsb: bool = True) -> bytes:
    bits = [byte & 1 for byte in raw]
    if first_bit_is_lsb:
        return bytes(
            sum(bits[offset + bit] << bit for bit in range(8))
            for offset in (0, 8)
        )
    return bytes(
        sum(bits[offset + bit] << (7 - bit) for bit in range(8))
        for offset in (0, 8)
    )


def main() -> None:
    recorder_path = ROOT / "evidence/recorder/trip-recorder.raw"
    route_path = ROOT / "evidence/recovery-routing.json"
    format_path = ROOT / "evidence/recorder/format-note.txt"
    mail10_path = ROOT / "evidence/mail/10.eml"
    acceptance_path = ROOT / "acceptance.json"

    raw = recorder_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RECORDER_SHA256
    acceptance_raw = acceptance_path.read_bytes()
    format_raw = format_path.read_bytes()
    mail10_raw = mail10_path.read_bytes()
    route_raw = route_path.read_bytes()
    assert hashlib.sha256(acceptance_raw).hexdigest() == ACCEPTANCE_SHA256
    assert hashlib.sha256(format_raw).hexdigest() == FORMAT_SHA256
    assert hashlib.sha256(mail10_raw).hexdigest() == MAIL10_SHA256
    assert hashlib.sha256(route_raw).hexdigest() == ROUTE_SHA256
    acceptance = json.loads(acceptance_raw.decode("utf-8"))
    format_note = format_raw.decode("utf-8")
    mail10 = mail10_raw.decode("utf-8")
    route = json.loads(route_raw.decode("utf-8"))["K05"]

    assert "greatest sequence is the last write" in format_note
    assert "failed CRC is not a valid later write" in format_note
    assert "CRC failures are expected" in mail10
    assert "copied exactly as stored" in mail10
    assert route["node"] == 0x31 and route["event"] == 0x52

    magic, version, record_size, record_count = struct.unpack_from("<8sHHI", raw, 0)
    assert (magic, version, record_size, record_count) == (b"TRP2DUMP", 2, 24, 88)
    start = datetime.fromisoformat(route["start_utc"])
    end = datetime.fromisoformat(route["end_utc_exclusive"])

    all_matches = []
    valid_by_latch = defaultdict(list)
    invalid_by_latch = defaultdict(list)
    for index in range(record_count):
        row = raw[16 + index * record_size : 16 + (index + 1) * record_size]
        assert len(row) == record_size
        timestamp, node, event, latch, sequence = struct.unpack_from("<IHBBI", row, 0)
        when = datetime.fromtimestamp(timestamp, timezone.utc)
        if node != route["node"] or event != route["event"] or not (start <= when < end):
            continue
        good = (zlib.crc32(row[:20]) & 0xFFFFFFFF) == struct.unpack_from("<I", row, 20)[0]
        control = row[12:16]
        all_matches.append((latch, sequence, index, control, good))
        if good:
            valid_by_latch[latch].append((sequence, control))
        else:
            invalid_by_latch[latch].append((sequence, control))

    assert len(all_matches) == 12
    assert {latch: len(rows) for latch, rows in valid_by_latch.items()} == {0: 2, 1: 2, 2: 2, 3: 2}
    assert {
        latch: [(seq, word.hex().upper()) for seq, word in sorted(rows)]
        for latch, rows in valid_by_latch.items()
    } == EXPECTED_PAIRS
    assert {
        latch: [seq for seq, _ in rows]
        for latch, rows in invalid_by_latch.items()
    } == {0: [900], 1: [901], 2: [902], 3: [903]}

    pairs = {latch: sorted(rows) for latch, rows in valid_by_latch.items()}
    enumerated = defaultdict(list)
    detail = {}
    for mask in range(16):
        selected = [pairs[latch][(mask >> latch) & 1] for latch in range(4)]
        sequences = [sequence for sequence, _ in selected]
        mixed = b"".join(control for _, control in selected)
        packed = lowbit_pack(mixed)
        enumerated[packed].append(mask)
        detail[mask] = (sequences, mixed, packed)

    assert len(enumerated) == 8
    assert sorted(enumerated[bytes.fromhex("0A4D")]) == [8, 10]
    assert sorted(enumerated[bytes.fromhex("0343")]) == [13, 15]

    # Pre-registered interpretation: LOW on even latch ordinals, HIGH on odd.
    low_even_sequences, low_even_raw, low_even_packed = detail[LOW_IF_EVEN_MASK]
    assert low_even_sequences == [200, 301, 202, 303]
    assert low_even_raw.hex().upper() == "42BFD0530A56E8586FC2B743F01E4572"
    assert low_even_packed == bytes.fromhex("0A4D")

    # The official route selects the greatest CRC-valid sequence at each latch.
    official_sequences = [pairs[latch][-1][0] for latch in range(4)]
    official_raw = b"".join(pairs[latch][-1][1] for latch in range(4))
    official_packed = lowbit_pack(official_raw)
    expected_official_k05 = "FF8B78200A56E8586DCDA00EF01E4572"
    assert official_sequences == [300, 301, 302, 303]
    assert official_raw.hex().upper() == expected_official_k05
    assert hashlib.sha256(official_raw).hexdigest() == acceptance["slot_sha256"]["K05"]
    assert official_packed == bytes.fromhex("0343")
    assert hashlib.sha256(low_even_raw).hexdigest() != acceptance["slot_sha256"]["K05"]

    # Deliberate controls: all-low, opposite parity, and CRC-invalid late rows.
    all_low = detail[0]
    opposite_parity = detail[5]
    assert all_low[0] == [200, 201, 202, 203]
    assert all_low[2] == bytes.fromhex("0A1D")
    assert opposite_parity[0] == [300, 201, 302, 203]
    assert opposite_parity[2] == bytes.fromhex("0313")

    invalid_latest = [
        max(invalid_by_latch[latch], key=lambda item: item[0])
        for latch in range(4)
    ]
    invalid_raw = b"".join(control for _, control in invalid_latest)
    invalid_packed = lowbit_pack(invalid_raw)
    assert [sequence for sequence, _ in invalid_latest] == [900, 901, 902, 903]
    assert invalid_packed == bytes.fromhex("6428")
    assert lowbit_pack(low_even_raw, first_bit_is_lsb=False) == bytes.fromhex("50B2")

    print("SOURCE_SHA256", RECORDER_SHA256)
    print("FORMAT_SHA256", FORMAT_SHA256, "MAIL10_SHA256", MAIL10_SHA256)
    print("MATCHING_ROWS", len(all_matches), "CRC_GOOD",
          sum(len(v) for v in valid_by_latch.values()), "CRC_BAD",
          sum(len(v) for v in invalid_by_latch.values()))
    for latch in range(4):
        print("LATCH", latch, "VALID",
              ",".join(f"{seq}:{word.hex().upper()}" for seq, word in pairs[latch]),
              "CRC_BAD", ",".join(str(seq) for seq, _ in invalid_by_latch[latch]))
    print("LOW_IF_EVEN_MASK", LOW_IF_EVEN_MASK, "SEQUENCES", low_even_sequences,
          "RAW", low_even_raw.hex().upper(), "PACKED", low_even_packed.hex().upper())
    print("OFFICIAL_MASK", 15, "SEQUENCES", official_sequences,
          "RAW", official_raw.hex().upper(), "PACKED", official_packed.hex().upper(),
          "K05_COMMITMENT", "PASS")
    print("ALL_16_MASKS")
    for mask in range(16):
        sequences, mixed, packed = detail[mask]
        print(f"{mask:02d}", sequences, mixed.hex().upper(), packed.hex().upper())
    print("UNIQUE_LOWBIT_OUTPUTS", len(enumerated))
    print("M10_MASKS", sorted(enumerated[bytes.fromhex("0A4D")]))
    print("C3_MASKS", sorted(enumerated[bytes.fromhex("0343")]))
    print("CONTROLS all_low=0A1D opposite_parity=0313 invalid_crc_latest=6428 msb_first=50B2")
    print("BOUNDARY LOW_IF_EVEN_IS_INTERPRETIVE; M10_IS_NOT_A_UNIQUE_SELECTOR")


if __name__ == "__main__":
    main()
