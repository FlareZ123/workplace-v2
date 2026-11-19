#!/usr/bin/env python3
"""Source-stage LOW BIT component bridge for the K08 note selector network."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))

K02_RAW = bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
K07_RAW = bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9")


def low_value(text: str) -> int:
    return sum((ord(ch) & 1) << i for i, ch in enumerate(text))


def low_pack(raw: bytes) -> bytes:
    assert len(raw) % 8 == 0
    return bytes(
        sum((raw[i + j] & 1) << j for j in range(8))
        for i in range(0, len(raw), 8)
    )


def source_selector(raw: bytes) -> tuple[str, int]:
    packed = low_pack(raw).hex().upper()
    return packed, low_value(packed)


def main() -> None:
    assert (
        hashlib.sha256(K02_RAW).digest()[:16].hex().upper()
        == CANDIDATE["K02"]
    )
    assert (
        hashlib.sha256(K07_RAW).digest()[:16].hex().upper()
        == CANDIDATE["K07"]
    )

    source = {
        1: bytes.fromhex(CANDIDATE["K01"]),
        2: K02_RAW,
        5: bytes.fromhex(CANDIDATE["K05"]),
        6: bytes.fromhex(CANDIDATE["K06"]),
        7: K07_RAW,
    }
    decoded = {
        index: source_selector(raw)
        for index, raw in source.items()
    }
    assert decoded == {
        1: ("0479", 12),
        2: ("A3FC", 11),
        5: ("0343", 10),
        6: ("8345", 10),
        7: ("53D5", 11),
    }

    assert [low_value(w) for w in ("A", "LOW", "BIT")] == [1, 6, 2]
    assert [
        decoded[low_value(w)][1]
        for w in ("A", "LOW", "BIT")
    ] == [12, 10, 11]

    assert [low_value(w) for w in ("TEA", "SEA")] == [6, 7]
    assert [
        decoded[low_value(w)][1]
        for w in ("TEA", "SEA")
    ] == [10, 11]

    assert [low_value(w) for w in ("MUG", "SHELF")] == [7, 5]
    assert [
        decoded[low_value(w)][1]
        for w in ("MUG", "SHELF")
    ] == [11, 10]

    print(
        "SOURCE_MAP="
        + json.dumps({k: v[1] for k, v in decoded.items()}, sort_keys=True)
    )
    print("A_LOW_BIT -> 12,10,11")
    print("TEA_SEA -> 10,11")
    print("MUG_SHELF -> 11,10")
    print("PASS")


if __name__ == "__main__":
    main()
