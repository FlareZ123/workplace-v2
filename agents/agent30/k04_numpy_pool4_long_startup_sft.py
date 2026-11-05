"""K04 source-constrained NumPy MT19937 default SeedSequence pool4 recovery at later startup phases.

This is a distinct post-initial-cycle producer hypothesis. It predicts complete selected
coupons only after reproducing all 132 historical intact source packets. The dubious
selected ACK2 copy is never used in the producer fit.
"""
from __future__ import annotations
from itertools import product
from pathlib import Path
import hashlib
import random
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "resources"
AGENTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTS / "agent28"))
sys.path.insert(0, str(AGENTS / "agent33"))
from k04_cpython_real_output_offset_sft import source_states, mt
from k04_numpy_seedseq_pool_inversion import constants, initial_key, raw_output

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
COMMITMENT = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
U = 0xFFFFFFFF


def pool_options(states: list[tuple[int, int]]) -> dict[int, set[int]]:
    options: dict[int, set[int]] = {}
    for i, (mask, value) in enumerate(states):
        if i == 0 or mask.bit_count() < 31:
            continue
        vals = [value] if mask == U else [value, value | ((~mask) & U)]
        before, mul = constants(i)
        inv = pow(mul, -1, 1 << 32)
        possibility = {(((v ^ (v >> 16)) * inv) & U) ^ before for v in vals}
        lane = i % 4
        if lane not in options:
            options[lane] = possibility
        else:
            options[lane].intersection_update(possibility)
    return options


def packets(outputs: list[int], offset: int) -> list[bytes]:
    return [b"".join(outputs[1 + offset + start + j].to_bytes(4, "little")
                    for j in range(4)) for start in mt.STARTS]


def coupon(outputs: list[int], offset: int) -> bytes:
    p = mt.STARTS[129]
    return b"".join(outputs[1 + offset + p + j].to_bytes(4, "little")
                    for j in range(4))


def run(offset: int) -> None:
    assert offset >= 624
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    observed = [bytes.fromhex(w.decode()) for w in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(observed) == len(mt.STARTS) == 133

    seed = (1 << 127) | 0xDEADBEEF
    true_pool = tuple(int(x) for x in np.random.SeedSequence(seed).pool)
    true_key = np.random.MT19937(seed).state["state"]["key"].copy()
    assert np.array_equal(initial_key(true_pool), true_key)
    emitted = [int(x) for x in np.random.MT19937(seed).random_raw(
        1 + offset + max(mt.STARTS) + 4)]
    assert emitted == raw_output(initial_key(true_pool), len(emitted))
    genuine_packets = packets(emitted, offset)
    predicted = source_states(offset, genuine_packets)
    synthetic_options = pool_options(predicted)
    assert all(true_pool[lane] in vals for lane, vals in synthetic_options.items())
    assert all(vals for vals in synthetic_options.values())
    if len(synthetic_options) == 4:
        combinations = list(product(*(sorted(synthetic_options[i]) for i in range(4))))
        assert true_pool in combinations
        assert any(packets(raw_output(initial_key(p), len(emitted)), offset)[0] ==
                   genuine_packets[0] for p in combinations)
    planted = coupon(emitted, offset)
    planted_key = bytes(c ^ m for c, m in zip(planted, MASK))
    assert hashlib.sha256(planted_key).digest() == hashlib.sha256(
        bytes(c ^ m for c, m in zip(coupon(raw_output(initial_key(true_pool), len(emitted)), offset), MASK))
    ).digest()
    print("PLANTED_POOL_POSITIVE", offset, "pool", true_pool,
          "observed_lanes", {k: len(v) for k, v in synthetic_options.items()},
          flush=True)

    original_state = source_states(offset, observed)
    options = pool_options(original_state)
    print("ORIGINAL_POOL_LANE_DOMAINS", offset,
          {k: len(v) for k, v in options.items()}, flush=True)
    if len(options) < 4 or any(not vals for vals in options.values()):
        print("NO_COMPLETE_POOL_FIT", offset, "source_overdetermined",
              any(not vals for vals in options.values()), flush=True)
        return

    all_pools = product(*(sorted(options[i]) for i in range(4)))
    full_matches = 0
    target_matches = []
    complete_attempts = 0
    for p in all_pools:
        complete_attempts += 1
        outputs = raw_output(initial_key(p), len(emitted))
        predicted_packets = packets(outputs, offset)
        matched = sum(a == b for i, (a, b) in enumerate(zip(observed, predicted_packets))
                      if i != 129)
        if matched != 132:
            continue
        full_matches += 1
        selected_coupon = coupon(outputs, offset)
        component = bytes(c ^ m for c, m in zip(selected_coupon, MASK))
        if hashlib.sha256(component).digest() == COMMITMENT:
            target_matches.append((p, selected_coupon.hex().upper(), component.hex().upper()))
    print("ORIGINAL_COMPLETE_POOL_MODELS", offset, "attempts", complete_attempts,
          "source_132_of_132", full_matches, "authentic_K04", target_matches, flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("provide output startup offset >=624")
    run(int(sys.argv[1]))
