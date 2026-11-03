"""REC8: reconstruct both missing components as a two-erasure Reed-Solomon code.

Treat six verified 16-byte components K01,K02,K03,K05,K06,K07 as
known points of one degree <=5 polynomial over a binary finite field,
independently per field-symbol lane. Predict K04 and K08, check their
unchanged SHA256 commitments and the two-erasure planted controls.

This is an exploratory alternative to missing coupon and caption witnesses,
not a claim that the original REC8 envelope used error-correcting codes.
Run: python agents/agent48/rec8_crossslot_rs_erasure_sft.py
"""
import hashlib
import itertools
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
ACCEPT = json.loads((ROOT / "acceptance.json").read_text())
KNOWN = {
    1: "049AAB2E1CDE7A82CD7C60234303C91A",
    2: "0D7E3AB56FB75DA3EB0E2E06786D239E",
    3: "1384AF96E25D6ADA666209CB55E062FA",
    5: "FF8B78200A56E8586DCDA00EF01E4572",
    6: "5DBF40EE52FAAED9A536D3326CF0D95A",
    7: "93495F5E425AB8E592123DABAEB68545",
}
FIELDS = (
    (8, 0x1b), (8, 0x1d),
    (16, 0x100b), (16, 0x2b),
    (32, 0x8d), (32, 0x04c11db7),
    (64, 0x1b), (64, 0x1d),
    (128, 0x87),
)


def field(n, low):
    mask = (1 << n) - 1

    def mul(a, b):
        result = 0
        for _ in range(n):
            if b & 1:
                result ^= a
            b >>= 1
            a <<= 1
            if a >> n:
                a = (a & mask) ^ low
        return result

    def power(a, exponent):
        result = 1
        while exponent:
            if exponent & 1:
                result = mul(result, a)
            a = mul(a, a)
            exponent >>= 1
        return result

    def inverse(a):
        assert a
        return power(a, (1 << n) - 2)

    return mul, power, inverse


def coordinates(n, low, kind, reversed_slots):
    mul, power, inverse = field(n, low)

    def position(slot):
        index = 9 - slot if reversed_slots else slot
        if kind == "one_based":
            return index
        if kind == "zero_based":
            return index - 1
        return power(2, index - 1)

    result = {i: position(i) for i in range(1, 9)}
    assert len(set(result.values())) == 8
    return result


def weights(coords, missing, mul, inverse, locations):
    result = {}
    for i in locations:
        coefficient = 1
        for j in locations:
            if i != j:
                coefficient = mul(
                    coefficient,
                    mul(coords[missing] ^ coords[j],
                        inverse(coords[i] ^ coords[j])),
                )
        result[i] = coefficient
    return result


def view(raw, n, endian, reverse_symbols, reflect_bits):
    if reflect_bits:
        raw = bytes(int(f"{b:08b}"[::-1], 2) for b in raw)
    size = n // 8
    chunks = [raw[i:i+size] for i in range(0, 16, size)]
    if reverse_symbols:
        chunks.reverse()
    return [int.from_bytes(chunk, endian) for chunk in chunks]


def unview(symbols, n, endian, reverse_symbols, reflect_bits):
    size = n // 8
    chunks = [x.to_bytes(size, endian) for x in symbols]
    if reverse_symbols:
        chunks.reverse()
    raw = b"".join(chunks)
    if reflect_bits:
        raw = bytes(int(f"{b:08b}"[::-1], 2) for b in raw)
    return raw


def interpolate(source, coefficient, mul, count):
    result = [0] * count
    for slot, original in source.items():
        for j in range(count):
            result[j] ^= mul(original[j], coefficient[slot])
    return result


def synthetic_positive(n, low):
    mul, power, inverse = field(n, low)
    rng = random.Random(20261103 + n + low)
    coords = coordinates(n, low, "powers", True)
    count = 128 // n
    coefficients = [[rng.getrandbits(n) for _ in range(6)]
                    for _ in range(count)]
    full = {}
    for slot in range(1, 9):
        x = coords[slot]
        bases = [power(x, k) for k in range(6)]
        full[slot] = []
        for lane in range(count):
            answer = 0
            for v, basis in zip(coefficients[lane], bases):
                answer ^= mul(v, basis)
            full[slot].append(answer)
    known = {i: full[i] for i in KNOWN}
    for slot in (4, 8):
        w = weights(coords, slot, mul, inverse, known)
        predicted = interpolate(known, w, mul, count)
        assert predicted == full[slot]
    return True


def main():
    values = {i: bytes.fromhex(v) for i, v in KNOWN.items()}
    assert all(
        hashlib.sha256(value).hexdigest() == ACCEPT["slot_sha256"][f"K{i:02d}"]
        for i, value in values.items()
    )
    attempts = 0
    complete_pairs = {}
    individual_hits = {4: [], 8: []}
    planted = 0
    for n, low in FIELDS:
        mul, power, inverse = field(n, low)
        assert synthetic_positive(n, low)
        planted += 1
        for kind in ("one_based", "zero_based", "powers"):
            for reverse_slots in (False, True):
                coords = coordinates(n, low, kind, reverse_slots)
                coefficient = {
                    missing: weights(coords, missing, mul, inverse, KNOWN)
                    for missing in (4, 8)
                }
                endians = ("big", "little") if n != 8 else ("big",)
                for endian, symbol_order, bit_order in itertools.product(
                    endians, (False, True), (False, True)
                ):
                    attempts += 1
                    source = {
                        i: view(raw, n, endian, symbol_order, bit_order)
                        for i, raw in values.items()
                    }
                    predicted = {}
                    for missing in (4, 8):
                        symbols = interpolate(source, coefficient[missing],
                                              mul, 128 // n)
                        raw = unview(symbols, n, endian,
                                     symbol_order, bit_order)
                        assert len(raw) == 16
                        predicted[missing] = raw
                        if hashlib.sha256(raw).hexdigest() == (
                            ACCEPT["slot_sha256"][f"K{missing:02d}"]
                        ):
                            individual_hits[missing].append(
                                (n, hex(low), kind, reverse_slots,
                                 endian, symbol_order, bit_order)
                            )
                    pair = (predicted[4].hex().upper(),
                            predicted[8].hex().upper())
                    complete_pairs[pair] = True
    assert attempts == 384
    assert len(complete_pairs) == 158
    assert not individual_hits[4] and not individual_hits[8]
    assert planted == 9
    first = next(iter(complete_pairs))
    assert first == (
        "014C6CE879B6733912369A65DAE4C6AE",
        "656BEBFD2A3DCD888139FA3BFE062220",
    )
    print(json.dumps({
        "known_original_slots_SHA256": "6/6 PASS",
        "finite_field_models": len(FIELDS),
        "slot_coordinate_and_serialization_models": attempts,
        "distinct_complete_K04_K08_pairs": len(complete_pairs),
        "original_K04_commitment_hits": len(individual_hits[4]),
        "original_K08_commitment_hits": len(individual_hits[8]),
        "two-erasure_synthetic_positive": planted,
        "example_predicted_K04_K08": first,
        "result": "NO_MATCH_SOURCE_HYPOTHESIS_ONLY",
    }, indent=2))


if __name__ == "__main__":
    main()
