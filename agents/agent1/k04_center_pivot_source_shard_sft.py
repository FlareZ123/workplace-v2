#!/usr/bin/env python3
"""K04 original 8-bit center-pivot source inversion, one disjoint prefix shard.

Hypothesis: copied selected ACK2 tail8 and REQUESTED3 16 bytes are exact
xoroshiro128++ 1.0 successive generator outputs (3,4,5), with endian view 0/1.
No generator attribution is proven. Every complete middle coupon from any SAT
is immediately tested with the original unchanged mask and full K04 SHA256.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

SELF=Path(__file__).resolve()
sys.path.insert(0,str(SELF.parents[1]/"agent1"))
sys.path.insert(0,str(SELF.parents[1]/"agent50"))
from k04_center_pivot_triad_sft import backward, circuit_from_center
from k04_xoroshiropp_xorcnf_sft import SOURCE_SHA, ROOT, decode, encode, parse_source, stream


def solve_shard(view: int, start: int, seconds: int) -> None:
    from pycryptosat import Solver
    first, middle, later=parse_source()
    assert view in (0,1)
    assert 0<=start<=252 and start%4==0
    assert 1<=seconds<=120
    routing=json.loads((ROOT/"evidence/recovery-routing.json").read_text())
    mask=bytes.fromhex(routing["K04"]["masked_component"])
    acceptance=json.loads((ROOT/"acceptance.json").read_text())
    target=acceptance["slot_sha256"]["K04"]
    assert len(mask)==len(middle)==len(later)==16 and len(target)==64
    observed=[decode(middle,view)[1],*decode(later,view)]
    assert len(observed)==3
    print(json.dumps({"kind":"source_shard_start",
      "view":view,"prefix_first":start,"prefix_last":start+3,
      "original_source_sha256":SOURCE_SHA,
      "original_full_K04_target":target,
      "attempt2_copied_tail8_fit":True,
      "attempt2_copied_head8_fit":False,
      "first_flank_heldout":True,"time_limit_per_prefix":seconds,
      "historical_producer_authenticated":False}),flush=True)
    statuses={"SAT":0,"UNSAT":0,"UNKNOWN":0}
    hits=[]
    for prefix in range(start,start+4):
        c,a4,t4=circuit_from_center(observed)
        solver=Solver(threads=1,time_limit=float(seconds))
        for vars,rhs in c.xors: solver.add_xor_clause(vars,rhs)
        for clause in c.clauses: solver.add_clause(clause)
        for bit in range(8):
            solver.add_clause([a4[bit] if (prefix>>bit)&1 else -a4[bit]])
        then=time.monotonic()
        status,assignment=solver.solve()
        state="SAT" if status is True else "UNSAT" if status is False else "UNKNOWN"
        result={"kind":"historical_prefix_branch",
                "view":view,"prefix":prefix,"status":state,
                "seconds":round(time.monotonic()-then,3),
                "original_K04_commitment":"NOT_EVALUATED"}
        statuses[state]+=1
        if status is True:
            a=sum(int(assignment[v])<<i for i,v in enumerate(a4))
            t=sum(int(assignment[v])<<i for i,v in enumerate(t4))
            initial=(a,a^t)
            for _ in range(4):initial=backward(initial)
            six=stream(initial)
            assert six[3:6]==observed
            coupon=encode(six[2:4],view)
            assert coupon[8:]==middle[8:]
            component=bytes(x^y for x,y in zip(coupon,mask))
            accepted=hashlib.sha256(component).hexdigest()==target
            holdout=six[0:2]==decode(first,view)
            result.update({"candidate_coupon":coupon.hex().upper(),
                "candidate_component":component.hex().upper(),
                "original_K04_commitment":"PASS" if accepted else "MISS",
                "independent_request1_holdout_match":holdout,
                "full_generated_words":[f"{x:016X}" for x in six]})
            if accepted: hits.append(result)
        print(json.dumps(result,sort_keys=True),flush=True)
    print(json.dumps({"kind":"source_shard_summary","view":view,
                      "prefix_first":start,"prefix_last":start+3,
                      "disjoint_four_prefixes_evaluated":4,
                      "statuses":statuses,
                      "original_K04_hits":len(hits),
                      "unknown_remaining":statuses["UNKNOWN"]},sort_keys=True),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--view",type=int,choices=(0,1),required=True)
    parser.add_argument("--shard",type=int,choices=range(64),required=True)
    parser.add_argument("--seconds",type=int,default=20)
    args=parser.parse_args()
    solve_shard(args.view,args.shard*4,args.seconds)


if __name__=="__main__":main()
