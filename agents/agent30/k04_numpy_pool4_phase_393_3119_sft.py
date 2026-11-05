"""Finite source-only NumPy SeedSequence pool4 full-coupon search for printer startup phases 393..3119.
All 132 intact original packets required for any purported K04 reconstruction.
"""
from __future__ import annotations
from itertools import product
from pathlib import Path
import hashlib
import re
import sys
import time

import numpy as np

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] / "resources"
sys.path.insert(0, str(HERE.parents[1] / "agent30"))
from k04_numpy_pool4_long_startup_sft import (
    SOURCE_SHA, MASK, COMMITMENT, mt, source_states, pool_options,
    initial_key, raw_output, packets, coupon,
)


def explore(shard: int, total_shards: int = 32,
            start: int = 393, end: int = 3120) -> None:
    assert 0 <= shard < total_shards
    lo = start + (end - start) * shard // total_shards
    hi = start + (end - start) * (shard + 1) // total_shards
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    observed = [bytes.fromhex(b.decode())
                for b in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(observed) == len(mt.STARTS) == 133

    # Nontrivial real NumPy four-pool seeded positive, using the identical complete spool layout.
    seed = (1 << 127) | 0xDEADBEEF
    true_pool = tuple(int(x) for x in np.random.SeedSequence(seed).pool)
    emitted = [int(x) for x in np.random.MT19937(seed).random_raw(
        1 + lo + max(mt.STARTS) + 4)]
    synthetic_packets = packets(emitted, lo)
    true_state = source_states(lo, synthetic_packets)
    assert all(true_pool[k] in values
               for k, values in pool_options(true_state).items())
    assert len(pool_options(true_state)) == 4
    assert (true_state[0][1] ^ 0x80000000) & true_state[0][0] == 0

    s0_bad = no_pool = insufficient_lanes = pools_constructed = full_sources = 0
    target_hits = []
    begin = time.perf_counter()
    for k in range(lo, hi):
        state = source_states(k, observed)
        if (state[0][1] ^ 0x80000000) & state[0][0]:
            s0_bad += 1
            continue
        opts = pool_options(state)
        if any(not v for v in opts.values()):
            no_pool += 1
            continue
        if len(opts) < 4:
            insufficient_lanes += 1
            continue
        for pool in product(*(sorted(opts[j]) for j in range(4))):
            pools_constructed += 1
            outputs = raw_output(initial_key(pool), 1 + k + max(mt.STARTS) + 4)
            predicted = packets(outputs, k)
            if all(predicted[i] == observed[i] for i in range(133) if i != 129):
                full_sources += 1
                c = coupon(outputs, k)
                value = bytes(x ^ y for x, y in zip(c, MASK))
                if hashlib.sha256(value).digest() == COMMITMENT:
                    target_hits.append((k, pool, c.hex().upper(), value.hex().upper()))
                    print("AUTHENTIC_K04_FOUND", target_hits[-1], flush=True)
        if (k - lo) % 32 == 0:
            print("SHARD_PROGRESS", shard, k, hi, round(time.perf_counter() - begin, 2),
                  flush=True)
    assert s0_bad + no_pool + insufficient_lanes + (hi - lo - s0_bad - no_pool - insufficient_lanes) == hi - lo
    print("SHARD_COMPLETE", shard, lo, hi, "S0_contradiction", s0_bad,
          "pool_contradiction", no_pool, "insufficient_lanes", insufficient_lanes,
          "fully_pooled_phases", hi - lo - s0_bad - no_pool - insufficient_lanes,
          "complete_models", pools_constructed, "132_packet_matches", full_sources,
          "K04_hits", target_hits, "elapsed_seconds", round(time.perf_counter() - begin, 2),
          flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Expected shard integer 0..31")
    explore(int(sys.argv[1]))
