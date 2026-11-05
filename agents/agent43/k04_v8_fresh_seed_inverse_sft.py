"""Source gate for freshly seeded V8 Math.random() byte coupons.

Hypothesis: each 16-byte coupon was filled by Math.floor(256 * Math.random())
with a newly initialized modern 64-bit V8 context; in that implementation
state0=MurmurHash3(seed), state1=MurmurHash3(~seed) and outputs use top 8 bits
of successive xorshift state0. Selected printer row129 is excluded.
Uses Python 3 standard library only.
"""
from pathlib import Path
import hashlib
import re

MASK = (1 << 64) - 1
M1 = 0xFF51AFD7ED558CCD
M2 = 0xC4CEB9FE1A85EC53
I1 = pow(M1, -1, 1 << 64)
I2 = pow(M2, -1, 1 << 64)
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources/evidence/print/spool-reconstruction.log"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def murmur(x):
    x &= MASK
    x ^= x >> 33
    x = x * M1 & MASK
    x ^= x >> 33
    x = x * M2 & MASK
    return x ^ (x >> 33)


def inverse_murmur(x):
    x ^= x >> 33
    x = x * I2 & MASK
    x ^= x >> 33
    x = x * I1 & MASK
    return x ^ (x >> 33)


def step(a, b):
    x = a
    a = b
    x ^= (x << 23) & MASK
    x ^= x >> 17
    x ^= a
    x ^= a >> 26
    return a, x & MASK


def emit(state, count=16):
    a, b = state
    output = []
    for _ in range(count):
        a, b = step(a, b)
        output.append(a >> 56)
    return bytes(output), (a, b)


def inverse_state(observed):
    """Solve 128 binary output equations for 128 pre-output state bits."""
    if len(observed) != 16:
        raise ValueError("Exactly 16 output bytes required")
    eq = [0] * 128
    for bit in range(128):
        start = (1 << bit, 0) if bit < 64 else (0, 1 << (bit - 64))
        data, _ = emit(start)
        for row, byte in enumerate(data):
            for digit in range(8):
                if byte >> digit & 1:
                    eq[row * 8 + digit] |= 1 << bit
    for row, byte in enumerate(observed):
        for digit in range(8):
            eq[row * 8 + digit] |= ((byte >> digit) & 1) << 128

    pivots = []
    rank = 0
    for column in range(128):
        pivot = next((r for r in range(rank, 128) if eq[r] >> column & 1), None)
        if pivot is None:
            continue
        eq[rank], eq[pivot] = eq[pivot], eq[rank]
        for row in range(128):
            if row != rank and eq[row] >> column & 1:
                eq[row] ^= eq[rank]
        pivots.append(column)
        rank += 1

    if any((r & MASK128) == 0 and (r >> 128) & 1 for r in eq):
        return rank, []
    free = [column for column in range(128) if column not in pivots]
    if len(free) > 10:
        raise ValueError(f"Unexpected nullity: {len(free)}")
    states = []
    for combo in range(1 << len(free)):
        word = sum(((combo >> i) & 1) << col for i, col in enumerate(free))
        for row, col in reversed(list(enumerate(pivots))):
            rhs = (eq[row] >> 128) & 1
            rhs ^= (eq[row] & word).bit_count() & 1
            word |= rhs << col
        states.append((word & MASK, word >> 64))
    return rank, states


MASK128 = (1 << 128) - 1


def recover_fresh_seeds(data):
    rank, states = inverse_state(data)
    seeds = []
    for a, b in states:
        seed = inverse_murmur(a)
        if b == murmur(~seed & MASK):
            seeds.append(seed)
    return rank, len(states), seeds


def main():
    for seed in (0, 1, 20261003, MASK, 0x123456789ABCDEF0):
        assert inverse_murmur(murmur(seed)) == seed
        data, _ = emit((murmur(seed), murmur(~seed & MASK)))
        rank, size, recovered = recover_fresh_seeds(data)
        assert rank == 126 and size == 4 and recovered == [seed]
        print(f"synthetic fresh V8 seed={seed:016X}: PASS")

    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = [bytes.fromhex(m.group(1)) for line in raw.decode().splitlines()
            if (m := re.search(r"PAYLOAD=([0-9A-F]{32})", line))]
    assert len(rows) == 133
    compatible = 0
    found = []
    for i in list(range(128)) + [128, 130, 131, 132]:
        rank, size, seeds = recover_fresh_seeds(rows[i])
        assert rank == 126
        compatible += bool(size)
        found.extend((i, seed) for seed in seeds)
    print(f"original 132 intact coupons: {compatible} satisfy the 126-rank "
          f"local byte constraints; fresh 64-bit V8 seeded matches={found}")
    assert compatible == 40 and found == []
    print("NO_MATCH: newly seeded 64-bit V8 generator at the start of each "
          "coupon. No inference on unknown stream phase or selected row129.")


if __name__ == "__main__":
    main()
