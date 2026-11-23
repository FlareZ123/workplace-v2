"""H-17 K04 source-pinned PCG 64-bit-output / arbitrary affine retry bridge.

Recover a complete 16-byte missing attempt-2 coupon if its 64-bit states
follow the surviving request-1 and request-3 payloads in one stateful
64-bit LCG, with arbitrary affine multiplier/increment and 4..128 native
output-stage gap. Exact modular power-root enumeration, no random search.
The disputed selected ACK2 payload is never used as a model input.

Run from repo root: python agents/agent50/k04_pcg_affine_retry_sft.py
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MOD = 1 << 64
MASK = MOD - 1
RXS_MULT = 12605985483714917081
RXS_INV = pow(RXS_MULT, -1, MOD)


def rotl(x: int, bits: int, width: int = 64) -> int:
    bits %= width
    return ((x << bits) | (x >> (width - bits))) & ((1 << width) - 1)


def rotr(x: int, bits: int, width: int = 64) -> int:
    bits %= width
    return ((x >> bits) | (x << (width - bits))) & ((1 << width) - 1)


def undo_xor_right(x: int, shift: int) -> int:
    while shift < 64:
        x ^= x >> shift
        shift *= 2
    return x & MASK


def rxs_output(x: int) -> int:
    v = ((((x >> ((x >> 59) + 5)) ^ x) * RXS_MULT) & MASK)
    return v ^ (v >> 43)


def rxs_inverse(y: int) -> int:
    x = undo_xor_right(y, 43) * RXS_INV & MASK
    return undo_xor_right(x, (x >> 59) + 5)


def xsl_output(x: int) -> int:
    high, low = x >> 32, x & 0xFFFFFFFF
    newlow = rotr(high ^ low, high >> 27, 32)
    return (rotr(high, newlow & 31, 32) << 32) | newlow


def xsl_inverse(y: int) -> int:
    low, high = y & 0xFFFFFFFF, y >> 32
    oldhigh = rotl(high, low & 31, 32)
    return (oldhigh << 32) | (oldhigh ^ rotl(low, oldhigh >> 27, 32))


def state_after(x: int, multiplier: int, increment: int, steps: int) -> int:
    # Binary exponentiation in the affine transformation monoid.
    mul, inc = multiplier, increment
    while steps:
        if steps & 1:
            x = (mul * x + inc) & MASK
        inc = (mul * inc + inc) & MASK
        mul = mul * mul & MASK
        steps >>= 1
    return x


def v2(x: int) -> int:
    return 64 if x == 0 else (x & -x).bit_length() - 1


def roots_pow2(rhs: int, width: int, exponent: int) -> list[int]:
    """All roots of x**exponent == rhs (mod 2**width), exact bit-lift."""
    roots = [rhs & 1]
    for bits in range(1, width):
        modulus = 1 << (bits + 1)
        roots = [
            proposed
            for old in roots
            for proposed in (old, old + (1 << bits))
            if (pow(proposed, exponent, modulus) - rhs) % modulus == 0
        ]
        if not roots:
            break
    return roots


def affine_multipliers(s0: int, s1: int, sn: int, sn1: int,
                       distance: int) -> list[int]:
    """Necessary complete multipliers from Δ_n = a**n * Δ_0 mod 2**64."""
    d0, dn = (s1 - s0) & MASK, (sn1 - sn) & MASK
    t = v2(d0)
    if t >= 64 or dn % (1 << t):
        return []
    width = 64 - t
    modulus = 1 << width
    quotient = ((dn >> t) * pow(d0 >> t, -1, modulus)) % modulus
    roots = roots_pow2(quotient, width, distance)
    assert t <= 16, "The original direct-state gap is too degenerate for this bounded enumerator"
    return [root + (high << width) for root in roots for high in range(1 << t)]


def inverse_pair(packet: bytes, endian: str, reverse: bool, inverse):
    halves = [int.from_bytes(packet[i:i + 8], endian) for i in (0, 8)]
    if reverse:
        halves.reverse()
    return tuple(inverse(x) for x in halves)


def synthetic_controls():
    for name, output, inverse in (
        ("RXS", rxs_output, rxs_inverse),
        ("XSL", xsl_output, xsl_inverse),
    ):
        for state in (0, 1, MASK, 0x123456789ABCDEF1):
            assert inverse(output(state)) == state
        for distance in (4, 5, 7, 17, 32, 64, 128):
            for multiplier in (6364136223846793005, 0xF1357AEA2E62A9C5):
                increment = 0xC0FFEE123456789B
                initial = 0x123456789ABCDEF1
                next_state = state_after(initial, multiplier, increment, 1)
                later = state_after(initial, multiplier, increment, distance)
                later_next = state_after(next_state, multiplier, increment, distance)
                recovered = affine_multipliers(initial, next_state, later,
                                               later_next, distance)
                assert multiplier in recovered, (name, distance, multiplier)
                assert any(
                    state_after(initial, a, (next_state - a * initial) & MASK,
                                distance) == later
                    for a in recovered
                )
        print("SYNTHETIC_REVERSIBLE_OUTPUT_AND_GAP_RECOVERY", name, "PASS")


def main():
    synthetic_controls()
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    lines = [line for line in raw.decode("ascii").splitlines()
             if line.startswith("2026-")]
    assert len(lines) == 133
    assert "JOB=PS-261003-0417 ATTEMPT=1 STATE=REQUESTED" in lines[128]
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK" in lines[129]
    assert "JOB=PS-261003-0417 ATTEMPT=3 STATE=REQUESTED" in lines[130]
    # Only decode two request flanks. The selected copied ACK2 is never parsed.
    request_packets = [bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})", lines[i]).group(1))
                       for i in (128, 130)]
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    digest = acceptance["slot_sha256"]["K04"]
    assert digest == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
    counts = {}
    all_hits = []
    for name, output, inverse in (
        ("PCG-RXS-M-XS", rxs_output, rxs_inverse),
        ("PCG-XSL-RR-RR", xsl_output, xsl_inverse),
    ):
        for endian, reverse in itertools.product(("little", "big"), (False, True)):
            (s0, s1), (sn, sn1) = [
                inverse_pair(packet, endian, reverse, inverse)
                for packet in request_packets
            ]
            roots = issuers = 0
            coupons = set()
            for distance in range(4, 129):
                for multiplier in affine_multipliers(s0, s1, sn, sn1, distance):
                    roots += 1
                    increment = (s1 - multiplier * s0) & MASK
                    if state_after(s0, multiplier, increment, distance) != sn:
                        continue
                    assert state_after(s1, multiplier, increment, distance) == sn1
                    issuers += 1
                    mid0 = state_after(s1, multiplier, increment, 1)
                    mid1 = state_after(mid0, multiplier, increment, 1)
                    words = [output(mid0), output(mid1)]
                    if reverse:
                        words.reverse()
                    coupon = b"".join(v.to_bytes(8, endian) for v in words)
                    coupons.add(coupon)
                    component = bytes(x ^ y for x, y in zip(coupon, mask))
                    if hashlib.sha256(component).hexdigest() == digest:
                        all_hits.append((name, endian, reverse, distance,
                                         component.hex().upper()))
            counts[name, endian, reverse] = (roots, issuers, len(coupons))
            print("SOURCE_MODEL", name, endian, "reversed", reverse,
                  "NATIVE_GAPS", 125, "POWER_ROOTS", roots,
                  "SIX_OUTPUT_ISSUERS", issuers,
                  "COMPLETE_COUPONS", len(coupons))
    assert all(v[1] == 0 for v in counts.values()), counts
    assert not all_hits, all_hits
    print("SOURCE_SHA256", SOURCE_SHA)
    print("SELECTED_ACK2_PAYLOAD_USED", "NO")
    print("COMPLETE_K04_COMMITMENT_HITS", len(all_hits))


if __name__ == "__main__":
    main()
