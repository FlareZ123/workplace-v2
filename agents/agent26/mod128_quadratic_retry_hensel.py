"""Source-independent Z/(2^128) quadratic state-transition inverse.

Given A->B and U->V plus a further B->X->C via one unknown T(z)=a*z^2+b*z+c,
returns *every* withheld X when A-U is odd. Uses exact 2-adic Hensel
lifting of the cubic in the free quadratic coefficient; no original inputs.
Standalone synthetic controls only. No file or network access.
"""
from __future__ import annotations
import hashlib
MOD=1<<128
MASK=MOD-1

def solve(A:int,B:int,U:int,V:int,C:int,max_branches:int=50000)->list[int]:
    # For A-U odd, the affine interpolant is unique over Z/(2^128).
    if not ((A-U)&1):
        raise ValueError('this subfamily requires a unit A-U difference')
    m = ((B-V)*pow((A-U)&MASK,-1,MOD))&MASK
    k = (B-m*A)&MASK
    x0 = (m*B+k)&MASK
    q = ((B-A)*(B-U))&MASK
    alpha = (x0-A)&MASK
    beta = (x0-U)&MASK
    # G(a)=T_a(T_a(B))-C where T_a=L+a(z-A)(z-U).
    coeff = [(m*x0+k-C)&MASK, (m*q+alpha*beta)&MASK,
             (q*(alpha+beta))&MASK, (q*q)&MASK]
    roots = [0]   # Every integer is congruent 0 mod1.
    for exponent in range(1,129):
        modulus = 1 << exponent
        half = modulus >> 1
        nxt=[]
        for a in roots:
            for candidate in (a,a+half):
                # Evaluate exactly mod 2^exponent via arithmetic Horner.
                value = 0
                for c in reversed(coeff): value = (value*candidate+c)%modulus
                if value==0:nxt.append(candidate)
        roots=nxt
        if not roots: return []
        if len(roots)>max_branches:
            raise RuntimeError(f'singular 2-adic root family exceeds cap at exponent {exponent}')
    outputs=[]
    for a in roots:
        b=(m-a*(A+U))&MASK
        c=(k+a*A*U)&MASK
        T=lambda z:((a*z+b)*z+c)&MASK
        X=T(B)
        assert X == (x0+a*q)&MASK
        assert T(A)==B and T(U)==V and T(X)==C
        outputs.append(X)
    return outputs

def controls():
    results={'positive':0,'negative_mod2':0,'more_than_one_root':0}
    for i in range(100):
        def h(t):return int.from_bytes(hashlib.sha256(f'mod128:{t}:{i}'.encode()).digest()[:16],'big')
        A=h('A')|1;U=h('U')&~1
        a,b,c=h('a'),h('b'),h('c')
        T=lambda z:((a*z+b)*z+c)&MASK
        B=T(A);V=T(U);X=T(B);C=T(X)
        roots=solve(A,B,U,V,C)
        assert X in roots,('fixture',i)
        results['positive']+=1
        results['more_than_one_root']+=bool(len(roots)>1)
        # Perturb the known second flank by one bit in cases with parity
        # constraints to provide a reliably negative complete-source control.
        Cflip=C^1
        bad=solve(A,B,U,V,Cflip)
        assert not bad, ('parity control unexpectedly found a root',i)
        results['negative_mod2']+=1
    return results

if __name__=='__main__':
    print(f'synthetic_ring128_controls={controls()}')
