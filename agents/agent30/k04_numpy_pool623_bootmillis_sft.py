"""K04 NumPy pool623 startup-millisecond seed crack around first printer job 07:00 UTC.

Test all 64-bit Unix epoch-millisecond seeds within 15 minutes on either side
of the historical first intact printer job. Filter by original fully source-fixed
NumPy initialized-state word2 pool value, then require all 132 intact packets
before testing full selected-coupon mask and original K04 commitment.
"""
from __future__ import annotations
from datetime import datetime,timezone,timedelta
from pathlib import Path
import hashlib
import re
import sys
import time
import numpy as np

HERE=Path(__file__).resolve()
ROOT=HERE.parents[2]/"resources"
sys.path.insert(0,str(HERE.parent))
from k04_numpy_pool623_epochseed_sft import (
    inverse,mt,source_states,packets,coupon,SOURCE_SHA,MASK,COMMITMENT,
)
U=0xffffffff
SHARDS=32
CENTER=int(datetime(2026,10,3,7,0,0,tzinfo=timezone.utc).timestamp()*1000)
START=CENTER-900000
END=CENTER+900000


def run(shard:int):
    assert 0<=shard<SHARDS
    lo=START+(END-START)*shard//SHARDS
    hi=START+(END-START)*(shard+1)//SHARDS
    raw=(ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    observed=[bytes.fromhex(v.decode()) for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)]
    assert len(observed)==len(mt.STARTS)==133
    states=source_states(0,observed)
    assert states[2]==(U,0xE32E1557)
    pool_target=inverse(states[2][1],2)

    synthetic_seed=lo+123
    seeded=np.random.SeedSequence(synthetic_seed,pool_size=623)
    good_pool=int(seeded.pool[2])
    rng=np.random.MT19937(seeded)
    stream=[int(v) for v in rng.random_raw(max(mt.STARTS)+5)]
    fixture=source_states(0,packets(stream,0))
    assert fixture[2][0]==U and inverse(fixture[2][1],2)==good_pool
    print("PLANTED_MILLISECOND_NUMPY_POOL623_PASS",shard,synthetic_seed,
          hex(good_pool),flush=True)

    start=time.perf_counter()
    firsthits=fullsource=original_hits=0
    for seed in range(lo,hi):
        sq=np.random.SeedSequence(seed,pool_size=623)
        if int(sq.pool[2])!=pool_target:
            continue
        firsthits+=1
        outputs=[int(v) for v in np.random.MT19937(sq).random_raw(max(mt.STARTS)+5)]
        candidate=packets(outputs,0)
        if any(candidate[i]!=observed[i] for i in range(133) if i!=129):
            continue
        fullsource+=1
        c=coupon(outputs,0)
        component=bytes(a^b for a,b in zip(c,MASK))
        if hashlib.sha256(component).digest()==COMMITMENT:
            original_hits+=1
            print("ORIGINAL_K04_RECOVERED",seed,c.hex().upper(),
                  component.hex().upper(),flush=True)
    print("BOOTMILLIS_SHARD_COMPLETE",shard,lo,hi,"tested",hi-lo,
          "pool2_hits",firsthits,"full132_source_hits",fullsource,
          "K04_hits",original_hits,"elapsed_s",round(time.perf_counter()-start,2),
          flush=True)


if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Expected shard 0..31")
    run(int(sys.argv[1]))
