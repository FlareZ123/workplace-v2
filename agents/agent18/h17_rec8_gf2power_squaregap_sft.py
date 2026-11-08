"""H-17 K04/K08: independent GF(2^w) second-order erasure test.

Infer lane coefficients using source slots K01,K02,K03,K05 only.
Hold K06,K07 completely out of inference, then predict both missing slots.
"""
import hashlib
import itertools
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
TARGET = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]
KNOWN = {
    1: "049AAB2E1CDE7A82CD7C60234303C91A",
    2: "0D7E3AB56FB75DA3EB0E2E06786D239E",
    3: "1384AF96E25D6ADA666209CB55E062FA",
    5: "FF8B78200A56E8586DCDA00EF01E4572",
    6: "5DBF40EE52FAAED9A536D3326CF0D95A",
    7: "93495F5E425AB8E592123DABAEB68545",
}
FIELDS = (
    (8, 0x11B), (8, 0x11D), (16, 0x1100B),
    (32, 0x10000008D), (32, 0x104C11DB7), (32, 0x1000000AF),
    (64, 0x1000000000000001B), (64, 0x1000000000000001D),
    (128, 0x100000000000000000000000000000087),
)


def mul(x, y, width, field):
    result = 0
    while y:
        if y & 1:
            result ^= x
        y >>= 1
        x <<= 1
        if x >> width:
            x ^= field
    return result


def power(x, exponent, width, field):
    result = 1
    while exponent:
        if exponent & 1:
            result = mul(result, x, width, field)
        exponent >>= 1
        x = mul(x, x, width, field)
    return result


def fit(x1, x2, x3, x5, width, field):
    """For x[n]=a*x[n-1]+b*x[n-2], recover a,b over GF(2^w).

    a^2=(x1*x5+x3^2)/(x1*x3+x2^2), b=(x3+a*x2)/x1;
    additions are XOR, and square root is exponent 2**(width-1).
    """
    numerator = mul(x1, x5, width, field) ^ mul(x3, x3, width, field)
    denominator = mul(x1, x3, width, field) ^ mul(x2, x2, width, field)
    if x1 == 0 or denominator == 0:
        return None
    a2 = mul(numerator, power(denominator, (1 << width)-2, width, field), width, field)
    a = power(a2, 1 << (width-1), width, field)
    b = mul(x3 ^ mul(a, x2, width, field),
            power(x1, (1 << width)-2, width, field), width, field)
    return a, b


def step(x, y, coefficients, width, field):
    a, b = coefficients
    return mul(a, y, width, field) ^ mul(b, x, width, field)


def generate(x1, x2, coefficients, width, field):
    result = {1: tuple(x1), 2: tuple(x2)}
    for index in range(3, 9):
        result[index] = tuple(
            step(result[index-2][lane], result[index-1][lane],
                 coefficients[lane], width, field)
            for lane in range(len(coefficients))
        )
    return result


def split(hexvalue, width, endian, reverse):
    data = bytes.fromhex(hexvalue)
    if reverse:
        data = data[::-1]
    size = width // 8
    return tuple(int.from_bytes(data[i:i+size], endian)
                 for i in range(0, 16, size))


def join(words, width, endian, reverse):
    data = b"".join(word.to_bytes(width // 8, endian) for word in words)
    return data[::-1] if reverse else data


def controls():
    rng = random.Random(20261108)
    total = 0
    for width, field in FIELDS:
        lanes = 128 // width
        for shared in (False, True):
            for _ in range(8):
                while True:
                    coefficients = tuple(
                        (rng.getrandbits(width), rng.getrandbits(width))
                        for _ in range(1 if shared else lanes)
                    )
                    if shared:
                        coefficients = coefficients * lanes
                    x1 = tuple(rng.getrandbits(width) for _ in range(lanes))
                    x2 = tuple(rng.getrandbits(width) for _ in range(lanes))
                    truth = generate(x1, x2, coefficients, width, field)
                    recovered = tuple(
                        fit(truth[1][lane], truth[2][lane], truth[3][lane],
                            truth[5][lane], width, field)
                        for lane in range(lanes)
                    )
                    if all(recovered):
                        break
                assert recovered == coefficients
                assert generate(x1, x2, recovered, width, field) == truth
                total += 1
    return total


def main():
    assert controls() == 144
    assert all(hashlib.sha256(bytes.fromhex(value)).hexdigest() == TARGET[f"K{i:02d}"]
               for i, value in KNOWN.items())
    source_models = shared_models = holdouts = original_k04 = original_k08 = 0
    for (width, field), endian, reverse, shared in itertools.product(
            FIELDS, ("big", "little"), (False, True), (False, True)):
        lanes = 128 // width
        if shared and lanes == 1:
            continue
        source = {i: split(value, width, endian, reverse)
                  for i, value in KNOWN.items()}
        coefficients = tuple(
            fit(source[1][lane], source[2][lane],
                source[3][lane], source[5][lane], width, field)
            for lane in range(lanes)
        )
        if any(pair is None for pair in coefficients):
            continue
        if shared and len(set(coefficients)) != 1:
            continue
        source_models += 1
        shared_models += int(shared)
        output = generate(source[1], source[2], coefficients, width, field)
        assert output[3] == source[3] and output[5] == source[5]
        full_holdout = output[6] == source[6] and output[7] == source[7]
        holdouts += int(full_holdout)
        k04 = join(output[4], width, endian, reverse)
        k08 = join(output[8], width, endian, reverse)
        original_k04 += int(hashlib.sha256(k04).hexdigest() == TARGET["K04"])
        original_k08 += int(hashlib.sha256(k08).hexdigest() == TARGET["K08"])
        print("MODEL", width, hex(field), endian, reverse, "shared", shared,
              "K06_K07_historical_holdout", full_holdout)
    print("SIX_SOURCE_HASHES_PASS=6 SYNTHETIC_8SLOT_CONTROLS=144",
          "SOURCE_MODELS=", source_models, "SHARED_MODELS=", shared_models,
          "K06_K07_HOLDOUTS=", holdouts, "K04_HITS=", original_k04,
          "K08_HITS=", original_k08)
    assert (source_models, shared_models, holdouts, original_k04, original_k08) == (36, 0, 0, 0, 0)


if __name__ == "__main__":
    main()
