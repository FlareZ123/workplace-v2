"""K04 p951: source-only future-donor reachability, 967..5299 full native words.

Complete exhaustive search of *beneficial two-word pairs*, then unions of two
beneficial pairs, with source-independent exact MT GF(2) equations. The selected
ACK2 is removed before parsing and neither K04 nor K08 commitment is accessed.

Use: python agents/agent39/k04_p951_global_future_donor_pairs_sft.py
"""
from __future__ import annotations

import collections
import hashlib
import importlib.util
import itertools
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location(
    "coupon",ROOT/"agents/agent39/k04_p951_seven_donor_affine_sft.py"
)
coupon=importlib.util.module_from_spec(spec)
spec.loader.exec_module(coupon)
LO,HI=967,5300
TRIO=(1179,1180,1181)
U=0xffffffff
M=0x9908b0df


def states():
    out=[[1<<(32*i+b) for b in range(32)] for i in range(624)]
    for index in range(624,624+HI+1):
        p,n,q=out[index-624],out[index-623],out[index-227]
        out.append([
            q[bit]^(p[31] if bit==30 else n[bit+1] if bit<30 else 0)
            ^(n[0] if (M>>bit)&1 else 0)
            for bit in range(32)
        ])
    return out


def add(expr,basis):
    while expr:
        pivot=expr.bit_length()-1
        row=basis.get(pivot)
        if row is None:
            basis[pivot]=expr
            return 1
        expr^=row
    return 0


def canonical(expr,basis):
    """Eliminate every basis pivot, even below a free leading coordinate."""
    result=0
    while expr:
        pivot=expr.bit_length()-1
        known=basis.get(pivot)
        if known is not None:
            expr^=known
        else:
            bit=1<<pivot
            result|=bit
            expr^=bit
    return result


def source_basis(symbols):
    raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==coupon.SOURCE_SHA
    fields=re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)
    assert len(fields)==len(coupon.prior.STARTS)==133
    assert coupon.prior.STARTS[129]==951
    packets=[
        b"" if i==129 else bytes.fromhex(field.decode())
        for i,field in enumerate(fields)
    ]
    affine=coupon.source_basis(symbols,packets)
    result={p-1:row>>1 for p,row in affine.items()}
    assert len(result)==15365
    return result


def prepare(symbols):
    source=source_basis(symbols)
    with_trio=source.copy()
    assert sum(add(expr,with_trio) for at in TRIO for expr in symbols[624+at])==96
    with_target=with_trio.copy()
    assert sum(add(expr,with_target)
               for at in range(951,955) for expr in symbols[624+at])==33
    single={}
    for at in range(LO,HI):
        if at in TRIO:continue
        left,right={},{}
        for expr in symbols[624+at]:
            add(canonical(expr,with_trio),left)
            add(canonical(expr,with_target),right)
        assert len(left)==len(right),at # each singleton has zero target gain
        single[at]=(list(left.values()),list(right.values()),set(right))
    assert len(single)==4330
    return source,with_trio,with_target,single


def span_rank(first,second=()):
    basis={}
    for value in itertools.chain(first,second):
        add(value,basis)
    return len(basis)


def marginal(positions,symbols,base,target):
    left,right=base.copy(),target.copy()
    for at in positions:
        for expr in symbols[624+at]:
            add(expr,left)
            add(expr,right)
    return (len(left)-len(base))-(len(right)-len(target))


def main():
    symbols=states()
    # Independent positive controls from our target-reaching seven-native
    # full spool reconstructor. Symbolic states cover its shorter domain.
    coupon.positive_controls(symbols)
    source,base,target,single=prepare(symbols)
    keys=list(single)
    matches=[]
    pivot_overlap=0
    for idx,a in enumerate(keys):
        left,right,pivots=single[a]
        for b in keys[idx+1:]:
            more_left,more_right,more_pivots=single[b]
            if not pivots.intersection(more_pivots):
                continue
            pivot_overlap+=1
            gain=span_rank(left,more_left)-span_rank(right,more_right)
            if gain:
                matches.append((a,b,gain))
    assert pivot_overlap==156022,pivot_overlap
    assert len(matches)==85,len(matches)
    assert collections.Counter(g for _,_,g in matches)=={
        1:45,2:17,3:7,4:4,5:2,28:3,29:4,30:2,31:1
    }
    unique={}
    for x,y in itertools.combinations(matches,2):
        selected=tuple(sorted(set(x[:2]+y[:2])))
        if len(selected)<3 or selected in unique:
            continue
        unique[selected]=marginal(selected,symbols,base,target)
    assert len(unique)==3445,len(unique)
    complete=[
        choice for choice,gain in unique.items()
        if len(choice)==4 and gain==33
    ]
    assert len(complete)==46,len(complete)
    assert all(gain<33 for choice,gain in unique.items() if len(choice)==3)
    first=min(complete,key=lambda x:(max(x),sum(x)))
    assert first==(1347,1348,1574,1575),first
    for extra in ((1347,1348,1574,2029),
                  (1743,1744,2197,2198),
                  (2535,2536,3443,3444)):
        assert extra in complete,extra
    print("Exact original printer-only source rank",len(source))
    print("Selected quotient after three full future native words: 33/128")
    print("Global future 967..5299 donor singles",len(single))
    print("Pivot-overlap pair tests",pivot_overlap,
          "beneficial two-word pairs",len(matches))
    print("Two-positive-pair unions",len(unique),
          "distinct seven-word complete donor sets",len(complete))
    print("Closest complete donor set: 1179,1180,1181,1347,1348,1574,1575")
    print("Alternative examples:",(1347,1348,1574,2029),
          (1743,1744,2197,2198),(2535,2536,3443,3444))
    print("Three-plus-three combinations of two beneficial pairs: 0 complete")
    print("Other 3+way synergies with all two-word gains zero NOT excluded")
    print("No indexed authentic donors: actual K04 bits 0/128, K08 words 0")


if __name__=="__main__":
    main()
