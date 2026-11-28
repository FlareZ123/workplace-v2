#!/usr/bin/env python3
"""Source-free incremental P16 solver sharing one P12 Z3 context.

The first two xoroshiro128++ 64-bit outputs impose two exact constraints.
Every P12 parent has 16 disjoint P16 child cubes. Load the same circuit
ONCE and evaluate the children with scoped push/pop assertions, allowing the
solver to reuse its context. Model-block every SAT state; preserve UNKNOWN.
Original H-17 sources, masks, target commitments and candidate are not read.
"""
import ctypes, json, random, re, time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import circuit, stream, ror

P12=(0,1,2,3,22,23,24,25,45,46,47,48)
P16=P12+(4,5,6,7)
MASK64=(1<<64)-1


def solve_parent(first,parent,timeout_ms=350,retry_ms=1500,max_models=32):
    assert len(first)==2 and 0<=parent<4096
    assert 100<=timeout_ms<=retry_ms<=30000
    anchor=sum(((parent>>j)&1)<<pos for j,pos in enumerate(P12))
    smt=circuit({0:first[0],1:first[1]},anchor,P12,timeout_ms)
    assert smt.rstrip().endswith('(check-sat)')
    smt=smt.rsplit('(check-sat)',1)[0]
    lib=ctypes.CDLL('libz3.so.4');P=ctypes.c_void_p
    lib.Z3_mk_config.restype=P
    lib.Z3_mk_context.argtypes=[P];lib.Z3_mk_context.restype=P
    lib.Z3_del_config.argtypes=[P];lib.Z3_del_context.argtypes=[P]
    lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
    cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
    def ask(s):return (lib.Z3_eval_smtlib2_string(ctx,s.encode()) or b'').decode().strip()
    report=[]
    try:
        initial=ask(smt)
        if 'error' in initial.lower():raise RuntimeError('Base SMT parser error '+initial)
        for sub in range(16):
            cube=parent|(sub<<12)
            ask('(push 1)')
            for j,pos in enumerate(P16[len(P12):]):
                ask(f'(assert (= a0_{pos} {"true" if (sub>>j)&1 else "false"}))')
            ask(f'(set-option :timeout {timeout_ms})')
            result=ask('(check-sat)')
            recovered=[];did_retry=False
            while True:
                if result=='sat':
                    raw=ask('(get-value ('+' '.join(f'a0_{j}' for j in range(64))+'))')
                    bits={int(j):int(t=='true') for j,t in re.findall(r'\(a0_(\d+)\s+(true|false)\)',raw)}
                    assert len(bits)==64
                    a=sum(bits[j]<<j for j in range(64))
                    b=(ror((first[0]-a)&MASK64,17)-a)&MASK64
                    assert stream(a,b,2)==list(first)
                    assert all(((a>>pos)&1)==((cube>>j)&1) for j,pos in enumerate(P16))
                    recovered.append((a,b))
                    if len(recovered)>=max_models:
                        result='unknown';break
                    blocker=' '.join(f'(not a0_{j})' if bits[j] else f'a0_{j}' for j in range(64))
                    ask('(assert (or '+blocker+'))')
                    result=ask('(check-sat)')
                elif result=='unknown' and not did_retry and retry_ms>timeout_ms:
                    ask(f'(set-option :timeout {retry_ms})')
                    result=ask('(check-sat)')
                    did_retry=True
                elif result in ('unsat','unknown'):
                    break
                else:raise RuntimeError('Unexpected SMT result '+result[:200])
            report.append((sub,result,recovered,did_retry))
            ask('(pop 1)')
        return report
    finally:lib.Z3_del_context(ctx)


def synthetic_controls():
    t0=time.monotonic();checked=0;unknown=0;all_states=0
    for seed in (991,992):
        rng=random.Random(seed)
        original=(rng.getrandbits(64),rng.getrandbits(64))
        outputs=stream(*original,2)
        parent=sum(((original[0]>>pos)&1)<<j for j,pos in enumerate(P12))
        results=solve_parent(outputs,parent,350,3000)
        states=[s for _,_,group,_ in results for s in group]
        assert original in states,(seed,'planted full state absent')
        # The synthetic controls are valid only after all children terminate.
        assert all(t=='unsat' for _,t,_,_ in results),(seed,'open child')
        checked+=1;unknown+=sum(t=='unknown' for _,t,_,_ in results)
        all_states+=len(states)
    print(json.dumps({'source_free':True,'fixtures':checked,
          'P16_children':16*checked,
          'terminal_UNSAT_children':16*checked-unknown,
          'terminal_UNKNOWN':unknown,'planted_full_states_recovered':checked,
          'all_enumerated_states':all_states,
          'elapsed_s':round(time.monotonic()-t0,2)},sort_keys=True))


if __name__=='__main__':synthetic_controls()
