"""H-17 source-conditioned K04 cassette-branch coupon construction SFT.

Run in the repository as: python agents/agent12/h17_k04_decoy_cassette_sft.py
Or set H17_RESOURCE_ROOT to the extracted original archive directory.
Historical sources, acceptance commitments and candidate files are read-only.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import zlib

SOURCE_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
K05_SELECTED = "FF8B78200A56E8586DCDA00EF01E4572"
EXPECTED_CHECKS = 2_097_546


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def orient(data: bytes):
    yield data
    yield data[::-1]
    yield b"".join(data[n:n + 4][::-1] for n in range(0, 16, 4))


def run(root: Path):
    recorder = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
    acceptance_bytes = (root / "acceptance.json").read_bytes()
    routing = json.loads((root / "evidence/recovery-routing.json").read_text(encoding="utf-8"))
    assert digest(recorder) == SOURCE_SHA
    assert digest(acceptance_bytes) == ACCEPT_SHA
    acceptance = json.loads(acceptance_bytes)
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    assert recorder[:8] == b"TRP2DUMP"
    version, size, count = struct.unpack_from("<HHI", recorder, 8)
    assert (version, size, len(recorder)) == (2, 24, 16 + count * 24)
    series: dict[int, dict[int, bytes]] = {base: {} for base in (200, 300, 900, 990)}
    validity: dict[int, list[bool]] = {base: [] for base in series}
    for n in range(count):
        row = recorder[16 + n * 24:16 + (n + 1) * 24]
        sec, node, event, latch, seq, word, aux, crc = struct.unpack("<IHBBI4sII", row)
        base = seq - latch
        if node == 49 and event == 82 and base in series:
            assert 0 <= latch <= 3 and latch not in series[base]
            series[base][latch] = word
            validity[base].append(zlib.crc32(row[:20]) == crc)
    assert all(len(v) == 4 for v in series.values())
    assert validity == {200: [True] * 4, 300: [True] * 4,
                        900: [False] * 4, 990: [True] * 4}
    blocks = {base: b"".join(series[base][i] for i in range(4)) for base in series}
    assert blocks[300].hex().upper() == K05_SELECTED
    assert digest(blocks[300]) == acceptance["slot_sha256"]["K05"]

    # Source-visible complete variants and their 32 opaque four-byte words.
    # No assumption that recorder and printer share physical producer.
    word_choices = [word[::-1] if reverse else word
                    for data in blocks.values()
                    for n in range(4)
                    for reverse in (False, True)
                    for word in (data[n * 4:n * 4 + 4],)]
    assert len(word_choices) == len(set(word_choices)) == 32
    planted = b"".join(word_choices[i] for i in (1, 10, 19, 26))
    planted_hash = digest(xor_bytes(planted, mask))
    checked = 0
    actual_hits = 0
    planted_hits = 0

    def check(data: bytes):
        nonlocal checked, actual_hits, planted_hits
        for value in (data, xor_bytes(data, mask)):
            checked += 1
            d = digest(value)
            actual_hits += d == target
            planted_hits += d == planted_hash

    for data in blocks.values():
        for variant in orient(data):
            check(variant)
    for (base_a, a), (base_b, b) in itertools.combinations(blocks.items(), 2):
        for operation in ("xor", "add128", "sub128", "add8", "sub8"):
            for swap in (False, True):
                x, y = (b, a) if swap else (a, b)
                if operation == "xor":
                    result = xor_bytes(x, y)
                elif operation == "add128":
                    result = ((int.from_bytes(x, "little") + int.from_bytes(y, "little")) % (1 << 128)).to_bytes(16, "little")
                elif operation == "sub128":
                    result = ((int.from_bytes(x, "little") - int.from_bytes(y, "little")) % (1 << 128)).to_bytes(16, "little")
                elif operation == "add8":
                    result = bytes((i + j) % 256 for i, j in zip(x, y))
                else:
                    result = bytes((i - j) % 256 for i, j in zip(x, y))
                for variant in orient(result):
                    check(variant)
    for keys in itertools.combinations(blocks, 3):
        a, b, c = (blocks[k] for k in keys)
        check(bytes(i ^ j ^ k for i, j, k in zip(a, b, c)))
    check(bytes(a ^ b ^ c ^ d for a, b, c, d in zip(*blocks.values())))
    for words in itertools.product(word_choices, repeat=4):
        check(b"".join(words))

    print(f"original_recorder_sha256={SOURCE_SHA}")
    print(f"cassette_branch_blocks={{{', '.join(f'{k}: {v.hex().upper()}' for k, v in blocks.items())}}}")
    print(f"complete_original_K04_checks={checked} K04_matches={actual_hits} synthetic_positive={planted_hits}")
    assert checked == EXPECTED_CHECKS and actual_hits == 0 and planted_hits == 1


if __name__ == "__main__":
    root = Path(os.environ.get("H17_RESOURCE_ROOT", str(Path(__file__).resolve().parents[2] / "resources")))
    run(root)
