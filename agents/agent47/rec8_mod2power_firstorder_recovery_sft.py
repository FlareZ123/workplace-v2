"""Source-only first-order modular-affine REC8 slot reconstruction.

Each 128-bit key is divided into 8/16/32/64/128-bit lanes. Fits
T(x)=a*x+b (mod 2**w) using either preserved K01/02/03 or K05/06/07.
Recovers whole K04/K08 predictions, with other original keys as controls.
Never changes the original acceptance, candidate, or verifier.
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
assert all(hashlib.sha256(bytes.fromhex(h)).hexdigest() == ACCEPT["slot_sha256"][f"K{i:02d}"]
           for i, h in KNOWN.items())


def split(raw, bits, endian, reverse):
    if reverse:
        raw = raw[::-1]
    size = bits // 8
    return tuple(int.from_bytes(raw[j:j + size], endian)
                 for j in range(0, 16, size))


def join(words, bits, endian, reverse):
    raw = b"".join(w.to_bytes(bits // 8, endian) for w in words)
    return raw[::-1] if reverse else raw


def solve_mul(c, z, bits):
    """All roots of c*x == z mod 2**bits when c is nonzero."""
    mod = 1 << bits
    c %= mod
    z %= mod
    if c == 0:
        if z != 0:
            return ()
        raise ValueError("completely unconstrained coefficient")
    gcd = c & -c
    if z % gcd:
        return ()
    submod = mod // gcd
    x = (z // gcd * pow(c // gcd, -1, submod)) % submod
    return tuple(x + n * submod for n in range(gcd))


def fit(x, y, z, bits):
    mod = 1 << bits
    return tuple((a, (y - a * x) % mod)
                 for a in solve_mul(y - x, z - y, bits))


def advance(words, coefficients, bits):
    mod = 1 << bits
    return tuple((a * v + b) % mod
                 for v, (a, b) in zip(words, coefficients))


def planted_positive():
    rng = random.Random(20261104)
    for bits in (8, 16, 32, 64, 128):
        mod = 1 << bits
        lanes = 128 // bits
        a = tuple(2 * rng.randrange(mod // 2) + 1 for _ in range(lanes))
        b = tuple(rng.randrange(mod) for _ in range(lanes))
        coefficients = tuple(zip(a, b))
        seq = [tuple(rng.randrange(mod) for _ in range(lanes))]
        for _ in range(7):
            seq.append(advance(seq[-1], coefficients, bits))
        recovered = [fit(seq[0][i], seq[1][i], seq[2][i], bits)
                     for i in range(lanes)]
        assert all(coefficients[i] in recovered[i] for i in range(lanes))
        assert advance(seq[2], coefficients, bits) == seq[3]
        assert advance(seq[6], coefficients, bits) == seq[7]
        assert hashlib.sha256(join(seq[3], bits, "big", False)).digest() == hashlib.sha256(
            join(advance(seq[2], coefficients, bits), bits, "big", False)).digest()
    return 5


def run():
    assert planted_positive() == 5
    predictions = set()
    first_anchor = last_anchor = valid_source = 0
    print("six_original_slot_sha256=PASS; planted_eight_slot_generators=5 PASS")
    for bits, endian, reverse in itertools.product(
            (8, 16, 32, 64, 128), ("big", "little"), (False, True)):
        source = {i: split(bytes.fromhex(h), bits, endian, reverse)
                  for i, h in KNOWN.items()}
        width = 128 // bits
        options = [fit(source[1][j], source[2][j], source[3][j], bits)
                   for j in range(width)]
        nf = nr = 0
        if all(options):
            for coefficients in itertools.product(*options):
                nf += 1
                coupon = advance(source[3], coefficients, bits)
                v5 = advance(coupon, coefficients, bits)
                v6 = advance(v5, coefficients, bits)
                v7 = advance(v6, coefficients, bits)
                v8 = advance(v7, coefficients, bits)
                valid_source += v5 == source[5] and v6 == source[6] and v7 == source[7]
                predictions.add((join(coupon, bits, endian, reverse),
                                 join(v8, bits, endian, reverse)))
        last_options = [fit(source[5][j], source[6][j], source[7][j], bits)
                        for j in range(width)]
        if all(last_options):
            for coefficients in itertools.product(*last_options):
                prior_lanes = [solve_mul(a, source[5][j] - b, bits)
                               for j, (a, b) in enumerate(coefficients)]
                if all(prior_lanes):
                    for coupon in itertools.product(*prior_lanes):
                        nr += 1
                        valid_source += (
                            advance(source[3], coefficients, bits) == coupon
                            and advance(source[2], coefficients, bits) == source[3]
                            and advance(source[1], coefficients, bits) == source[2]
                        )
                        predictions.add((join(coupon, bits, endian, reverse),
                                         join(advance(source[7], coefficients, bits),
                                              bits, endian, reverse)))
        first_anchor += nf
        last_anchor += nr
        print(f"lane_bits={bits} endian={endian} reversed_bytes={reverse} "
              f"first_anchor_models={nf} last_anchor_models={nr}")
    k4_hits = [x.hex().upper() for x, _ in predictions
               if hashlib.sha256(x).hexdigest() == ACCEPT["slot_sha256"]["K04"]]
    k8_hits = [y.hex().upper() for _, y in predictions
               if hashlib.sha256(y).hexdigest() == ACCEPT["slot_sha256"]["K08"]]
    print(f"first_anchor={first_anchor} last_anchor={last_anchor} "
          f"distinct_complete_pairs={len(predictions)} "
          f"all_six_original_holdout_fits={valid_source} "
          f"K04_commitment_matches={len(k4_hits)} K08_commitment_matches={len(k8_hits)}")
    assert (first_anchor, last_anchor, len(predictions),
            valid_source, len(k4_hits), len(k8_hits)) == (26, 4, 5, 0, 0, 0)


if __name__ == "__main__":
    run()
