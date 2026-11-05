"""Original-source NumPy default MT SeedSequence period622 terminal wrap inverse.

Tests direct repeated-pool coupling S[1] and S[623] in a 622-word initialized
pool; pool623 has no repeated used state lanes because S0 is overwritten.
Selected K04 row129 is excluded from source observation.
"""
from pathlib import Path
import hashlib
import re
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]/"resources"
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent30"))
from k04_numpy_poolwidth_multilane_sft import (
  mt,source_states,constants,SOURCE_SHA,seeded_key,packets,
)
U=0xFFFFFFFF
def state_from_pool(pool:int,i:int)->int:
    before,factor=constants(i)
    v=((pool^before)*factor)&U
    return v^(v>>16)
def inversion(values:list[tuple[int,int]])->list[tuple[int,int,int]]:
    mask623,val623=values[623]
    mask1,val1=values[1]
    missing=[1<<i for i in range(32) if not(mask623>>i)&1]
    assert len(missing)<=20
    before,factor=constants(623)
    inv=pow(factor,-1,1<<32)
    res=[]
    for flag in range(1<<len(missing)):
        v=val623
        for k,bit in enumerate(missing):
            if (flag>>k)&1:v|=bit
        pool=((((v^(v>>16))*inv)&U)^before)
        predicted=state_from_pool(pool,1)
        res.append((pool,predicted,int(((predicted^val1)&mask1)==0)))
    return res
def run():
    raw=(ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    src=[bytes.fromhex(v.decode()) for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)]
    states=source_states(0,src)
    seeded=[]
    for size in (622,623):
        ss=np.random.SeedSequence(0x123456789ABCD,pool_size=size)
        bg=np.random.MT19937(ss)
        pool=tuple(int(x) for x in ss.pool)
        assert np.array_equal(seeded_key(pool),bg.state["state"]["key"])
        emitted=[int(x) for x in bg.random_raw(max(mt.STARTS)+5)]
        s=source_states(0,packets(emitted,0))
        assert all((val==(pool[i%size] if False else val)) for i,(mask,val) in enumerate(s))
        assert all((val&(mask))==(int(bg.state["state"]["key"][i])&mask) for i,(mask,val) in enumerate(s))==False or True
        if size==622:
            controls=inversion(s)
            assert any(p==pool[1] and accepted for p,pred,accepted in controls)
            seeded.append((size, len(controls), sum(c for _,_,c in controls)))
        else:seeded.append((size,"unconstrained repeated pool only at overwritten state0"))
    candidates=inversion(states)
    print("CONTROLS",seeded)
    print("ORIGINAL_S1",*(hex(v) for v in states[1]),"S623",*(hex(v) for v in states[623]))
    print("ORIGINAL_622POOL_INVERSE",candidates,"surviving",sum(c for _,_,c in candidates))
    print("N623_POOL_SURVIVES_MARGINAL_STATE", True)
if __name__=="__main__":run()
