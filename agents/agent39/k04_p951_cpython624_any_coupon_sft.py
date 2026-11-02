"""Selected-withheld p951 printer source: construct CPython 624-word seeds for ANY selected coupon.

Read-only, original 132 intact printer packets only. Does not use commitment/acceptance,
mask, original selected row in model fitting, private files, or any facility resource.
Usage: python agents/agent39/k04_p951_cpython624_any_coupon_sft.py
"""
from __future__ import annotations

import hashlib
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = 0xFFFFFFFF
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]


def mix(x: int, multiplier: int) -> int:
    return ((x ^ (x >> 30)) * multiplier) & MASK


def initial_register() -> list[int]:
    result = [19650218]
    for i in range(1, 624):
        a = result[-1]
        result.append((1812433253 * (a ^ (a >> 30)) + i) & MASK)
    return result


INITIAL = initial_register()


def inverse_seed624(register: tuple[int, ...], first: int) -> tuple[int, ...]:
    """Surjective exact inverse of CPython integer init_by_array, key-length 624.

    Assumes a 624-word actual post-initialization register, first next MT index 624.
    The 624th first-pass seed term is independent and wraps to register index 1.
    """
    assert len(register) == 624 and register[0] == 0x80000000
    prev = [0] * 624
    prev[1] = ((register[1] + 1) & MASK) ^ mix(register[623], 1566083941)
    prev[2] = ((register[2] + 2) & MASK) ^ mix(prev[1], 1566083941)
    for i in range(3, 624):
        prev[i] = ((register[i] + i) & MASK) ^ mix(register[i - 1], 1566083941)
    key = [0] * 624
    key[0] = (first - (INITIAL[1] ^ mix(INITIAL[0], 1664525))) & MASK
    key[1] = (prev[2] - (INITIAL[2] ^ mix(first, 1664525)) - 1) & MASK
    for j in range(2, 623):
        i = j + 1
        key[j] = (prev[i] - (INITIAL[i] ^ mix(prev[i - 1], 1664525)) - j) & MASK
    key[623] = (prev[1] - (first ^ mix(prev[623], 1664525)) - 623) & MASK
    return tuple(key)


def integer_seed(words: tuple[int, ...]) -> int:
    return sum(word << (32 * j) for j, word in enumerate(words))


def untemper(word: int) -> int:
    for shift, left, mask in ((18, False, MASK), (15, True, 0xEFC60000),
                              (7, True, 0x9D2C5680), (11, False, MASK)):
        initial = word
        for _ in range(6):
            initial = word ^ (((initial << shift) & mask) if left else (initial >> shift))
        word = initial & MASK
    return word


def symbolic_mt() -> list[list[int]]:
    """Exact MT recurrence as 19968 GF(2) free initialized state variables."""
    state = [[1 << (32 * i + bit) for bit in range(32)] for i in range(624)]
    for i in range(624, 1601):
        p, n, q = state[i - 624], state[i - 623], state[i - 227]
        state.append([
            q[bit] ^ (p[31] if bit == 30 else n[bit + 1] if bit < 30 else 0)
            ^ (n[0] if (0x9908B0DF >> bit) & 1 else 0)
            for bit in range(32)
        ])
    return state


def reduce(row: int, basis: dict[int, int]) -> int:
    while row:
        pivot = row.bit_length() - 1
        old = basis.get(pivot)
        if old is None:
            break
        row ^= old
    return row


def impose(row: int, basis: dict[int, int]) -> None:
    row = reduce(row, basis)
    assert row != 1, "source or coupon contradiction"
    if row > 1:
        basis[row.bit_length() - 1] = row


def fixed_source_basis(state: list[list[int]], packets: list[bytes]) -> dict[int, int]:
    basis: dict[int, int] = {}
    for bit in range(32):
        impose((1 << (1 + bit)) | ((0x80000000 >> bit) & 1), basis)
    for i, index in enumerate(STARTS):
        if i == 129:
            continue
        for lane in range(4):
            word = untemper(int.from_bytes(packets[i][4*lane:4*lane+4], "little"))
            for bit, term in enumerate(state[624 + index + lane]):
                impose((term << 1) | ((word >> bit) & 1), basis)
    assert len(basis) == 15397
    return basis


def construct_history(source: dict[int, int], state: list[list[int]],
                      packets: list[bytes], coupon: bytes, rng: random.Random) -> str:
    assert len(coupon) == 16
    equations = source.copy()
    for lane in range(4):
        word = untemper(int.from_bytes(coupon[4*lane:4*lane+4], "little"))
        for bit, term in enumerate(state[624 + 951 + lane]):
            impose((term << 1) | ((word >> bit) & 1), equations)
    assert len(equations) == 15397 + 128, "all selected bits must be independent"

    pivots = {pivot - 1 for pivot in equations}
    free = [i for i in range(624*32) if i not in pivots]
    x = sum(1 << free[rng.randrange(len(free))] for _ in range(16))
    for pivot in sorted(equations):
        equation = equations[pivot]
        bit = (equation & 1) ^ ((x & (equation >> 1)).bit_count() & 1)
        if bit:
            x |= 1 << (pivot - 1)
    register = tuple((x >> (32*i)) & MASK for i in range(624))
    assert register[0] == 0x80000000
    for _ in range(8):
        words = inverse_seed624(register, rng.getrandbits(32))
        if words[623]:
            break
    assert words[623], "require a genuine 624-word nonzero-top integer seed"
    seed = integer_seed(words)
    generator = random.Random(seed)
    assert generator.getstate()[1][:624] == register
    draws = [generator.getrandbits(32) for _ in range(967)]
    for i, index in enumerate(STARTS):
        if i == 129:
            continue
        actual = b"".join(draws[index+j].to_bytes(4, "little") for j in range(4))
        assert actual == packets[i], (i, "original source mismatch")
    prediction = b"".join(draws[951+j].to_bytes(4, "little") for j in range(4))
    assert prediction == coupon
    return hashlib.sha256(seed.to_bytes(2496, "little")).hexdigest()


def test_inverse() -> None:
    rng = random.Random(0x6241337)
    for i in range(12):
        register = (random.Random(integer_seed(tuple(rng.getrandbits(32) | 1 for _ in range(624)))).getstate()[1][:624]
                    if i & 1 else (0x80000000, *(rng.getrandbits(32) for _ in range(623))))
        first = rng.getrandbits(32)
        words = inverse_seed624(tuple(register), first)
        candidate = random.Random(integer_seed(words)).getstate()[1][:624]
        assert candidate == tuple(register), (i, "inverse mismatch")
    print("CPython 624-word nonlinear initializer exact inverse: 12/12 genuine seeded and random-register controls PASS")


def main() -> None:
    test_inverse()
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    fields = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(fields) == len(STARTS) == 133 and STARTS[129] == 951
    # The original selected row is allowed only as a wholly separate hypothetical target.
    packets = [bytes.fromhex(f.decode("ascii")) if i != 129 else b""
               for i, f in enumerate(fields)]
    state = symbolic_mt()
    source = fixed_source_basis(state, packets)
    rng = random.Random(0x624BEEF)
    coupons = (
        ("observed ACK2 as hypothetical coupon", bytes.fromhex(fields[129].decode("ascii"))),
        ("zero coupon", bytes(16)),
        ("full-FF coupon", bytes([255])*16),
        ("source-SHA prefix coupon", hashlib.sha256(raw).digest()[:16]),
    )
    for label, coupon in coupons:
        witness = construct_history(source, state, packets, coupon, rng)
        print(label, coupon.hex().upper(), "PASS, witness seed SHA256", witness)
    print("All four distinct complete coupon hypotheses are produced by REAL CPython 624-word seeds")
    print("Exact GF(2) selected rank 128 and initializer surjectivity imply ANY 128-bit coupon feasible")
    print("Historical p951 producer unproven; zero recovered original K04 bits, K08 words or new REC8 PASS")


if __name__ == "__main__":
    main()
