#!/usr/bin/env python3
"""Test NumPy/MT19937 low-bit randbelow(3) semantics on source-compatible K04 chronologies.

This is a distinct API hypothesis from CPython getrandbits(2): NumPy's legacy
MT19937 interval sampler uses a low-bit mask and rejects code 3 for a range of
three. The existing conditional-route evaluator is reused unchanged; only the
bit plane used to expose the sampler codes and the planted control are changed.
No K04 mask, commitment, or selected ACK2 payload is loaded by this experiment.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.agent50 import k04_conditional_route_sampler_sft as base


def low_two_domains(expressions, basis):
    """Allowed NumPy-style low-two-bit codes at each tempered MT output stage."""
    domains = []
    for bits in expressions:
        tempered = base.joint.chronology.tempered_bits(bits)
        lo = base.joint.mt.reduce_row(tempered[0] << 1, basis)
        hi = base.joint.mt.reduce_row(tempered[1] << 1, basis)
        lows = (lo,) if lo <= 1 else (0, 1)
        highs = (hi,) if hi <= 1 else (0, 1)
        domains.append({int(low) + 2 * int(high) for low in lows for high in highs})
    return domains


def sample_below3_lowbits(rng: random.Random):
    """NumPy RandomState-style mask/reject sampler, using the low two bits."""
    draws = 0
    while True:
        value = rng.getrandbits(32) & 3
        draws += 1
        if value < 3:
            return value, draws


def planted_positive_lowbits(order: str):
    """Full seeded MT control using low-bit metadata draws and hidden row 129."""
    for seed in range(1000, 11000):
        rng = random.Random(seed)
        starts, rows, labels = [], [], []
        route_codes_by_row = {}
        stage = 0
        class_to_name = {0: "LABEL", 1: "RECOVER", 2: "STORES"}
        dest_to_name = {0: "bench", 1: "desk", 2: "store"}
        for row in range(133):
            if row:
                if order == "class_route_dest":
                    cls, n = sample_below3_lowbits(rng); stage += n
                    route = None
                    if cls == 1:
                        route, n = sample_below3_lowbits(rng); stage += n
                    dest, n = sample_below3_lowbits(rng); stage += n
                elif order == "class_dest_route":
                    cls, n = sample_below3_lowbits(rng); stage += n
                    dest, n = sample_below3_lowbits(rng); stage += n
                    route = None
                    if cls == 1:
                        route, n = sample_below3_lowbits(rng); stage += n
                elif order == "dest_class_route":
                    dest, n = sample_below3_lowbits(rng); stage += n
                    cls, n = sample_below3_lowbits(rng); stage += n
                    route = None
                    if cls == 1:
                        route, n = sample_below3_lowbits(rng); stage += n
                else:
                    raise AssertionError(order)
                labels.append((class_to_name[cls], dest_to_name[dest]))
                if route is not None:
                    route_codes_by_row[row] = route
            else:
                labels.append(("LABEL", "bench"))
            starts.append(stage)
            if row == 129:
                for _ in range(4):
                    rng.getrandbits(32)  # consume, but do not expose target words
                rows.append([])
            else:
                rows.append([base.mt.untemper(rng.getrandbits(32)) for _ in range(4)])
            stage += 4

        late_codes = [route_codes_by_row.get(row) for row in (129, 131, 132)]
        if None in late_codes or len(set(late_codes)) != 3:
            continue
        if set(name for name, _ in labels[:128]) != set(base.CLASS_NAMES):
            continue
        if set(name for _, name in labels[:128]) != set(base.DEST_NAMES):
            continue
        code_to_route = dict(zip(late_codes, base.ROUTE_NAMES))
        route_by_row = {
            row: code_to_route[code]
            for row, code in route_codes_by_row.items()
            if row in (129, 131, 132)
        }
        expressions = base.mt.state_expressions(stage + 3)
        basis = base.six.build_source_basis(expressions, rows, starts)
        domains = low_two_domains(expressions, basis)
        result = base.evaluate(
            starts, domains, labels, route_by_row, keep_all_examples=True
        )
        assert result["best_training_mismatches"] == 0, (order, result)
        assert result["zero_training_models"] > 0, (order, result)
        assert result["zero_holdout_models"] > 0, (order, result)
        assert result["route_codebook_survivors"] > 0, (order, result)
        planted_route_codes = tuple(
            {value: key for key, value in code_to_route.items()}[name]
            for name in base.ROUTE_NAMES
        )
        assert any(
            item["order"] == order
            and item["binding"] == "next"
            and item["at_first"] is True
            and item["class_codes"] == (0, 1, 2)
            and item["dest_codes"] == (0, 1, 2)
            and item["route_codes"] == planted_route_codes
            for item in result["examples"]
        ), (order, result["examples"])
        print(
            "PLANTED_LOWBIT_CONDITIONAL_ROUTE_POSITIVE",
            order, "PASS", "seed", seed, "native_draws", stage,
            "route_rows", route_by_row, flush=True,
        )
        return
    raise AssertionError(f"no low-bit seeded positive with distinct late route codes for {order}")


def main():
    base.joint.top_two_domains = low_two_domains
    base.planted_positive = planted_positive_lowbits
    print("MODEL_VARIANT", "MT19937 low-two-bit mask/reject randbelow(3)")
    base.main()


if __name__ == "__main__":
    main()
