"""K04: expand genuine CPython n32 key-term intersections at 64 previously open phases.
Selected physical ACK2 bytes and original K04 target hash are excluded.
Uses real original source native packet constraints and 64B Python seed controls.
Run from GitHub checkout via workflow h17-agent5-n32-term-domain.yml.
"""
from __future__ import annotations
import argparse
import hashlib
import random
from itertools import combinations

from k04_source_n24_phase_sweep_sft import (
    OFFSET, mt, words, original_native, phase_equations
)
from k04_k2496_nineteen_term_source_sft import (
    reduce_source, source_dimension, key_term
)

OPEN = tuple(range(166, 202)) + tuple(range(310, 338))
assert len(OPEN) == 64

def triple_groups(coefficients, constants, at, ceiling):
    indices = [32*i+b for i in (at-2, at-1, at) for b in range(32)]
    value = sum(constants[index] << bit
                for bit,index in enumerate(indices))
    projection = {}
    for bit,index in enumerate(indices):
        expression = coefficients[index]
        while expression:
            low = expression & -expression
            source_bit = low.bit_length()-1
            projection[source_bit] = projection.get(source_bit,0) | (1<<bit)
            expression ^= low
    basis = {}
    for expression in projection.values():
        while expression:
            pivot=expression.bit_length()-1
            if pivot not in basis:
                basis[pivot]=expression
                break
            expression^=basis[pivot]
    assert len(basis) == source_dimension(coefficients[i] for i in indices)
    assert len(basis)<=ceiling
    values=[value]
    for direction in basis.values():
        old=values[:]
        values.extend(v ^ direction for v in old)
    assert len(values)==(1<<len(basis))
    return [
        ((v>>(32*j))&0xffffffff for j in range(3))
        for v in values
    ]

def test_phase(packets, symbolic, phase, ceiling):
    coefficients, constants=reduce_source(
        phase_equations(packets, symbolic, phase)
    )
    dimensions={
        at: source_dimension(
            coefficients[32*i+b]
            for i in (at-2,at-1,at)
            for b in range(32)
        )
        for at in range(4,624)
    }
    ids={at for at,rank in dimensions.items() if rank<=ceiling}
    pairs=[(a,b) for a,b in combinations(sorted(ids),2) if (b-a)%32==0]
    termsets={}
    disjoint=[]
    for a,b in pairs:
        for at in (a,b):
            if at not in termsets:
                groups=triple_groups(coefficients,constants,at,ceiling)
                vals={key_term(at,tuple(group)) for group in groups}
                assert len(vals)==len(groups)
                termsets[at]=vals
        if termsets[a].isdisjoint(termsets[b]):
            disjoint.append((a,b,dimensions[a],dimensions[b]))
    return len(ids),len(pairs),disjoint,dimensions

def genuine_control(symbolic, phase, ceiling):
    seed=bytes(((29+11*i)&255) for i in range(64))
    key=int.from_bytes(seed+hashlib.sha512(seed).digest(),"big")
    assert (key.bit_length()+31)//32==32
    rng=random.Random(seed)
    state=rng.getstate()[1][:624]
    assert state==random.Random(key).getstate()[1][:624]
    generated=[rng.getrandbits(32) for _ in range(phase+974)]
    native=[[mt.untemper(generated[phase+position+lane])
             for lane in range(4)] for position in mt.STARTS]
    count,pairs,disjoint,dims=test_phase(native,symbolic,phase,ceiling)
    assert not disjoint,disjoint
    print(f"GENUINE_BYTES64_N32_CONTROL PASS phase={phase} terms={count} reused_pairs={pairs}",flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--shard",type=int,required=True,choices=range(8))
    parser.add_argument("--ceiling",type=int,default=12,choices=(10,11,12,13,14))
    args=parser.parse_args()
    phases=OPEN[args.shard*8:args.shard*8+8]
    assert len(phases)==8
    symbolic=words(OFFSET+623)
    native=original_native()
    genuine_control(symbolic,OFFSET+phases[0],args.ceiling)
    excluded=0
    for k in phases:
        count,pairs,disjoint,dims=test_phase(native,symbolic,OFFSET+k,args.ceiling)
        excluded+=bool(disjoint)
        low=sum(1 for d in dims.values() if d<=9)
        assert low>=13
        witness=disjoint[0] if disjoint else None
        print(f"PHASE_RESULT k={k} prior={OFFSET+k} original_n9_terms={low} "
              f"ceiling={args.ceiling} terms={count} repeated_mod32_pairs={pairs} "
              f"n32={'EXCLUDED' if disjoint else 'OPEN'} witness={witness}",flush=True)
    print(f"SHARD_COMPLETE shard={args.shard} phases=8 n32_excluded={excluded} "
          f"n32_open={8-excluded} ceiling={args.ceiling}",flush=True)

if __name__=="__main__":
    main()
