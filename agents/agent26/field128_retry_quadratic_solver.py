"""Pure finite-field cubic inversion for quadratic state transitions.

No original recovery inputs, historic coupons, source paths or target hashes.
Given observed A->B, U->V, B->X, X->C, recover all field-valued X
from an unknown quadratic T(z)=a*z^2+b*z+c by factoring a cubic.
Standalone synthetic examples only; no archive or facility interaction.
"""
from __future__ import annotations
import hashlib
P=(1<<128)-159
FIELD_MASK=(1<<128)-1
POLY=0x87

class Field:
    def __init__(self,kind):
        self.kind=kind
        self.p=P if kind=='prime' else 1<<128
        self.binary=(kind=='binary')
    def add(self,a,b):return a^b if self.binary else (a+b)%P
    def sub(self,a,b):return a^b if self.binary else (a-b)%P
    def neg(self,a):return a if self.binary else (-a)%P
    def mul(self,a,b):
        if not self.binary:return a*b%P
        ans=0
        while b:
            if b&1:ans^=a
            b>>=1
            a=((a<<1)^(POLY if a>>127 else 0))&FIELD_MASK
        return ans
    def pow(self,a,e):
        out=1
        while e:
            if e&1:out=self.mul(out,a)
            e>>=1
            if e:a=self.mul(a,a)
        return out
    def inv(self,a):
        if not a:raise ZeroDivisionError
        return self.pow(a,(1<<128)-2) if self.binary else pow(a,-1,P)
    def div(self,a,b):return self.mul(a,self.inv(b))
    def normalize(self,a):return a if self.binary else a%P

class Poly:
    def __init__(self,F):self.F=F
    def trim(self,p):
        p=list(p)
        while len(p)>1 and p[-1]==0:p.pop()
        return p
    def deg(self,p):return len(self.trim(p))-1
    def add(self,p,q):
        F=self.F;n=max(len(p),len(q));return self.trim([F.add(p[i] if i<len(p) else 0,q[i] if i<len(q) else 0) for i in range(n)])
    def sub(self,p,q):
        F=self.F;n=max(len(p),len(q));return self.trim([F.sub(p[i] if i<len(p) else 0,q[i] if i<len(q) else 0) for i in range(n)])
    def mul(self,p,q):
        F=self.F;out=[0]*(len(p)+len(q)-1)
        for i,a in enumerate(p):
            if not a:continue
            for j,b in enumerate(q):
                if b:out[i+j]=F.add(out[i+j],F.mul(a,b))
        return self.trim(out)
    def divmod(self,p,q):
        F=self.F;p=self.trim(p);q=self.trim(q)
        if q==[0]:raise ZeroDivisionError
        if len(p)<len(q):return [0],p
        out=[0]*(len(p)-len(q)+1);inv=F.inv(q[-1])
        while p!=[0] and len(p)>=len(q):
            shift=len(p)-len(q);coef=F.mul(p[-1],inv)
            out[shift]=coef
            for i,b in enumerate(q):p[i+shift]=F.sub(p[i+shift],F.mul(coef,b))
            p=self.trim(p)
        return self.trim(out),p
    def mod(self,p,q):return self.divmod(p,q)[1]
    def gcd(self,p,q):
        F=self.F
        while q!=[0]:p,q=q,self.mod(p,q)
        if p==[0]:return [0]
        inv=F.inv(p[-1]);return self.trim([F.mul(v,inv) for v in p])
    def powmod(self,b,e,m):
        out=[1]
        while e:
            if e&1:out=self.mod(self.mul(out,b),m)
            e>>=1
            if e:b=self.mod(self.mul(b,b),m)
        return out
    def root_linear(self,p):return self.F.div(self.F.neg(p[0]),p[1])
    def split(self,g):
        F=self.F;d=self.deg(g)
        if d==0:return []
        if d==1:return [self.root_linear(g)]
        for seed in range(1,50):
            a=F.normalize(int.from_bytes(hashlib.sha256(f'{F.kind}:split:{seed}'.encode()).digest()[:16],'big'))
            if F.binary:
                v=[0,a]; t=[0]
                for _ in range(128):
                    t=self.add(t,v)
                    v=self.mod(self.mul(v,v),g)
                g0=self.gcd(g,t)
            else:
                h=self.powmod([a,1],(P-1)//2,g)
                g0=self.gcd(g,self.sub(h,[1]))
            if 0<self.deg(g0)<d:
                quot,rem=self.divmod(g,g0)
                assert rem==[0]
                return self.split(g0)+self.split(quot)
        raise RuntimeError('could not split fully separable polynomial')
    def roots(self,p):
        x=[0,1];F=self.F
        # GCD(f, x^q-x) eliminates non-field and multiple roots.
        if F.binary:
            v=x
            for _ in range(128):v=self.mod(self.mul(v,v),p)
        else:v=self.powmod(x,P,p)
        g=self.gcd(p,self.sub(v,x))
        roots=self.split(g)
        assert len(set(roots))==len(roots)
        for r in roots:
            val=0
            for coefficient in reversed(p):val=F.add(F.mul(val,r),coefficient)
            assert val==0
        return sorted(roots)

def candidate_roots(A,B,U,V,C,kind):
    F=Field(kind);Q=Poly(F)
    if A==U:return []
    # Linear interpolant L(A)=B, L(U)=V; all quadratics satisfying both
    # equal L(z)+a*(z-A)*(z-U), with arbitrary leading coefficient a.
    m=F.div(F.sub(B,V),F.sub(A,U))
    k=F.sub(B,F.mul(m,A))
    x0=F.add(F.mul(m,B),k)
    qB=F.mul(F.sub(B,A),F.sub(B,U))
    if qB==0:return [] # source degeneracy: no unique a from X
    # (X-x0)*(X-A)*(X-U)+qB*(m*X+k-C)=0
    poly=Q.add(Q.mul(Q.mul([F.neg(x0),1],[F.neg(A),1]),[F.neg(U),1]),[F.mul(qB,F.sub(k,C)),F.mul(qB,m)])
    assert Q.deg(poly)==3
    roots=Q.roots(poly)
    recovered=[]
    for X in roots:
        a=F.div(F.sub(X,x0),qB)
        b=F.sub(m,F.mul(a,F.add(A,U)))
        c=F.add(k,F.mul(a,F.mul(A,U)))
        f=lambda z:F.add(F.add(F.mul(a,F.mul(z,z)),F.mul(b,z)),c)
        assert f(A)==B and f(U)==V and f(B)==X and f(X)==C
        recovered.append(X)
    return recovered

def synthetic_controls():
    count=0
    for kind in ('binary','prime'):
        F=Field(kind)
        for i in range(30):
            def h(tag):
                return F.normalize(int.from_bytes(hashlib.sha256(
                    f'fixture:{tag}:{kind}:{i}'.encode()).digest()[:16], 'big'))
            A,U=h('A'),h('U')
            if A==U: U=F.add(U,1)
            a,b,c=h('a'),h('b'),h('c')
            T=lambda z:F.add(F.add(F.mul(a,F.mul(z,z)),F.mul(b,z)),c)
            B,V=T(A),T(U)
            X,C=T(B),T(T(B))
            roots=candidate_roots(A,B,U,V,C,kind)
            assert X in roots, (kind,i)
            assert 1<=len(roots)<=3
            count+=1
    return count

if __name__=='__main__':
    print(f'synthetic_quadratic_fullstate_controls_pass={synthetic_controls()}')
