"""Original-source, read-only short-state generator tests for H-17 spool.

The first 128 regular ACKs are intact controls. The disputed selected ACK,
requested attempts, and special print jobs are deliberately excluded.
Tests xoshiro128**, xoroshiro128**, and xoshiro256** direct output.
No acceptance commitment or candidate is read by this experiment.
"""
from __future__ import annotations

import re
from pathlib import Path
from random import Random

MASK64 = (1 << 64) - 1
SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"


def rol(x: int, k: int, bits: int) -> int:
    mask = (1 << bits) - 1
    return ((x << k) | (x >> (bits - k))) & mask


def ror(x: int, k: int, bits: int) -> int:
    mask = (1 << bits) - 1
    return ((x >> k) | (x << (bits - k))) & mask


def inverse_output(y: int, bits: int) -> int:
    mask = (1 << bits) - 1
    return (ror((y * pow(9, -1, 1 << bits)) & mask, 7, bits)
            * pow(5, -1, 1 << bits)) & mask


def xoshiro_output(s: tuple[int, int, int, int], bits: int) -> int:
    return (rol((s[1] * 5) & ((1 << bits) - 1), 7, bits) * 9) & ((1 << bits) - 1)


def xoshiro_step(s: tuple[int, int, int, int], bits: int) -> tuple[int, int, int, int]:
    a, b, c, d = s
    mask = (1 << bits) - 1
    t = (b << (9 if bits == 32 else 17)) & mask
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= t
    d = rol(d, 11 if bits == 32 else 45, bits)
    return a & mask, b & mask, c & mask, d & mask


def xoroshiro_output(s: tuple[int, int]) -> int:
    return (rol((s[0] * 5) & MASK64, 7, 64) * 9) & MASK64


def xoroshiro_step(s: tuple[int, int]) -> tuple[int, int]:
    a, b = s
    b ^= a
    a = rol(a, 24, 64) ^ b ^ ((b << 16) & MASK64)
    return a & MASK64, rol(b, 37, 64)


def solve_gf2(equations: list[tuple[int, int]]) -> tuple[int, int]:
    pivots: dict[int, tuple[int, int]] = {}
    for row, rhs in equations:
        while row:
            i = row.bit_length() - 1
            if i in pivots:
                prow, prhs = pivots[i]
                row ^= prow
                rhs ^= prhs
            else:
                pivots[i] = (row, rhs)
                break
        if row == 0 and rhs:
            raise AssertionError("Inconsistent source equations")
    x = 0
    for i, (row, rhs) in sorted(pivots.items()):
        x |= (rhs ^ ((row & x).bit_count() & 1)) << i
    return x, len(pivots)


def basis(bits: int) -> list[int]:
    rows = [0] * (4 * bits)
    mask = (1 << bits) - 1
    for j in range(4 * bits):
        s = tuple(((1 << j) >> (bits * i)) & mask for i in range(4))
        for t in range(4):
            for k in range(bits):
                if (s[1] >> k) & 1:
                    rows[t * bits + k] |= 1 << j
            s = xoshiro_step(s, bits)
    return rows


BASES = {32: basis(32), 64: basis(64)}


def recover_xoshiro(values: list[int], bits: int) -> tuple[tuple[int, int, int, int], int]:
    assert len(values) == 4
    known = [inverse_output(v, bits) for v in values]
    equations = [(BASES[bits][t * bits + b], (known[t] >> b) & 1)
                 for t in range(4) for b in range(bits)]
    x, rank = solve_gf2(equations)
    mask = (1 << bits) - 1
    s = tuple((x >> (bits * i)) & mask for i in range(4))
    for v in values:
        assert xoshiro_output(s, bits) == v
        s = xoshiro_step(s, bits)
    return s, rank


def recover_xoroshiro(values: list[int]) -> tuple[tuple[int, int], int]:
    assert len(values) == 2
    a0, a1 = [inverse_output(v, 64) for v in values]
    q = a1 ^ rol(a0, 24, 64)
    # Invert x ^ (x << 16), modulo 2**64.
    b = q
    b ^= (b << 16) & MASK64
    b ^= (b << 32) & MASK64
    s = (a0, b ^ a0)
    assert xoroshiro_output(s) == values[0]
    s = xoroshiro_step(s)
    assert xoroshiro_output(s) == values[1]
    return xoroshiro_step(s), 128


def load_regular() -> list[bytes]:
    lines = [line for line in SOURCE.read_text(encoding="utf-8").splitlines()
             if "PAYLOAD=" in line]
    assert len(lines) == 133
    result = []
    for i, line in enumerate(lines[:128]):
        assert f"JOB=PS-261003-{300 + i:04d} " in line
        assert "ATTEMPT=1 STATE=ACK" in line
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match
        result.append(bytes.fromhex(match.group(1)))
    return result


def decode(payload: bytes, bits: int, endian: str, reverse: bool) -> list[int]:
    width = bits // 8
    result = [int.from_bytes(payload[j:j + width], endian)
              for j in range(0, 16, width)]
    if reverse:
        result.reverse()
    return result


def synthetic_controls() -> None:
    rng = Random(20261103)
    for bits in (32, 64):
        for _ in range(20):
            s = tuple(rng.getrandbits(bits) for _ in range(4))
            values = []
            for _ in range(16):
                values.append(xoshiro_output(s, bits))
                s = xoshiro_step(s, bits)
            recovered, rank = recover_xoshiro(values[:4], bits)
            assert rank == bits * 4
            for v in values[4:]:
                assert xoshiro_output(recovered, bits) == v
                recovered = xoshiro_step(recovered, bits)
        print(f"SYNTHETIC xoshiro{bits * 4}** 20/20 full-state rank={rank}")
    for _ in range(20):
        s = (rng.getrandbits(64), rng.getrandbits(64))
        values = []
        for _ in range(16):
            values.append(xoroshiro_output(s))
            s = xoroshiro_step(s)
        recovered, rank = recover_xoroshiro(values[:2])
        for v in values[2:]:
            assert xoroshiro_output(recovered) == v
            recovered = xoroshiro_step(recovered)
    print("SYNTHETIC xoroshiro128** 20/20 full-state rank=128")


def test_original() -> None:
    source = load_regular()
    for bits, model in ((32, "xoshiro128**"), (64, "xoroshiro128**"),
                        (64, "xoshiro256**")):
        for endian in ("big", "little"):
            for reverse in (False, True):
                rows = [decode(payload, bits, endian, reverse) for payload in source]
                fit_rows = 2 if model == "xoshiro256**" else 1
                best = 0
                matches = 0
                for i in range(len(rows) - fit_rows):
                    values = [v for row in rows[i:i + fit_rows] for v in row]
                    if model == "xoroshiro128**":
                        state, rank = recover_xoroshiro(values)
                        step = xoroshiro_step
                        out = xoroshiro_output
                    else:
                        state, rank = recover_xoshiro(values, bits)
                        step = lambda s: xoshiro_step(s, bits)
                        out = lambda s: xoshiro_output(s, bits)
                    count = 0
                    for actual in rows[i + fit_rows]:
                        count += int(out(state) == actual)
                        state = step(state)
                    best = max(best, count)
                    matches += int(count == len(rows[i + fit_rows]))
                print(f"ORIGINAL {model} {endian} reverse={reverse}"
                      f" rank={rank} full next-row={matches}/{len(rows) - fit_rows}"
                      f" maximum next-word matches={best}")


def test_intervening_draws() -> None:
    source = load_regular()
    rng = Random(20261103)
    for bits, model in ((32, "xoshiro128**"), (64, "xoroshiro128**")):
        n = 16 // (bits // 8)
        step = xoroshiro_step if bits == 64 else lambda s: xoshiro_step(s, bits)
        out = xoroshiro_output if bits == 64 else lambda s: xoshiro_output(s, bits)
        recover = recover_xoroshiro if bits == 64 else lambda vs: recover_xoshiro(vs, bits)
        for endian in ("big", "little"):
            for reverse in (False, True):
                after = [recover(decode(raw, bits, endian, reverse))[0] for raw in source]
                matches = []
                for i in range(len(after) - 1):
                    s = after[i]
                    for _ in range(n):
                        s = step(s)
                    for gap in range(4097):
                        if s == after[i + 1]:
                            matches.append((i, gap))
                            break
                        s = step(s)
                print(f"ORIGINAL {model} gap 0..4096 {endian}"
                      f" reverse={reverse}: {len(matches)}/127 matching adjacent states")
        for _ in range(5):
            s = tuple(rng.getrandbits(bits) for _ in range(2 if bits == 64 else 4))
            left = []
            for _ in range(n):
                left.append(out(s))
                s = step(s)
            gap = rng.randrange(1, 128)
            right_source = s
            for _ in range(gap):
                right_source = step(right_source)
            right = []
            for _ in range(n):
                right.append(out(right_source))
                right_source = step(right_source)
            left_after, _ = recover(left)
            right_after, _ = recover(right)
            assert left_after == s
            for _ in range(n + gap):
                left_after = step(left_after)
            assert left_after == right_after
        print(f"SYNTHETIC {model} gap positive controls=5/5")


if __name__ == "__main__":
    synthetic_controls()
    test_original()
    test_intervening_draws()
