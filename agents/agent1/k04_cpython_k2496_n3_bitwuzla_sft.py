"""K04 independently source-derived CPython k2496 n3 Bitwuzla trial.

Only the 132 selected-withheld original printer packets constrain keys.
Requires full original 132/132 exact historical predictions before a K04
candidate can reach the unmodified commitment.
"""
from __future__ import annotations

import hashlib
import random
import sys
from pathlib import Path

from bitwuzla import Result

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent1"))
from k04_cpython_initarray_wrap_sft import direct_initialized, U
from k04_cpython_k2496_shortforward_source_sft import (
    original_source, synthetic_controls, mt, OFFSET,
)
from k04_cpython_k2496_shortforward_smt import model_source
from k04_cpython_k2496_n2_bitwuzla_sft import parse_solver, original_packets

MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET4 = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
RUNTIME_SECONDS = 12 * 60


def get_keys(parser):
    engine = parser.bitwuzla()
    return [
        int(engine.get_value(parser.parse_term(f"k{i}")).value(16), 16)
        for i in range(3)
    ]


def validated_packets(keys, packets):
    seed = sum(k << (32*i) for i, k in enumerate(keys))
    rng = random.Random(seed)
    stream = [rng.getrandbits(32)
              for _ in range(OFFSET + max(mt.STARTS) + 4)]
    predicted = [
        b"".join(stream[OFFSET+stage+j].to_bytes(4, "little")
                 for j in range(4))
        for stage in mt.STARTS
    ]
    matched = sum(predicted[i] == packets[i]
                  for i in range(133) if i != 129)
    return matched, predicted[129]


def main():
    synthetic_controls()
    masks = original_source()
    keys = [0x12345678, 0x1535AF52, 0x1847082C]
    _, _, state = direct_initialized(keys)
    planted = [(mask, state[i] & mask) for i, (mask, _) in enumerate(masks)]
    planted_smt = model_source(
        3, 41, planted, state[6], state[7],
        frozen_keys=keys, timeout_ms=10000,
    )
    positive = parse_solver(planted_smt, 10)
    assertion = positive.bitwuzla().check_sat()
    assert assertion == Result.SAT, ("n3 planted CPython source", assertion)
    assert get_keys(positive) == keys
    print("N3_GENUINE_CPYTHON_BITWUZLA_SEEDED_SOURCE_PASS", flush=True)

    original_smt = model_source(3, 41, masks,
                                masks[6][1], masks[7][1],
                                timeout_ms=RUNTIME_SECONDS*1000)
    print("ORIGINAL_N3_S41_QFBV_SHA256",
          hashlib.sha256(original_smt.encode()).hexdigest(), flush=True)
    parser = parse_solver(original_smt, RUNTIME_SECONDS)
    solver = parser.bitwuzla()
    packets = original_packets()
    for attempt in range(8):
        result = solver.check_sat()
        print("ORIGINAL_N3_K2496_STATUS", result, "try", attempt, flush=True)
        if result == Result.UNSAT:
            print("ORIGINAL_N3_K2496_FULL_SOURCE_IMPOSSIBLE", flush=True)
            return
        if result == Result.UNKNOWN:
            print("ORIGINAL_N3_K2496_UNDECIDED", flush=True)
            return
        assert result == Result.SAT
        keys = get_keys(parser)
        matched, coupon = validated_packets(keys, packets)
        print("N3_KEYS", [f"{x:08X}" for x in keys],
              "ORIGINAL_MATCHED", f"{matched}/132", flush=True)
        if matched == 132:
            component = bytes(x ^ y for x,y in zip(coupon, MASK))
            accepted = hashlib.sha256(component).hexdigest() == TARGET4
            print("ORIGINAL_K04_COMMITMENT_PASS", accepted, flush=True)
            if accepted:
                print("RECOVERED_K04_COMPONENT", component.hex().upper(), flush=True)
            return
        blocker = "(assert (or " + " ".join(
            f"(distinct k{i} #x{keys[i]:08X})" for i in range(3)
        ) + "))"
        parser.parse(blocker, parse_only=True, parse_file=False)
    print("ORIGINAL_N3_REMAINING_SEEDS_UNRESOLVED", flush=True)


if __name__ == "__main__":
    main()
