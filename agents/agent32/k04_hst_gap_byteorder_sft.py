"""Source-only HST one-word uniform quantizer, four physical 16/32bit byte orders.

Run: python agents/agent32/k04_hst_gap_byteorder_sft.py
"""
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from agents.agent32.k04_hst_gap_uint32_sft import load_source, prefix_bits, stages
from agents.agent49.k04_p951_symbolic_basis import STARTS, ORIGIN, Basis, untemper, temper

ORDERS={
    "identity":(0,1,2,3),
    "whole_word_reverse":(3,2,1,0),
    "swap_16bit_halves":(2,3,0,1),
    "swap_bytes_within_halves":(1,0,3,2),
}


def swap_word(value, order):
    data=value.to_bytes(4, "little")
    return int.from_bytes(bytes(data[i] for i in order), "little")


def check(basis, vectors, stage, millivalue, order):
    predicted=temper(vectors[stage-ORIGIN])
    required=prefix_bits(millivalue)
    fixed=0
    matched=0
    for idx,expected in enumerate(required):
        bit=31-idx
        original_bit=8*order[bit//8]+bit%8
        observed=basis.predict(predicted[original_bit])
        if observed is not None:
            fixed+=1
            matched+=observed==expected
    return fixed,matched


def original(pv,basis,vectors,order):
    contradictions=[]
    informative=0
    for seq,row in sorted(pv.items()):
        i=seq-100
        value=int(round(float(row["value"])*1000))
        results=[check(basis,vectors,q,value,order) for q in stages(i)]
        assert results
        informative+=any(fixed>0 for fixed,_ in results)
        if all(fixed != matched for fixed,matched in results):
            contradictions.append((seq,row["quality"]))
    return informative,contradictions


def planted(vectors,order):
    rng=random.Random(0x4A17C9)
    words=[rng.getrandbits(32) for _ in range(967)]
    basis=Basis()
    for row,pos in enumerate(STARTS):
        if row==129:
            continue
        for lane in range(4):
            state=untemper(words[pos+lane])
            for bit,v in enumerate(vectors[pos+lane-ORIGIN]):
                basis.insert(v,(state>>bit)&1)
    assert basis.rank==15365
    informative=0
    for i in range(112):
        stage=STARTS[i]+4
        millivalue=round((12+76*swap_word(words[stage],order)/(1<<32))*1000)
        fixed,matched=check(basis,vectors,stage,millivalue,order)
        assert fixed==matched,(i,stage,fixed,matched)
        informative+=fixed>0
    return informative


if __name__=="__main__":
    pv,basis,vectors=load_source()
    for name,order in ORDERS.items():
        informative,contradictions=original(pv,basis,vectors,order)
        synthetic=planted(vectors,order)
        print("BYTE_ORDER",name,"ORIGINAL_INFORMATIVE",informative,
              "ALL_STAGE_CONTRADICTIONS",len(contradictions),
              "GOOD",sum(q=="GOOD" for _,q in contradictions),
              "LATE",sum(seq>=180 for seq,_ in contradictions),
              "SYNTHETIC_112_PASS_INFORMATIVE",synthetic,flush=True)
        assert len(contradictions)>0
