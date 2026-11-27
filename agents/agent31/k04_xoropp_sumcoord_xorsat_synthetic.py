#!/usr/bin/env python3
"""Synthetic-only carry-factored sum-coordinate xoroshiro128++ inversion.

This is *not* the same as the native-XOR two-output circuit: it eliminates
one whole 64-bit prestate via the first known output and factors subtraction
of the second known output, turning three carry chains into constant-minus-
variable chains. Historical archive values are never used here.
"""
import argparse
import random
import time
from k04_xoropp_native_xorsat_synthetic import Circuit, step, MASK

class Factored(Circuit):
    def or2(self,a,b):
        z=self.v()
        self.clause(a,b,-z)
        self.clause(-a,z)
        self.clause(-b,z)
        return z

    def sub_const(self,constant,word):
        """Bitblast result = constant - word (mod 2^64).
        Only OR or AND gates in borrow chain; all sum bits native XOR.
        """
        borrow=None
        out=[]
        for i,w in enumerate(word):
            bit=(constant>>i)&1
            di=self.v()
            self.s.add_xor_clause([di,w] if borrow is None else [di,w,borrow],bool(bit))
            self.gates['xor']+=1
            out.append(di)
            if i<63:
                if borrow is None:
                    borrow=w if bit==0 else None
                else:
                    borrow=self.or2(w,borrow) if bit==0 else self.and2(w,borrow)
        return out

    def sub_word(self,a,b):
        """Bitblast result = a - b with a single majority borrow chain."""
        borrow=None
        out=[]
        for i in range(64):
            di=self.v()
            self.s.add_xor_clause([di,a[i],b[i]] if borrow is None
                                  else [di,a[i],b[i],borrow],False)
            self.gates['xor']+=1
            out.append(di)
            if i<63:
                borrow=self.and2(-a[i],b[i]) if borrow is None else self.majority(-a[i],b[i],borrow)
        return out

    def sum_equals(self,a,b,target):
        """Constraint a+b==target (mod2^64), without needless sum vars."""
        carry=None
        for i in range(64):
            self.s.add_xor_clause([a[i],b[i],target[i]] if carry is None
                                  else [a[i],b[i],target[i],carry],False)
            self.gates['xor']+=1
            if i<63:
                carry=self.and2(a[i],b[i]) if carry is None else self.majority(a[i],b[i],carry)

def solve_pair(y0,y1,seconds,hint_bits=0,known_c=None):
    assert (hint_bits==0)==(known_c is None)
    q=Factored(seconds)
    c=q.word()
    # y0 = rotl(c,17) + a => a = y0 - rotl(c,17)
    a=q.sub_const(y0,q.rotate(c,17))
    # c=a+b => b=c-a
    b=q.sub_word(c,a)
    a1,b1=q.step(a,b)
    # y1 = rotl(a1+b1,17) + a1 => sum1=ror(y1-a1,17)
    sum1=q.rotate(q.sub_const(y1,a1),-17)
    q.sum_equals(a1,b1,sum1)
    if hint_bits:
        for i in range(hint_bits):
            q.clause(c[i] if (known_c>>i)&1 else -c[i])
    start=time.monotonic()
    sat,model=q.s.solve()
    elapsed=round(time.monotonic()-start,3)
    res={'status':'SAT' if sat is True else 'UNSAT' if sat is False else 'UNKNOWN',
         'elapsed_s':elapsed,'variables':q.n,'gates':q.gates}
    if sat:
        C=sum(int(model[x])<<i for i,x in enumerate(c))
        A=(y0-((C<<17)|(C>>(64-17))&MASK))&MASK
        B=(C-A)&MASK
        yy,aa,bb=step(A,B)
        ypred=step(aa,bb)[0]
        assert yy==y0 and ypred==y1, 'incorrect encoding yielded spurious solution'
    return res

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seed',type=int,default=20261127)
    p.add_argument('--seconds',type=float,default=120)
    p.add_argument('--hint',type=int,default=0)
    args=p.parse_args()
    r=random.Random(args.seed)
    a,b=r.getrandbits(64),r.getrandbits(64)
    y0,a1,b1=step(a,b)
    y1=step(a1,b1)[0]
    s=solve_pair(y0,y1,args.seconds,args.hint,(a+b)&MASK if args.hint else None)
    print(s)
    assert s['status']!='UNSAT','planted synthetic prestate excluded'

if __name__=='__main__': main()
