#!/usr/bin/env python3
"""H-17 K04 compact reverse fourword xoroshiro128++ inverse: collapse linear history.

Compared with explicit reverse-step XOR gates, this uses the exact GF(2)
two-step inverse state matrix to express the earlier independent REQUESTED1
second output with just 128 native-XOR parity rows. The copied selected ACK2
first eight bytes and REQUESTED1 first output are withheld as blind checks.
This is a conditional generator model, not a native printer authentication.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
import random
import sys
import time
from pathlib import Path

AGENTS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AGENTS/"agent36"))
sys.path.insert(0,str(AGENTS/"agent50"))
sys.path.insert(0,str(AGENTS/"agent30"))

from k04_dual_inverse_borrow_reference import BorrowCircuit,MASK64,SEED,stream
from k04_xoroshiropp_xorcnf_sft import ROOT,SOURCE_SHA,decode,encode,parse_source
from k04_xoropp_reverse_fourword_sft import backward,forward


@lru_cache(maxsize=1)
def reverse2_matrix() -> tuple[int,...]:
    """Rows mapping (a3[0..63], t3[0..63]) to (a1[0..63],b1[0..63])."""
    rows=[0]*128
    for col in range(128):
        if col<64:
            a3=1<<col
            b3=a3
        else:
            a3=0
            b3=1<<(col-64)
        a1,b1=backward(backward((a3,b3)))
        for bit in range(64):
            if (a1>>bit)&1:
                rows[bit]|=1<<col
            if (b1>>bit)&1:
                rows[64+bit]|=1<<col
    return tuple(rows)


def projected_reverse2(c:BorrowCircuit,a3:list[int],t3:list[int]):
    state_basis=a3+t3
    rows=reverse2_matrix()
    past=[]
    for mask in rows:
        literals=[state_basis[j] for j in range(128) if (mask>>j)&1]
        past.append(c.xor_rhs(literals))
    return past[:64],past[64:]


def build(observed_1:int,observed_345:list[int],
          seed3:tuple[int,int]|None=None):
    c=BorrowCircuit()
    (a3,t3),_=c.build_first_pair(observed_345[0],observed_345[1],
                                 seed=seed3,include_middle=False)
    a4,b4=c.step_from_t(a3,t3)
    a5,b5=c.step(a4,b4)
    c.constrain_output(a5,b5,observed_345[2])
    a1,b1=projected_reverse2(c,a3,t3)
    c.constrain_output(a1,b1,observed_1)
    return c,a3,t3


def solve(observed_1:int,observed_345:list[int],limit_seconds:int,
          experiment:str,view:int)->dict:
    from pycryptosat import Solver
    c,a3,t3=build(observed_1,observed_345)
    s=Solver(threads=1,time_limit=float(limit_seconds))
    for row,rhs in c.xors:
        s.add_xor_clause(row,rhs)
    for clause in c.clauses:
        s.add_clause(clause)
    started=time.monotonic()
    status,model=s.solve()
    result=dict(
        experiment=experiment,view=view,linear_reverse="precomputed_inverse_two_step_GF2",
        fitted_output_indices=[1,3,4,5],blind_output_index=0,
        ACK2_copied_head8_withheld=True,
        status="SAT" if status is True else "UNSAT" if status is False else "UNKNOWN",
        seconds=round(time.monotonic()-started,3),
        variables=c.count,cnf_clauses=len(c.clauses),xor_clauses=len(c.xors),
        original_K04_status="NOT_EVALUATED",
    )
    if status is not True:
        return result
    a=sum(int(model[v])<<i for i,v in enumerate(a3))
    t=sum(int(model[v])<<i for i,v in enumerate(t3))
    initial=(a,a^t)
    for _ in range(3):
        initial=backward(initial)
    outputs=stream(initial,6)
    assert outputs[1]==observed_1 and outputs[3:]==observed_345
    result["recovered_state"]=[f"{w:016X}" for w in initial]
    result["recovered_mid"]=[f"{w:016X}" for w in outputs[2:4]]
    result["blind0"]=f"{outputs[0]:016X}"
    return result


def circuit_controls()->None:
    rng=random.Random(0x20261122)
    rows=reverse2_matrix()
    assert len(rows)==128 and min(x.bit_count() for x in rows)>0
    for i in range(100):
        seed=SEED if i==0 else (rng.getrandbits(64),rng.getrandbits(64))
        words=stream(seed,6)
        state3=seed
        for _ in range(3):
            state3=forward(state3)
        c,a3,t3=build(words[1],words[3:],seed3=state3)
        c.validate_witness()
        assert c.bits_to_int(a3)==state3[0]
        assert c.bits_to_int(t3)==(state3[0]^state3[1])
    print(json.dumps({"control":"100 source-free exact seeded GF2 projected-CNF/XOR witnesses",
                      "status":"PASS","matrix_rows":128,
                      "row_weight_min":min(x.bit_count() for x in rows),
                      "row_weight_max":max(x.bit_count() for x in rows)}),flush=True)


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--limit-seconds",type=int,default=240)
    ap.add_argument("--synthetic-only",action="store_true")
    args=ap.parse_args()
    assert 1<=args.limit_seconds<=300
    circuit_controls()
    words=stream(SEED,6)
    positive=solve(words[1],words[3:],args.limit_seconds,"blind_planted_matrix_fourword",0)
    if positive["status"]=="SAT":
        positive["complete_seed_recovered"]=positive["recovered_state"]==[f"{w:016X}" for w in SEED]
        positive["complete_middle_recovered"]=positive["recovered_mid"]==[f"{w:016X}" for w in words[2:4]]
        positive["blind0_matches"]=positive["blind0"]==f"{words[0]:016X}"
    print(json.dumps(positive,sort_keys=True),flush=True)
    if args.synthetic_only or not all(positive.get(k) is True for k in (
        "complete_seed_recovered","complete_middle_recovered","blind0_matches"
    )):
        print(json.dumps({"historical_source":"SKIPPED",
                          "reason":"full blind planted positive not solved",
                          "original_K04_status":"NOT_EVALUATED"}),flush=True)
        return
    first,selected,third=parse_source()
    for view in (0,1):
        y1=decode(first,view)[1]
        selected2=decode(selected,view)
        other=decode(third,view)
        result=solve(y1,[selected2[1],*other],args.limit_seconds,"historical_matrix_fourword",view)
        result["source_sha256"]=SOURCE_SHA
        if result["status"]=="SAT":
            result["blind_first_REQUESTED_word_match"]=result["blind0"]==f"{decode(first,view)[0]:016X}"
            mid=[int(w,16) for w in result["recovered_mid"]]
            coupon=encode(mid,view)
            assert coupon[8:]==selected[8:]
            result["candidate_coupon"]=coupon.hex().upper()
            if result["blind_first_REQUESTED_word_match"]:
                route=json.loads((ROOT/"evidence/recovery-routing.json").read_text())
                original=json.loads((ROOT/"acceptance.json").read_text())
                mask=bytes.fromhex(route["K04"]["masked_component"])
                candidate=bytes(a^b for a,b in zip(coupon,mask))
                result["candidate_K04"]=candidate.hex().upper()
                result["original_K04_status"]=(
                    "PASS" if hashlib.sha256(candidate).hexdigest()==original["slot_sha256"]["K04"].lower()
                    else "MISS_ONE_COMPLETE_CANDIDATE"
                )
            else:
                result["original_K04_status"]="NOT_EVALUATED_BLIND_FAIL"
        print(json.dumps(result,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
