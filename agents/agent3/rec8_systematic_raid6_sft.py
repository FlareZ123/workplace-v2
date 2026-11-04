#!/usr/bin/env python3
"""H-17 six-known/two-missing: systematic GF256 RAID6 P+Q reconstruction SFT.

Exhaustively permute two parity roles among the six accepted slots, two
source-prehash alternatives, standard GF256 fields/bases, data-coordinate
orders and reversible per-slot bit/byte views. Test complete K04 and K08
against their untouched SHA256 commitments. No sources are modified.
"""
from pathlib import Path
from itertools import product, permutations
from hashlib import sha256
from functools import reduce
import json
import random

root = Path(__file__).resolve().parents[2] / "resources"
pinned = {
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "evidence/telemetry/freeze-export.jsonl": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
    "evidence/transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
}
for path, expected in pinned.items():
    assert sha256((root / path).read_bytes()).hexdigest() == expected, path

accept = json.loads((root / "acceptance.json").read_text())
route = json.loads((root / "evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
known = {
    1: "049AAB2E1CDE7A82CD7C60234303C91A",
    2: "0D7E3AB56FB75DA3EB0E2E06786D239E",
    3: "1384AF96E25D6ADA666209CB55E062FA",
    5: "FF8B78200A56E8586DCDA00EF01E4572",
    6: "5DBF40EE52FAAED9A536D3326CF0D95A",
    7: "93495F5E425AB8E592123DABAEB68545",
}
assert all(sha256(bytes.fromhex(value)).hexdigest() ==
           accept["slot_sha256"][f"K{i:02d}"] for i, value in known.items())
raw2 = "E1A5E474BAD7E853A2E8C71D3317D507"
raw7 = "8947CEDCB9CC73BAB7E87BE63302C5C9"
assert sha256(bytes.fromhex(raw2)).digest()[:16].hex().upper() == known[2]
assert sha256(bytes.fromhex(raw7)).digest()[:16].hex().upper() == known[7]

def multiply(a, b, poly):
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 256:
            a ^= poly
    return result

def field(poly):
    table = [[multiply(a, b, poly) for b in range(256)]
             for a in range(256)]
    inverse = [0] * 256
    for a in range(1, 256):
        inverse[a] = next(b for b in range(1, 256) if table[a][b] == 1)
    return table, inverse

def serial(raw, reverse_words, reverse_bytes, reflect):
    words = [raw[i:i+4] for i in range(0, 16, 4)]
    if reverse_words:
        words.reverse()
    if reverse_bytes:
        words = [w[::-1] for w in words]
    data = b"".join(words)
    if reflect:
        data = bytes(int(f"{b:08b}"[::-1], 2) for b in data)
    return data

def coefficients(data_slots, base, reverse, mode, table):
    order = sorted(data_slots, reverse=reverse)
    index = ({s: s - 1 for s in data_slots} if mode == "slot"
             else {s: i for i, s in enumerate(order)})
    result = {}
    for slot in data_slots:
        coef = 1
        for _ in range(index[slot]):
            coef = table[coef][base]
        result[slot] = coef
    return result

def recover(observed, pslot, qslot, coef, table, inverse):
    data = sorted(set(range(1, 9)) - {pslot, qslot})
    c4, c8 = coef[4], coef[8]
    assert c4 != c8
    scale = inverse[c4 ^ c8]
    o4, o8 = bytearray(16), bytearray(16)
    for j in range(16):
        x, y = observed[pslot][j], observed[qslot][j]
        for slot in data:
            if slot not in (4, 8):
                x ^= observed[slot][j]
                y ^= table[coef[slot]][observed[slot][j]]
        o4[j] = table[scale][y ^ table[c8][x]]
        o8[j] = x ^ o4[j]
        assert table[c4][o4[j]] ^ table[c8][o8[j]] == y
    return bytes(o4), bytes(o8)

planted = 0
rng = random.Random(20261104)
for poly in (0x11B, 0x11D):
    table, inverse = field(poly)
    pslot, qslot = 1, 7
    data = sorted(set(range(1, 9)) - {pslot, qslot})
    coef = coefficients(data, 3, False, "rank", table)
    original = {slot: bytes(rng.getrandbits(8) for _ in range(16))
                for slot in data}
    P = bytes(reduce(lambda x, s: x ^ original[s][j], data, 0)
              for j in range(16))
    Q = bytes(reduce(lambda x, s: x ^ table[coef[s]][original[s][j]],
                     data, 0) for j in range(16))
    got = recover({**original, pslot: P, qslot: Q},
                  pslot, qslot, coef, table, inverse)
    assert got == (original[4], original[8])
    planted += 1

models, hit4, hit4_coupon, hit8, pairhits = 0, 0, 0, 0, 0
distinct = set()
for poly in (0x11B, 0x11D):
    table, inverse = field(poly)
    for is_raw2, is_raw7 in product((False, True), repeat=2):
        real = {slot: bytes.fromhex(value) for slot, value in known.items()}
        if is_raw2:
            real[2] = bytes.fromhex(raw2)
        if is_raw7:
            real[7] = bytes.fromhex(raw7)
        for layout in product((False, True), repeat=3):
            observed = {slot: serial(value, *layout)
                        for slot, value in real.items()}
            for pslot, qslot in permutations(known, 2):
                data = sorted(set(range(1, 9)) - {pslot, qslot})
                for base, reverse, mode in product(
                        (2, 3, 5, 11, 0x1D), (False, True),
                        ("rank", "slot")):
                    coef = coefficients(data, base, reverse, mode, table)
                    r4, r8 = recover(observed, pslot, qslot,
                                     coef, table, inverse)
                    raw4, raw8 = serial(r4, *layout), serial(r8, *layout)
                    candidate4 = bytes(a ^ b for a, b in zip(raw4, mask))
                    good4 = sha256(raw4).hexdigest() == accept["slot_sha256"]["K04"]
                    good4c = sha256(candidate4).hexdigest() == accept["slot_sha256"]["K04"]
                    good8 = sha256(raw8).hexdigest() == accept["slot_sha256"]["K08"]
                    models += 1
                    hit4 += good4
                    hit4_coupon += good4c
                    hit8 += good8
                    pairhits += (good4 or good4c) and good8
                    distinct.add((raw4, raw8))

assert (models, hit4, hit4_coupon, hit8, pairhits, len(distinct), planted) == (
    38400, 0, 0, 0, 0, 7200, 2)
print({
    "known_source_slot_hashes": "6/6 PASS",
    "systematic_RAID6_PQ_assignments": models,
    "distinct_K04_K08_pairs": len(distinct),
    "K04_direct_original_hits": hit4,
    "K04_masked_coupon_original_hits": hit4_coupon,
    "K08_original_hits": hit8,
    "both_original_hits": pairhits,
    "two_erasure_synthetic_positive_controls": planted,
})
