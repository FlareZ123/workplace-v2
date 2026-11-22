#!/usr/bin/env python3
"""H-17 K04 source-conditional reverse four-output xoroshiro128++ state bridge.

Observations: alleged original ACK2 copied last 8 bytes = output3,
untouched REQUESTED3 16 bytes = outputs4,5, and REQUESTED1 second
64-bit word = output1. Output0 of REQUESTED1 remains entirely BLIND.
The first eight copied ACK bytes remain ENTIRELY WITHHELD.
State3 is inferred through a small local three-word inverse augmented by
one backward-propagated independent earlier full-word constraint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

AGENTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTS / "agent36"))
sys.path.insert(0, str(AGENTS / "agent50"))

from k04_dual_inverse_borrow_reference import BorrowCircuit, MASK64, SEED, stream
from k04_xoroshiropp_xorcnf_sft import ROOT, SOURCE_SHA, decode, encode, parse_source


def rotl(word: int, n: int) -> int:
    return ((word << n) | (word >> (64-n))) & MASK64


def rotr(word: int, n: int) -> int:
    return ((word >> n) | (word << (64-n))) & MASK64


def forward(state: tuple[int,int]) -> tuple[int,int]:
    a,b=state
    t=a^b
    return (rotl(a,49)^t^((t<<21)&MASK64),rotl(t,28))


def backward(state: tuple[int,int]) -> tuple[int,int]:
    a,b=state
    t=rotr(b,28)
    prev_a=rotr(a^t^((t<<21)&MASK64),49)
    return prev_a,prev_a^t


def reverse_bits(c: BorrowCircuit, a: list[int], b: list[int]) -> tuple[list[int], list[int]]:
    """Exact symbolic inverse of xoroshiro128++ state update, modulo 2^64."""
    t=c.rotated(b,-28)
    inner=[c.xor(a[i],t[i],t[i-21] if i>=21 else 0) for i in range(64)]
    prev_a=c.rotated(inner,-49)
    prev_b=[c.xor(x,y) for x,y in zip(prev_a,t)]
    return prev_a,prev_b


def build_four(observed_1: int, observed_345: list[int],
               seed3: tuple[int,int] | None = None):
    c=BorrowCircuit()
    (a3,t3),_=c.build_first_pair(
        observed_345[0],observed_345[1],seed=seed3,include_middle=False
    )
    a4,b4=c.step_from_t(a3,t3)
    a5,b5=c.step(a4,b4)
    c.constrain_output(a5,b5,observed_345[2])
    b3=[c.xor(x,y) for x,y in zip(a3,t3)]
    a2,b2=reverse_bits(c,a3,b3)
    a1,b1=reverse_bits(c,a2,b2)
    c.constrain_output(a1,b1,observed_1)
    return c,a3,t3


def solve(observed_1: int, observed_345: list[int], limit_seconds: int,
          label: str, view: int) -> dict:
    from pycryptosat import Solver
    c,a3,t3=build_four(observed_1,observed_345)
    solver=Solver(threads=1,time_limit=float(limit_seconds))
    for terms,rhs in c.xors:
        solver.add_xor_clause(terms,rhs)
    for clause in c.clauses:
        solver.add_clause(clause)
    started=time.monotonic()
    outcome,model=solver.solve()
    result=dict(
        experiment=label,view=view,
        fitted_positions=[1,3,4,5],holdout_position=0,
        copied_ACK2_head8_withheld=True,
        status="SAT" if outcome is True else "UNSAT" if outcome is False else "UNKNOWN",
        elapsed_seconds=round(time.monotonic()-started,3),
        variables=c.count,cnf_clauses=len(c.clauses),
        xor_clauses=len(c.xors),
        original_K04_commitment="NOT_EVALUATED",
    )
    if outcome is not True:
        return result
    sa=sum(int(model[x]) << i for i,x in enumerate(a3))
    st=sum(int(model[x]) << i for i,x in enumerate(t3))
    state3=(sa,sa^st)
    initial=state3
    for _ in range(3):
        initial=backward(initial)
    generated=stream(initial,6)
    assert generated[1] == observed_1 and generated[3:6] == observed_345
    result.update(
        initial_state=[f"{x:016X}" for x in initial],
        whole_middle_words=[f"{x:016X}" for x in generated[2:4]],
        blind_output0=f"{generated[0]:016X}",
    )
    return result


def witness_controls() -> None:
    rng=random.Random(0x20261122)
    for i in range(100):
        state=SEED if i==0 else (rng.getrandbits(64),rng.getrandbits(64))
        full=stream(state,6)
        state3=state
        for _ in range(3):
            state3=forward(state3)
        assert state3[0] >=0
        assert backward(forward(state3)) == state3
        c,a3,t3=build_four(full[1],full[3:6],seed3=state3)
        c.validate_witness()
        assert c.bits_to_int(a3) == state3[0]
        assert c.bits_to_int(t3) == (state3[0]^state3[1])
    print(json.dumps({"control":"100 exact seeded forward/reverse four-output CNF/XOR witnesses",
                      "status":"PASS"}),flush=True)


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--limit-seconds",type=int,default=240)
    parser.add_argument("--synthetic-only",action="store_true")
    args=parser.parse_args()
    assert 1<=args.limit_seconds<=300
    witness_controls()
    expected=stream(SEED,6)
    positive=solve(expected[1],expected[3:6],args.limit_seconds,"unseeded_planted_four-output",0)
    if positive["status"] == "SAT":
        positive["entire_seed_recovered"]=positive["initial_state"]==[f"{x:016X}" for x in SEED]
        positive["both_middle_outputs_recovered"]=positive["whole_middle_words"]==[f"{x:016X}" for x in expected[2:4]]
        positive["blind_output0_matches"]=positive["blind_output0"]==f"{expected[0]:016X}"
    print(json.dumps(positive,sort_keys=True),flush=True)
    if args.synthetic_only or not all(positive.get(k) is True for k in
       ("entire_seed_recovered","both_middle_outputs_recovered","blind_output0_matches")):
        print(json.dumps({"historical":"SKIPPED",
                          "reason":"unseeded planted full coupon and blind holdout not recovered",
                          "original_K04_commitment":"NOT_EVALUATED"}),flush=True)
        return
    first,middle,third=parse_source()
    for view in (0,1):
        earlier=decode(first,view)
        copied=decode(middle,view)
        later=decode(third,view)
        result=solve(earlier[1],[copied[1],*later],args.limit_seconds,"original_four-output",view)
        result["source_sha256"]=SOURCE_SHA
        if result["status"] == "SAT":
            result["blind_REQUESTED1_output0_match"]=result["blind_output0"] == f"{earlier[0]:016X}"
            words=[int(v,16) for v in result["whole_middle_words"]]
            coupon=encode(words,view)
            assert coupon[8:]==middle[8:]
            result["whole_coupon"]=coupon.hex().upper()
            # The previous REQUESTED packet is a separate attribution test.
            # Hash any complete coupon even when that blind holdout fails.
            route=json.loads((ROOT/"evidence/recovery-routing.json").read_text())
            acceptance=json.loads((ROOT/"acceptance.json").read_text())
            mask=bytes.fromhex(route["K04"]["masked_component"])
            component=bytes(a^b for a,b in zip(coupon,mask))
            result["whole_component"]=component.hex().upper()
            result["original_K04_commitment"]=(
                "PASS" if hashlib.sha256(component).hexdigest()==acceptance["slot_sha256"]["K04"].lower()
                else "MISS_COMPLETE_CANDIDATE"
            )
        print(json.dumps(result,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
