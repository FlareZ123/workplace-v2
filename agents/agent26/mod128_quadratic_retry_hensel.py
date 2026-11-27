"""Exact source-independent quadratic transition inversion over Z/(2^128).

Given A->B and U->V, B->X, X->C under common T(z)=a*z²+b*z+c,
recover every missing middle X when A-U has v2 <=6. Enumerates the
2-adic lift(s) of the affine pair interpolation and all cubic roots in a.
No historical inputs, source readers, route masks or target hashes.
"""
from __future__ import annotations
import hashlib
M=1<<128
MASK=M-1

def v2(x):
    x &= MASK
    return (x&-x).bit_length()-1 if x else 128

def rootlift(coeff, cap=50000):
    aroots=[0]
    for shift in range(128):
        half=1<<shift; modulus=2*half
        nxt=[]
        for a in aroots:
            for trial in (a,a+half):
                val=0
                for c in coeff[::-1]:val=(val*trial+c)%modulus
                if val==0:nxt.append(trial)
        aroots=nxt
        if not aroots:break
        if len(aroots)>cap:raise RuntimeError('singular polynomial root explosion')
    return aroots

def recover(A,B,U,V,C,max_lifts=64):
    D=(A-U)&MASK;E=(B-V)&MASK;v=v2(D)
    if v>=128:
        raise ValueError('source anchor points coincide; underdetermined')
    g=1<<v
    if E%g:return []
    if g>max_lifts:raise ValueError('source anchor nonunit valuation requires too many lifts')
    mmod=M//g
    m0=( (E//g)*pow(D//g,-1,mmod) )%mmod
    output=[]
    for lift in range(g):
        m=m0+lift*mmod
        k=(B-m*A)&MASK
        x0=(m*B+k)&MASK
        q=(B-A)*(B-U)&MASK
        alpha=(x0-A)&MASK; beta=(x0-U)&MASK
        c0=(m*x0+k-C)&MASK
        c1=(m*q+alpha*beta)&MASK
        c2=q*(alpha+beta)&MASK
        c3=q*q&MASK
        for a in rootlift([c0,c1,c2,c3]):
            b=(m-a*(A+U))&MASK
            c=(k+a*A*U)&MASK
            T=lambda z:((a*z+b)*z+c)&MASK
            X=T(B)
            assert T(A)==B and T(U)==V and T(X)==C
            assert X==((x0+a*q)&MASK)
            output.append(X)
    return output

def synthetic():
    stats={}
    for v in (0,1,2,3):
        count=0
        for i in range(40):
            def h(t):return int.from_bytes(hashlib.sha256(f'generalring:{v}:{i}:{t}'.encode()).digest()[:16],'big')
            A=h('A'); U=(A-(1<<v)*(2*(h('D')&0xffff)+1))&MASK
            assert v2(A-U)==v
            a,b,c=h('a'),h('b'),h('c')
            T=lambda z:((a*z+b)*z+c)&MASK
            B=T(A);V=T(U);X=T(B);C=T(X)
            roots=recover(A,B,U,V,C)
            assert X in roots,(v,i)
            count+=1
        stats['difference_valuation_'+str(v)]=count
    return stats

def unit_controls():
    pos=neg=0
    for i in range(100):
        def h(t):return int.from_bytes(hashlib.sha256(f'mod128:{t}:{i}'.encode()).digest()[:16],'big')
        A=h('A')|1;U=h('U')&~1
        a,b,c=h('a'),h('b'),h('c')
        T=lambda z:((a*z+b)*z+c)&MASK
        B=T(A);V=T(U);X=T(B);C=T(X)
        assert X in recover(A,B,U,V,C);pos+=1
        assert not recover(A,B,U,V,C^1);neg+=1
    return {'complete_coupon_positives':pos,'wrong_flank_negatives':neg}

if __name__=='__main__':
    print('unit_controls',unit_controls())
    print('general_nonunit_and_unit_controls',synthetic())
