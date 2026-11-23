#!/usr/bin/env python3
"""Original spool: exact MT word witnesses versus a hypothetical UTC+11 clock offset.

Read-only, standalone, Python standard library. Test:
    python agents/agent21/k04_late_clock_mt_witness_sft.py
    python agents/agent21/k04_late_clock_mt_witness_sft.py h17-archive-dump.zip

The selected RECOVER/ACK2 copied payload is never decoded or used.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U32 = 0xFFFFFFFF
MAG = 0x9908B0DF


def untemper(value: int) -> int:
    for shift, left, mask in ((18, False, U32), (15, True, 0xEFC60000),
                               (7, True, 0x9D2C5680), (11, False, U32)):
        initial = value
        for _ in range(6):
            value = (initial ^ (((value << shift) & mask) if left else (value >> shift))) & U32
    return value


def temper(value: int) -> int:
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    return (value ^ (value >> 18)) & U32


def twist(a: int, b: int) -> int:
    joined = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (joined >> 1) ^ (MAG if joined & 1 else 0)


def witness_triples(native: list[tuple[int, ...] | None]) -> list[tuple[int, int, int, str, int, int, int]]:
    reverse: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for row, packet in enumerate(native):
        if packet is not None:
            for lane, word in enumerate(packet):
                reverse[word].append((row, lane))
    triples = []
    for r, packet in enumerate(native):
        if packet is None:
            continue
        for k in range(r + 1, len(native)):
            if native[k] is None:
                continue
            for lane, word in enumerate(native[k]):
                for p in (1, 2, 3):
                    for l, q in reverse.get(word ^ twist(packet[p - 1], packet[p]), ()):
                        if l > k:
                            triples.append((r, k, l, "full", p, lane, q))
                for top in (0, 0x80000000):
                    for l, q in reverse.get(word ^ twist(top, packet[0]), ()):
                        if l > k:
                            triples.append((r, k, l, "partial", 0, lane, q))
    return triples


def read_spool(path: Path) -> bytes:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            return archive.read("evidence/print/spool-reconstruction.log")
    return (path / "evidence/print/spool-reconstruction.log").read_bytes()


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / "resources"
    # Synthetic recurrence control tests the full-word witness extractor.
    initial = [(i * 0x9E3779B9 ^ (i << 9) ^ 0xF0101234) & U32 for i in range(624)]
    future = initial[397] ^ twist(initial[0], initial[1])
    assert untemper(temper(future)) == future
    synthetic = witness_triples([
        tuple(initial[0:4]), tuple(initial[397:401]),
        (future, 0x13572468, 0xABCDEF02, 0x789A3210)
    ])
    assert (0, 1, 2, "full", 1, 0, 0) in synthetic

    raw = read_spool(root)
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw, re.M
    )
    assert len(rows) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    native = [
        None if i == 129 else tuple(
            untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4 * j:4 * j + 4], "little"))
            for j in range(4)
        )
        for i, row in enumerate(rows)
    ]
    triples = witness_triples(native)
    assert (sum(t[3] == "full" for t in triples),
            sum(t[3] == "partial" for t in triples)) == (25, 17)
    late = [t for t in triples if t[2] >= 128]
    assert {t[:4] for t in late} == {
        (43, 96, 128, "partial"), (44, 97, 130, "partial"),
        (44, 97, 131, "full"), (45, 98, 132, "partial"),
        (45, 98, 132, "full")
    }

    clock = [datetime.fromisoformat(row[0].decode().replace("Z", "+00:00")) for row in rows]
    offsets = [clock[l] - clock[k] for _, k, l, *_ in late]
    assert min(offsets) == timedelta(hours=2, minutes=58)
    assert all(clock[l] - timedelta(hours=11) < clock[k] for _, k, l, *_ in late)
    mail16 = datetime.fromisoformat("2026-10-03T07:49:00+00:00")
    mail16_required = clock[130] - mail16
    assert mail16_required == timedelta(hours=10, minutes=14)
    print(json.dumps({
        "original_spool_sha256": SPOOL_SHA,
        "selected_copied_payload_decoded": False,
        "synthetic_MT_word_control": "PASS",
        "full_word_witnesses": 25,
        "firstword_partial_witnesses": 17,
        "late_cohort_witnesses": [list(t) for t in late],
        "max_clock_offset_minutes_exclusive_if_monotone_shared_MT": 178,
        "offset_minutes_minimum_to_precede_MAIL16": 614,
        "UTC_plus_11_monotone_shared_MT_compatible": False,
        "actual_K04_recovered": False,
        "assumption": "exact word identities represent one monotone common MT writer"
    }, indent=2))


if __name__ == "__main__":
    main()
