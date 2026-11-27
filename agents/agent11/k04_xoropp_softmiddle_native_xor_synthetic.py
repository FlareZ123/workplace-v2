#!/usr/bin/env python3
"""Synthetic-only xoroshiro128++ damaged-middle exact XOR-SAT benchmark.

Two intact 64-bit output pairs at stages 0/1 and 4/5 are hard constraints.
Two intentionally corrupted 64-bit middle outputs at stages 2/3 are soft
constraints, allowing up to K mismatched bits. Positive planted controls
verify an actual complete original state without any archive input.
No original source, K04/K08 values, route masks, commitments or PDF.
Requires PyPI pycryptosat, provided by the manual synthetic workflow.
"""
import argparse, random, sys, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent31"))
from k04_xoropp_native_xorsat_synthetic import Circuit, step
from k04_xoropp_sumcoord_xorsat_synthetic import Factored

def at_most(circuit, bits, k):
    """Correct Sinz-like monotone sequential counter O(n*k) CNF."""
    assert 0<=k<=len(bits)
    if k==len(bits):return
    if k==0:
        for e in bits:circuit.clause(-e)
        return
    previous={}
    for i,e in enumerate(bits,1):
        current={}
        for j in range(1,min(i,k+1)+1):
            s=circuit.v();current[j]=s
            if j in previous:circuit.clause(-previous[j],s)
            if j==1:circuit.clause(-e,s)
            elif (j-1) in previous:circuit.clause(-e,-previous[j-1],s)
        previous=current
    circuit.clause(-previous[k+1])

def build(y0,y1,y4,y5,middle,limit,soft_budget,mode="atmost",hint_bits=16):
    c=Factored(limit)
    sum0=c.word()
    a0=c.sub_const(y0,c.rotate(sum0,17))
    b0=c.sub_word(sum0,a0)
    state_a,state_b=a0,b0
    err=[]
    for stage in range(1,6):
        state_a,state_b=c.step(state_a,state_b)
        if stage in (1,4,5):
            val={1:y1,4:y4,5:y5}[stage]
            needed=c.rotate(c.sub_const(val,state_a),-17)
            c.sum_equals(state_a,state_b,needed)
        if stage in (2,3):
            produced=c.emit(state_a,state_b)
            observed=middle[stage-2]
            for j,bitvar in enumerate(produced):
                e=c.v()
                c.s.add_xor_clause([bitvar,e],bool((observed>>j)&1))
                c.gates['xor']+=1
                err.append(e)
    if mode=="atmost":at_most(c,err,soft_budget)
    elif mode=="prefix":
        for e in err[:hint_bits]:c.clause(-e)
    else:raise ValueError(mode)
    return c,(a0,b0),err

def evaluate(seed,errors,budget,seconds,mode,hint_bits,anchor):
    rng=random.Random(seed)
    aa,bb=rng.getrandbits(64),rng.getrandbits(64)
    original=(aa,bb)
    ys=[]
    for _ in range(6):
        out,aa,bb=step(aa,bb);ys.append(out)
    corrupted=list(ys[2:4])
    if mode=="prefix":
        positions=rng.sample(range(hint_bits,128),errors)
    else:
        positions=rng.sample(range(128),errors)
    for p in positions:corrupted[p//64]^=1<<(p%64)
    c,(root_a,root_b),err=build(ys[0],ys[1],ys[4],ys[5],corrupted,
                               seconds,budget,mode,hint_bits)
    if anchor:
        for i in range(anchor):
            c.clause(root_a[i] if (original[0]>>i)&1 else -root_a[i])
    print("source_free=True","seed=",seed,"flank_outputs=4",
          "middle_bit_errors=",errors,"budget=",budget,"mode=",mode,
          "hint_bits=",hint_bits,"correct_initial_a_anchor=",anchor,
          "variables=",c.n,"gates=",c.gates,flush=True)
    start=time.monotonic()
    sat,model=c.s.solve()
    print("status=","SAT" if sat is True else "UNSAT" if sat is False else "UNKNOWN",
          "seconds=",round(time.monotonic()-start,3),flush=True)
    if sat:
        aa=sum(int(model[v])<<i for i,v in enumerate(root_a))
        bb=sum(int(model[v])<<i for i,v in enumerate(root_b))
        replay=[]
        for _ in range(6):
            y,aa,bb=step(aa,bb);replay.append(y)
        assert all(replay[i]==ys[i] for i in (0,1,4,5))
        mismatches=(replay[2]^corrupted[0]).bit_count()+(replay[3]^corrupted[1]).bit_count()
        if mode=="atmost":assert mismatches<=budget
        if mode=="prefix":assert ((replay[2]^corrupted[0])&((1<<hint_bits)-1))==0
        print("full_state_planted_match=", (sum(int(model[v])<<i for i,v in enumerate(root_a)),sum(int(model[v])<<i for i,v in enumerate(root_b)))==original,
             "middle_mismatch_count=",mismatches,flush=True)
    assert sat is not False,"Incorrect circuit excluded planted original"
    return sat

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--seed",type=int,default=20261127)
    p.add_argument("--errors",type=int,default=12)
    p.add_argument("--budget",type=int,default=16)
    p.add_argument("--seconds",type=int,default=150)
    p.add_argument("--mode",choices=["atmost","prefix"],default="atmost")
    p.add_argument("--hint-bits",type=int,default=16)
    p.add_argument("--anchor",type=int,default=0)
    a=p.parse_args()
    assert 0<=a.errors<=a.budget<=128 if a.mode=="atmost" else 0<=a.errors<=128-a.hint_bits
    evaluate(a.seed,a.errors,a.budget,a.seconds,a.mode,a.hint_bits,a.anchor)

if __name__=="__main__":main()
