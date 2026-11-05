"""Original K04: exhaust UTC 2-4 October 2026 epoch-second seeds for NumPy pool623.

Under the tested genuine p951 NumPy first-output producer, source-fixed S[2]
determines seed pool[2] exactly. This rejects almost all candidate timestamps
without constructing arbitrary coupons. Every full seed/pool hit must predict all
132 surviving printer packets before deriving and verifying a full masked K04.
Selected ACK2 copy is withheld from all producer inference.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import re
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]/"resources"
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent30"))
from k04_numpy_poolwidth_multilane_sft import (
    mt,source_states,constants,SOURCE_SHA,packets,
)
from k04_numpy_pool4_long_startup_sft import MASK,COMMITMENT,coupon

START=int(datetime(2026,10,2,tzinfo=timezone.utc).timestamp())
END=int(datetime(2026,10,5,tzinfo=timezone.utc).timestamp())
SHARDS=16
U=0xffffffff

def inverse(v:int, i:int)->int:
    before,m=constants(i)
    return (((v^(v>>16))*pow(m,-1,1<<32))&U)^before

def run(shard:int):
    assert 0<=shard<SHARDS
    lo=START+(END-START)*shard//SHARDS
    hi=START+(END-START)*(shard+1)//SHARDS
    raw=(ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    observed=[bytes.fromhex(v.decode()) for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)]
    assert len(observed)==len(mt.STARTS)==133
    state=source_states(0,observed)
    assert state[2]==(U,0xE32E1557)
    pool_target=inverse(state[2][1],2)

    # One planted genuine in-domain clock seed exercises the same source lane
    # inverse and whole-output producer, using independent NumPy implementation.
    planted_seed=lo+11
    true_seq=np.random.SeedSequence(planted_seed,pool_size=623)
    true_pool=tuple(int(v) for v in true_seq.pool)
    out=np.random.MT19937(true_seq).random_raw(max(mt.STARTS)+5)
    synthetic=packets([int(v) for v in out],0)
    st=source_states(0,synthetic)
    assert st[2][0]==U and inverse(st[2][1],2)==true_pool[2]
    assert synthetic[0] == packets([int(v) for v in out],0)[0]
    print("GENUINE_NUMPY_POOL623_CONTROL",shard,planted_seed,
          hex(true_pool[2]),flush=True)

    began=time.perf_counter()
    seed_matches=historical_sources=authentic=0
    for seed in range(lo,hi):
        seq=np.random.SeedSequence(seed,pool_size=623)
        if int(seq.pool[2])!=pool_target:
            continue
        seed_matches+=1
        raw_out=np.random.MT19937(seq).random_raw(max(mt.STARTS)+5)
        values=[int(v) for v in raw_out]
        src=packets(values,0)
        if any(src[i]!=observed[i] for i in range(133) if i!=129):
            continue
        historical_sources+=1
        c=coupon(values,0)
        component=bytes(a^b for a,b in zip(c,MASK))
        if hashlib.sha256(component).digest()==COMMITMENT:
            authentic+=1
            print("AUTHENTIC_K04_RECOVERY",seed,c.hex().upper(),
                  component.hex().upper(),flush=True)
    print("SOURCE_CLOCKSEED_RESULT",shard,"start",lo,"end",hi,
          "tested",hi-lo,"exact_pool2_hits",seed_matches,
          "complete_original_packet_matches",historical_sources,
          "original_K04_hits",authentic,
          "elapsed_s",round(time.perf_counter()-began,2),flush=True)


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Expected shard 0..15")
    run(int(sys.argv[1]))
