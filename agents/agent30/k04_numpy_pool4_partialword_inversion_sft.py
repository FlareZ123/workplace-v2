"""Recover NumPy MT19937 SeedSequence pool lanes from partially fixed initialized words.

For every lane, invert the best source-known initialized state word over all its
unknown bits and screen against every other original source-fixed bit in that lane.
Positive controls use genuine independently seeded NumPy generators.
"""
from __future__ import annotations

from pathlib import Path
from itertools import product
import hashlib
import re
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "resources"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent30"))
from k04_numpy_pool4_long_startup_sft import (
    mt, source_states, SOURCE_SHA, MASK, COMMITMENT, initial_key, raw_output,
    packets, coupon, constants,
)
U = 0xFFFFFFFF
LIMIT = 20


def inverse_lane(states: list[tuple[int, int]], lane: int,
                 max_missing: int = LIMIT) -> tuple[int, list[int]]:
    known = [(i, mask, val) for i, (mask, val) in enumerate(states)
             if i > 0 and i % 4 == lane and mask]
    if not known:
        return 32, []
    known.sort(key=lambda a: (-a[1].bit_count(), a[0]))
    index, mask, value = known[0]
    unknown_positions = [1 << bit for bit in range(32) if not (mask >> bit) & 1]
    missing = len(unknown_positions)
    if missing > max_missing:
        return missing, []
    before, mult = constants(index)
    inverse = pow(mult, -1, 1 << 32)
    others = [(m, val, *constants(i)) for i, m, val in known[1:]]
    found = []
    native = value
    for t in range(1 << missing):
        if t:
            native ^= unknown_positions[(t & -t).bit_length() - 1]
        unhashed = native ^ (native >> 16)
        pool = ((unhashed * inverse) & U) ^ before
        good = True
        for other_mask, other_value, other_before, other_mult in others:
            v = ((pool ^ other_before) * other_mult) & U
            predicted = v ^ (v >> 16)
            if (predicted & other_mask) != other_value:
                good = False
                break
        if good:
            found.append(pool)
    return missing, found


def model_outcome(offset: int) -> None:
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    original = [bytes.fromhex(v.decode())
                for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(original) == len(mt.STARTS) == 133

    seed = (1 << 127) | 0xDEADBEEF
    true_pool = tuple(int(v) for v in np.random.SeedSequence(seed).pool)
    sample = [int(v) for v in np.random.MT19937(seed).random_raw(
        1 + offset + max(mt.STARTS) + 4)]
    reference = source_states(offset, packets(sample, offset))
    control = []
    for lane in range(4):
        missing, vals = inverse_lane(reference, lane)
        assert not vals or true_pool[lane] in vals
        control.append((missing, len(vals)))
    print("PLANTED_NUMPY_POOL_CONTROL", offset, true_pool, control, flush=True)

    states = source_states(offset, original)
    fixed_bits = sum(m.bit_count() for m, _ in states)
    possible_s0 = (states[0][1] ^ 0x80000000) & states[0][0] == 0
    out = [inverse_lane(states, lane) for lane in range(4)]
    counts = [(missing, len(v)) for missing, v in out]
    print("ORIGINAL_PARTIAL_POOL", offset, "source_fixed_bits", fixed_bits,
          "S0_possible", possible_s0, "lane_missingbits_and_options", counts,
          flush=True)
    if not possible_s0 or any(missing <= LIMIT and not values for missing, values in out):
        print("SOURCE_EXCLUDES_POOL4", offset, flush=True)
        return
    if any(missing > LIMIT for missing, values in out):
        print("SOME_LANES_NOT_RECOVERABLE", offset, flush=True)
        return
    total_models = 1
    for _, vals in out:
        total_models *= len(vals)
    print("SOURCE_POOL4_COMPLETE_CANDIDATES", offset, total_models, flush=True)
    if total_models > 65536:
        print("MODEL_CARTESIAN_UNRESOLVED", offset, flush=True)
        return
    full_matches = hits = 0
    for p in product(*(vals for _, vals in out)):
        outputs = raw_output(initial_key(p), 1 + offset + max(mt.STARTS) + 4)
        if not all(packets(outputs, offset)[i] == original[i]
                   for i in range(133) if i != 129):
            continue
        full_matches += 1
        c = coupon(outputs, offset)
        value = bytes(x ^ y for x, y in zip(c, MASK))
        if hashlib.sha256(value).digest() == COMMITMENT:
            hits += 1
            print("AUTHENTIC_K04", offset, c.hex().upper(), value.hex().upper(),
                  flush=True)
    print("SOURCE_MODEL_MATCHES", offset, full_matches, "K04_matches", hits,
          flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Provide one startup output offset")
    model_outcome(int(sys.argv[1]))
