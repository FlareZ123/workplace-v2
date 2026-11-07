"""SFT for two erased REC8 slots under a shared bytewise GF(256) order-3 recurrence."""
from __future__ import annotations
import json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLYS = (0x11B, 0x11D)
KNOWN = {
    "K01":"049AAB2E1CDE7A82CD7C60234303C91A",
    "K02":"0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03":"1384AF96E25D6ADA666209CB55E062FA",
    "K05":"FF8B78200A56E8586DCDA00EF01E4572",
    "K06":"5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07":"93495F5E425AB8E592123DABAEB68545",
}
TARGETS = {
    "K04":"930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0",
    "K08":"285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747",
}

def m(a,b,p):
    r=0; red=p&255
    for _ in range(8):
        if b&1:r^=a
        hi=a&128
        a=((a<<1)&255)^(red if hi else 0); b>>=1
    return r

def pw(a,n,p):
    r=1
    while n:
        if n&1:r=m(r,a,p)
        a=m(a,a,p); n>>=1
    return r

def inv(a,p):
    if not a: raise ZeroDivisionError
    return pw(a,254,p)

def rank2(rows,p):
    return any(m(x,v,p)^m(u,y,p) for i,(x,u,_) in enumerate(rows)
               for y,v,_ in rows[i+1:])

def solve2(rows,p):
    for i,(x1,y1,z1) in enumerate(rows):
        for x2,y2,z2 in rows[i+1:]:
            d=m(x1,y2,p)^m(x2,y1,p)
            if not d: continue
            di=inv(d,p)
            a=m(m(z1,y2,p)^m(z2,y1,p),di,p)
            b=m(m(x1,z2,p)^m(x2,z1,p),di,p)
            if all((m(x,a,p)^m(y,b,p))==z for x,y,z in rows):
                return a,b
    return None

def ratio(numer,denom,p):
    for n,d in zip(numer,denom):
        if d:
            q=m(n,inv(d,p),p)
            return q if all(m(q,x,p)==y for x,y in zip(denom,numer)) else None
    return None

def solve_order3(cs,p):
    k1,k2,k3,k5,k6,k7=[cs[i] for i in (0,1,2,4,5,6)]
    out=set()
    def add(a,b,c):
        k4=bytes(m(a,k3[j],p)^m(b,k2[j],p)^m(c,k1[j],p) for j in range(16))
        k8=bytes(m(a,k7[j],p)^m(b,k6[j],p)^m(c,k5[j],p) for j in range(16))
        for j in range(16):
            if m(a,k4[j],p)^m(b,k3[j],p)^m(c,k2[j],p)!=k5[j]: return
            if m(a,k5[j],p)^m(b,k4[j],p)^m(c,k3[j],p)!=k6[j]: return
            if m(a,k6[j],p)^m(b,k5[j],p)^m(c,k4[j],p)!=k7[j]: return
        out.add((a,b,c,k4,k8))
    for a in range(1,256):
        a2=m(a,a,p)
        for b in range(1,256):
            b2=m(b,b,p); c=None; impossible=False
            for j in range(16):
                d=m(b,k2[j],p)^m(a,k3[j],p)
                n=m(a,k6[j],p)^m(a2,k5[j],p)^m(b,k5[j],p)^m(b2,k3[j],p)
                if d:c=m(n,inv(d,p),p);break
                if n:impossible=True;break
            if impossible:continue
            candidates=range(1,256) if c is None else ((c,) if c else ())
            for c in candidates:
                good=True
                for j in range(16):
                    q=k5[j]^m(b,k3[j],p)^m(c,k2[j],p)
                    if m(b,q,p)!=m(a,k6[j]^m(a,k5[j],p)^m(c,k3[j],p),p):good=False;break
                    if m(c,q,p)!=m(a,k7[j]^m(a,k6[j],p)^m(b,k5[j],p),p):good=False;break
                if good:add(a,b,c)
    ra=[(k3[j],k2[j],k5[j]) for j in range(16)]
    rb=[(k5[j],k3[j],k6[j]) for j in range(16)]
    rc=[(k6[j],k5[j],k7[j]) for j in range(16)]
    assert rank2(ra,p) and rank2(rb,p) and rank2(rc)
    pair=solve2(ra,p)
    if pair:
        b,c=pair
        if b and c:
            k4=bytes(m(k6[j]^m(c,k3[j],p),inv(b,p),p) for j in range(16))
            if all((m(b,k5[j],p)^m(c,k4[j],p))==k7[j] for j in range(16)):
                out.add((0,b,c,k4,bytes(m(b,k6[j],p)^m(c,k5[j],p) for j in range(16))))
    pair=solve2(rb,p)
    if pair:
        a,c=pair
        if a and c:
            k4=bytes(m(k5[j]^m(c,k2[j],p),inv(a,p),p) for j in range(16))
            if all((m(a,k6[j],p)^m(c,k4[j],p))==k7[j] for j in range(16)):
                out.add((a,0,c,k4,bytes(m(a,k7[j],p)^m(c,k5[j],p) for j in range(16))))
    pair=solve2(rc,p)
    if pair:
        a,b=pair
        if a and b:
            k4=bytes(m(k5[j]^m(b,k3[j],p),inv(a,p),p) for j in range(16))
            if all((m(a,k5[j],p)^m(b,k4[j],p))==k6[j] for j in range(16)):
                out.add((a,b,0,k4,bytes(m(a,k7[j],p)^m(b,k6[j],p) for j in range(16))))
    c=ratio(k5,k2,p)
    if c and all(m(c,k3[j],p)==k6[j] for j in range(16)):
        k4=bytes(m(k7[j],inv(c,p),p) for j in range(16))
        if all(m(c,k4[j],p)==k7[j] for j in range(16)):
            out.add((0,0,c,k4,bytes(m(c,k5[j],p) for j in range(16))))
    b=ratio(k5,k3,p)
    if b and all(m(b,k5[j],p)==k7[j] for j in range(16)):
        k4=bytes(m(k6[j],inv(b,p),p) for j in range(16))
        if all(m(b,k4[j],p)==k6[j] for j in range(16)):
            out.add((0,b,0,k4,bytes(m(b,k6[j],p) for j in range(16))))
    a=ratio(k6,k5,p)
    if a and all(m(a,k6[j],p)==k7[j] for j in range(16)):
        k4=bytes(m(k5[j],inv(a,p),p) for j in range(16))
        if all(m(a,k4[j],p)==k5[j] for j in range(16)):
            out.add((a,0,0,k4,bytes(m(a,k7[j],p) for j in range(16))))
    if not any(k5+k6+k7):out.add((0,0,0,bytes(16),bytes(16)))
    return list(out)

def reverse_k08(k5,k6,k7,a,b,c,p):
    return bytes(m(k5[j]^m(a,k6[j],p)^m(b,k7[j],p),inv(c,p),p) for j in range(16))

def sequence(a,b,c,p,seed):
    rng=random.Random(seed)
    s=[bytes(rng.randrange(256) for _ in range(16)) for _ in range(3)]
    for i in range(3,8):
        s.append(bytes(m(a,s[i-1][j],p)^m(b,s[i-2][j],p)^m(c,s[i-3][j],p) for j in range(16)))
    return s

def synthetic():
    patterns=((60,201,82),(0,73,141),(51,0,92),(13,201,0))
    count=0
    for p in POLYS:
        for i,(a,b,c) in enumerate(patterns):
            s=sequence(a,b,c,p,0x3A128+i)
            cs=[s[j] if j not in (3,7) else None for j in range(8)]
            assert any((aa,bb,cc)==(a,b,c) and x==s[3] and y==s[7]
                       for aa,bb,cc,x,y in solve_order3(cs,p))
            count+=1
        for i,(a,b,c) in enumerate(patterns[:3]):
            z=sequence(a,b,c,p,0x4B219+i)
            cs=[z[0],z[1],z[2],None,z[4],z[5],z[6],None]
            k8=reverse_k08(z[2],z[1],z[0],a,b,c,p)
            assert any((aa,bb,cc)==(a,b,c) and x==z[3]
                       and reverse_k08(z[2],z[1],z[0],aa,bb,cc,p)==k8
                       for aa,bb,cc,x,_ in solve_order3(cs,p))
            count+=1
    print(f"SYNTHETIC: {count} forward/reverse controls PASS")

def original():
    cand=json.loads((ROOT/"candidate.json").read_text())
    acc=json.loads((ROOT/"acceptance.json").read_text())
    assert {k:cand[k] for k in KNOWN}==KNOWN
    assert cand["K04"] is None and cand["K08"] is None
    assert acc["slot_sha256"]["K04"]==TARGETS["K04"]
    assert acc["slot_sha256"]["K08"]==TARGETS["K08"]
    cs=[bytes.fromhex(cand[f"K{i:02d}"]) if cand.get(f"K{i:02d}") else None for i in range(1,9)]
    rev=[cs[6],cs[5],cs[4],None,cs[2],cs[1],cs[0],None]
    for p in POLYS:
        fwd=solve_order3(cs,p)
        backward=solve_order3(rev,p)
        recoverable=[(a,b,c,x,reverse_k08(cs[4],cs[5],cs[6],a,b,c,p))
                     for a,b,c,x,_ in backward if c]
        assert not fwd and not recoverable
        print(f"GF(256) 0x{p:X}: forward=0, reverse-recoverable=0")
    print("RESULT: no tested shared bytewise GF(256) order-3 recurrence recovers K04/K08")

if __name__=="__main__":
    synthetic()
    original()
