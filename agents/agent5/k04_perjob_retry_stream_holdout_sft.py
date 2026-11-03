"""Test exceptional per-job retry stream hypotheses against withheld original packets.

Original selected PS-261003-0417 attempt-2 ACK is never read as a test value.
Source holdouts: 0417 later REQUESTED x2, 0420 later RECOVER ACK.
For each generator: 2 endian readings x 24 word orders x 129 admissible
whole-output starts (0..128 hidden 32-bit words after the first packet).
Uses no original K04 acceptance commitment.
"""
import hashlib
import re
from itertools import permutations
from pathlib import Path

MASK = (1 << 32) - 1
SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"


def rotl(v, n):
    return ((v << n) | (v >> (32 - n))) & MASK


def next_xoshiro(s):
    a, b, c, d = s
    output = (rotl(b * 5 & MASK, 7) * 9) & MASK
    t = (b << 9) & MASK
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= t
    d = rotl(d, 11)
    return output, (a, b, c, d)


def invert_output(v):
    return (rotl(v * pow(9, -1, 1 << 32) & MASK, 25)
            * pow(5, -1, 1 << 32)) & MASK


def next_xorshift(s):
    a, b, c, d = s
    t = (a ^ (a << 11)) & MASK
    n = (d ^ (d >> 19) ^ t ^ (t >> 8)) & MASK
    return n, (b, c, d, n)


def generate(initial, fn, count):
    state = initial
    output = []
    for _ in range(count):
        v, state = fn(state)
        output.append(v)
    return output


# The four invertible xoshiro128** outputs reveal the first four state b words.
# Reconstruct all 128 state bits using an exact GF(2) matrix inverse.
columns = []
for bit in range(128):
    state = tuple((1 << bit >> (32 * j)) & MASK for j in range(4))
    measured = []
    for _ in range(4):
        measured.append(state[1])
        _, state = next_xoshiro(state)
    columns.append(sum(v << (32 * i) for i, v in enumerate(measured)))

rows = [sum(((col >> i) & 1) << j for j, col in enumerate(columns))
        for i in range(128)]


def invert_xoshiro(first_words):
    rhs = sum(invert_output(v) << (32 * i)
              for i, v in enumerate(first_words))
    a = [r | (((rhs >> i) & 1) << 128) for i, r in enumerate(rows)]
    pivots = []
    rank = 0
    for col in range(128):
        pivot = next((r for r in range(rank, 128)
                      if (a[r] >> col) & 1), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        for r in range(128):
            if r != rank and ((a[r] >> col) & 1):
                a[r] ^= a[rank]
        pivots.append(col)
        rank += 1
    assert rank == 128
    integer = sum(((a[r] >> 128) & 1) << col
                  for r, col in enumerate(pivots))
    return tuple((integer >> (32 * j)) & MASK for j in range(4))


# Independent seeded positive controls for both continuous-stream engines.
seed = (0x1337ABCD, 0x89ABCDEF, 0x55667788, 0x99AABBCC)
first = generate(seed, next_xoshiro, 4)
assert invert_xoshiro(first) == seed
assert generate(invert_xoshiro(first), next_xoshiro, 8) == \
       generate(seed, next_xoshiro, 8)
assert generate(seed, next_xorshift, 12)[4:8] == \
       generate(tuple(generate(seed, next_xorshift, 4)),
                next_xorshift, 4)

data = SOURCE.read_bytes()
assert hashlib.sha256(data).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
records = []
for line in data.decode().splitlines():
    if not line or line.startswith("#"):
        continue
    fields = dict(re.findall(r"([A-Z]+)=([^ ]+)", line))
    if fields["JOB"].endswith(("0417", "0420")):
        records.append(dict(job=fields["JOB"][-4:],
                            state=fields["STATE"],
                            time=line.split()[0],
                            payload=bytes.fromhex(fields["PAYLOAD"])))

assert [r["state"] for r in records if r["job"] == "0417"] == \
       ["ACK", "REQUESTED", "ACK", "REQUESTED"]
assert [r["state"] for r in records if r["job"] == "0420"] == \
       ["ACK", "ACK"]


def words(packet, endian, order):
    w = [int.from_bytes(packet[i:i + 4], endian)
         for i in range(0, 16, 4)]
    return tuple(w[i] for i in order)


for job in ("0417", "0420"):
    series = [r for r in records if r["job"] == job]
    # Exclude the selected ACK 18:02 even from withheld-control comparisons.
    holdouts = [r for r in series[1:]
                if not (job == "0417" and r["state"] == "ACK")]
    assert len(holdouts) == (2 if job == "0417" else 1)
    for family in ("xoshiro128**", "xorshift128"):
        checked = 0
        hits = []
        for endian in ("big", "little"):
            for order in permutations(range(4)):
                start = words(series[0]["payload"], endian, order)
                if family == "xoshiro128**":
                    state = invert_xoshiro(start)
                    output = generate(state, next_xoshiro, 136)[4:]
                else:
                    output = generate(start, next_xorshift, 132)
                predictions = {tuple(output[i:i+4]): i for i in range(129)}
                for row in holdouts:
                    actual = words(row["payload"], endian, order)
                    if actual in predictions:
                        hits.append((endian, order, row["time"],
                                     predictions[actual]))
                    checked += 1
        print(job, family, "whole-packet models", checked,
              "matches", hits)
        assert not hits, "This source model has an unexpected exact holdout hit"
print("Selected original K04 coupon remained excluded; no recovery is claimed.")


# Incremental target-facing inverse route: use only the later 18:03
# REQUESTED3 packet as a source anchor. Agent24 already tested xorshift128
# forward from 18:01 REQUESTED1 (0..8192 positions), while Agent3 tested
# xoshiro128** joint REQUESTED outer-packet exact consistency (4 word orders).
# The inverse route below tests all 24 four-word orders, 0..128 reverse
# inter-draw positions, with separate exact seeded inversion controls.
# No historical original payload authenticity is implied.

import json


def inverse_xoshiro_state(s):
    a, b, c, d = s
    d_b = rotl(d, 21)
    old_a = a ^ d_b
    q = c ^ b
    old_b = q
    old_b ^= (old_b << 9) & MASK
    old_b ^= (old_b << 18) & MASK
    return (old_a, b ^ old_b ^ old_a, d_b ^ old_b ^ 0 ^ 0
            if False else b ^ old_b ^ old_a, d_b ^ old_b)


def inverse_xorshift_state(s):
    b, c, d, v = s
    t = v ^ d ^ (d >> 19)
    t ^= t >> 8
    t ^= t >> 16
    old_a = t
    old_a ^= (old_a << 11) & MASK
    old_a ^= (old_a << 22) & MASK
    return (old_a, b, c, d)


for forward, backward in ((next_xoshiro, inverse_xoshiro_state),
                          (next_xorshift, inverse_xorshift_state)):
    current = seed
    for _ in range(17):
        _, advanced = forward(current)
        assert backward(advanced) == current
        current = advanced

root = Path(__file__).resolve().parents[2] / "resources"
route = json.loads((root / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((root / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
later_request = next(r["payload"] for r in records
                     if r["job"] == "0417" and r["state"] == "REQUESTED"
                     and "18:03:00" in r["time"])


def pack_order(output, endian, order):
    physical = [None] * 4
    for i, source_pos in enumerate(order):
        physical[source_pos] = output[i].to_bytes(4, endian)
    return b"".join(physical)


attempts = 0
hits = []
for family in ("xoshiro128**", "xorshift128"):
    forward = next_xoshiro if family == "xoshiro128**" else next_xorshift
    backward = inverse_xoshiro_state if family == "xoshiro128**" \
        else inverse_xorshift_state
    for endian in ("big", "little"):
        for order in permutations(range(4)):
            observed = words(later_request, endian, order)
            if family == "xoshiro128**":
                state = invert_xoshiro(observed)  # before 18:03 block
            else:
                state = tuple(observed)           # after 18:03 block
                for _ in range(4):
                    state = backward(state)
            for gap in range(129):
                earlier = state
                for _ in range(4):
                    earlier = backward(earlier)
                coupon_words = generate(earlier, forward, 4)
                coupon = pack_order(coupon_words, endian, order)
                component = bytes(a ^ b for a, b in zip(coupon, mask))
                attempts += 1
                if hashlib.sha256(component).digest() == target:
                    hits.append((family, endian, order, gap,
                                 component.hex().upper()))
                state = backward(state)
print("reverse-only candidate tests", attempts, "original K04 matches", hits)
assert attempts == 12384
