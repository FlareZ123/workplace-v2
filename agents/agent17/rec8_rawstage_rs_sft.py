"""REC8 raw-reducer-stage polynomial two-erasure recovery; whole-source holdouts.
Python 3 standard library; run from the repository root: python agents/agent17/rec8_rawstage_rs_sft.py.
"""
import hashlib, itertools, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
ACCEPT = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]
MASK = bytes.fromhex(json.loads((ROOT / "evidence/recovery-routing.json").read_text())["K04"]["masked_component"])
KNOWN = {
    1:"049AAB2E1CDE7A82CD7C60234303C91A",
    2:"0D7E3AB56FB75DA3EB0E2E06786D239E",
    3:"1384AF96E25D6ADA666209CB55E062FA",
    5:"FF8B78200A56E8586DCDA00EF01E4572",
    6:"5DBF40EE52FAAED9A536D3326CF0D95A",
    7:"93495F5E425AB8E592123DABAEB68545",
}
RAW = {
    2:"E1A5E474BAD7E853A2E8C71D3317D507",
    3:"D7DAD6BC9714519B7DAD0AD4BE8E87FD",
    7:"8947CEDCB9CC73BAB7E87BE63302C5C9",
}
REFLECT = bytes(int(f"{i:08b}"[::-1], 2) for i in range(256))

def mul(a, b, poly):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1
        a <<= 1
        if a & 256: a ^= poly
    return r

def inv(a, poly):
    assert a
    result = 1
    for _ in range(254):
        result = mul(result, a, poly)
    assert mul(a, result, poly) == 1
    return result

def interpolate(xs, ys, x, poly):
    factors = []
    for i, xi in enumerate(xs):
        num, den = 1, 1
        for j, xj in enumerate(xs):
            if i != j:
                num = mul(num, x ^ xj, poly)
                den = mul(den, xi ^ xj, poly)
        factors.append(mul(num, inv(den, poly), poly))
    return bytes(
        __import__("functools").reduce(
            lambda accum, pair: accum ^ mul(pair[0], pair[1], poly),
            ((ys[i][j], factors[i]) for i in range(len(xs))), 0
        ) for j in range(16)
    )

def coordinates(mode, reverse, poly):
    indices = list(range(8))
    if reverse: indices.reverse()
    if mode == 0: return [i + 1 for i in indices]
    if mode == 1: return indices
    values = [1]
    for _ in range(7): values.append(mul(values[-1], 2, poly))
    return [values[i] for i in indices]

def main():
    for slot, code in KNOWN.items():
        assert hashlib.sha256(bytes.fromhex(code)).hexdigest() == ACCEPT[f"K{slot:02d}"]
    for slot in (2, 7):
        assert hashlib.sha256(bytes.fromhex(RAW[slot])).digest()[:16].hex().upper() == KNOWN[slot]
    signed = b"SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD"
    assert hashlib.sha256(signed).digest()[:16].hex().upper() == KNOWN[3]
    # K03 16-byte raw source is four selected serial suffixes; the real
    # K03 prehash is their 47-byte SG-labelled ASCII join above.
    ids = tuple(KNOWN)
    total, holdouts, hits = 0, 0, []
    for use_raw in itertools.product((False, True), repeat=3):
        blocks = {
            slot: bytes.fromhex(RAW[slot] if slot in RAW and use_raw[(2, 3, 7).index(slot)] else KNOWN[slot])
            for slot in ids
        }
        for bit_reverse in (False, True):
            code = {k: v.translate(REFLECT) if bit_reverse else v for k, v in blocks.items()}
            for poly in (0x11B, 0x11D):
                for mode in range(3):
                    for backwards in (False, True):
                        xs = coordinates(mode, backwards, poly)
                        assert len(set(xs)) == 8
                        known_x = [xs[i-1] for i in ids]
                        known_y = [code[i] for i in ids]
                        for excluded in range(6):
                            other_x = [x for n, x in enumerate(known_x) if n != excluded]
                            other_y = [y for n, y in enumerate(known_y) if n != excluded]
                            holdouts += (interpolate(other_x, other_y, known_x[excluded], poly) == known_y[excluded])
                        coupon = interpolate(known_x, known_y, xs[3], poly)
                        digest = interpolate(known_x, known_y, xs[7], poly)
                        if bit_reverse:
                            coupon = coupon.translate(REFLECT)
                            digest = digest.translate(REFLECT)
                        slot4 = bytes(a ^ b for a, b in zip(coupon, MASK))
                        hit4 = hashlib.sha256(slot4).hexdigest() == ACCEPT["K04"]
                        hit8 = hashlib.sha256(digest).hexdigest() == ACCEPT["K08"]
                        if hit4 or hit8:
                            hits.append((use_raw, bit_reverse, hex(poly), mode, backwards, hit4, hit8))
                        total += 1
    assert total == 192 and holdouts == 0 and hits == []
    print("Original historical six slot SHA controls: PASS")
    print("Original GF256 raw/digest stage models:", total)
    print("Original independent historical degree-4 whole-block holdout fits:", holdouts)
    print("Original full K04/K08 commitment matches:", hits)
    # Genuine planted degree-five polynomial controls with held-out slots 4 and 8.
    import random
    for poly in (0x11B, 0x11D):
        xs = coordinates(2, False, poly)
        rng = random.Random(20261109)
        coefficients = [[rng.randrange(256) for _ in range(16)] for _ in range(6)]
        ys = [bytes(
            __import__("functools").reduce(
                lambda old, col: mul(old, x, poly) ^ col[j],
                coefficients[::-1], 0
            ) for j in range(16)) for x in xs]
        observed = [ys[i-1] for i in ids]
        for missing in (3, 7):
            assert interpolate([xs[i-1] for i in ids], observed, xs[missing], poly) == ys[missing]
    print("Two independent genuine 8-point polynomial planted controls: PASS")

if __name__ == "__main__":
    main()
