"""K04 event-matched retry inverse over GF(2^128) and four GF(2^32) lanes.

Source 0420: STORES ACK1 -> RECOVER ACK2, a genuine two-attempt pair.
Source 0417: RECOVER REQUESTED1 -> [missing RECOVER ACK2] -> REQUESTED3.
Assume one shared affine attempt law Y=g*X XOR h over a finite field.
Eliminate g,h to form a quadratic and recover all possible missing X1.
The original copied ACK2 payload is excluded from all model inputs.
"""
import hashlib
import itertools
import json
import random
from pathlib import Path

from k04_gf128_secondorder_middle_sft import (
    inverse as inv128, mul as mul128, roots as roots128,
    viewed, unviewed,
)
from k04_gf32_reverse_late_packet_sft import field as field32

ROOT = Path(__file__).resolve().parents[2] / "resources"
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def original_inputs():
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    rows = [x for x in raw.decode("ascii").splitlines() if "PAYLOAD=" in x]
    assert len(rows) == 133
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in rows[129]

    def packet(marker):
        matches = [s for s in rows if marker in s]
        assert len(matches) == 1, marker
        return int(matches[0].split("PAYLOAD=")[1].split()[0], 16)

    return (
        packet("JOB=PS-261003-0417 ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER"),
        packet("JOB=PS-261003-0417 ATTEMPT=3 STATE=REQUESTED CLASS=RECOVER"),
        packet("JOB=PS-261003-0420 ATTEMPT=1 STATE=ACK CLASS=STORES"),
        packet("JOB=PS-261003-0420 ATTEMPT=2 STATE=ACK CLASS=RECOVER"),
    )


def homogeneous_quadratic_inputs(a, c, x, y):
    # x -> y is one observed attempt; a -> ? -> c is another.
    # y = g*x XOR h; c = g*(g*a XOR h) XOR h.
    return a ^ x, y ^ x, y ^ c


def field128_candidate_roots(a, c, x, y):
    u, v, w = homogeneous_quadratic_inputs(a, c, x, y)
    options = []
    for g in roots128(u, v, w) or []:
        h = y ^ mul128(g, x)
        mid = mul128(g, a) ^ h
        assert mul128(g, x) ^ h == y
        assert mul128(g, mid) ^ h == c
        options.append((g, h, mid))
    return options


def root32(u, v, w, mul, inv):
    if u == 0:
        return [] if v == 0 and w else (
            None if v == 0 else [mul(w, inv(v))]
        )
    if v == 0:
        z = mul(w, inv(u))
        for _ in range(31):
            z = mul(z, z)
        return [z]
    q = mul(mul(u, w), inv(mul(v, v)))
    basis = {}
    for i in range(32):
        val, combo = mul(1 << i, 1 << i) ^ (1 << i), 1 << i
        while val:
            p = val.bit_length() - 1
            if p in basis:
                row, mask = basis[p]
                val ^= row
                combo ^= mask
            else:
                basis[p] = val, combo
                break
    val, combo = q, 0
    while val:
        p = val.bit_length() - 1
        if p not in basis:
            return []
        row, mask = basis[p]
        val ^= row
        combo ^= mask
    assert mul(combo, combo) ^ combo == q
    scale = mul(v, inv(u))
    return [mul(scale, combo), mul(scale, combo ^ 1)]


def field32_lane_solutions(a, c, x, y, poly):
    mul, inv = field32(poly)
    pa = [(a >> (32 * (3-i))) & 0xffffffff for i in range(4)]
    pc = [(c >> (32 * (3-i))) & 0xffffffff for i in range(4)]
    px = [(x >> (32 * (3-i))) & 0xffffffff for i in range(4)]
    py = [(y >> (32 * (3-i))) & 0xffffffff for i in range(4)]
    counts = []
    for j in range(4):
        u, v, w = homogeneous_quadratic_inputs(
            pa[j], pc[j], px[j], py[j]
        )
        counts.append(len(root32(u, v, w, mul, inv) or []))
    return counts


def synthetic_positive():
    rng = random.Random(0x20261103)
    correct = []
    for _ in range(3):
        g, h = rng.getrandbits(128), rng.getrandbits(128)
        a, x = rng.getrandbits(128), rng.getrandbits(128)
        mid = mul128(g, a) ^ h
        c = mul128(g, mid) ^ h
        y = mul128(g, x) ^ h
        options = field128_candidate_roots(a, c, x, y)
        assert (g, h, mid) in options
        changed = field128_candidate_roots(a, c ^ 1, x, y)
        assert mid not in [candidate[2] for candidate in changed]
        correct.append({"original_middle_recovered": True,
                        "wrong_later_attempt_rejected": True})
    return correct


def main():
    original = original_inputs()
    mask = int(json.loads(
        (ROOT / "evidence/recovery-routing.json").read_text()
    )["K04"]["masked_component"], 16)
    target = json.loads(
        (ROOT / "acceptance.json").read_text()
    )["slot_sha256"]["K04"]
    candidate_values = {}
    lane_models = []
    for flags in itertools.product((False, True), repeat=3):
        a, c, x, y = [viewed(word, *flags) for word in original]
        for g, h, mid in field128_candidate_roots(a, c, x, y):
            packet = unviewed(mid, *flags)
            K04 = packet ^ mask
            key = f"{K04:032X}"
            candidate_values[key] = {
                "serialization": list(flags),
                "K04": key,
                "original_sha_pass": hashlib.sha256(
                    K04.to_bytes(16, "big")
                ).hexdigest() == target,
            }
        for poly in (0x8d, 0x04c11db7):
            counts = field32_lane_solutions(a, c, x, y, poly)
            lane_models.append({
                "polynomial_low_bits": hex(poly),
                "serialization": list(flags),
                "lane_solution_counts": counts,
                "whole_coupon_solution_exists": all(counts),
            })
    assert len(candidate_values) == 12
    assert all(not v["original_sha_pass"] for v in candidate_values.values())
    assert len(lane_models) == 16
    assert all(not x["whole_coupon_solution_exists"] for x in lane_models)
    print(json.dumps({
        "source_SHA256": PIN,
        "disputed_ACK2_copied_bytes_decoded": False,
        "GF128_source_models": 8,
        "GF128_distinct_full_candidates": len(candidate_values),
        "authentic_K04_hits": 0,
        "GF32_four_lane_models": len(lane_models),
        "GF32_models_with_complete_source_consistency": 0,
        "genuine_synthetic_controls": synthetic_positive(),
        "example_full_K04": candidate_values[
            "A6EEFA024E6415CF76978B768C8E1CB7"
        ],
        "result": "NO_MATCH_EVENT_MATCHED_AFFINE_FIELD_RETRY",
    }, indent=2))


if __name__ == "__main__":
    main()
