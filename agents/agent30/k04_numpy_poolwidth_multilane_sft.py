"""Full K04 coupon reconstruction under NumPy SeedSequence nondefault pool widths.

An independent pool byte word feeds each initialized MT state word at index
modulo pool_size; test authentic intact printer packets before selected coupon.
"""
from __future__ import annotations

from itertools import product
from pathlib import Path
import hashlib
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "resources"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent30"))
from k04_numpy_pool4_long_startup_sft import (
    SOURCE_SHA, MASK, COMMITMENT, mt, source_states, constants,
    raw_output, packets, coupon,
)
U = 0xFFFFFFFF


def seeded_key(pool: tuple[int, ...]) -> np.ndarray:
    n = len(pool)
    state = np.empty(624, dtype=np.uint32)
    for i in range(624):
        before, mult = constants(i)
        value = ((pool[i % n] ^ before) * mult) & U
        state[i] = value ^ (value >> 16)
    state[0] = 0x80000000
    return state


def constrained_pool(states: list[tuple[int, int]], size: int) -> dict[int, set[int]]:
    found: dict[int, set[int]] = {}
    for i, (mask, value) in enumerate(states):
        if i == 0 or mask.bit_count() < 31:
            continue
        before, mul = constants(i)
        inv = pow(mul, -1, 1 << 32)
        choices = (value,) if mask == U else (value, value | (U ^ mask))
        vals = {(((v ^ (v >> 16)) * inv) & U) ^ before for v in choices}
        lane = i % size
        if lane not in found:
            found[lane] = vals
        else:
            found[lane].intersection_update(vals)
    return found


def experiment(phase: int, size: int) -> None:
    assert size in (4, 8, 16, 32)
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    observed = [bytes.fromhex(w.decode())
                for w in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(observed) == len(mt.STARTS) == 133

    seedseq = np.random.SeedSequence((1 << 127) | 0xDEADBEEF, pool_size=size)
    actual = np.random.MT19937(seedseq)
    true_pool = tuple(int(x) for x in seedseq.pool)
    assert np.array_equal(seeded_key(true_pool), actual.state["state"]["key"])
    outputs = [int(x) for x in actual.random_raw(1 + phase + max(mt.STARTS) + 4)]
    assert outputs == raw_output(seeded_key(true_pool), len(outputs))
    states = source_states(phase, packets(outputs, phase))
    synthetic = constrained_pool(states, size)
    assert all(true_pool[lane] in pool for lane, pool in synthetic.items())
    assert all(pool for pool in synthetic.values())
    print("PLANTED_POOL_CONTROL", phase, size, "anchored_lanes",
          len(synthetic), "lengths", [len(x) for x in synthetic.values()], flush=True)

    states = source_states(phase, observed)
    inferred = constrained_pool(states, size)
    zero = ((states[0][1] ^ 0x80000000) & states[0][0]) == 0
    print("ORIGINAL_POOL_WIDTH", phase, size, "S0_possible", zero,
          "anchored_lanes", len(inferred),
          "empty_lanes", [i for i,v in inferred.items() if not v],
          "pool_sets", {i:len(v) for i,v in inferred.items()}, flush=True)
    if not zero or any(not v for v in inferred.values()):
        print("ORIGINAL_MODEL_EXCLUDED", phase, size, flush=True)
        return
    if len(inferred) < size:
        print("ORIGINAL_MODEL_UNDETERMINED", phase, size, flush=True)
        return
    models = 0
    historical = 0
    hits = []
    for pool in product(*(sorted(inferred[i]) for i in range(size))):
        models += 1
        generated = raw_output(seeded_key(pool), len(outputs))
        candidate_packets = packets(generated, phase)
        if any(candidate_packets[i] != observed[i] for i in range(133) if i != 129):
            continue
        historical += 1
        selected_coupon = coupon(generated, phase)
        comp = bytes(x ^ y for x,y in zip(selected_coupon, MASK))
        if hashlib.sha256(comp).digest() == COMMITMENT:
            hits.append((selected_coupon.hex().upper(),comp.hex().upper()))
    print("COMPLETE_SEEDPOOL_PRODUCERS", phase, size, "pools", models,
          "full132matches", historical, "K04_hits", hits, flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: phase pool_size")
    experiment(int(sys.argv[1]), int(sys.argv[2]))
