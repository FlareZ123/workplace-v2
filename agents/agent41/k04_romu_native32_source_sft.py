"""Source-only H-17 RomuTrio32 and RomuMono32 producer test.

Reads the official unmodified printer log. The disputed selected 18:02
ACK2 row is excluded. Genuine planted generator outputs are positive
controls. Requires Python 3 and NumPy for vectorized 2^16 Mono inversion.
"""
from __future__ import annotations

import hashlib
import os
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
M32 = (1 << 32) - 1
TRIO_CONSTANT = 3323815723
MONO_CONSTANT = 3611795771
INVERSE = pow(TRIO_CONSTANT, -1, 1 << 32)
LOW16 = np.arange(1 << 16, dtype=np.uint32)


def rol32(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & M32


def ror32(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & M32


def trio_step(state: tuple[int, int, int]) -> tuple[int, int, int]:
    x, y, z = state
    return (
        TRIO_CONSTANT * z & M32,
        rol32((y - x) & M32, 6),
        rol32((z - y) & M32, 22),
    )


def trio_next(x0: int, x1: int, x2: int) -> int:
    z0 = INVERSE * x1 & M32
    z1 = INVERSE * x2 & M32
    y0 = (z0 - ror32(z1, 22)) & M32
    state = (x0, y0, z0)
    for _ in range(3):
        state = trio_step(state)
    return state[0]


def mono_step(v: np.ndarray) -> np.ndarray:
    x = v * np.uint32(MONO_CONSTANT)
    return (x << np.uint32(12)) | (x >> np.uint32(20))


def mono_packet_survivors(words: list[int]) -> tuple[int, int]:
    # Entire 2^16 unknown low-state residue for the first observed high16.
    states = (np.uint32(words[0]) << np.uint32(16)) | LOW16
    pair_count = 0
    for j in range(1, len(words)):
        states = mono_step(states)
        matching = ((states >> np.uint32(16)) == words[j])
        if j == 1:
            pair_count = int(matching.sum())
        states = states[matching]
        if states.size == 0:
            return pair_count, 0
    return pair_count, int(states.size)


def planted() -> None:
    for offset in range(30):
        state = (0x831BAC72 + offset, 0x6A1FD99E + offset, 0x75230C84 + offset)
        values = []
        for _ in range(8):
            values.append(state[0])
            state = trio_step(state)
        assert all(trio_next(*values[i:i+3]) == values[i+3] for i in range(5))
    seed = np.uint32(0xABCD1234)
    values = []
    for _ in range(8):
        values.append(int(seed >> np.uint32(16)))
        seed = mono_step(np.array([seed], dtype=np.uint32))[0]
    assert mono_packet_survivors(values)[1] >= 1
    values[-1] ^= 1
    assert mono_packet_survivors(values)[1] == 0
    print("Planted Trio32 and Mono32 sequence / mutation controls: PASS")


def main() -> None:
    planted()
    data = Path(os.environ.get("H17_PRINTER_SOURCE", SOURCE)).read_bytes()
    assert hashlib.sha256(data).hexdigest() == PIN
    rows = [
        dict(re.findall(r"(\w+)=([^\s]+)", line))
        for line in data.decode("ascii").splitlines() if "JOB=" in line
    ]
    assert len(rows) == 133
    assert rows[129]["JOB"] == "PS-261003-0417"
    assert rows[129]["ATTEMPT"] == "2" and rows[129]["STATE"] == "ACK"
    for i, row in enumerate(rows[:128]):
        assert row["JOB"] == f"PS-261003-{i+300:04d}"
        assert row["STATE"] == "ACK" and row["ATTEMPT"] == "1"

    grouped = {"all": rows[:128]}
    for field in ("CLASS", "DEST", "JOINT"):
        parts = defaultdict(list)
        for row in rows[:128]:
            label = row["CLASS"] + "/" + row["DEST"] if field == "JOINT" else row[field]
            parts[label].append(row)
        grouped.update({field+":"+label:subset for label,subset in parts.items()})

    trio_checked = trio_matches = 0
    within_checked = within_matches = 0
    for subset in grouped.values():
        for endian in ("big", "little"):
            for reverse in (False, True):
                stream = []
                for row in subset:
                    blob = bytes.fromhex(row["PAYLOAD"])
                    words = [int.from_bytes(blob[i:i+4], endian) for i in (0, 4, 8, 12)]
                    if reverse:
                        words.reverse()
                    within_checked += 1
                    within_matches += (trio_next(*words[:3]) == words[3])
                    stream.extend(words)
                trio_checked += len(stream)-3
                trio_matches += sum(trio_next(*stream[i:i+3]) == stream[i+3]
                                    for i in range(len(stream)-3))
    print("RomuTrio32:", trio_matches, "/", trio_checked,
          "source-next-word; within-packet:", within_matches, "/", within_checked)
    assert (trio_matches, trio_checked, within_matches, within_checked) == (0, 8000, 0, 2048)

    mono_checks = mono_pairs = mono_full = 0
    for i, row in enumerate(rows):
        if i == 129:
            continue  # withhold the selected ACK2 entirely
        blob = bytes.fromhex(row["PAYLOAD"])
        for endian in ("big", "little"):
            words = [int.from_bytes(blob[j:j+2], endian) for j in range(0, 16, 2)]
            for reverse in (False, True):
                candidate = list(reversed(words)) if reverse else words
                pair_count, survived = mono_packet_survivors(candidate)
                mono_checks += 1
                mono_pairs += pair_count
                mono_full += survived
    print("RomuMono32:", mono_full, "/", mono_checks,
          "whole 16-byte original packet matches;", mono_pairs,
          "one-step residue matches")
    assert (mono_checks, mono_pairs, mono_full) == (528, 518, 0)
    print("selected_K04_or_K08_recovered: no; original files unchanged")


if __name__ == "__main__":
    main()
