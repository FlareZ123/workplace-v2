"""Source-only SFT: joint CLASS x DEST affine 4-word printer recurrence.

Read-only. K04 selected late ACK, route mask, commitments and verifier are not used.
Original input: resources/evidence/print/spool-reconstruction.log.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import random
import re

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
CLASSES = ("LABEL", "STORES", "RECOVER")
DESTS = ("store", "bench", "desk")
WITNESS = (
    4, 5, 13, 16, 20, 21, 22, 23, 24, 25, 26, 31, 32, 36,
    38, 40, 41, 42, 45, 46, 47, 48, 52, 53, 54, 55, 58, 59,
    60, 61, 62, 63, 64, 66, 67, 68, 69, 70, 71, 74, 77, 78,
    82, 84, 88, 89, 90, 95, 97, 100, 101, 102, 104, 106,
    107, 108, 110, 112, 113, 116, 117, 118, 125, 127, 131,
    132, 133, 135, 136, 139,
)


def source() -> tuple[list[int], list[int]]:
    path = Path(__file__).resolve().parents[2] / "resources" / "evidence" / "print" / "spool-reconstruction.log"
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SPOOL_SHA256
    rows = [
        dict(re.findall(r"([A-Z]+)=([^ ]+)", line))
        for line in data.decode("ascii").splitlines()
        if line and not line.startswith("#") and "+00:00" in line
    ]
    assert len(rows) == 128
    words = [
        int.from_bytes(bytes.fromhex(row["PAYLOAD"])[i : i + 4], "little")
        for row in rows
        for i in range(0, 16, 4)
    ]
    labels = [
        CLASSES.index(row["CLASS"]) * 3 + DESTS.index(row["DEST"])
        for row in rows
    ]
    assert len(words) == 512 and len(labels) == 128
    print(f"Source SHA256 OK; routine printer rows={len(rows)}; words={len(words)}")
    return words, labels


def feature(words: list[int], labels: list[int], t: int) -> int:
    # 128 unrestricted predecessor bits and nine mutually exclusive joint flags.
    value = sum(words[t - 4 + j] << (32 * j) for j in range(4))
    return value | (1 << (128 + labels[t // 4]))


def reduce(
    basis: dict[int, tuple[int, int]],
    x: int,
    y: int,
) -> tuple[int, int]:
    while x:
        pivot = x.bit_length() - 1
        if pivot not in basis:
            break
        bx, by = basis[pivot]
        x ^= bx
        y ^= by
    return x, y


def original_certificate(words: list[int], labels: list[int]) -> None:
    feature_xor = 0
    output_xor = 0
    class_parity = [0] * 9
    for t in WITNESS:
        feature_xor ^= feature(words, labels, t)
        output_xor ^= words[t]
        class_parity[labels[t // 4]] ^= 1

    assert len(WITNESS) == 70
    assert feature_xor == 0 and class_parity == [0] * 9
    assert output_xor == 0x10078F4E
    print(
        "Original 70-word contradiction: input XOR=0, all nine joint "
        f"category parities=0, successor XOR=0x{output_xor:08X}"
    )

    basis: dict[int, tuple[int, int]] = {}
    first_contradiction: tuple[int, int, int] | None = None
    for t in range(4, 196):
        x, y = reduce(basis, feature(words, labels, t), words[t])
        if x:
            basis[x.bit_length() - 1] = (x, y)
        elif y:
            first_contradiction = (t, y, len(basis))
            break
    assert first_contradiction == (139, 0x10078F4E, 135)
    print("Blind-frozen training stops at t=139; rank=135; no held-out or selected row used")


def synthetic_positive(labels: list[int]) -> None:
    rand = random.Random(4312026)
    coefficients = [rand.getrandbits(128) for _ in range(32)]
    offsets = [rand.getrandbits(32) for _ in range(9)]
    words = [rand.getrandbits(32) for _ in range(4)]

    for t in range(4, 276):
        inputs = sum(words[t - 4 + j] << (32 * j) for j in range(4))
        next_word = sum(
            ((inputs & matrix_row).bit_count() & 1) << bit
            for bit, matrix_row in enumerate(coefficients)
        ) ^ offsets[labels[t // 4]]
        words.append(next_word)

    basis: dict[int, tuple[int, int]] = {}
    for t in range(4, 196):
        x, y = reduce(basis, feature(words, labels, t), words[t])
        if x:
            basis[x.bit_length() - 1] = (x, y)
        else:
            assert y == 0, (t, y)

    assert len(basis) == 137
    for t in range(196, 276):
        x, predicted = reduce(basis, feature(words, labels, t), 0)
        assert x == 0 and predicted == words[t], (t, predicted, words[t])

    print("Synthetic positive: rank 137, 80/80 withheld successor words correctly predicted")


if __name__ == "__main__":
    observed_words, observed_tags = source()
    original_certificate(observed_words, observed_tags)
    synthetic_positive(observed_tags)
    print("Model excluded by intact routine source; K04 selected bits recovered: 0")
