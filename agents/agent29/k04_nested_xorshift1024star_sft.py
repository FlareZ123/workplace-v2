"""Original-source nested xorshift1024star seed-stream test; no selected coupon/hash use.
Run: python agents/agent29/k04_nested_xorshift1024star_sft.py
"""
from __future__ import annotations
import hashlib
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent15"))
import k04_p951_sha512_seed_fingerprint_sft as source
MASK = (1 << 64) - 1
MULTIPLIER = 1181783497276652981
INVERSE = pow(MULTIPLIER, -1, 1 << 64)
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def next_inner(state: list[int], pointer: int) -> tuple[int, int]:
    previous = state[pointer]
    pointer = (pointer + 1) & 15
    current = state[pointer]
    current ^= (current << 31) & MASK
    current ^= current >> 11
    previous ^= previous >> 30
    state[pointer] = (previous ^ current) & MASK
    return pointer, state[pointer]

def original_domains() -> dict[int, list[int]]:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    packets = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(packets) == len(source.STARTS) == 133 and source.STARTS[129] == 951
    intact = [b"" if n == 129 else bytes.fromhex(word.decode())
              for n, word in enumerate(packets)]
    _, _, result = source.derive_seed_digest_words(intact, source.expressions())
    assert len(result) == 86 and sum(len(v) == 1 for v in result.values()) == 62
    assert result[602] == [0x64589C88, 0xE4589C88]
    assert result[22] == [0xFD6A4CF7]
    return result

def seed_byte_masks(domains: dict[int, list[int]]) -> tuple[list[int], list[int]]:
    values = [0] * (4 * (602 - 16 + 1))
    masks = [0] * len(values)
    for j, choices in domains.items():
        base = 4 * (602 - j)
        options = [value.to_bytes(4, "big") for value in choices]
        for k in range(4):
            first = options[0][k]
            uncertain = 0
            for alternative in options[1:]:
                uncertain |= first ^ alternative[k]
            values[base + k] = first & ~uncertain
            masks[base + k] = 255 & ~uncertain
            assert masks[base + k] in (0x7F, 0xFF)
    return values, masks

def observations(domains: dict[int, list[int]], phase: int, endian: str) -> list[tuple[int, int, int]]:
    values, masks = seed_byte_masks(domains)
    found = []
    for t in range((len(values) - phase + 7) // 8):
        base = phase + 8 * t
        if base >= len(values):
            break
        offsets = range(base, base + 8) if endian == "little" else range(base + 7, base - 1, -1)
        known = raw_value = 0
        for offset in offsets:
            if offset >= len(values) or offset < 0 or not masks[offset]:
                break
            n = masks[offset].bit_length()
            assert masks[offset] == (1 << n) - 1
            raw_value |= (values[offset] & masks[offset]) << known
            known += n
            if n < 8:
                break
        if known:
            unmultiplied = (raw_value * INVERSE) & ((1 << known) - 1)
            found.append((t, known, unmultiplied))
    return found

def coefficient_rows(observations_: list[tuple[int, int, int]]) -> list[int]:
    times = {t: (i, k) for i, (t, k, _) in enumerate(observations_)}
    offsets = []
    count = 0
    for _, k, _ in observations_:
        offsets.append(count)
        count += k
    rows = [0] * count
    for bit in range(1024):
        state = [0] * 16
        state[bit // 64] = 1 << (bit % 64)
        pointer = 0
        for t in range(observations_[-1][0] + 1):
            pointer, word = next_inner(state, pointer)
            slot = times.get(t)
            if slot is None:
                continue
            index, known = slot
            word &= (1 << known) - 1
            while word:
                pivot = (word & -word).bit_length() - 1
                rows[offsets[index] + pivot] |= 1 << bit
                word &= word - 1
    return rows

def consistent(domains: dict[int, list[int]], phase: int, endian: str) -> tuple[bool, int, int, int]:
    obs = observations(domains, phase, endian)
    rows = coefficient_rows(obs)
    basis: dict[int, int] = {}
    index = 0
    for output, known, result in obs:
        for bit in range(known):
            equation = (rows[index] << 1) | ((result >> bit) & 1)
            index += 1
            while equation > 1:
                pivot = equation.bit_length() - 1
                prev = basis.get(pivot)
                if prev is None:
                    basis[pivot] = equation
                    break
                equation ^= prev
            if equation == 1:
                return False, len(basis), index, len(rows)
    return True, len(basis), index, len(rows)

def positive(ground: dict[int, list[int]], phase: int, endian: str) -> None:
    state = [(0x123456789ABCDEF0 ^ i * 0x9E3779B97F4A7C15) & MASK for i in range(16)]
    pointer = 0
    stream = bytearray()
    for _ in range(310):
        pointer, word = next_inner(state, pointer)
        stream.extend(((word * MULTIPLIER) & MASK).to_bytes(8, endian))
    offset = (8 - phase) % 8
    synthetic = {}
    for j, options in ground.items():
        start = 4 * (602 - j) + offset
        value = int.from_bytes(stream[start:start + 4], "big")
        synthetic[j] = ([value & 0x7FFFFFFF, value | 0x80000000]
                        if len(options) == 2 else [value])
    ok, rank, used, total = consistent(synthetic, phase, endian)
    assert ok and rank == 1024 and used == total, (phase, endian, rank)

def main() -> None:
    domains = original_domains()
    for phase in range(8):
        for endian in ("big", "little"):
            positive(domains, phase, endian)
            ok, rank, used, total = consistent(domains, phase, endian)
            print(f"phase={phase} endian={endian} planted=PASS original_consistent={ok} "
                  f"rank={rank} equations={total} checked={used}", flush=True)
            assert not ok
    print("PASS: 16 phase/endianness original-source exclusions and 16 planted positives")

if __name__ == "__main__":
    main()
