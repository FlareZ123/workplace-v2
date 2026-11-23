#!/usr/bin/env python3
"""Source-blind RC-17 footer / printer MT firstword recurrence census.

No native stage mapping, 624word state fit, K04 target, mask, or copied ACK2.
Execute: python agents/agent21/k04_rc17_sourceblind_firstword_census_sft.py [resources-or-zip]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
RC17_SHA = "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"
U32 = 0xFFFFFFFF


def read_evidence(root: Path, name: str) -> bytes:
    if root.is_file() and root.suffix.lower() == ".zip":
        with zipfile.ZipFile(root) as archive:
            return archive.read("evidence/" + name)
    return (root / "evidence" / name).read_bytes()


def untemper(value: int) -> int:
    for shift, left, mask in ((18, False, U32), (15, True, 0xEFC60000),
                               (7, True, 0x9D2C5680), (11, False, U32)):
        original = value
        for _ in range(6):
            value = (original ^ (((value << shift) & mask) if left else
                                 value >> shift)) & U32
    return value


def twist(first: int, second: int) -> int:
    both = (first & 0x80000000) | (second & 0x7FFFFFFF)
    return (both >> 1) ^ (0x9908B0DF if both & 1 else 0)


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else ROOT / "resources"
    raw_spool = read_evidence(root, "print/spool-reconstruction.log")
    raw_rc17 = read_evidence(root, "procedures/RC-17-scans.txt")
    assert hashlib.sha256(raw_spool).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(raw_rc17).hexdigest() == RC17_SHA

    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw_spool, re.M
    )
    assert len(rows) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    native = [
        None if index == 129 else tuple(
            untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4 * lane:4 * lane + 4],
                                    "little")) for lane in range(4)
        )
        for index, row in enumerate(rows)
    ]
    assert native[129] is None
    footers = []
    for page in raw_rc17.split(b"\x0c"):
        title = re.search(rb"DOCUMENT RC-17 / REV ([^ /]+) / SECTION ([A-Z]+)", page)
        footer = re.search(rb"Footer control strip: ([0-9A-F]{8})", page)
        if title and footer:
            footers.append((title[1].decode(), title[2].decode(), bytes.fromhex(footer[1].decode())))
    assert len(footers) == 12

    # Positive arithmetic MT native recurrence control from 624 independent words.
    planted = [(i * 0x9E3779B9 ^ (i << 9) ^ 0xF0101234) & U32
               for i in range(624)]
    assert planted[397] ^ twist(planted[0], planted[1]) == 0x420FCFC8

    exact = defaultdict(list)
    for row, packet in enumerate(native):
        if packet is not None:
            for lane, word in enumerate(packet):
                exact[word].append((row, lane))
    assert sum(len(x) for x in exact.values()) == 528

    hits = []
    proposals = 0
    for endian in ("little", "big"):
        for view in ("tempered", "native"):
            values = [
                untemper(int.from_bytes(v, endian)) if view == "tempered"
                else int.from_bytes(v, endian) for _, _, v in footers
            ]
            for first in range(12):
                for second in range(12):
                    if first == second:
                        continue
                    transfer = twist(values[first], values[second])
                    for middle_row, packet in enumerate(native):
                        if packet is None:
                            continue
                        for middle_lane, word in enumerate(packet):
                            proposals += 1
                            for later_row, later_lane in exact.get(word ^ transfer, ()):
                                if later_row > middle_row:
                                    hits.append((
                                        endian, view, first, second,
                                        middle_row, middle_lane, later_row, later_lane
                                    ))
    assert proposals == 278784
    assert len(hits) == 12
    assert all(endian == "little" and view == "tempered" for endian, view, *_ in hits)
    assert {second for _, _, _, second, *_ in hits} == {0, 1}
    assert Counter((second, row, lane, later, out)
                   for _, _, _, second, row, lane, later, out in hits) == {
        (0, 28, 2, 59, 3): 6, (1, 28, 1, 59, 2): 6
    }
    a = untemper(int.from_bytes(bytes.fromhex("C130C9BB"), "little"))
    b = untemper(int.from_bytes(bytes.fromhex("759E0027"), "little"))
    assert native[28][2] ^ twist(a, b) == native[59][3]
    assert native[28][1] ^ twist(b, a) == native[59][2]
    assert twist(a ^ 0x7FFFFFFF, b) == twist(a, b)
    assert twist(a ^ 0x80000000, b) != twist(a, b)

    print(json.dumps({
        "source_spool_sha256": SPOOL_SHA,
        "source_rc17_sha256": RC17_SHA,
        "selected_payload_parsed": False,
        "sourceblind_footer_pair_printer_proposals": proposals,
        "sourceblind_fullword_matches": len(hits),
        "matches_by_second_footer": {
            "B_PURGE": 6,
            "B_VERIFY": 6
        },
        "distinct_printer_middle_future_pairs": [[28, 2, 59, 3], [28, 1, 59, 2]],
        "additional_first_footer_value_information_bits_per_match": 1,
        "unrestricted_first_footer_identity_authenticated": False,
        "K04_recovered": False,
        "note": "MT twist ignores all first-word bits except bit31; twelve matches collapse into two near-equivalent families"
    }, indent=2))


if __name__ == "__main__":
    main()
