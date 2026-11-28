#!/usr/bin/env python3
"""Source-free compact exact first-two-output xoroshiro128++ P16 state solver.

The two genuine 64-bit output words, no later outputs, no original records:
only 64 initial-a0 Boolean variables remain. Four unused future xoroshiro
transition rounds are omitted from the output-conditioned circuit. Every SAT
model is integer-native replayed and explicitly blocked to a terminal status.
UNSAT after model blocking certifies an exact empty P16 cube; UNKNOWN does not.
"""
import ctypes,json,random,re
M=(1<<64)-1
P12=(0,1,2,3,22,23,24,25,45,46,47,48)
P16=P12+(4,5,6,7)

def rol(x,n):
    return ((x<<n)|(x>>(64-n)))&M

def ror(x,n):
    return ((x>>n)|(x<<(64-n)))&M

def stream(a,b,n=64):
    out=[]
    for _ in range(n):
        out.append((rol((a+b)&M,17)+a)&M)
        t=a^b
        a,b=rol(a,49)^t^((t<<21)&M),rol(t,28)
    return out

def xor(*xs):
    xs=[x for x in xs if x!='false']
    return 'false' if not xs else (xs[0] if len(xs)==1 else '(xor '+' '.join(xs)+')')

def circuit(first,anchor,positions,timeout_ms):
    """The exact first two output constraints, no unused future state."""
    lines=['(set-logic QF_UF)','(set-option :sat.anf true)',
           '(set-option :sat.anf.exlin true)',f'(set-option :timeout {timeout_ms})']
    def put(name,expr):
        lines.append(f'(define-fun {name} () Bool {expr})')
        return name
    def implied_t(a,y,s):
        v=['false']*64
        for j in range(63):
            v[j+1]=put(f'v{s}_{j+1}',
                       f'({"and" if (y>>j)&1 else "or"} {a[j]} {v[j]})')
        u=['false']*64;t=[]
        for k in range(64):
            j=(k+17)&63
            tk=put(f't{s}_{k}',xor(a[j],v[j],u[k],
                       'true' if (y>>j)&1 else 'false'))
            t.append(tk)
            if k<63:
                u[k+1]=put(f'u{s}_{k+1}',f'(ite {tk} {u[k]} {a[k]})')
        return t
    a0=[f'a0_{i}' for i in range(64)]
    lines.extend(f'(declare-const {x} Bool)' for x in a0)
    t0=implied_t(a0,first[0],0)
    a1=[put(f'a1_{j}',xor(a0[(j-49)&63],t0[j],
                         t0[j-21] if j>=21 else 'false'))
        for j in range(64)]
    t1=[put(f'tf1_{j}',xor(a1[j],t0[(j-28)&63]))
        for j in range(64)]
    require=implied_t(a1,first[1],1)
    lines.extend(f'(assert (= {t1[j]} {require[j]}))' for j in range(64))
    lines.extend(f'(assert (= a0_{j} {"true" if (anchor>>j)&1 else "false"}))'
                 for j in positions)
    lines.append('(check-sat)')
    return '\n'.join(lines)+'\n'

def exact_states(first,cube,timeout_ms=350,max_models=32):
    assert len(first)==2 and 0<=cube<65536
    assert 100<=timeout_ms<=30000 and 1<=max_models<=1024
    anchor=sum(((cube>>j)&1)<<p for j,p in enumerate(P16))
    lib=ctypes.CDLL('libz3.so.4')
    P=ctypes.c_void_p
    lib.Z3_mk_config.restype=P
    lib.Z3_mk_context.argtypes=[P]
    lib.Z3_mk_context.restype=P
    lib.Z3_del_config.argtypes=[P]
    lib.Z3_del_context.argtypes=[P]
    lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
    cfg=lib.Z3_mk_config()
    ctx=lib.Z3_mk_context(cfg)
    lib.Z3_del_config(cfg)
    def ask(s):
        return (lib.Z3_eval_smtlib2_string(ctx,s.encode()) or b'').decode().strip()
    try:
        status=ask(circuit(first,anchor,P16,timeout_ms))
        states=[]
        while status=='sat':
            model=ask('(get-value ('+
                      ' '.join(f'a0_{j}' for j in range(64))+'))')
            bits={int(j):int(v=='true') for j,v in re.findall(
                r'\(a0_(\d+)\s+(true|false)\)',model)}
            if len(bits)!=64:
                raise AssertionError('Incomplete 64-bit initial-state model')
            a=sum(bits[j]<<j for j in range(64))
            b=(ror((first[0]-a)&M,17)-a)&M
            assert stream(a,b,2)==list(first)
            assert all(((a>>p)&1)==((cube>>j)&1)
                       for j,p in enumerate(P16))
            states.append((a,b))
            if len(states)>=max_models:
                return states,'unknown'
            block=' '.join(f'(not a0_{j})' if bits[j] else f'a0_{j}'
                           for j in range(64))
            ask('(assert (or '+block+'))')
            status=ask('(check-sat)')
        if status not in ('unsat','unknown'):
            raise RuntimeError('Unexpected solver disposition '+status[:200])
        return states,status
    finally:
        lib.Z3_del_context(ctx)

def synthetic_controls():
    checked=0
    for seed in (20261128,20261129,20261130,2199,5311):
        rng=random.Random(seed)
        a,b=rng.getrandbits(64),rng.getrandbits(64)
        first=stream(a,b,2)
        cube=sum(((a>>p)&1)<<j for j,p in enumerate(P16))
        states,terminal=exact_states(first,cube,5000)
        assert terminal=='unsat' and (a,b) in states,(seed,terminal,len(states))
        checked+=1
    # Agent37's source-free same-firstpacket collision: two distinct full
    # 128-bit initial states must survive in different P16 subcubes.
    twins=((0xB02543CFB686BB4A,0xF9DA21F56A996103),
           (0xCE695E4122B2739A,0xFF6DF861F134F29D))
    twinfirst=stream(*twins[0],2)
    assert stream(*twins[1],2)==twinfirst
    recovered=set()
    for true in twins:
        cube=sum(((true[0]>>p)&1)<<j for j,p in enumerate(P16))
        models,status=exact_states(twinfirst,cube,10000)
        assert status=='unsat' and true in models
        recovered.update(models)
    assert set(twins).issubset(recovered) and len(recovered)==2
    print(json.dumps({'source_free':True,'planted_complete_state_recoveries':checked,
        'same_firstpacket_two_distinct_states_recovered':True,
        'exact_terminal_UNSAT_after_model_blocking':checked,
        'future_transition_rounds_unconstrained':0,
        'original_sources_read':False},sort_keys=True))

if __name__=='__main__':
    synthetic_controls()
