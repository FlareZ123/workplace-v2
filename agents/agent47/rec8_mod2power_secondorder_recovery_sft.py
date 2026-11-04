"""H-17 source-gated second-order REC8 affine recurrence over Z/(2**w).

Fit coefficients A,B from two separated original intact slot equations:
  K03=A*K02+B*K01; K07=A*K06+B*K05.
Calculate missing K04,K08 and independently check K05,K06. Read-only.
"""
import hashlib
import itertools
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
ACCEPTANCE = json.loads((ROOT / "acceptance.json").read_text())
KNOWN = {
    1: "049AAB2E1CDE7A82CD7C60234303C91A",
    2: "0D7E3AB56FB75DA3EB0E2E06786D239E",
    3: "1384AF96E25D6ADA666209CB55E062FA",
    5: "FF8B78200A56E8586DCDA00EF01E4572",
    6: "5DBF40EE52FAAED9A536D3326CF0D95A",
    7: "93495F5E425AB8E592123DABAEB68545",
}
assert all(hashlib.sha256(bytes.fromhex(h)).hexdigest() == ACCEPTANCE["slot_sha256"][f"K{i:02d}"]
           for i, h in KNOWN.items())


def split(hexstr, bits, endian, rev):
    raw = bytes.fromhex(hexstr)
    if rev:
        raw = raw[::-1]
    size = bits // 8
    return tuple(int.from_bytes(raw[i:i+size], endian)
                 for i in range(0, 16, size))


def join(words, bits, endian, rev):
    raw = b"".join(x.to_bytes(bits//8, endian) for x in words)
    return raw[::-1] if rev else raw


def solve2(x1, x2, y1, y2, z1, z2, bits):
    """Exact two-equation modular solve via power-of-two Hensel lifting."""
    roots = [(0, 0)]
    for bit in range(bits):
        stride = 1 << bit
        mod = stride * 2
        roots = [(a+i*stride, b+j*stride)
                 for a, b in roots for i in (0,1) for j in (0,1)
                 if (x1*(a+i*stride)+y1*(b+j*stride)-z1) % mod == 0
                 and (x2*(a+i*stride)+y2*(b+j*stride)-z2) % mod == 0]
        if not roots:
            break
    return tuple(roots)


def advance(x, y, coefficients, bits):
    mod = 1 << bits
    return tuple((a*y[i]+b*x[i])%mod for i,(a,b) in enumerate(coefficients))


def synthetic_controls():
    r = random.Random(20261104)
    for bits in (8,16,32,64,128):
        mod = 1 << bits
        n = 128 // bits
        coefficients = tuple((r.randrange(mod),r.randrange(mod)) for _ in range(n))
        series = [tuple(r.randrange(mod) for _ in range(n)) for _ in (0,1)]
        for i in range(2,8):
            series.append(advance(series[-2],series[-1],coefficients,bits))
        solutions = [solve2(series[1][j],series[5][j],
                            series[0][j],series[4][j],
                            series[2][j],series[6][j],bits)
                     for j in range(n)]
        assert all(coefficients[j] in solutions[j] for j in range(n))
        assert advance(series[1],series[2],coefficients,bits) == series[3]
        assert advance(series[5],series[6],coefficients,bits) == series[7]
        for i in (3,7):
            expected = hashlib.sha256(join(series[i],bits,"big",False)).digest()
            actual = hashlib.sha256(join(
                advance(series[i-2],series[i-1],coefficients,bits),
                bits,"big",False)).digest()
            assert actual == expected
    return 5


def run():
    assert synthetic_controls() == 5
    models = 0
    holdouts = 0
    predictions = set()
    for bits, endian, rev in itertools.product(
            (8,16,32,64,128), ("big","little"), (False,True)):
        known = {i:split(h,bits,endian,rev) for i,h in KNOWN.items()}
        n = 128 // bits
        options = [solve2(known[2][j],known[6][j],
                          known[1][j],known[5][j],
                          known[3][j],known[7][j],bits)
                   for j in range(n)]
        nmodels = 0
        if all(options):
            for coefficients in itertools.product(*options):
                nmodels += 1
                v4 = advance(known[2],known[3],coefficients,bits)
                v5 = advance(known[3],v4,coefficients,bits)
                v6 = advance(v4,known[5],coefficients,bits)
                v8 = advance(known[6],known[7],coefficients,bits)
                holdouts += (v5 == known[5] and v6 == known[6])
                predictions.add((join(v4,bits,endian,rev),
                                 join(v8,bits,endian,rev)))
        models += nmodels
        print(f"width={bits} endian={endian} reversed_bytes={rev} "
              f"original_two_anchor_solutions={nmodels}")
    k4 = sum(hashlib.sha256(x).hexdigest() == ACCEPTANCE["slot_sha256"]["K04"]
             for x,y in predictions)
    k8 = sum(hashlib.sha256(y).hexdigest() == ACCEPTANCE["slot_sha256"]["K08"]
             for x,y in predictions)
    print(f"accepted_six_sha256=PASS planted_8slot_controls=5_PASS "
          f"original_models={models} distinct_complete_pairs={len(predictions)} "
          f"authentic_K05_K06_full_holdouts={holdouts} "
          f"K04_original_sha256_hits={k4} K08_original_sha256_hits={k8}")
    assert (models,len(predictions),holdouts,k4,k8) == (6,3,0,0,0)


if __name__ == "__main__":
    run()
