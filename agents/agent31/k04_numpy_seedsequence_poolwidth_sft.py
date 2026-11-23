"""H-17 K04: all42-source inversion of arbitrary NumPy SeedSequence MT pool sizes.

Read-only original-source test. The disputed selected printer ACK2 row129 is
withheld *before decoding bytes*. No original SHA-256 target is used to fit
a pool or output stage. Run: python agents/agent31/k04_numpy_seedsequence_poolwidth_sft.py

Requires numpy (for genuine NumPy planted controls) and the existing exact
Agent1 all42 MT source projector. This program covers 625 prehistory offsets
and every pool size 4..623. Larger pools are not ruled out.
"""
import collections
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents/agent1"))
import k04_all42_cpython_n98_extended_sft as base
import k04_numpy_pool4_all42_source_sft as template

U=0xFFFFFFFF
INIT_B=0x8B51F9DD
MULT_B=0x58F38DED
MOD=1<<32
WIDTHS=range(4,624)
_B=[INIT_B*pow(MULT_B,i,MOD)&U for i in range(624)]
_F=[x*MULT_B&U for x in _B]
_INV=[pow(x,-1,MOD) for x in _F]

def poolword(i,stateword):
    raw=stateword^(stateword>>16)
    return ((raw*_INV[i])&U)^_B[i]

def stateword(i,p):
    word=((p^_B[i])*_F[i])&U
    return word^(word>>16)

def pair_constraint(states,n,cap=12):
    # Even when no residue is fixed by a full 32-bit state word, two
    # partially observed words in the same pool residue may be inconsistent.
    buckets={}
    for i in range(1,624):
        mask,value=states[i]
        if mask:buckets.setdefault(i%n,[]).append((i,mask,value))
    for obs in buckets.values():
        if len(obs)<2:continue
        i,mask,value=min(obs,key=lambda q:32-q[1].bit_count())
        absent=[j for j in range(32) if not mask&(1<<j)]
        if len(absent)>cap:continue
        vals=[value]
        for j in absent:vals.extend([v|(1<<j) for v in vals])
        found=False
        for actual in vals:
            p=poolword(i,actual)
            if all(((stateword(k,p)^v)&m)==0 for k,m,v in obs):
                found=True
                break
        if not found:return False
    return True

def classify(states,n):
    if (states[0][1]^0x80000000)&states[0][0]:
        return "bad_init0",None
    pool={}
    for i in range(1,624):
        mask,value=states[i]
        if mask==U:
            r=i%n
            candidate=poolword(i,value)
            if r in pool and pool[r]!=candidate:
                return "fullword_contradiction",None
            pool[r]=candidate
    for i in range(1,624):
        mask,value=states[i]
        if 0<mask<U and i%n in pool:
            if (stateword(i,pool[i%n])^value)&mask:
                return "partialword_contradiction",None
    if not pair_constraint(states,n):
        return "pair_contradiction",None
    if len(pool)<n:
        return "insufficient",None
    actual_pool=[pool[j] for j in range(n)]
    for i,(mask,value) in enumerate(states):
        actual=0x80000000 if not i else stateword(i,actual_pool[i%n])
        if (actual^value)&mask:return "incompatible",None
    return "complete",actual_pool

def actual_seedseq_state(pool):
    n=len(pool)
    state=[0x80000000]
    for i in range(1,624):state.append(stateword(i,pool[i%n]))
    return state

def genuine_planted(n,offset,seed):
    ss=np.random.SeedSequence(seed,pool_size=n)
    mt=np.random.MT19937(ss)
    original=[int(x) for x in mt.state["state"]["key"]]
    assert mt.state["state"]["pos"]==623
    assert original[0]==0x80000000
    assert all(poolword(i,original[i])==int(ss.pool[i%n]) for i in range(1,624))
    assert actual_seedseq_state(tuple(map(int,ss.pool)))==original
    words=template.native_stream(original,624+offset+base.S[-1]+4)
    packets=[None if r==129 else b"".join(
       template.temper(words[624+offset+s+j]).to_bytes(4,"little")
       for j in range(4)) for r,s in enumerate(base.S)]
    chosen=b"".join(
       template.temper(words[624+offset+base.S[129]+j]).to_bytes(4,"little")
       for j in range(4))
    return original,tuple(map(int,ss.pool)),packets,chosen

def planted_controls():
    route=json.loads((ROOT/"resources/evidence/recovery-routing.json").read_text())
    mask=bytes.fromhex(route["K04"]["masked_component"])
    controls=[(4,-1),(5,0),(8,93),(16,616),(32,1),(64,300),
              (128,616),(256,93),(512,5),(593,292),(600,31),(623,5)]
    for n,off in controls:
        initialized,pool,packets,coupon=genuine_planted(n,off,0xC0FFEE+n)
        states=base.projection(off,packets)
        assert all((initialized[i]&m)==v for i,(m,v) in enumerate(states))
        status,solved=classify(states,n)
        assert status in ("complete","insufficient"),(n,off,status)
        if status=="complete":
            assert tuple(solved)==pool
            target=hashlib.sha256(bytes(a^b for a,b in zip(coupon,mask))).digest()
            reconstructed=actual_seedseq_state(solved)
            words=template.native_stream(reconstructed,624+off+base.S[129]+4)
            predicted=b"".join(
               template.temper(words[624+off+base.S[129]+j]).to_bytes(4,"little")
               for j in range(4))
            assert hashlib.sha256(bytes(a^b for a,b in zip(predicted,mask))).digest()==target
            assert predicted==coupon
        print("PLANTED_NUMPY_PASS",n,off,status,flush=True)

def main():
    st=time.monotonic()
    planted_controls()
    original=base.source()
    assert original[129] is None and len(original)==133
    counts={n:collections.Counter() for n in WIDTHS}
    source_reconstructed=0
    acceptance=json.loads((ROOT/"resources/acceptance.json").read_text())
    route=json.loads((ROOT/"resources/evidence/recovery-routing.json").read_text())
    mask=bytes.fromhex(route["K04"]["masked_component"])
    for off in range(-1,624):
        states=base.projection(off,original)
        if (states[0][1]^0x80000000)&states[0][0]:
            for n in WIDTHS:counts[n]["bad_init0"]+=1
        else:
            for n in WIDTHS:
                state,pool=classify(states,n)
                counts[n][state]+=1
                if state=="complete":
                    source_reconstructed+=1
                    words=template.native_stream(actual_seedseq_state(pool),
                                624+off+base.S[129]+4)
                    coupon=b"".join(
                        template.temper(words[624+off+base.S[129]+j]).to_bytes(4,"little")
                        for j in range(4))
                    component=bytes(a^b for a,b in zip(coupon,mask))
                    if hashlib.sha256(component).hexdigest()==acceptance["slot_sha256"]["K04"]:
                        raise RuntimeError("ORIGINAL_K04_FOUND: "+component.hex().upper())
        if off%125==0:print("SOURCE_PROGRESS",off,round(time.monotonic()-st,1),flush=True)
    surviving=[n for n in WIDTHS if counts[n]["insufficient"] or counts[n]["complete"]]
    excluded=[n for n in WIDTHS if n not in surviving]
    assert source_reconstructed==0,source_reconstructed
    assert len(excluded)==598,(len(excluded),surviving)
    assert len(surviving)==22 and min(surviving)==598,surviving
    assert counts[4]=={"bad_init0":126,"fullword_contradiction":499}
    assert counts[393]=={"bad_init0":126,"fullword_contradiction":399,
                          "partialword_contradiction":99,"pair_contradiction":1}
    print("ORIGINAL_RESULT",json.dumps({
      "source_sha256":base.SOURCE_SHA,
      "source_rows":132,"selected_row_withheld":129,
      "offsets_checked":625,"pool_widths_checked":620,
      "widths_falsified":len(excluded),"first_unexcluded_width":min(surviving),
      "not_excluded_widths":surviving,
      "completed_original_numpy_pool_models":source_reconstructed,
      "source4_counts":dict(counts[4]),
      "source393_counts":dict(counts[393]),
      "elapsed_seconds":round(time.monotonic()-st,1),
      "original_K04_recovered":False,
    },sort_keys=True),flush=True)

if __name__=="__main__":main()
