#!/usr/bin/env python3
"""Check whether authoritative K05 recorder controls anchor the p951 printer MT stream.

Read-only source test. Run from any directory:
    python3 agents/agent50/k04_trip_recorder_cross_stream_sft.py
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt  # noqa: E402


def utc_seconds(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def parse_records(path: Path) -> list[dict]:
    raw = path.read_bytes()
    if raw[:8] != b"TRP2DUMP":
        raise ValueError("unexpected recorder magic")
    version, record_size, count = struct.unpack("<HHI", raw[8:16])
    if version != 2 or record_size != 24 or len(raw) != 16 + count * record_size:
        raise ValueError("unexpected recorder header/length")
    out = []
    for index in range(count):
        rec = raw[16 + index * record_size : 16 + (index + 1) * record_size]
        expected_crc = struct.unpack("<I", rec[20:24])[0]
        actual_crc = zlib.crc32(rec[:20]) & 0xFFFFFFFF
        out.append(
            {
                "index": index,
                "timestamp": struct.unpack("<I", rec[0:4])[0],
                "node": struct.unpack("<H", rec[4:6])[0],
                "event": rec[6],
                "latch": rec[7],
                "sequence": struct.unpack("<I", rec[8:12])[0],
                "control": rec[12:16],
                "aux": struct.unpack("<I", rec[16:20])[0],
                "crc_ok": expected_crc == actual_crc,
            }
        )
    return out


def known_tempered_outputs(basis, symbolic) -> list[tuple[int, int]]:
    known = []
    for stage in range(mt.ORIGIN, mt.LAST + 1):
        mask = value = 0
        for bit, expr in enumerate(mt.temper(mt.get(symbolic, stage))):
            prediction = basis.predict(expr)
            if prediction is not None:
                mask |= 1 << bit
                value |= prediction << bit
        known.append((mask, value))
    return known


def match_summary(word: int, known: list[tuple[int, int]]) -> dict:
    best = (-1, None, None)
    exact = []
    for offset, (mask, value) in enumerate(known):
        known_bits = mask.bit_count()
        agrees = known_bits - ((word ^ value) & mask).bit_count()
        stage = mt.ORIGIN + offset
        if agrees > best[0]:
            best = (agrees, stage, known_bits)
        if mask == 0xFFFFFFFF and value == word:
            exact.append(stage)
    return {
        "best_agreeing_known_bits": best[0],
        "best_stage": best[1],
        "known_bits_at_best_stage": best[2],
        "exact_stages": exact,
    }


def main() -> None:
    basis, symbolic = mt.source(ROOT)
    if basis.rank != 15365:
        raise ValueError(f"unexpected printer source rank: {basis.rank}")

    route = json.loads((ROOT / "resources" / "evidence" / "recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources" / "acceptance.json").read_text())
    k05 = route["K05"]
    records = parse_records(ROOT / "resources" / "evidence" / "recorder" / "trip-recorder.raw")
    valid = [record for record in records if record["crc_ok"]]
    start = utc_seconds(k05["start_utc"])
    end = utc_seconds(k05["end_utc_exclusive"])
    eligible = [
        record
        for record in valid
        if record["node"] == int(k05["node"])
        and record["event"] == int(k05["event"])
        and start <= record["timestamp"] < end
    ]
    selected = []
    for latch in range(4):
        candidates = [record for record in eligible if record["latch"] == latch]
        if not candidates:
            raise ValueError(f"no CRC-valid K05 record for latch {latch}")
        selected.append(max(candidates, key=lambda record: record["sequence"]))

    component = b"".join(record["control"] for record in selected)
    digest = hashlib.sha256(component).hexdigest()
    target = acceptance["slot_sha256"]["K05"]
    known = known_tempered_outputs(basis, symbolic)

    selected_summary = []
    for record in selected:
        word_le = int.from_bytes(record["control"], "little")
        word_be = int.from_bytes(record["control"], "big")
        selected_summary.append(
            {
                "record_index": record["index"],
                "latch": record["latch"],
                "sequence": record["sequence"],
                "timestamp_utc": datetime.fromtimestamp(
                    record["timestamp"], timezone.utc
                ).isoformat(),
                "control_hex": record["control"].hex().upper(),
                "little_endian": match_summary(word_le, known),
                "big_endian": match_summary(word_be, known),
            }
        )

    selected_indices = {record["index"] for record in selected}
    apparent_stale_matches = []
    for record in eligible:
        if record["index"] in selected_indices:
            continue
        summary = match_summary(int.from_bytes(record["control"], "little"), known)
        if summary["exact_stages"]:
            apparent_stale_matches.append(
                {
                    "record_index": record["index"],
                    "latch": record["latch"],
                    "sequence": record["sequence"],
                    "timestamp_utc": datetime.fromtimestamp(
                        record["timestamp"], timezone.utc
                    ).isoformat(),
                    "control_hex": record["control"].hex().upper(),
                    "exact_stages": summary["exact_stages"],
                }
            )

    result = {
        "basis_rank": basis.rank,
        "symbolic_stage_range": [mt.ORIGIN, mt.LAST],
        "recorder_records": len(records),
        "crc_valid_records": len(valid),
        "K05_selected_records": selected_summary,
        "K05_component_hex": component.hex().upper(),
        "K05_component_sha256": digest,
        "K05_acceptance_sha256": target,
        "K05_acceptance_match": digest == target,
        "nonselected_exact_matches_inside_K05_window": apparent_stale_matches,
        "interpretation": (
            "The authoritative K05 selection is not an exact raw-output anchor "
            "for this printer-only MT basis in the scanned stage range. Exact "
            "matches occur only among nonselected records; do not substitute "
            "them for the route-defined latest-per-latch K05 records."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
