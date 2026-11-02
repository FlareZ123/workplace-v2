"""Source-only exact inverse pilot for two invertible 64-bit PCG output functions.
Use: python agents/agent29/k04_pcg_reversible_heldout_sft.py
Withhold selected K04 printer record, mask, and all commitments.
Official formula: https://github.com/imneme/pcg-c/blob/master/include/pcg_variants.h
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import re

MASK = (1 << 64) - 1
MOD = 1 << 64
PCG_MUL = 6364136223846793005
RXS_MULT = 12605985483714917081
RXS_INV = pow(RXS_MULT, -1, MOD)
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def rotl(v: int, k: int, bits: int) -> int:
    k %= bits
    mask = (1 << bits) - 1
    return ((v << k) | (v >> (bits - k))) & mask


def rotr(v: int, k: int, bits: int) -> int:
    k %= bits
    mask = (1 << bits) - 1
    return ((v >> k) | (v << (bits - k))) & mask


def undo_xor_right(v: int, n: int) -> int:
    while n < 64:
        v ^= v >> n
        n *= 2
    return v & MASK


def rxs_output(state: int) -> int:
    x = (((state >> ((state >> 59) + 5)) ^ state) * RXS_MULT) & MASK
    return x ^ (x >> 43)


def rxs_inverse(output: int) -> int:
    x = (undo_xor_right(output, 43) * RXS_INV) & MASK
    return undo_xor_right(x, (x >> 59) + 5)


def xsl_output(state: int) -> int:
    high = state >> 32
    low = state & 0xFFFFFFFF
    newlow = rotr(high ^ low, high >> 27, 32)
    newhigh = rotr(high, newlow & 31, 32)
    return (newhigh << 32) | newlow


def xsl_inverse(output: int) -> int:
    newlow = output & 0xFFFFFFFF
    newhigh = output >> 32
    high = rotl(newhigh, newlow & 31, 32)
    low = high ^ rotl(newlow, high >> 27, 32)
    return (high << 32) | low


def fit_affine_pairs(pairs: list[tuple[int, int]]) -> tuple[int, int, int, int]:
    x0, y0 = pairs[0]
    for j in range(1, len(pairs)):
        x1, y1 = pairs[j]
        delta = (x1 - x0) & MASK
        if delta & 1:
            mul = ((y1 - y0) * pow(delta, -1, MOD)) & MASK
            inc = (y0 - mul * x0) & MASK
            train = sum(y == (x * mul + inc) & MASK for k, (x, y) in enumerate(pairs) if k in (0, j))
            heldout = sum(y == (x * mul + inc) & MASK for k, (x, y) in enumerate(pairs) if k not in (0, j))
            return mul, inc, train, heldout
    raise AssertionError("No invertible odd-spaced training states")


def main() -> None:
    source = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    data = source.read_bytes()
    assert sha256(data).hexdigest() == SPOOL_HASH
    payloads = []
    for line in data.decode("ascii").splitlines():
        if "PAYLOAD=" not in line or "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line:
            continue
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match is not None
        payloads.append(bytes.fromhex(match.group(1)))
    assert len(payloads) == 132

    test_states = [0, 1, 1234567890123456789, MASK, 0xC0FFEE13579246AB]
    for label, output, inverse in (("RXS-M-XS", rxs_output, rxs_inverse),
                                    ("XSL-RR-RR", xsl_output, xsl_inverse)):
        assert all(inverse(output(state)) == state for state in test_states)
        syn_pairs = [(state, (state * PCG_MUL + 0xC0FFEE123456789B) & MASK)
                     for state in test_states[1:]]
        syn_observed = [(inverse(output(a)), inverse(output(b))) for a, b in syn_pairs]
        assert syn_observed == syn_pairs
        assert len({(b - a * PCG_MUL) & MASK for a, b in syn_observed}) == 1
        common = 0xC0FFEE123456789B
        synt_affine = [(3, (3 * PCG_MUL + common) & MASK), (8, (8 * PCG_MUL + common) & MASK),
                       (27, (27 * PCG_MUL + common) & MASK), (4, (4 * PCG_MUL + common) & MASK)]
        recovered_mul, recovered_inc, control_train, control_test = fit_affine_pairs(synt_affine)
        assert (recovered_mul, recovered_inc, control_train, control_test) == (PCG_MUL, common, 2, 2)
        print(f"{label}: inverse and fixed/free multiplier synthetic controls PASS")
        for reverse in (False, True):
            for endian in ("little", "big"):
                pairs = []
                for payload in payloads:
                    halves = [int.from_bytes(payload[i:i + 8], endian) for i in (0, 8)]
                    if reverse:
                        halves.reverse()
                    pairs.append((inverse(halves[0]), inverse(halves[1])))
                inc = Counter(((b - PCG_MUL * a) & MASK) for a, b in pairs)
                a, b, train, heldout = fit_affine_pairs(pairs)
                assert train == 2
                print(f" {endian:6s} reversed={reverse}: fixed-mul max increment repeat={max(inc.values())}/132; "
                      f"free-mul trained={train}, heldout={heldout}/130; "
                      f"fit mul={a:016X}, inc={b:016X}")
    print("All original checks source-only; historical K04/K08 commitments not consulted.")


if __name__ == "__main__":
    main()
