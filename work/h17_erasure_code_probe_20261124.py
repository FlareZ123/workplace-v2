#!/usr/bin/env python3
"""Bounded six-of-eight erasure-code probe for H-17.

Reads candidate.json and resources/acceptance.json from the repository root.
It prints only trial counts and commitment-match booleans; it never prints
candidate component bytes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
candidate = json.loads((ROOT / "candidate.json").read_text())
acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
known_ids = ("K01", "K02", "K03", "K05", "K06", "K07")
known = {k: bytes.fromhex(candidate[k]) for k in known_ids}
targets = acceptance["slot_sha256"]
assert all(len(v) == 16 for v in known.values())


def matches(slot: str, value: bytes) -> bool:
    return hashlib.sha256(value).hexdigest() == targets[slot]


def poly_mod(a: int, p: int) -> int:
    degree = p.bit_length() - 1
    while a and a.bit_length() - 1 >= degree:
        a ^= p << ((a.bit_length() - 1) - degree)
    return a


def poly_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, poly_mod(a, b)
    return a


def poly_square_mod(a: int, p: int) -> int:
    squared = 0
    bit = 0
    while a:
        if a & 1:
            squared |= 1 << (2 * bit)
        a >>= 1
        bit += 1
    return poly_mod(squared, p)


def irreducible_polynomials(m: int) -> list[int]:
    """Enumerate all monic irreducible binary polynomials of degree m."""
    result = []
    x = 2
    for low in range(1, 1 << m, 2):
        p = (1 << m) | low
        z = x
        for _ in range(m // 2):
            z = poly_square_mod(z, p)
        if poly_gcd(z ^ x, p) != 1:
            continue
        for _ in range(m - m // 2):
            z = poly_square_mod(z, p)
        if z == poly_mod(x, p):
            result.append(p)
    return result


def gf_mul(a: int, b: int, p: int, m: int) -> int:
    mask = (1 << m) - 1
    reduction = p & mask
    out = 0
    for _ in range(m):
        if b & 1:
            out ^= a
        b >>= 1
        carry = a & (1 << (m - 1))
        a = (a << 1) & mask
        if carry:
            a ^= reduction
    return out


def gf_pow(a: int, exponent: int, p: int, m: int) -> int:
    out = 1
    while exponent:
        if exponent & 1:
            out = gf_mul(out, a, p, m)
        a = gf_mul(a, a, p, m)
        exponent >>= 1
    return out


def gf_inv(a: int, p: int, m: int) -> int:
    if not a:
        raise ZeroDivisionError
    return gf_pow(a, (1 << m) - 2, p, m)


def lagrange_weights(xs: list[int], target_x: int, p: int, m: int) -> list[int]:
    weights = []
    for i, xi in enumerate(xs):
        numerator = denominator = 1
        for j, xj in enumerate(xs):
            if i == j:
                continue
            numerator = gf_mul(numerator, target_x ^ xj, p, m)
            denominator = gf_mul(denominator, xi ^ xj, p, m)
        weights.append(gf_mul(numerator, gf_inv(denominator, p, m), p, m))
    return weights


def interpolate_symbols(
    symbols: dict[str, list[int]], xs: list[int], target_x: int, p: int, m: int
) -> list[int]:
    weights = lagrange_weights(xs, target_x, p, m)
    width = len(next(iter(symbols.values())))
    output = []
    for j in range(width):
        value = 0
        for key, weight in zip(known_ids, weights):
            value ^= gf_mul(symbols[key][j], weight, p, m)
        output.append(value)
    return output


def test_gf256_rs() -> tuple[int, int]:
    trials = 0
    hits = 0
    fields = irreducible_polynomials(8)
    assert len(fields) == 30
    byte_symbols = {k: list(known[k]) for k in known_ids}
    for p in fields:
        # Consecutive integer abscissas, both zero- and one-based.
        for offset in (0, 1):
            xs = [int(k[1:]) - 1 + offset for k in known_ids]
            for slot, tx in (("K04", 3 + offset), ("K08", 7 + offset)):
                out = bytes(interpolate_symbols(byte_symbols, xs, tx, p, 8))
                trials += 1
                hits += int(matches(slot, out))
        # Standard RS-style primitive-power abscissas, every primitive element.
        for alpha in range(2, 256):
            if gf_pow(alpha, 255, p, 8) != 1:
                continue
            if any(gf_pow(alpha, 255 // q, p, 8) == 1 for q in (3, 5, 17)):
                continue
            for offset in (0, 1):
                xs = [
                    gf_pow(alpha, int(k[1:]) - 1 + offset, p, 8)
                    for k in known_ids
                ]
                for slot, tx in (("K04", 3 + offset), ("K08", 7 + offset)):
                    target_x = gf_pow(alpha, tx, p, 8)
                    out = bytes(interpolate_symbols(byte_symbols, xs, target_x, p, 8))
                    trials += 1
                    hits += int(matches(slot, out))
    return len(fields), trials, hits


def test_gf65536_rs() -> tuple[int, int]:
    fields = irreducible_polynomials(16)
    assert len(fields) == 4080
    trials = hits = 0
    for p in fields:
        for endian in ("big", "little"):
            symbols = {
                k: [
                    int.from_bytes(known[k][i : i + 2], endian)
                    for i in range(0, 16, 2)
                ]
                for k in known_ids
            }
            for offset in (0, 1):
                xs = [int(k[1:]) - 1 + offset for k in known_ids]
                for slot, tx in (("K04", 3 + offset), ("K08", 7 + offset)):
                    out_symbols = interpolate_symbols(symbols, xs, tx, p, 16)
                    out = b"".join(v.to_bytes(2, endian) for v in out_symbols)
                    trials += 1
                    hits += int(matches(slot, out))
    return len(fields), trials, hits


def gf128_mul(a: int, b: int) -> int:
    """GF(2^128), modulus x^128+x^7+x^2+x+1."""
    mask = (1 << 128) - 1
    out = 0
    value = a
    for bit in range(128):
        if (b >> bit) & 1:
            out ^= value
        value = (((value << 1) & mask) ^ 0x87) if value & (1 << 127) else ((value << 1) & mask)
    return out


def gf128_pow(a: int, exponent: int) -> int:
    out = 1
    while exponent:
        if exponent & 1:
            out = gf128_mul(out, a)
        a = gf128_mul(a, a)
        exponent >>= 1
    return out


def gf128_inv(a: int) -> int:
    if not a:
        raise ZeroDivisionError
    return gf128_pow(a, (1 << 128) - 2)


def test_gf128_rs() -> tuple[int, int]:
    trials = hits = 0
    for endian in ("big", "little"):
        raw = {k: int.from_bytes(known[k], endian) for k in known_ids}
        for bit_reversed in (False, True):
            values = {
                k: int(f"{raw[k]:0128b}"[::-1], 2) if bit_reversed else raw[k]
                for k in known_ids
            }
            for offset in (0, 1):
                xs = [int(k[1:]) - 1 + offset for k in known_ids]
                for slot, tx in (("K04", 3 + offset), ("K08", 7 + offset)):
                    output = 0
                    for i, xi in enumerate(xs):
                        numerator = denominator = 1
                        for j, xj in enumerate(xs):
                            if i == j:
                                continue
                            numerator = gf128_mul(numerator, tx ^ xj)
                            denominator = gf128_mul(denominator, xi ^ xj)
                        weight = gf128_mul(numerator, gf128_inv(denominator))
                        output ^= gf128_mul(values[known_ids[i]], weight)
                    if bit_reversed:
                        output = int(f"{output:0128b}"[::-1], 2)
                    out = output.to_bytes(16, endian)
                    trials += 1
                    hits += int(matches(slot, out))
    return trials, hits


def test_raid6_and_cauchy() -> tuple[int, int]:
    trials = hits = 0
    data_keys = ("K01", "K02", "K03", "K05", "K06", "K07")
    # P parity (XOR) as either missing parity slot.
    p = bytearray(16)
    for key in data_keys:
        for j, value in enumerate(known[key]):
            p[j] ^= value
    for slot in ("K04", "K08"):
        trials += 1
        hits += int(matches(slot, bytes(p)))

    fields = irreducible_polynomials(8)
    for poly in fields:
        for alpha in range(2, 256):
            if gf_pow(alpha, 255, poly, 8) != 1:
                continue
            if any(gf_pow(alpha, 255 // q, poly, 8) == 1 for q in (3, 5, 17)):
                continue
            for offset in (0, 1):
                coefficients = [gf_pow(alpha, i + offset, poly, 8) for i in range(6)]
                q = bytearray(16)
                for key, coefficient in zip(data_keys, coefficients):
                    for j, value in enumerate(known[key]):
                        q[j] ^= gf_mul(value, coefficient, poly, 8)
                for slot in ("K04", "K08"):
                    trials += 1
                    hits += int(matches(slot, bytes(q)))

        # Cauchy 6+2 parity, common consecutive x/y choices.
        for base in (0, 1):
            xs = [base + i for i in range(6)]
            ys = (base + 6, base + 7)
            parities = []
            for y in ys:
                q = bytearray(16)
                for key, x in zip(data_keys, xs):
                    coefficient = gf_inv(x ^ y, poly, 8)
                    for j, value in enumerate(known[key]):
                        q[j] ^= gf_mul(value, coefficient, poly, 8)
                parities.append(bytes(q))
            for slot, value in (("K04", parities[0]), ("K08", parities[1]),
                                ("K04", parities[1]), ("K08", parities[0])):
                trials += 1
                hits += int(matches(slot, value))
    return trials, hits


def main() -> None:
    gf256_fields, gf256_trials, gf256_hits = test_gf256_rs()
    gf16_fields, gf16_trials, gf16_hits = test_gf65536_rs()
    gf128_trials, gf128_hits = test_gf128_rs()
    raid_trials, raid_hits = test_raid6_and_cauchy()
    print(json.dumps({
        "gf256_irreducible_fields": gf256_fields,
        "gf256_trials": gf256_trials,
        "gf256_commitment_matches": gf256_hits,
        "gf65536_irreducible_fields": gf16_fields,
        "gf65536_trials": gf16_trials,
        "gf65536_commitment_matches": gf16_hits,
        "gf128_trials": gf128_trials,
        "gf128_commitment_matches": gf128_hits,
        "raid6_cauchy_trials": raid_trials,
        "raid6_cauchy_commitment_matches": raid_hits,
    }, indent=2))


if __name__ == "__main__":
    main()
