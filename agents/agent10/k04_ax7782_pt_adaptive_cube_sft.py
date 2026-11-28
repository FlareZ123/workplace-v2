#!/usr/bin/env python3
"""Exhaustive adaptive cube proof for the 16 AX-7782 PT-anchored K04 erasure models.
Private local source execution only; returns aggregate statuses, no original values.
Use: env -u CI -u GITHUB_ACTIONS python agents/agent10/k04_ax7782_pt_adaptive_cube_sft.py resources
Reference circuit: agents/agent3/k04_xoropp_anchored_gap_synthetic.py
"""
import ctypes,hashlib,os,random,re,sys
from collections import Counter,deque
from pathlib import Path
if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
    raise SystemExit('No original-source test in public CI')
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'agent3'))
from k04_xoropp_anchored_gap_synthetic import circuit,stream,ror,M
from k04_ax7782_pt_xoropp_anchor_sft import source,decode,encode

def solve_fixed(obs,anchor,width,val,timeout_ms):
    assert width in (0,4,8) and 0<=val<(1<<width)
    smt=circuit(obs,anchor,timeout_ms)
    extras='\n'.join(f'(assert (= a0_{16+j} {"true" if (val>>j)&1 else "false"}))' for j in range(width))
    smt=smt.replace('(check-sat)',extras+'\n(check-sat)')
    lib=ctypes.CDLL('libz3.so.4');P=ctypes.c_void_p
    lib.Z3_mk_config.restype=P;lib.Z3_mk_context.argtypes=[P];lib.Z3_mk_context.restype=P
    lib.Z3_del_config.argtypes=[P];lib.Z3_del_context.argtypes=[P]
    lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p];lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
    cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
    try:
        st=(lib.Z3_eval_smtlib2_string(ctx,smt.encode()) or b'').decode().strip()
        assert st in ('sat','unsat','unknown'),st
        if st!='sat':return st,None
        names=' '.join(f'a0_{j}' for j in range(64))
        model=(lib.Z3_eval_smtlib2_string(ctx,f'(get-value ({names}))'.encode()) or b'').decode()
        bits={int(i):v=='true' for i,v in re.findall(r'\(a0_(\d+)\s+(true|false)\)',model)}
        assert len(bits)==64
        a=sum(int(v)<<i for i,v in bits.items())
        b=(ror((obs[0]-a)&M,17)-a)&M
        assert all(stream(a,b,6)[i]==y for i,y in obs.items())
        return st,(a,b)
    finally:
        lib.Z3_del_context(ctx)

def controls():
    rng=random.Random(20261128);a,b=rng.getrandbits(64),rng.getrandbits(64)
    ys=stream(a,b,6);obs={j:ys[j] for j in (0,1,4,5)}
    for width in (0,4,8):
        st,state=solve_fixed(obs,a&0xffff,width,(a>>16)&((1<<width)-1),1000)
        assert st=='sat' and state==(a,b)
    for bit in (0,17,39,63):
        po=obs.copy();po[4]^=1<<bit
        st,_=solve_fixed(po,a&0xffff,8,(a>>16)&255,1000)
        assert st=='unsat'
    print('SYNTHETIC exact full-state recoveries=3/3 poisoned=4/4 PASS')

def prove(obs,anchor):
    # Source-independent, exhaustive disjoint partition of all lower-16 anchored states.
    st,state=solve_fixed(obs,anchor,0,0,5000)
    tally=Counter({(0,st):1})
    if st!='unknown':return tally,state
    queue=deque((4,n) for n in range(16))
    while queue:
        width,val=queue.popleft()
        st,state=solve_fixed(obs,anchor,width,val,2000 if width==4 else 5000)
        tally[(width,st)]+=1
        if st=='sat':return tally,state
        if st=='unknown' and width<8:
            for nibble in range(16):queue.append((8,val|(nibble<<4)))
    return tally,None

def main(root):
    controls()
    (first,last),mask,expected,anchors=source(root)
    combined=Counter();unresolved=[]
    for case in range(16):
        ai,layout=divmod(case,4)
        order=('little','big')[layout//2];swap=bool(layout%2)
        y0,y1=decode(first,order,swap);y4,y5=decode(last,order,swap)
        obs={0:y0,1:y1,4:y4,5:y5}
        tallies,state=prove(obs,anchors[ai])
        if state:
            predicted=encode(stream(*state,6)[2:4],order,swap)
            component=bytes(x^y for x,y in zip(predicted,mask))
            if hashlib.sha256(component).hexdigest()==expected:
                raise RuntimeError('PRIVATE K04 COMMITMENT MATCH: escrow without logging')
            unresolved.append(case)
        unknown_leaves=sum(v for (width,st),v in tallies.items() if width==8 and st=='unknown')
        if unknown_leaves:unresolved.append(case)
        combined.update(tallies)
        print(f'PT_COVER case={case} final_UNSAT_cubes={sum(v for (width,st),v in tallies.items() if st=="unsat")} depth8_UNKNOWN={unknown_leaves}',flush=True)
    print('PT_COVER cases=16 unresolved=',len(set(unresolved)),'proof_tree_stats=',dict(combined))
    assert not unresolved,'incomplete proof / unexpected SAT'
    print('PT_COVER ALL_16_SOURCE_ANCHOR_MODELS=UNSAT; original K04 still MISSING')
if __name__=='__main__':
    assert len(sys.argv)==2,'usage: source-local-script /path/to/resources'
    main(Path(sys.argv[1]))
