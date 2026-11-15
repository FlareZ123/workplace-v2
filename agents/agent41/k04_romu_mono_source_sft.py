"""Source-only RomuMono native32 printer-packet producer test.

RomuMono emits the low 32 bits of its 64-bit state; rotation by 32 and
an odd 64-bit multiplier make consecutive outputs sufficient to
reconstruct its full state. Original selected K04 ACK2 is never read.
"""
from __future__ import annotations

import hashlib
import os
import re
from collections import defaultdict
from pathlib import Path

C = 15241094284759029579
M64 = (1 << 64) - 1
M32 = (1 << 32) - 1
I32 = pow(C, -1, 1 << 32)
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SOURCE = Path(__file__).resolve().parents[2] / "resources" / "evidence" / "print" / "spool-reconstruction.log"


def next_state(state: int) -> int:
    return ((((state & M32) << 32) | (state >> 32)) * C) & M64


def predict(a: int, b: int) -> int:
    high = (b * I32) & M32
    state = (high << 32) | a
    state = next_state(state)
    assert state & M32 == b
    return next_state(state) & M32


def test() -> None:
    state = 0xD3ABBB18331286AA
    values = []
    for _ in range(15):
        values.append(state & M32)
        state = next_state(state)
    assert all(predict(values[i], values[i + 1]) == values[i + 2] for i in range(13))
    assert predict(values[-3], values[-2]) != (values[-1] ^ 1)
    print("RomuMono planted and mutation controls: PASS")

    source = Path(os.environ.get("H17_PRINTER_SOURCE", SOURCE)).read_bytes()
    assert hashlib.sha256(source).hexdigest() == PIN
    rows = [
        dict(re.findall(r"(\w+)=([^\s]+)", line))
        for line in source.decode("ascii").splitlines() if "JOB=" in line
    ]
    assert len(rows) == 133
    assert rows[129]["JOB"] == "PS-261003-0417" and rows[129]["ATTEMPT"] == "2"
    for i, row in enumerate(rows[:128]):
        assert row["JOB"] == f"PS-261003-{300 + i:04d}"
        assert row["ATTEMPT"] == "1" and row["STATE"] == "ACK"

    groups = {"whole": rows[:128]}
    for key in ("CLASS", "DEST", "JOINT"):
        by = defaultdict(list)
        for row in rows[:128]:
            group = row["CLASS"] + "/" + row["DEST"] if key == "JOINT" else row[key]
            by[group].append(row)
        groups.update({key + ":" + name: items for name, items in by.items()})

    checked = matched = 0
    for group_name, group in groups.items():
        for endian in ("big", "little"):
            for reverse in (False, True):
                words = []
                for row in group:
                    payload = bytes.fromhex(row["PAYLOAD"])
                    packet = [int.from_bytes(payload[i:i + 4], endian) for i in range(0, 16, 4)]
                    if reverse:
                        packet.reverse()
                    words.extend(packet)
                for i in range(len(words) - 2):
                    checked += 1
                    if predict(words[i], words[i + 1]) == words[i + 2]:
                        matched += 1
                        print("ORIGINAL MATCH:", group_name, endian, reverse, i)
    print("RomuMono original source predictions:", checked, "matched", matched)
    assert matched == 0, "Historical prediction match requires investigation"


if __name__ == "__main__":
    test()
