#!/usr/bin/env python3
"""Synthetic-only native-XOR SAT benchmark for xoroshiro128++ two-output inversion.

No archive, verification key, source packets or historical values.
Requires PyPI pycryptosat (CryptoMiniSat). Use only planted random streams.
"""
import argparse
import random
import time
from pycryptosat import Solver

MASK = (1 << 64) - 1
def rol(x,n): return ((x << n) | (x >> (64-n))) & MASK
def step(a,b):
    y=(rol((a+b)&MASK,17)+a)&MASK
    t=a^b
    return y,(rol(a,49)^t^((t<<21)&MASK))&MASK,rol(t,28)

class Circuit:
    def __init__(self,limit):
        self.s=Solver(time_limit=limit,threads=1,verbose=0)
        self.n=0
        self.gates={"xor":0,"cnf":0}
    def v(self):
        self.n+=1
        return self.n
    def word(self): return [self.v() for _ in range(64)]
    def clause(self,*lits):
        self.s.add_clause(list(lits)); self.gates["cnf"]+=1
    def xor(self,*v):
        if len(v)==1:return v[0]
        out=self.v()
        self.s.add_xor_clause([out,*v],False)
        self.gates["xor"]+=1
        return out
    def and2(self,a,b):
        z=self.v()
        self.clause(-a,-b,z); self.clause(a,-z); self.clause(b,-z)
        return z
    def majority(self,a,b,c):
        z=self.v()
        for clause in ((-a,-b,z),(-a,-c,z),(-b,-c,z),
                       (a,b,-z),(a,c,-z),(b,c,-z)):
            self.clause(*clause)
        return z
    @staticmethod
    def rotate(w,n):return [w[(i-n)%64] for i in range(64)]
    def add(self,a,b):
        res=[];carry=None
        for i in range(64):
            if i==0:
                res.append(self.xor(a[i],b[i]))
                carry=self.and2(a[i],b[i])
            else:
                res.append(self.xor(a[i],b[i],carry))
                if i<63:carry=self.majority(a[i],b[i],carry)
        return res
    def emit(self,a,b):
        return self.add(self.rotate(self.add(a,b),17),a)
    def step(self,a,b):
        t=[self.xor(x,y) for x,y in zip(a,b)]
        aa=[self.xor(self.rotate(a,49)[i],t[i],t[i-21]) if i>=21
            else self.xor(self.rotate(a,49)[i],t[i]) for i in range(64)]
        return aa,self.rotate(t,28)
    def observe(self,word,value,bits):
        for i,v in enumerate(word[:bits]):
            self.clause(v if (value>>i)&1 else -v)

def solve(outputs,seconds,hint_bits=0,initial_a=None,observed_bits=64):
    m=Circuit(seconds)
    a,b=m.word(),m.word()
    root_a,root_b=a,b
    for value in outputs:
        m.observe(m.emit(a,b),value,observed_bits)
        a,b=m.step(a,b)
    if hint_bits:
        assert initial_a is not None
        for i in range(hint_bits):
            m.clause(root_a[i] if (initial_a>>i)&1 else -root_a[i])
    t=time.monotonic()
    sat,model=m.s.solve()
    dur=round(time.monotonic()-t,3)
    result={"status":"SAT" if sat is True else "UNSAT" if sat is False else "UNKNOWN",
            "seconds":dur,"variables":m.n,"gates":m.gates}
    if sat:
        aa=sum(int(model[v])<<i for i,v in enumerate(root_a))
        bb=sum(int(model[v])<<i for i,v in enumerate(root_b))
        for y in outputs:
            out,aa,bb=step(aa,bb)
            assert (out&((1<<observed_bits)-1))==(y&((1<<observed_bits)-1))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--seed",type=int,default=20261127)
    p.add_argument("--outputs",type=int,default=2)
    p.add_argument("--seconds",type=float,default=120)
    p.add_argument("--hint",type=int,default=0)
    p.add_argument("--observed-bits",type=int,default=64)
    v=p.parse_args()
    r=random.Random(v.seed)
    original_a,original_b=r.getrandbits(64),r.getrandbits(64)
    a,b=original_a,original_b
    ys=[]
    for _ in range(v.outputs):
        y,a,b=step(a,b);ys.append(y)
    result=solve(ys,v.seconds,v.hint,original_a,v.observed_bits)
    print(result)
    assert result["status"]!="UNSAT","incorrect encoding excluded planted original state"

if __name__=="__main__":main()
