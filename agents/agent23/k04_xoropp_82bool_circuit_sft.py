#!/usr/bin/env python3
"""Source-free xoroshiro128++ output-inversion circuit with 82 primary Booleans.

Original archive files, printer data, hashes, commitments, accepted
components and candidate values are NOT imported or printed. The unanchored
model can return UNKNOWN at a finite time limit; never treat it as UNSAT.

One known y0 leaves a 64-bit state entropy. Instead of 128 independent state
bits, introduce 64 independent bits t=a0 XOR b0, 17 low bits of a0 and one
second-addition carry v17. All a0 high bits are then deterministic from y0.
The remaining low17 output equations close the carry/rotation wrap exactly.
This is an 82-Boolean *encoding*, not a claim of 82 independent state bits.
"""
from __future__ import annotations
import random
from typing import Mapping
from k04_xoropp_singleword_smt import emit, MASK, rot, _z3

def majority(a: str,b: str,c: str) -> str:
    return f'(or (and {a} {b}) (and {a} {c}) (and {b} {c}))'

def xor(*xs: str) -> str:
    xs=[x for x in xs if x!='false']
    return 'false' if not xs else xs[0] if len(xs)==1 else '(xor '+' '.join(xs)+')'

def make_circuit(observed: Mapping[int,int],
                 t_known_bits: Mapping[int,int]|None = None,
                 timeout_ms: int = 20000) -> str:
    assert 0 in observed and len(observed)>=2
    assert all(isinstance(i,int) and 0<=i<=50 and isinstance(y,int) and 0<=y<=MASK for i,y in observed.items())
    assert 100<=timeout_ms<=600000
    if t_known_bits is None:t_known_bits={}
    assert all(isinstance(k,int) and 0<=k<64 and v in (0,1) for k,v in t_known_bits.items())
    yy=observed[0]
    lines=['(set-logic QF_UF)',f'(set-option :timeout {timeout_ms})']
    def decl(n):lines.append(f'(declare-const {n} Bool)');return n
    def define(n,e):lines.append(f'(define-fun {n} () Bool {e})');return n
    t=[decl(f't_{i}') for i in range(64)]
    a0=[decl(f'a0_{i}') for i in range(17)]+[None]*47
    v17=decl('v0_17')
    for k,v in sorted(t_known_bits.items()):
        lines.append(f'(assert (= t_{k} {"true" if v else "false"}))')
    u=[define('u0_0','false')]+[None]*64
    v={17:v17}
    for j in range(17,64):
        k=j-17
        q=define(f'q0_{j}',xor(t[k],u[k]))
        a0[j]=define(f'a0_{j}',xor('true' if (yy>>j)&1 else 'false',q,v[j]))
        v[j+1]=define(f'v0_{j+1}',majority(q,a0[j],v[j]))
        u[k+1]=define(f'u0_{k+1}',f'(ite {t[k]} {u[k]} {a0[k]})')
    for k in range(47,64):
        u[k+1]=define(f'u0_{k+1}',f'(ite {t[k]} {u[k]} {a0[k]})')
    lowcarry=define('vl0_0','false')
    for j in range(17):
        q=define(f'q0_{j}',xor(t[j+47],u[j+47]))
        lines.append(f'(assert (= {xor(q,a0[j],lowcarry)} {"true" if (yy>>j)&1 else "false"}))')
        lowcarry=define(f'vl0_{j+1}',majority(q,a0[j],lowcarry))
    lines.append(f'(assert (= {lowcarry} {v17}))')
    states=[(a0,[define(f'b0_{i}',xor(a0[i],t[i])) for i in range(64)])]
    for stage in range(1,max(observed)+1):
        olda,oldb=states[-1]
        x=[define(f'x{stage-1}_{j}',xor(olda[j],oldb[j])) for j in range(64)]
        aa=[define(f'a{stage}_{j}',xor(olda[(j-49)%64],x[j],x[j-21] if j>=21 else 'false')) for j in range(64)]
        bb=[define(f'b{stage}_{j}',x[(j-28)%64]) for j in range(64)]
        states.append((aa,bb))
        if stage not in observed:continue
        carry=define(f'u{stage}_0','false')
        c=[]
        for j in range(64):
            c.append(define(f'c{stage}_{j}',xor(aa[j],bb[j],carry)))
            carry=define(f'u{stage}_{j+1}',majority(aa[j],bb[j],carry))
        carry=define(f'v{stage}_0','false')
        for j in range(64):
            lines.append(f'(assert (= {xor(c[(j-17)%64],aa[j],carry)} {"true" if (observed[stage]>>j)&1 else "false"}))')
            carry=define(f'v{stage}_{j+1}',majority(c[(j-17)%64],aa[j],carry))
    return '\n'.join([*lines,'(check-sat)'])+'\n'

def exact_initial_from_bits(y0: int,t: int,lo_a: int,carry_at17: int) -> tuple[int,int]:
    """Reconstruct full (a,b); requires model satisfying original low-wrap checks."""
    assert 0<=y0<=MASK and 0<=t<=MASK and 0<=lo_a<(1<<17) and carry_at17 in (0,1)
    a=lo_a;u=0;v=carry_at17
    for j in range(17,64):
        k=j-17
        q=((t>>k)&1)^u
        bit_a=((y0>>j)&1)^q^v
        a|=bit_a<<j
        v=(q&bit_a)|(q&v)|(bit_a&v)
        u=u if (t>>k)&1 else ((a>>k)&1)
    return a,a^t

def self_test():
    rng=random.Random(0x20261127)
    for i in range(128):
        a,b=rng.getrandbits(64),rng.getrandbits(64)
        y=emit(a,b)
        t=a^b
        c=(a+b)&MASK
        q=rot(c,17)
        carry=0
        for j in range(17):
            x=(q>>j)&1;z=(a>>j)&1
            carry=(x&z)|(x&carry)|(z&carry)
        assert exact_initial_from_bits(y[0],t,a&((1<<17)-1),carry)==(a,b)
    a,b=rng.getrandbits(64),rng.getrandbits(64)
    y=emit(a,b)
    obs={i:y[i] for i in (0,1,4,5)}
    t=a^b
    anchored={i:(t>>i)&1 for i in range(32,64)}
    positive=make_circuit(obs,anchored,12000)
    assert positive.count('(declare-const')==82
    sat=_z3(positive)
    if sat is not None:
        assert sat=='sat',f'planted 32bit-anchored four-output solver did not SAT: {sat}'
        contradicted={i:(t>>i)&1 for i in range(64)}
        altered=dict(obs);altered[1]^=1
        fail=_z3(make_circuit(altered,contradicted,12000))
        assert fail=='unsat',f'poisoned fully-anchored model did not UNSAT: {fail}'
    print('synthetic_exact_roundtrip=128/128 four-output_32bit_anchor='+('PASS' if sat is not None else 'SKIPPED_NO_LIBZ3'))

if __name__=='__main__':self_test()


# Two-phase extraction preserves the same Z3 context between check-sat and
# get-value. A single check-sat+get-value script can time out before producing
# a model even when a separate check-sat script reaches SAT.
def solve_complete(observed: Mapping[int,int], t_known_bits: Mapping[int,int]|None=None,
                   timeout_ms: int=150000) -> tuple[str,tuple[int,int,tuple[int,...]]|None]:
    import ctypes,re
    script='(set-option :sat.anf true)\n(set-option :sat.anf.exlin true)\n'+make_circuit(observed,t_known_bits,timeout_ms)
    lib=ctypes.CDLL('libz3.so.4')
    lib.Z3_mk_config.restype=ctypes.c_void_p
    lib.Z3_mk_context.argtypes=[ctypes.c_void_p]
    lib.Z3_mk_context.restype=ctypes.c_void_p
    lib.Z3_del_config.argtypes=[ctypes.c_void_p]
    lib.Z3_del_context.argtypes=[ctypes.c_void_p]
    lib.Z3_eval_smtlib2_string.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
    cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg)
    try:
        status=(lib.Z3_eval_smtlib2_string(ctx,script.encode()) or b'').decode().strip()
        assert status in ('sat','unsat','unknown'),status[:256]
        if status!='sat':return status,None
        names=[*(f't_{i}' for i in range(64)),*(f'a0_{i}' for i in range(17)),'v0_17']
        m=(lib.Z3_eval_smtlib2_string(ctx,f'(get-value ({" ".join(names)}))'.encode()) or b'').decode()
        d={k:int(v=='true') for k,v in re.findall(r'\((t_\d+|a0_\d+|v0_17)\s+(true|false)\)',m)}
        assert all(n in d for n in names),f'missing model fields {len(d)} of {len(names)}'
        t=sum(d[f't_{i}']<<i for i in range(64))
        lo=sum(d[f'a0_{i}']<<i for i in range(17))
        a,b=exact_initial_from_bits(observed[0],t,lo,d['v0_17'])
        out=emit(a,b,max(observed)+1)
        assert all(out[i]==y for i,y in observed.items()),'independent complete model replay failed'
        return status,(a,b,out)
    finally:
        lib.Z3_del_context(ctx);lib.Z3_del_config(cfg)

if __name__=='__main__':
    import sys
    if '--slow-unanchored' in sys.argv:
        import time
        rng=random.Random(20261127)
        a,b=rng.getrandbits(64),rng.getrandbits(64)
        ys=emit(a,b)
        start=time.monotonic()
        status,witness=solve_complete({i:ys[i] for i in (0,1,4,5)},timeout_ms=150000)
        assert status=='sat' and witness is not None
        aa,bb,outputs=witness
        assert (a,b)==(aa,bb) and outputs[2:4]==ys[2:4]
        print('unanchored_synthetic_middle_state_exact=PASS seconds=',round(time.monotonic()-start,3))
