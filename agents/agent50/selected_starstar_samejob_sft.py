"""Full original K04 selected-job **-scrambler inversion SFT (Agent 50).

Use historical job PS-261003-0417 REQUESTED attempts 1 and 3 as two
source witnesses. Withhold disputed ACK attempt 2 during model fitting.
Produce complete hypothetical middle attempt 2 coupon and check untouched
K04 SHA256 after recorded mask XOR. Includes exact synthetic positives.
"""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spool=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
routing=json.loads((ROOT/"resources/evidence/recovery-routing.json").read_text())
accept=json.loads((ROOT/"resources/acceptance.json").read_text())
sha=hashlib.sha256(spool).hexdigest()
assert sha=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
mask=bytes.fromhex(routing["K04"]["masked_component"])
target=accept["slot_sha256"]["K04"]
lines=spool.decode().splitlines()
source=[]
for attempt in (1,3):
    rows=[line for line in lines
          if f"JOB=PS-261003-0417 ATTEMPT={attempt} STATE=REQUESTED CLASS=RECOVER" in line]
    assert len(rows)==1,(attempt,rows)
    source.append(bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})",rows[0]).group(1)))
assert [s.hex().upper() for s in source]==[
  "CD3E4F216ADB2FB180DA2AA90B33F7A4",
  "44D53DFC29D7943A95D89371DA58EC64"]
assert len(mask)==16

MOD=1<<64;M=MOD-1
INVERSE5=pow(5,-1,MOD)
INVERSE9=pow(9,-1,MOD)

def rol(x,n):return ((x<<n)|(x>>(64-n)))&M
def ror(x,n):return ((x>>n)|(x<<(64-n)))&M
def scramble(x):return (rol((x*5)&M,7)*9)&M
def uns(x):return (ror((x*INVERSE9)&M,7)*INVERSE5)&M

def raw_words(blob,endian,swap):
    left,right=blob[:8],blob[8:]
    if swap:left,right=right,left
    return (int.from_bytes(left,endian),int.from_bytes(right,endian))

def raw_bytes(pair,endian,swap):
    left,right=pair
    if swap:left,right=right,left
    return left.to_bytes(8,endian)+right.to_bytes(8,endian)

def reduced_coupon(pair,endian,swap):
    physical=raw_bytes(pair,endian,swap)
    return bytes(x^y for x,y in zip(physical,mask))

def original_match(component):return hashlib.sha256(component).hexdigest()==target

def xoro_next(state,c):
    a,b=state
    l,q,r=c
    x=a^b
    return scramble(a),((rol(a,l)^x^((x<<q)&M))&M,rol(x,r))

def xoro_recover(first,second,c):
    s0=uns(first);later=uns(second)
    l,q,r=c
    rhs=later^rol(s0,l)
    delta=rhs
    for _ in range(7):delta=rhs^((delta<<q)&M)
    assert delta^((delta<<q)&M)==rhs
    return (s0,delta^s0)

# Reversible 64-bit scrambler controls, including high-bit edge cases.
for x in (0,1,2,3,5,9,0x8000000000000000,0x1234567890ABCDEF,M):
    assert uns(scramble(x))==x

# Genuine planted same-job history with 31/48 hidden generator outputs.
p=(24,16,37)
real_initial=(0x0123456789ABCDEF,0xFEDCBA9876543210)
real=[];st=real_initial
for _ in range(2+31+2+48+2):
    val,st=xoro_next(st,p);real.append(val)
reconstructed=xoro_recover(real[0],real[1],p)
assert reconstructed==real_initial
history=[];st=reconstructed
for _ in range(len(real)):
    val,st=xoro_next(st,p);history.append(val)
assert history[33:35]==real[33:35] and history[83:85]==real[83:85]
plant=reduced_coupon(history[33:35],"big",False)
assert hashlib.sha256(plant).digest()==hashlib.sha256(reduced_coupon(real[33:35],"big",False)).digest()

out={"original_spool_sha256":sha,"selected_job":"PS-261003-0417",
     "source_attempts":[1,3],"unknown_selected_attempt":2,"xoro":{},
     "xoshiro":{},"original_k04_hits":[],"positive_controls":"PASS"}
for name,c in [("xoroshiro128starstar2018",(24,16,37)),
               ("xoroshiro128starstar2016hypothetical",(55,14,36))]:
    checks=0;source_controls=0
    for endian in ("big","little"):
        for swap in (False,True):
            first=raw_words(source[0],endian,swap)
            third=raw_words(source[1],endian,swap)
            state=xoro_recover(*first,c)
            words=[];st=state
            for _ in range(2+2*256+2+2):
                w,st=xoro_next(st,c);words.append(w)
            assert tuple(words[:2])==first
            for gap1 in range(257):
                comp=reduced_coupon(words[2+gap1:4+gap1],endian,swap)
                checks+=1
                if original_match(comp):
                    out["original_k04_hits"].append([name,endian,swap,gap1,comp.hex().upper()])
            for total_gap in range(513):
                source_controls+=1
                if tuple(words[4+total_gap:6+total_gap])==third:
                    out.setdefault("later_source_matches",[]).append(
                        [name,endian,swap,total_gap])
    out["xoro"][name]={"full_original_k04_checks":checks,
                       "complete_later_source_packet_checks":source_controls}

def xoshiro_next(st):
    a,b,c,d=st
    result=scramble(b)
    t=(b<<17)&M
    c^=a;d^=b;b^=c;a^=d;c^=t;d=rol(d,45)
    return result,(a,b,c,d)

def coeff_s1(n):
    s=[[1<<(64*k+j) for j in range(64)] for k in range(4)]
    result=[]
    for _ in range(n):
        a,b,c,d=s
        result.append(tuple(b))
        t=[b[j-17] if j>=17 else 0 for j in range(64)]
        c1=[c[j]^a[j] for j in range(64)]
        d1=[d[j]^b[j] for j in range(64)]
        b1=[b[j]^c1[j] for j in range(64)]
        a1=[a[j]^d1[j] for j in range(64)]
        c2=[c1[j]^t[j] for j in range(64)]
        d2=[d1[(j-45)%64] for j in range(64)]
        s=[a1,b1,c2,d2]
    return result

def affine_solution(rows,bits):
    pivots={}
    for row,bit in zip(rows,bits):
        x=row;y=bit
        while x:
            i=x.bit_length()-1
            if i not in pivots:
                pivots[i]=(x,y);break
            u,v=pivots[i];x^=u;y^=v
        else:
            if y:return len(pivots),None,None
    free=[i for i in range(256) if i not in pivots]
    def solve_from(initial):
        state=initial
        for i in sorted(pivots):
            x,y=pivots[i]
            if y^((x&state).bit_count()&1):state|=1<<i
        return state
    particular=solve_from(0)
    nullspace=[solve_from(1<<i)^particular for i in free]
    return len(pivots),particular,nullspace

def index_coeffs(coefficient,indices):
    return [v for i in indices for v in coefficient[i]]

def exact_state_bits(words):
    return [(uns(w)>>i)&1 for w in words for i in range(64)]

def generated(seed,limit):
    st=tuple((seed>>(64*k))&M for k in range(4))
    values=[]
    for _ in range(limit):
        v,st=xoshiro_next(st);values.append(v)
    return values

COEFF=coeff_s1(520)

# Planted nonlinear scrambler source endpoints -> complete missing coupon.
planted=0x0123456789ABCDEFFEDCBA987654321000112233445566778899AABBCCDDEEFF
gap1,gap2=31,48
pi=[0,1,4+gap1+gap2,5+gap1+gap2]
known=generated(planted,max(pi)+1)
rank,particular,basis=affine_solution(index_coeffs(COEFF,pi),
                                     exact_state_bits([known[i] for i in pi]))
assert basis is not None and rank>=253
assert planted in [particular ^ (basis[0] if k&1 else 0)
                   for k in range(1<<len(basis))]
synthetic_component=reduced_coupon(known[2+gap1:4+gap1],"big",False)
synthetic_target=hashlib.sha256(synthetic_component).digest()
synthetic_hits=0
for assignment in range(1<<len(basis)):
    seed=particular
    for b in range(len(basis)):
        if assignment&(1<<b):seed^=basis[b]
    proposed=generated(seed,2+gap1+2)
    val=reduced_coupon(proposed[2+gap1:4+gap1],"big",False)
    if hashlib.sha256(val).digest()==synthetic_target:
        assert val==synthetic_component
        synthetic_hits+=1
assert synthetic_hits==1

counts=Counter()
for endian in ("big","little"):
    for swap in (False,True):
        observed=[v for r in source for v in raw_words(r,endian,swap)]
        bits=exact_state_bits(observed)
        for h in range(513):
            indices=[0,1,4+h,5+h]
            rows=index_coeffs(COEFF,indices)
            rank,particular,basis=affine_solution(rows,bits)
            counts["models"]+=1
            if basis is None:continue
            counts["compatible_models"]+=1
            counts[f"nullspace_dimension_{len(basis)}"]+=1
            lo=max(0,h-256);hi=min(256,h)
            state=particular
            for assignment in range(1<<len(basis)):
                if assignment:
                    state^=basis[(assignment&-assignment).bit_length()-1]
                counts["complete_state_assignments"]+=1
                predicted=generated(state,max(indices)+1)
                assert [predicted[i] for i in indices]==observed
                for g1 in range(lo,hi+1):
                    comp=reduced_coupon(predicted[2+g1:4+g1],endian,swap)
                    counts["complete_k04_sha256_checks"]+=1
                    if original_match(comp):
                        out["original_k04_hits"].append(
                            ["xoshiro256starstar",endian,swap,h,g1,comp.hex().upper()])
out["xoshiro"]=dict(counts)
out["total_original_k04_checks"]=sum(v["full_original_k04_checks"] for v in out["xoro"].values())+counts["complete_k04_sha256_checks"]

# 32-bit xoshiro128** complete 128-bit state inverse via four source words.
M32=(1<<32)-1
I5_32=pow(5,-1,1<<32)
I9_32=pow(9,-1,1<<32)

def rol32(x,n):return ((x<<n)|(x>>(32-n)))&M32
def ror32(x,n):return ((x>>n)|(x<<(32-n)))&M32
def scr32(x):return (rol32(x*5&M32,7)*9)&M32
def uns32(x):return (ror32(x*I9_32&M32,7)*I5_32)&M32

def next32(st):
    a,b,c,d=st;res=scr32(b);t=b<<9&M32
    c^=a;d^=b;b^=c;a^=d;c^=t;d=rol32(d,11)
    return res,(a,b,c,d)

def coeff32():
    s=[[1<<(32*k+j) for j in range(32)] for k in range(4)]
    rows=[]
    for _ in range(4):
        a,b,c,d=s
        rows.extend(b)
        t=[b[j-9] if j>=9 else 0 for j in range(32)]
        c1=[c[j]^a[j] for j in range(32)]
        d1=[d[j]^b[j] for j in range(32)]
        b1=[b[j]^c1[j] for j in range(32)]
        a1=[a[j]^d1[j] for j in range(32)]
        s=[a1,b1,[c1[j]^t[j] for j in range(32)],
           [d1[(j-11)%32] for j in range(32)]]
    return rows

ROW32=coeff32()

def invert32(first):
    rights=[(uns32(x)>>j)&1 for x in first for j in range(32)]
    basis={}
    for row,rhs in zip(ROW32,rights):
        v=row;b=rhs
        while v:
            i=v.bit_length()-1
            if i not in basis:
                basis[i]=(v,b)
                break
            x,y=basis[i];v^=x;b^=y
        else:assert b==0
    assert len(basis)==128
    state=0
    for i in sorted(basis):
        v,b=basis[i]
        if b^((v&state).bit_count()&1):state|=1<<i
    return tuple((state>>(32*k))&M32 for k in range(4))

def parse32(block,endian,reverse):
    values=[int.from_bytes(block[j:j+4],endian) for j in range(0,16,4)]
    if reverse:values.reverse()
    return values

def pack32(values,endian,reverse):
    values=list(values)
    if reverse:values.reverse()
    return b"".join(x.to_bytes(4,endian) for x in values)

# Genuine first-packet state inversion, selected and later source stages.
first_state=(0x12345678,0x9ABCDEF0,0x01234567,0x89ABCDEF)
values=[];st=first_state
for _ in range(12+35+37):
    v,st=next32(st);values.append(v)
st=invert32(values[:4])
assert st==first_state
replay=[]
for _ in range(len(values)):
    v,st=next32(st);replay.append(v)
assert replay[39:43]==values[39:43]
assert replay[80:84]==values[80:84]
synthetic=bytes(x^y for x,y in zip(pack32(values[39:43],"little",False),mask))
recovered=bytes(x^y for x,y in zip(pack32(replay[39:43],"little",False),mask))
assert hashlib.sha256(synthetic).digest()==hashlib.sha256(recovered).digest()

x128_ks=0;x128_source=0;x128_hits=[];x128_later=[]
for endian in ("big","little"):
    for reverse in (False,True):
        early=parse32(source[0],endian,reverse)
        later=parse32(source[1],endian,reverse)
        state=invert32(early)
        predicted=[]
        for _ in range(8+512+4):
            v,state=next32(state);predicted.append(v)
        assert early==predicted[:4]
        for gap in range(257):
            physical=pack32(predicted[4+gap:8+gap],endian,reverse)
            component=bytes(a^b for a,b in zip(physical,mask))
            x128_ks+=1
            if original_match(component):
                x128_hits.append([endian,reverse,gap,component.hex().upper()])
        for g in range(513):
            x128_source+=1
            if predicted[8+g:12+g]==later:
                x128_later.append([endian,reverse,g])
out["xoshiro128starstar"]={"full_original_k04_checks":x128_ks,
                           "complete_later_source_packet_checks":x128_source,
                           "original_k04_hits":x128_hits,"later_source_matches":x128_later}
out["total_original_k04_checks"]+=x128_ks

print(json.dumps(out,indent=2))
