"""Exact PCG-XSH-RR 64/32 existence test with arbitrary 64-bit increment.

Read-only original spool test: four separated routine ACKs, 4 byte layouts.
Enumerates 32**4 output rotations per packet; no K04 commitment or selected
coupon is used. Exact lattice nearest-coordinate bound proves completeness.
Only the Python standard library is required.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from random import Random

A = 6364136223846793005
M = 1 << 64
L = 1 << 27
MASK = M - 1
SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

# Reduced lattice row basis for the (d1,d2,d3) low-state difference
# equations. R inverse is N / 2**64. Validate these exact identities below.
R = [
    [-781967691603, 4059941835286, 383048353931],
    [-28986796055, 344362115806, 9578098891503],
    [8119758543249, 3449264998158, 1264207595783],
]
N = [
    [-1767361, -206615, 2100892],
    [4218007, -222198, 405419],
    [-156999, 1933293, -8218],
]


def rotate_left(x: int, r: int) -> int:
    return ((x << r) | (x >> (32 - r))) & 0xFFFFFFFF if r else x


def rotate_right(x: int, r: int) -> int:
    return ((x >> r) | (x << (32 - r))) & 0xFFFFFFFF if r else x


def pcg_output(state: int) -> int:
    return rotate_right((((state >> 18) ^ state) >> 27) & 0xFFFFFFFF,
                        state >> 59)


def high37(y: int, rotation: int) -> int:
    """Each rotation guess determines all high 37 state bits uniquely."""
    x = rotate_left(y, rotation)
    state = rotation << 59
    for bit in range(31, -1, -1):
        value = ((x >> bit) & 1) ^ (
            ((state >> (bit + 45)) & 1) if bit <= 18 else 0)
        state |= value << (bit + 27)
    assert pcg_output(state) == y
    return state >> 27


def nearest_integer_div_m(n: int) -> int:
    return (n + M // 2) // M if n >= 0 else -((-n + M // 2) // M)


def low_differences(highs: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    h0, h1, h2, h3 = highs
    c0 = (-(A * h0 - (A + 1) * h1 + h2) * L) & MASK
    c1 = (-(A * h1 - (A + 1) * h2 + h3) * L) & MASK
    p1 = c0
    p2 = ((A + 1) * c0 + c1) & MASK
    coeff = [
        nearest_integer_div_m(-p1 * N[1][j] - p2 * N[2][j])
        for j in range(3)
    ]
    return (
        0,
        sum(coeff[j] * R[j][0] for j in range(3)),
        p1 + sum(coeff[j] * R[j][1] for j in range(3)),
        p2 + sum(coeff[j] * R[j][2] for j in range(3)),
    )


def prove_lattice_exactness() -> None:
    # R * N = 2**64 * identity. The center-to-true coefficient
    # discrepancy for |d_i| < L is rigorously below 1/2 in all directions,
    # so rounding is exhaustive, requiring no arbitrary Babai neighborhood.
    for i in range(3):
        for j in range(3):
            assert sum(R[i][k] * N[k][j] for k in range(3)) == (
                M if i == j else 0)
    assert max(L * sum(abs(N[k][j]) for k in range(3))
               for j in range(3)) * 2 < M
    # Homogeneous rows must satisfy both modular second-difference rules.
    for b in R:
        d1, d2, d3 = b
        assert (d2 - (A + 1) * d1) % M == 0
        assert (A * d1 - (A + 1) * d2 + d3) % M == 0


def recover_four(values: list[int]) -> tuple[int, list[tuple[int, ...]]]:
    """Enumerate 32**4 rotations, solve unique low-difference lattice cell."""
    assert len(values) == 4
    guesses = [[high37(y, rotation) for rotation in range(32)]
               for y in values]
    count = 0
    first_hits = []
    for r0 in range(32):
        h0 = guesses[0][r0]
        for r1 in range(32):
            h1 = guesses[1][r1]
            for r2 in range(32):
                h2 = guesses[2][r2]
                for r3 in range(32):
                    h3 = guesses[3][r3]
                    d = low_differences((h0, h1, h2, h3))
                    if max(d) - min(d) >= L:
                        continue
                    low_start = max(0, -min(d))
                    low_end = min(L - 1, L - 1 - max(d))
                    if low_start > low_end:
                        continue
                    states = (
                        h0 * L + low_start,
                        h1 * L + low_start + d[1],
                        h2 * L + low_start + d[2],
                        h3 * L + low_start + d[3],
                    )
                    increment = (states[1] - A * states[0]) & MASK
                    assert all(((A * a + increment) & MASK) == b
                               for a, b in zip(states, states[1:]))
                    assert [pcg_output(s) for s in states] == values
                    count += 1
                    if len(first_hits) < 5:
                        first_hits.append((r0, r1, r2, r3,
                                           low_start, low_end, increment))
    return count, first_hits


def controls() -> None:
    rng = Random(20261103)
    for j in range(3):
        state = rng.getrandbits(64)
        increment = rng.getrandbits(64) | 1
        states = [state]
        for _ in range(3):
            states.append((A * states[-1] + increment) & MASK)
        observed = [pcg_output(s) for s in states]
        found, witnesses = recover_four(observed)
        assert found and witnesses
        print(f"SYNTHETIC planted full-state case {j + 1}/3:"
              f" PASS, complete rotation witnesses={found}")


def original_source() -> None:
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256
    lines = [s for s in raw.decode("ascii").splitlines() if "PAYLOAD=" in s]
    assert len(lines) == 133
    for index in (0, 43, 84, 127):
        line = lines[index]
        assert f"JOB=PS-261003-{300 + index:04d} " in line
        assert "ATTEMPT=1 STATE=ACK" in line
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match
        payload = bytes.fromhex(match.group(1))
        for endian in ("little", "big"):
            for reverse in (False, True):
                values = [int.from_bytes(payload[j:j + 4], endian)
                          for j in range(0, 16, 4)]
                if reverse:
                    values.reverse()
                found, _ = recover_four(values)
                assert found == 0, (index, endian, reverse, found)
                print(f"ORIGINAL row={index} endian={endian}"
                      f" reverse={reverse}: 0 complete PCG32 models")


if __name__ == "__main__":
    prove_lattice_exactness()
    controls()
    original_source()
