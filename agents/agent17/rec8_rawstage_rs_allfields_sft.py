"""Extended pre-reducer REC8 two-erasure GF(2^m) stage test, m=8..128.
Run: python agents/agent17/rec8_rawstage_rs_allfields_sft.py
Original sources and canonical candidate remain read-only.
"""
import hashlib
import itertools
import random
import time
from rec8_rawstage_rs_sft import KNOWN, RAW, MASK, ACCEPT, REFLECT

FIELDS = {
    8: (0x1B, 0x1D),
    16: (0x100B, 0x2B),
    32: (0x8D, 0x04C11DB7),
    64: (0x1B, 0x1D),
    128: (0x87,),
}

def mul(a, b, bits, reduction):
    result = 0
    limit = 1 << bits
    while b:
        if b & 1: result ^= a
        b >>= 1
        a <<= 1
        if a & limit: a ^= limit | reduction
    return result

def inv(a, bits, reduction):
    assert a
    u, v, g1, g2 = a, (1 << bits) | reduction, 1, 0
    while u != 1:
        assert u
        shift = u.bit_length() - v.bit_length()
        if shift < 0:
            u, v = v, u
            g1, g2 = g2, g1
            shift = -shift
        u ^= v << shift
        g1 ^= g2 << shift
    result = g1 & ((1 << bits) - 1)
    assert mul(a, result, bits, reduction) == 1
    return result

def points(mode, reverse, bits, reduction):
    if mode == 0: values = list(range(1, 9))
    elif mode == 1: values = list(range(8))
    else:
        values = [1]
        for _ in range(7):
            values.append(mul(values[-1], 2, bits, reduction))
    if reverse: values.reverse()
    assert len(set(values)) == 8
    return values

def view(data, flags):
    if flags & 1: data = data[::-1]
    if flags & 2: data = b"".join(data[i:i+4][::-1] for i in range(0, 16, 4))
    if flags & 4: data = b"".join(data[i:i+4] for i in (12, 8, 4, 0))
    if flags & 8: data = data.translate(REFLECT)
    return data

def interpolate(source, bits, reduction, coordinates, view_code, training, missing):
    x = coordinates[missing - 1]
    width = bits // 8
    factors = []
    for i in training:
        top, bottom = 1, 1
        for j in training:
            if i != j:
                top = mul(top, x ^ coordinates[j - 1], bits, reduction)
                bottom = mul(bottom, coordinates[i - 1] ^ coordinates[j - 1], bits, reduction)
        factors.append(mul(top, inv(bottom, bits, reduction), bits, reduction))
    values = [
        [int.from_bytes(view(source[i], view_code)[offset:offset + width], "little")
         for offset in range(0, 16, width)]
        for i in training
    ]
    result = []
    for lane in range(16 // width):
        number = 0
        for idx, factor in enumerate(factors):
            number ^= mul(values[idx][lane], factor, bits, reduction)
        result.append(number.to_bytes(width, "little"))
    return view(b"".join(result), view_code)

def main():
    ids = list(KNOWN)
    assert ids == [1, 2, 3, 5, 6, 7]
    for i, value in KNOWN.items():
        assert hashlib.sha256(bytes.fromhex(value)).hexdigest() == ACCEPT[f"K{i:02d}"]
    for i in (2, 7):
        assert hashlib.sha256(bytes.fromhex(RAW[i])).digest()[:16].hex().upper() == KNOWN[i]
    assert hashlib.sha256(b"SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD").digest()[:16].hex().upper() == KNOWN[3]
    n = historical_holdouts = k04_hits = k08_hits = 0
    for bits, polynomials in FIELDS.items():
        perfield = perholdout = 0
        start = time.perf_counter()
        for polynomial, location, reverse in itertools.product(polynomials, range(3), (False, True)):
            coordinates = points(location, reverse, bits, polynomial)
            for stages in itertools.product((False, True), repeat=3):
                source = {
                    i: bytes.fromhex(RAW[i] if i in RAW and stages[(2, 3, 7).index(i)] else KNOWN[i])
                    for i in ids
                }
                for view_code in (range(2) if bits == 8 else range(16)):
                    raw4 = interpolate(source, bits, polynomial, coordinates, view_code, ids, 4)
                    raw8 = interpolate(source, bits, polynomial, coordinates, view_code, ids, 8)
                    component4 = bytes(a ^ b for a, b in zip(raw4, MASK))
                    k04_hits += hashlib.sha256(component4).hexdigest() == ACCEPT["K04"]
                    k08_hits += hashlib.sha256(raw8).hexdigest() == ACCEPT["K08"]
                    n += 1
                    perfield += 1
                    for held in ids:
                        others = [i for i in ids if i != held]
                        match = interpolate(source, bits, polynomial, coordinates, view_code, others, held) == source[held]
                        historical_holdouts += match
                        perholdout += match
        print(f"GF(2^{bits}): models={perfield} historical whole-source holdouts={perholdout} seconds={time.perf_counter()-start:.3f}", flush=True)
    assert (n, historical_holdouts, k04_hits, k08_hits) == (5568, 0, 0, 0)
    print("TOTAL", n, "HISTORICAL FULL SOURCE HOLDOUTS", historical_holdouts,
          "ORIGINAL K04", k04_hits, "ORIGINAL K08", k08_hits)
    for bits, polynomials in FIELDS.items():
        for polynomial in polynomials:
            coordinates = points(2, False, bits, polynomial)
            rng = random.Random(bits * 65536 + polynomial)
            coefficients = [[rng.getrandbits(bits) for _ in range(128 // bits)] for _ in range(6)]
            blocks = []
            for x in coordinates:
                lanes = []
                for j in range(128 // bits):
                    value = 0
                    for coefficient in coefficients[::-1]:
                        value = mul(value, x, bits, polynomial) ^ coefficient[j]
                    lanes.append(value.to_bytes(bits // 8, "little"))
                blocks.append(b"".join(lanes))
            authentic = {i: blocks[i-1] for i in ids}
            assert interpolate(authentic, bits, polynomial, coordinates, 0, ids, 4) == blocks[3]
            assert interpolate(authentic, bits, polynomial, coordinates, 0, ids, 8) == blocks[7]
    print("All 9 genuinely coded synthetic two-erasure fields: PASS")

if __name__ == "__main__":
    main()
