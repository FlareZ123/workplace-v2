"""REC8 cross-slot second-order finite-field recurrence with two intact holdouts.

Hypothesis: K[n] = A*K[n-1] XOR B*K[n-2] over the same binary field,
independently per 8/16/32/64/128-bit lane. Fit A,B with original K01,
K02, K03 and K05,K06,K07; reconstruct both K04 and K08; verify original
K05 and K06 as genuine whole-component holdouts. Validates original
six SHA256 slots and planted 8-slot recurrence streams.
Run from repository root:
python agents/agent48/rec8_crossslot_secondorder_sft.py
"""
import hashlib
import itertools
import json
import random
from pathlib import Path

from rec8_crossslot_rs_erasure_sft import (
    ACCEPT, FIELDS, KNOWN, field, view, unview,
)

KNOWN_BYTES = {i: bytes.fromhex(v) for i, v in KNOWN.items()}


def derive(source, n, low, endian, reverse_symbols, reflect_bits):
    mul, power, inv = field(n, low)
    v = {
        i: view(data, n, endian, reverse_symbols, reflect_bits)
        for i, data in source.items()
    }
    predictions = {4: [], 8: []}
    holdout_5 = True
    holdout_6 = True
    for j in range(128 // n):
        s1, s2, s3, s5, s6, s7 = [
            v[i][j] for i in (1, 2, 3, 5, 6, 7)
        ]
        determinant = mul(s2, s5) ^ mul(s1, s6)
        if determinant == 0:
            return None
        determinant_inv = inv(determinant)
        a = mul(mul(s3, s5) ^ mul(s1, s7), determinant_inv)
        b = mul(mul(s2, s7) ^ mul(s3, s6), determinant_inv)
        s4 = mul(a, s3) ^ mul(b, s2)
        s8 = mul(a, s7) ^ mul(b, s6)
        predictions[4].append(s4)
        predictions[8].append(s8)
        holdout_5 &= mul(a, s4) ^ mul(b, s3) == s5
        holdout_6 &= mul(a, s5) ^ mul(b, s4) == s6
    recovered = {
        i: unview(symbols, n, endian, reverse_symbols, reflect_bits)
        for i, symbols in predictions.items()
    }
    return recovered, (holdout_5, holdout_6)


def positive(n, low):
    mul, power, inv = field(n, low)
    rng = random.Random(0x20261103 + low + n)
    for _ in range(200):
        rows = {i: [] for i in range(1, 9)}
        for _ in range(128 // n):
            a, b = rng.getrandbits(n), rng.getrandbits(n)
            symbols = [rng.getrandbits(n), rng.getrandbits(n)]
            for i in range(2, 8):
                symbols.append(mul(a, symbols[-1]) ^ mul(b, symbols[-2]))
            for i, symbol in enumerate(symbols, start=1):
                rows[i].append(symbol)
        original = {i: unview(rows[i], n, "big", False, False)
                    for i in (1, 2, 3, 5, 6, 7)}
        result = derive(original, n, low, "big", False, False)
        if result is None:
            continue
        prediction, holdouts = result
        assert holdouts == (True, True)
        assert prediction[4] == unview(rows[4], n, "big", False, False)
        assert prediction[8] == unview(rows[8], n, "big", False, False)
        return True
    raise AssertionError("Could not choose nondegenerate planted source")


def main():
    assert all(
        hashlib.sha256(data).hexdigest() == (
            ACCEPT["slot_sha256"][f"K{i:02d}"]
        ) for i, data in KNOWN_BYTES.items()
    )
    evaluated = 0
    distinct = set()
    source_control_5 = source_control_6 = 0
    hits = {4: 0, 8: 0}
    positive_count = 0
    for n, low in FIELDS:
        assert positive(n, low)
        positive_count += 1
        endians = ("big", "little") if n > 8 else ("big",)
        for endian, reverse_symbols, reflect_bits in itertools.product(
            endians, (False, True), (False, True)
        ):
            result = derive(KNOWN_BYTES, n, low, endian,
                            reverse_symbols, reflect_bits)
            if result is None:
                continue
            predictions, controls = result
            evaluated += 1
            source_control_5 += controls[0]
            source_control_6 += controls[1]
            distinct.add((predictions[4], predictions[8]))
            for missing in (4, 8):
                hits[missing] += hashlib.sha256(
                    predictions[missing]
                ).hexdigest() == ACCEPT["slot_sha256"][f"K{missing:02d}"]
    assert evaluated == 64
    assert source_control_5 == source_control_6 == 0
    assert hits == {4: 0, 8: 0}
    assert positive_count == 9
    print(json.dumps({
        "original_known_SHA256_PASSES": 6,
        "binary_fields": len(FIELDS),
        "full_interpolation_models": evaluated,
        "distinct_full_K04_K08_pairs": len(distinct),
        "intact_K05_predictions_correct": source_control_5,
        "intact_K06_predictions_correct": source_control_6,
        "original_missing_slot_hits": hits,
        "true_generated_recurrence_controls": positive_count,
        "example_K04_K08": [
            "3CA5E43E1F64398062CD6A10D3A65ED8",
            "2D5DA0F928C41D2A2E9AD2561B7B9FC0",
        ],
        "result": "NO_MATCH_SOURCE_HELDOUT_REJECTS_SLOT_RECURRENCE",
    }, indent=2))


if __name__ == "__main__":
    main()
