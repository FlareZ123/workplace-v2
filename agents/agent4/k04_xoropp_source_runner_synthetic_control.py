#!/usr/bin/env python3
"""Independent synthetic-only end-to-end control of Agent4's LOCAL original-source runner.

Tests exact erased y2/y3 reconstruction and XOR-mask/SHA256 commitment across
all four fixed packet serializers with zero or one unobserved intervening
packet before the later y4/y5 or y6/y7 holdout. Produces no real source data.
The planted sparse-anchor bucket is 0 for fast CI-safe regression, NOT a
zero-witness exhaustive-search performance demonstration.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent4.k04_xoropp_zero_witness_source_local import branch_job, pack, unpack
from agents.agent4.k04_xoropp_zero_witness_synthetic import POSITIONS
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import stream

def run() -> None:
    rng = random.Random(20261128 ^ 1741)
    banned = sum(1 << p for p in POSITIONS)
    a = rng.getrandbits(64) & (~banned & ((1 << 64) - 1))
    b = rng.getrandbits(64)
    ys = stream(a, b, 8)
    synthetic_mask = rng.randbytes(16)
    passed = 0
    for extra in (0, 1):
        for endian in ('big', 'little'):
            for order in ('ab', 'ba'):
                first_bytes = pack(tuple(ys[:2]), endian, order)
                later_bytes = pack(tuple(ys[4 + 2 * extra:6 + 2 * extra]), endian, order)
                first = unpack(first_bytes, endian, order)
                later = unpack(later_bytes, endian, order)
                assert first == tuple(ys[:2])
                assert later == tuple(ys[4 + 2 * extra:6 + 2 * extra])
                status, valid, middle = branch_job((0, first, later, 12000, extra))
                assert status == 'sat' and valid and middle == tuple(ys[2:4]), (
                    extra, endian, order, status, valid
                )
                predicted = pack(middle, endian, order)
                correct = pack(tuple(ys[2:4]), endian, order)
                candidate = bytes(x ^ m for x, m in zip(predicted, synthetic_mask))
                commitment = hashlib.sha256(
                    bytes(x ^ m for x, m in zip(correct, synthetic_mask))
                ).hexdigest()
                assert hashlib.sha256(candidate).hexdigest() == commitment
                passed += 1
    assert passed == 8
    print({'synthetic_source_presentation_and_gap_controls': '8/8 PASS',
           'external_state_bits': 0,
           'true_bucket_only_for_test_speed': True,
           'historical_source_used': False,
           'actual_coupon_claimed': False})

if __name__ == '__main__':
    run()
