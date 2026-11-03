"""Source-pinned xoshiro** / xoroshiro** / Marsaglia xorshift exact producer SFT.

Invert multiplication/rotation output scramblers and solve the resulting
linear state equations. Training uses only 6 ordinary rows; the remaining
122 are withheld. The selected PS-261003-0417 attempt-2 ACK is excluded.
"""
from __future__ import annotations

import hashlib
import itertools
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
GAPS = (0, 1, 2, 3, 4, 8, 16, 32)
MODELS = (
    "xoshiro256ss", "xoshiro128ss", "xoroshiro128ss",
    "marsaglia_xorshift128", "marsaglia_xorshift32", "marsaglia_xorshift64",
)

def xor(a: list[int], b: list[int]) -> list[int]:
    return [x ^ y for x, y in zip(a, b)]

def rot(v: list[int], k: int) -> list[int]:
    k %= len(v)
    return v[-k:] + v[:-k] if k else v[:]

def left(v: list[int], k: int) -> list[int]:
    return [0] * k + v[:-k]

def right(v: list[int], k: int) -> list[int]:
    return v[k:] + [0] * k

def rot_int(x: int, k: int, width: int) -> int:
    mask = (1 << width) - 1
    return ((x << k) | (x >> (width - k))) & mask

def width_for(model: str) -> int:
    return 32 if model in ("xoshiro128ss", "marsaglia_xorshift128", "marsaglia_xorshift32") else 64

def state_words(model: str) -> int:
    if model.startswith("xoshiro") or model == "marsaglia_xorshift128":
        return 4
    return 1 if model.startswith("marsaglia_") else 2

def step(model: str, state: list):
    """Exact generator state step, with integer or symbolic GF(2) words."""
    symbolic = isinstance(state[0], list)
    width = width_for(model)
    mask = (1 << width) - 1
    a = xor if symbolic else lambda x, y: x ^ y
    b = rot if symbolic else lambda x, k: rot_int(x, k, width)
    shift = left if symbolic else lambda x, k: (x << k) & mask
    rshift = right if symbolic else lambda x, k: x >> k

    if model.startswith("marsaglia_"):
        if model == "marsaglia_xorshift128":
            x, y, z, w = state
            t = a(x, shift(x, 11))
            t = a(t, rshift(t, 8))
            nw = a(a(w, rshift(w, 19)), t)
            return nw, [y, z, w, nw]
        x = state[0]
        shifts = (("L", 13), ("R", 17), ("L", 5)) if width == 32 else (
            ("L", 13), ("R", 7), ("L", 17))
        for direction, k in shifts:
            x = a(x, shift(x, k) if direction == "L" else rshift(x, k))
        return x, [x]

    if model.startswith("xoshiro"):
        s0, s1, s2, s3 = state
        out = s1
        t = shift(s1, 9 if width == 32 else 17)
        s2 = a(s2, s0)
        s3 = a(s3, s1)
        s1 = a(s1, s2)
        s0 = a(s0, s3)
        s2 = a(s2, t)
        s3 = b(s3, 11 if width == 32 else 45)
        return out, [s0, s1, s2, s3]

    s0, s1 = state
    out = s0
    s1 = a(s1, s0)
    return out, [a(a(b(s0, 24), s1), shift(s1, 16)), b(s1, 37)]

def scramble(word: int, width: int) -> int:
    mask = (1 << width) - 1
    return rot_int(word * 5 & mask, 7, width) * 9 & mask

def unscramble(out: int, width: int) -> int:
    mask = (1 << width) - 1
    return rot_int(out * pow(9, -1, 1 << width) & mask, width - 7, width) * pow(5, -1, 1 << width) & mask

def symbolic_model(model: str, count: int, gap: int) -> list[list[int]]:
    width = width_for(model)
    state = [[1 << (w * width + j) for j in range(width)] for w in range(state_words(model))]
    out = []
    packet_words = 128 // width
    for index in range(count):
        word, state = step(model, state)
        out.append(word)
        if (index + 1) % packet_words == 0 and index + 1 < count:
            for _ in range(gap):
                _, state = step(model, state)
    return out

def recover(model: str, packets: list[bytes], endian: str, order: tuple[int, ...], gap: int):
    width = width_for(model)
    size = width // 8
    observations = [
        int.from_bytes(p[i * size:(i + 1) * size], endian)
        for p in packets[:6] for i in order
    ]
    linear = symbolic_model(model, len(observations), gap)
    rank = 0
    basis = {}
    for idx, (symbols, value) in enumerate(zip(linear, observations)):
        state_word = value if model.startswith("marsaglia_") else unscramble(value, width)
        for bit, equation in enumerate(symbols):
            rhs = (state_word >> bit) & 1
            while equation:
                pivot = equation.bit_length() - 1
                if pivot in basis:
                    prev, val = basis[pivot]
                    equation ^= prev
                    rhs ^= val
                else:
                    basis[pivot] = (equation, rhs)
                    rank += 1
                    break
            if not equation and rhs:
                return False, rank, idx, bit
    nvars = width * state_words(model)
    if rank < nvars:
        return None, rank, None, None
    seed = 0
    for pivot in sorted(basis):
        row, rhs = basis[pivot]
        if rhs ^ ((row & seed).bit_count() & 1):
            seed |= 1 << pivot
    state = [(seed >> (i * width)) & ((1 << width) - 1) for i in range(state_words(model))]
    matches = 0
    for packet in packets:
        assembled = [None] * len(order)
        for idx in order:
            word, state = step(model, state)
            result = word if model.startswith("marsaglia_") else scramble(word, width)
            assembled[idx] = result.to_bytes(size, endian)
        if b"".join(assembled) != packet:
            return False, rank, matches, None
        matches += 1
        for _ in range(gap):
            _, state = step(model, state)
    return True, rank, matches, seed

def synthetic(model: str, gap: int, endian: str, reverse: bool, count: int = 12):
    width = width_for(model)
    state = [
        (0xA5F304927CAB16D5 >> (i * 9)) & ((1 << width) - 1)
        for i in range(state_words(model))
    ]
    packets = []
    for _ in range(count):
        words = []
        for _ in range(128 // width):
            out, state = step(model, state)
            value = out if model.startswith("marsaglia_") else scramble(out, width)
            words.append(value.to_bytes(width // 8, endian))
        packets.append(b"".join(reversed(words) if reverse else words))
        for _ in range(gap):
            _, state = step(model, state)
    return packets

def main():
    source_sha = hashlib.sha256(SPOOL.read_bytes()).hexdigest()
    assert source_sha == PIN
    rows = []
    for line in SPOOL.read_text().splitlines():
        match = re.search(r"JOB=PS-261003-(\d{4}) ATTEMPT=1 STATE=ACK .*?PAYLOAD=([0-9A-F]{32})", line)
        if match and 300 <= int(match.group(1)) <= 427:
            rows.append((int(match.group(1)), bytes.fromhex(match.group(2))))
    rows.sort()
    assert [job for job, _ in rows] == list(range(300, 428))
    packets = [data for _, data in rows]
    print("sha256=", source_sha, "ordinary packets=", len(packets))

    controls = (
        ("xoshiro256ss", "little", False, 0),
        ("xoshiro128ss", "big", True, 3),
        ("xoroshiro128ss", "little", True, 1),
        ("marsaglia_xorshift128", "big", False, 2),
        ("marsaglia_xorshift32", "little", True, 4),
        ("marsaglia_xorshift64", "big", True, 8),
    )
    for model, endian, reverse, gap in controls:
        n = 128 // width_for(model)
        order = tuple(reversed(range(n))) if reverse else tuple(range(n))
        ok, rank, matched, _ = recover(model, synthetic(model, gap, endian, reverse), endian, order, gap)
        print("synthetic", model, "rank=", rank, "matched=", matched, "PASS=", ok)
        assert ok is True and matched == 12

    attempts = fullrank = 0
    matches = []
    for model in MODELS:
        n = 128 // width_for(model)
        orders = (tuple(range(n)), tuple(reversed(range(n))))
        for endian, order, gap in itertools.product(("little", "big"), orders, GAPS):
            attempts += 1
            ok, rank, matched, _ = recover(model, packets, endian, order, gap)
            if rank == width_for(model) * state_words(model):
                fullrank += 1
            if ok:
                matches.append((model, endian, order, gap, matched))
    print("attempts=", attempts, "full_rank=", fullrank, "source_matches=", matches)
    assert attempts == 192
    assert not matches

if __name__ == "__main__":
    main()
