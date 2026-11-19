#!/usr/bin/env python3
"""Independent K05 LOW-IF-EVEN review; no K08 target or phrase is read.

The only alternate rule tested is the frozen interpretation from the prior
source-local note analysis: choose the lower sequence for even latch ordinals
and the higher sequence for odd latch ordinals. All 16 low/high masks are
enumerated as a finite specificity/control check.
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
ROUTE_SHA256 = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
EXPECTED_OFFICIAL = bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572")
EXPECTED_ALT = bytes.fromhex("42BFD0530A56E8586FC2B743F01E4572")
LOW_IF_EVEN_MASK = 0b1010  # bit=1 means choose higher; L,H,L,H for latches 0..3


def pack_lsb(bits: list[int]) -> int:
    return sum(bit << i for i, bit in enumerate(bits))


def lowpack(raw: bytes) -> bytes:
    bits = [byte & 1 for byte in raw]
    assert len(bits) == 16
    return bytes(pack_lsb(bits[i:i + 8]) for i in (0, 8))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2] / "resources")
    args = ap.parse_args()
    root = args.root

    recorder_path = root / "evidence/recorder/trip-recorder.raw"
    route_path = root / "evidence/recovery-routing.json"
    fmt_path = root / "evidence/recorder/format-note.txt"
    acceptance_path = root / "acceptance.json"

    recorder = recorder_path.read_bytes()
    route_bytes = route_path.read_bytes()
    assert hashlib.sha256(recorder).hexdigest() == RECORDER_SHA256
    assert hashlib.sha256(route_bytes).hexdigest() == ROUTE_SHA256
    route = json.loads(route_bytes)["K05"]

    header = struct.unpack_from("<8sHHI", recorder, 0)
    assert header == (b"TRP2DUMP", 2, 24, 88)
    assert "offset 16: uint32 auxiliary process reading" in fmt_path.read_text()

    start = datetime.fromisoformat(route["start_utc"])
    end = datetime.fromisoformat(route["end_utc_exclusive"])
    by_latch: dict[int, list[tuple[int, bytes, int]]] = {i: [] for i in range(4)}
    bad_crc = 0
    for index in range(header[3]):
        row = recorder[16 + index * 24:16 + (index + 1) * 24]
        stored_crc = struct.unpack_from("<I", row, 20)[0]
        if (zlib.crc32(row[:20]) & 0xFFFFFFFF) != stored_crc:
            bad_crc += 1
            continue
        ts, node, event, latch, sequence = struct.unpack_from("<IHBBI", row, 0)
        when = datetime.fromtimestamp(ts, timezone.utc)
        if (node == route["node"] and event == route["event"]
                and start <= when < end and latch in by_latch):
            control = row[12:16]
            auxiliary = struct.unpack_from("<I", row, 16)[0]
            by_latch[latch].append((sequence, control, auxiliary))

    expected = {
        0: [(200, "42BFD053", 4312), (300, "FF8B7820", 4318)],
        1: [(201, "8052760C", 4312), (301, "0A56E858", 4318)],
        2: [(202, "6FC2B743", 4312), (302, "6DCDA00E", 4318)],
        3: [(203, "BFB00270", 4312), (303, "F01E4572", 4318)],
    }
    normalized = {
        latch: [(seq, control.hex().upper(), aux) for seq, control, aux in sorted(rows)]
        for latch, rows in by_latch.items()
    }
    assert normalized == expected
    assert sum(len(rows) for rows in by_latch.values()) == 8

    official = b"".join(sorted(by_latch[latch], key=lambda x: x[0])[-1][1] for latch in range(4))
    assert official == EXPECTED_OFFICIAL
    acceptance = json.loads(acceptance_path.read_text())
    assert hashlib.sha256(official).hexdigest() == acceptance["slot_sha256"]["K05"]

    outputs: dict[str, list[int]] = {}
    rows_for_mask: dict[int, tuple[str, list[int], bytes]] = {}
    for mask in range(16):
        chosen = []
        for latch in range(4):
            pair = sorted(by_latch[latch], key=lambda x: x[0])
            chosen.append(pair[(mask >> latch) & 1])
        raw = b"".join(item[1] for item in chosen)
        packed = lowpack(raw)
        pattern = "".join("H" if (mask >> latch) & 1 else "L" for latch in range(4))
        seqs = [item[0] for item in chosen]
        outputs.setdefault(packed.hex().upper(), []).append(mask)
        rows_for_mask[mask] = (pattern, seqs, raw)

    assert len(outputs) == 8
    assert outputs["0A4D"] == [8, 10]
    assert outputs["0343"] == [13, 15]
    assert rows_for_mask[LOW_IF_EVEN_MASK][0] == "LHLH"
    assert rows_for_mask[LOW_IF_EVEN_MASK][2] == EXPECTED_ALT
    assert lowpack(EXPECTED_ALT).hex().upper() == "0A4D"
    assert rows_for_mask[15][2] == EXPECTED_OFFICIAL
    assert lowpack(EXPECTED_OFFICIAL).hex().upper() == "0343"

    # The source fields do not identify what "even" is applied to.
    for latch, pair in by_latch.items():
        seqs = [seq for seq, _, _ in pair]
        assert all(seq % 2 == latch % 2 for seq in seqs)
        assert all(aux % 2 == 0 for _, _, aux in pair)
    # Latch 1's two controls have identical byte-LSB vectors, causing the alias.
    latch1 = sorted(by_latch[1], key=lambda x: x[0])
    assert [b & 1 for b in latch1[0][1]] == [b & 1 for b in latch1[1][1]] == [0, 0, 0, 0]

    alternate_hash = hashlib.sha256(EXPECTED_ALT).hexdigest()
    assert alternate_hash != acceptance["slot_sha256"]["K05"]

    print("RECORDER_SHA256", RECORDER_SHA256)
    print("ROUTE_SHA256", ROUTE_SHA256)
    print("VALID_MATCHES", sum(map(len, by_latch.values())), "BAD_CRC_RECORDS", bad_crc)
    for latch in range(4):
        print("LATCH", latch, normalized[latch])
    print("OFFICIAL", official.hex().upper(), "LOWPACK", lowpack(official).hex().upper(), "K05_ACCEPTED", True)
    print("MASK TABLE: bit=1 selects higher sequence; L=lower, H=higher")
    for mask in range(16):
        pattern, seqs, raw = rows_for_mask[mask]
        print(f"{mask:02d} {pattern} seq={','.join(map(str, seqs))} lowpack={lowpack(raw).hex().upper()}")
    print("UNIQUE_OUTPUTS", len(outputs), "M10_MASKS", outputs["0A4D"], "M10_MASK_SHARE", f"{len(outputs['0A4D'])}/16")
    print("C3_MASKS", outputs["0343"])
    print("LOW_IF_EVEN_INTERPRETATION", LOW_IF_EVEN_MASK, rows_for_mask[LOW_IF_EVEN_MASK][0], EXPECTED_ALT.hex().upper(), lowpack(EXPECTED_ALT).hex().upper())
    print("REVERSE_PARITY_CONTROL", 5, rows_for_mask[5][0], lowpack(rows_for_mask[5][2]).hex().upper())
    print("ALL_LOW_CONTROL", 0, rows_for_mask[0][0], lowpack(rows_for_mask[0][2]).hex().upper())
    print("ALT_K05_SHA256", alternate_hash, "MATCHES_K05", False)
    print("AMBIGUITY: sequence parity duplicates latch parity; all auxiliary readings are even")
    print("PASS independent K05 enumeration; K08 target not read")


if __name__ == "__main__":
    main()
