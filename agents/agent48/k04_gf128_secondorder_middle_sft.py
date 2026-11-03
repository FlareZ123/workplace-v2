"""Exact GF(2^128) second-order middle-packet K04 interpolation.

Each five-packet group satisfies x[n+2] = A*x[n+1] XOR B*x[n] XOR C
over GF(2^128), with unknown A,B and C either zero or original K04
route mask. Given X0,X2,X3,X4, recover all possible missing X1 by a
quadratic. Test source-selected late packets with source/commitment
untouched, three earlier intact holdouts, and planted synthetic sources.
"""
import hashlib
import itertools
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK128 = (1 << 128) - 1


def mul(a, b):
    result = 0
    for _ in range(128):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a >> 128:
            a = (a & MASK128) ^ 0x87
    assert b == 0
    return result


def power(a, n):
    out = 1
    while n:
        if n & 1:
            out = mul(out, a)
        a = mul(a, a)
        n >>= 1
    return out


def inverse(x):
    assert x
    return power(x, (1 << 128) - 2)


def sqrt(x):
    for _ in range(127):
        x = mul(x, x)
    return x


def roots(a, b, c):
    if a == 0:
        return [] if b == 0 and c else (
            None if b == 0 else [mul(c, inverse(b))]
        )
    if b == 0:
        return [sqrt(mul(c, inverse(a)))]
    q = mul(mul(a, c), inverse(mul(b, b)))
    basis = {}
    for i in range(128):
        v, bits = mul(1 << i, 1 << i) ^ (1 << i), 1 << i
        while v:
            pivot = v.bit_length() - 1
            if pivot in basis:
                r, rb = basis[pivot]
                v ^= r
                bits ^= rb
            else:
                basis[pivot] = v, bits
                break
    bits, x = 0, q
    while x:
        p = x.bit_length() - 1
        if p not in basis:
            return []
        r, rb = basis[p]
        x ^= r
        bits ^= rb
    assert mul(bits, bits) ^ bits == q
    scale = mul(b, inverse(a))
    return [mul(scale, bits), mul(scale, bits ^ 1)]


def recover(x0, x2, x3, x4, const):
    assert x2
    inv2 = inverse(x2)
    b0 = mul(x4 ^ const, inv2)
    b1 = mul(x3, inv2)
    a2 = x2 ^ mul(mul(b1, b1), x0)
    a1 = mul(b1, const) ^ const
    a0 = mul(b0, x2 ^ const) ^ mul(mul(b0, b0), x0)
    outcomes = []
    for a in roots(a2, a1, a0) or []:
        b = mul(x4 ^ const ^ mul(a, x3), inv2)
        if a:
            middle = mul(x2 ^ const ^ mul(b, x0), inverse(a))
        elif b:
            middle = mul(x3 ^ const, inverse(b))
        else:
            continue
        assert mul(a, middle) ^ mul(b, x0) ^ const == x2
        assert mul(a, x2) ^ mul(b, middle) ^ const == x3
        assert mul(a, x3) ^ mul(b, x2) ^ const == x4
        outcomes.append((a, b, middle))
    return outcomes


def viewed(x, reverse_words, reverse_word_bytes, reflect_bits):
    ws = [x.to_bytes(16, "big")[i:i+4] for i in range(0, 16, 4)]
    if reverse_words:
        ws.reverse()
    if reverse_word_bytes:
        ws = [w[::-1] for w in ws]
    bs = b"".join(ws)
    if reflect_bits:
        bs = bytes(int(f"{v:08b}"[::-1], 2) for v in bs)
    return int.from_bytes(bs, "big")


def unviewed(x, reverse_words, reverse_word_bytes, reflect_bits):
    bs = x.to_bytes(16, "big")
    if reflect_bits:
        bs = bytes(int(f"{v:08b}"[::-1], 2) for v in bs)
    ws = [bs[i:i+4] for i in range(0, 16, 4)]
    if reverse_word_bytes:
        ws = [w[::-1] for w in ws]
    if reverse_words:
        ws.reverse()
    return int.from_bytes(b"".join(ws), "big")


def source():
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    lines = [s for s in raw.decode("ascii").splitlines() if "PAYLOAD=" in s]
    assert len(lines) == 133
    assert lines[129].startswith(
        "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER "
    )
    packets = []
    for i, line in enumerate(lines):
        if i == 129:
            packets.append(None)
            continue
        m = re.search(r"PAYLOAD=([0-9A-F]{32})(?:\s|$)", line)
        assert m is not None
        packets.append(int(m.group(1), 16))
    return packets


def seeded_controls():
    rng = random.Random(20261103)
    out = []
    for const in (0, rng.getrandbits(128)):
        a, b = rng.getrandbits(128), rng.getrandbits(128)
        words = [rng.getrandbits(128), rng.getrandbits(128)]
        for _ in range(3):
            words.append(mul(a, words[-1]) ^ mul(b, words[-2]) ^ const)
        solutions = recover(words[0], words[2], words[3], words[4], const)
        assert words[1] in [x[2] for x in solutions]
        changed = recover(words[0], words[2], words[3], words[4] ^ 1, const)
        assert words[1] not in [x[2] for x in changed]
        out.append({"fixed_offset_zero": const == 0,
                    "hidden_packet_recovered": True,
                    "one_bit_tamper_rejected": True})
    return out


def main():
    packets = source()
    mask = int(json.loads(
        (ROOT / "evidence/recovery-routing.json").read_text()
    )["K04"]["masked_component"], 16)
    target = json.loads(
        (ROOT / "acceptance.json").read_text()
    )["slot_sha256"]["K04"]
    candidates = {}
    heldout_solutions = heldout_hits = models = 0
    for flags in itertools.product((False, True), repeat=3):
        for x in (0, 1, mask, packets[128], packets[130]):
            assert unviewed(viewed(x, *flags), *flags) == x
        late = [viewed(packets[i], *flags) for i in (128, 130, 131, 132)]
        for offset_label, offset in (("zero", 0),
                                     ("route_mask", viewed(mask, *flags))):
            models += 1
            for a, b, middle in recover(*late, offset):
                coupon = unviewed(middle, *flags)
                value = coupon ^ mask
                candidate = f"{value:032X}"
                candidates[candidate] = {
                    "serialization_flags": list(flags),
                    "offset_source": offset_label,
                    "K04": candidate,
                    "accepted": hashlib.sha256(value.to_bytes(16, "big")
                                               ).hexdigest() == target,
                }
            for start in (0, 61, 120):
                window = [viewed(packets[start + j], *flags)
                          for j in (0, 2, 3, 4)]
                options = recover(*window, offset)
                heldout_solutions += len(options)
                heldout_hits += any(
                    unviewed(triple[2], *flags) == packets[start+1]
                    for triple in options
                )
    assert models == 16 and len(candidates) == 16
    assert not any(c["accepted"] for c in candidates.values())
    assert heldout_hits == 0
    controls = seeded_controls()
    print(json.dumps({
        "source_sha256": PIN,
        "selected_ACK_payload_decoded": False,
        "GF128_modulus": "x^128+x^7+x^2+x+1",
        "frozen_models": models,
        "full_distinct_K04_candidates": len(candidates),
        "accepted_original": 0,
        "ordinary_heldout_windows": 48,
        "ordinary_prediction_options": heldout_solutions,
        "ordinary_heldout_hits": heldout_hits,
        "synthetic_controls": controls,
        "example_candidate": candidates["D8EB07D2F7EFCA50B8E9F85134936F92"],
        "status": "NO_K04_MATCH",
    }, indent=2))


if __name__ == "__main__":
    main()
