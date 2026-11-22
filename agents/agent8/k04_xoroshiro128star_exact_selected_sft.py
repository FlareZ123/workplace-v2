#!/usr/bin/env python3
"""Exact 128-bit xoroshiro128* two-output original K04 producer screen.

Tests a *specified* multiplier-only 64-bit scrambler on both published
xoroshiro128 state-transition choices. This is exploratory, not historically
identified printer firmware. The copied selected ACK2 is never used.
Depends on nearby Agent8 two-anchor source/parser/state-transition module.
"""
import argparse
import hashlib
import json
import random
from pathlib import Path

from k04_xoroshiro128plus_summed_twoanchor_sft import (
    M64, step, backward, source, decode, encode
)

SCRAMBLER = 0x9E3779B97F4A7C13
INVERSE = pow(SCRAMBLER, -1, 1 << 64)


def rol(value, shift):
    return ((value << shift) | (value >> (64 - shift))) & M64


def output(state):
    return state[0] * SCRAMBLER & M64


def inverse_pair(words, recurrence):
    L, B, R = recurrence
    a = words[0] * INVERSE & M64
    next_a = words[1] * INVERSE & M64
    value = next_a ^ rol(a, L)
    v = value
    for _ in range(64 // B + 2):
        v = value ^ ((v << B) & M64)
    state = a, a ^ v
    assert output(state) == words[0]
    assert output(step(state, L, B, R)[1]) == words[1]
    return state


def generate(state, recurrence, count, reverse_time):
    for _ in range(count):
        if reverse_time:
            state = backward(state, *recurrence)
        emitted = output(state)
        yield emitted
        if not reverse_time:
            _, state = step(state, *recurrence)


def controls(mask):
    for recurrence in ((55, 14, 36), (24, 16, 37)):
        random_generator = random.Random(0x17 + recurrence[0])
        for _ in range(10000):
            seed = (random_generator.getrandbits(64),
                    random_generator.getrandbits(64))
            _, after = step(seed, *recurrence)
            words = [output(seed), output(after)]
            assert inverse_pair(words, recurrence) == seed
            assert backward(after, *recurrence) == seed
        seed = (0x123456789ABCDEF0, 0xFEDCBA9876543210)
        words = list(generate(seed, recurrence, 20, False))
        assert inverse_pair(words[:2], recurrence) == seed
        known = encode(words[10:12], "big", False)
        target = hashlib.sha256(bytes(a ^ b for a, b in zip(known, mask))).digest()
        original_like_hits = []
        for i in range(2, 19):
            coupon = encode(words[i:i+2], "big", False)
            digest = hashlib.sha256(bytes(a ^ b for a, b in zip(coupon, mask))).digest()
            if digest == target:
                original_like_hits.append(i)
        assert original_like_hits == [10]
        print(json.dumps({"synthetic": recurrence,
                          "exact_source_inverse": "PASS",
                          "reverse_roundtrips": 10000,
                          "planted_masked_coupon_SHA256": "PASS"}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resources", type=Path,
                        default=Path(__file__).resolve().parents[2] / "resources")
    parser.add_argument("--windows", type=int, default=65536)
    args = parser.parse_args()
    assert args.windows >= 4
    packets, mask, commitment = source(args.resources)
    controls(mask)
    summary = {"complete_K04_assignments": 0,
               "official_K04_hits": [],
               "opposite_whole_request_matches": 0}
    for recurrence in ((55, 14, 36), (24, 16, 37)):
        for anchor in (0, 1):
            reverse_time = anchor == 1
            for endian in ("little", "big"):
                for reversed_words in (False, True):
                    observed = decode(packets[anchor], endian, reversed_words)
                    other = decode(packets[1 - anchor], endian, reversed_words)
                    state = inverse_pair(observed, recurrence)
                    produced = list(generate(state, recurrence,
                                             args.windows, reverse_time))
                    row = {
                        "recurrence": recurrence,
                        "anchor_attempt": (1, 3)[anchor],
                        "reverse_time": reverse_time,
                        "endian": endian,
                        "reverse_words": reversed_words,
                        "complete_K04_assignments": 0,
                        "official_K04_hits": [],
                        "opposite_whole_request_matches": [],
                    }
                    start = 0 if reverse_time else 2
                    for pos in range(start, args.windows - 1):
                        words = produced[pos:pos+2]
                        if reverse_time:
                            words = words[::-1]
                        if words == other:
                            row["opposite_whole_request_matches"].append(pos)
                        coupon = encode(words, endian, reversed_words)
                        candidate = bytes(a ^ b for a, b in zip(coupon, mask))
                        if hashlib.sha256(candidate).hexdigest() == commitment:
                            row["official_K04_hits"].append({
                                "position": pos,
                                "coupon": coupon.hex().upper(),
                                "component": candidate.hex().upper()})
                        row["complete_K04_assignments"] += 1
                    summary["complete_K04_assignments"] += row["complete_K04_assignments"]
                    summary["official_K04_hits"] += row["official_K04_hits"]
                    summary["opposite_whole_request_matches"] += len(
                        row["opposite_whole_request_matches"])
                    print(json.dumps({"historical": row}, sort_keys=True), flush=True)
    print(json.dumps({"summary": summary}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
