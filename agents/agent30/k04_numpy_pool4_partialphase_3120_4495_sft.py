"""Source-gated complete NumPy pool4 K04 search from output offset3120 to4495 inclusive.

Partial-word lane inversion enumerates only the unknown bits of the best
source-fixed initialized state word per independent pool lane, then filters
against every other source-fixed bit in that lane. The selected ACK2 copy is
never a source observation. Each model must reproduce all 132 intact packets.
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
from k04_numpy_pool4_partialword_inversion_sft import (
    SOURCE_SHA, MASK, COMMITMENT, mt, source_states,
    inverse_lane, raw_output, initial_key, packets, coupon, LIMIT,
)


def scan(shard: int, shards: int = 32,
         start: int = 3120, end: int = 4496) -> None:
    assert 0 <= shard < shards
    lo = start + (end-start)*shard//shards
    hi = start + (end-start)*(shard+1)//shards
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    observed = [bytes.fromhex(b.decode())
                for b in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(observed) == len(mt.STARTS) == 133

    true_seed = (1 << 127) | 0xDEADBEEF
    true_pool = tuple(int(v) for v in np.random.SeedSequence(true_seed).pool)
    stream = [int(v) for v in np.random.MT19937(true_seed).random_raw(
        1 + lo + max(mt.STARTS) + 4)]
    control = source_states(lo, packets(stream, lo))
    rank_lane = max(range(4), key=lambda l:
                    max((m.bit_count() for i, (m, v) in enumerate(control)
                         if i > 0 and i % 4 == l), default=0))
    missing, found = inverse_lane(control, rank_lane)
    if missing <= LIMIT:
        assert true_pool[rank_lane] in found
    print("PLANTED_PARTIAL_WORD_CONTROL", shard, lo, rank_lane,
          "unknown_bits", missing, "candidate_count", len(found), flush=True)

    started = time.perf_counter()
    s0_wrong = contradicted = insufficient = all_lanes = actual_sources = 0
    full_pool_models = 0
    authentic = []
    for k in range(lo,hi):
        state = source_states(k, observed)
        if ((state[0][1] ^ 0x80000000) & state[0][0]) != 0:
            s0_wrong += 1
            continue
        rank = sorted(range(4),key=lambda lane:
                      max((m.bit_count() for i,(m,v) in enumerate(state)
                           if i > 0 and i % 4 == lane), default=0),
                      reverse=True)
        lane_options = {}
        broken = unresolved = False
        for lane in rank:
            missing, values = inverse_lane(state, lane)
            if missing > LIMIT:
                unresolved = True
                break
            if not values:
                broken = True
                break
            lane_options[lane] = values
        if broken:
            contradicted += 1
            continue
        if unresolved:
            insufficient += 1
            continue
        all_lanes += 1
        combos = 1
        for p in lane_options.values():
            combos *= len(p)
        if combos > 65536:
            insufficient += 1
            continue
        full_pool_models += combos
        for pool in product(*(lane_options[j] for j in range(4))):
            outputs = raw_output(initial_key(pool), 1 + k + max(mt.STARTS) + 4)
            data = packets(outputs,k)
            if any(data[j] != observed[j] for j in range(133) if j != 129):
                continue
            actual_sources += 1
            c = coupon(outputs, k)
            comp = bytes(a ^ b for a,b in zip(c, MASK))
            if hashlib.sha256(comp).digest() == COMMITMENT:
                authentic.append((k, pool, c.hex().upper(), comp.hex().upper()))
                print("AUTHENTIC_K04",authentic[-1],flush=True)
    assert hi-lo == s0_wrong + contradicted + insufficient + all_lanes
    print("SHARD_RESULT", shard, lo, hi,
          "S0_violations", s0_wrong, "pool_lane_contradictions", contradicted,
          "insufficient_or_many_models", insufficient,
          "all_lanes_seeded", all_lanes, "fully_constructed_pools", full_pool_models,
          "source_132_packet_matches", actual_sources, "K04_hits", authentic,
          "elapsed_seconds", round(time.perf_counter()-started,2),flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("expected shard ID 0..31")
    scan(int(sys.argv[1]))
