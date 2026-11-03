"""Exact PCG64 XSL-RR 128/64 unknown-increment quotient; source-independent SFT.

Given two consecutive low64 states and the six-bit rotations for every
observed output, this reconstructs the *unique* 128-bit LCG increment and
pre-first-output state. It is a structural reduction, not a recovered printer
value or a solution to the remaining two-low/rotation search.
"""
import random

M64 = (1 << 64) - 1
M128 = (1 << 128) - 1
A = 0x2360ED051FC65DA44385DF649FCCF645
A64 = A & M64


def rol(x: int, n: int) -> int:
    return ((x << n) | (x >> ((64 - n) % 64))) & M64


def output(s: int) -> tuple[int, int]:
    h, l = s >> 64, s & M64
    r = h >> 58
    x = h ^ l
    return ((x >> r) | (x << ((64 - r) % 64))) & M64, r


def generate(seed: int, increment: int, count: int) -> list[int]:
    states = []
    for _ in range(count):
        seed = (A * seed + increment) & M128
        states.append(seed)
    return states


def recover(
    values: list[int], low0: int, low1: int, rotations: list[int]
) -> tuple[int, int, list[int]] | None:
    """Exact reconstruction from the two low64 parameters + output rotations."""
    if len(values) < 2 or len(values) != len(rotations):
        raise ValueError("Require matching observed outputs and >=2 rotations")
    lows = [low0, low1]
    for _ in range(2, len(values)):
        lows.append(((A64 + 1) * lows[-1] - A64 * lows[-2]) & M64)
    states = []
    for y, low, r in zip(values, lows, rotations):
        if r not in range(64):
            return None
        h = rol(y, r) ^ low
        if (h >> 58) != r:
            return None
        states.append((h << 64) | low)
    inc = (states[1] - A * states[0]) & M128
    if inc % 2 != 1:
        return None
    if any(((A * s + inc) & M128) != t for s, t in zip(states, states[1:])):
        return None
    initial = ((states[0] - inc) * pow(A, -1, 1 << 128)) & M128
    return initial, inc, states


def main() -> None:
    # Genuine independent NumPy PCG64(1234) control recorded by Agent13.
    initial = 0x160AD84006FE21EAF69B873D9FE45409
    inc = 0x50C8FB163C7CEA4ED0F51CE6006E4325
    raw = [0xFA08FEF3FAB6BBBA, 0x615481F7FCE9AC81,
           0xEC59DD7C2BDE3CB4, 0x42FE46521ADA3E8E]
    states = generate(initial, inc, len(raw))
    values, rotations = zip(*(output(s) for s in states))
    assert list(values) == raw
    rec = recover(list(values), states[0] & M64, states[1] & M64, list(rotations))
    assert rec is not None and rec[0:2] == (initial, inc)
    print("PASS genuine NumPy PCG64(1234) 4-word control")

    rng = random.Random(20261103)
    for _ in range(300):
        initial = rng.getrandbits(128)
        inc = rng.getrandbits(128) | 1
        states = generate(initial, inc, 6)
        values, rotations = zip(*(output(s) for s in states))
        rec = recover(list(values), states[0] & M64, states[1] & M64, list(rotations))
        assert rec is not None and rec[0:2] == (initial, inc)
        altered = list(values)
        altered[2] ^= 1
        assert recover(altered, states[0] & M64, states[1] & M64, list(rotations)) is None
    print("PASS 300 randomized 6-word inversions + 300 output-mutation controls")
    print("UNRESOLVED: infer the first two low64 states and output rotations without oracle")


if __name__ == "__main__":
    main()
