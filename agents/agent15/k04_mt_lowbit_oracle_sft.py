"""K04 target-rank consequences of hypothetically observed unprinted MT bits.

Source-only diagnostic. No target commitment, masked ACK or K04 coupon is used.
Run: python agents/agent15/k04_mt_lowbit_oracle_sft.py
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'agents'/'agent49'))
import k04_p951_symbolic_basis as mt

source,symbolic=mt.source(ROOT/'resources')
assert source.rank==15365
printed={mt.STARTS[i]+j for i in range(133) if i!=129 for j in range(4)}
target=range(951,955)
gaps=[stage for stage in range(967) if stage not in printed and stage not in target]
assert len(gaps)==435


def insert(rows,expr):
    while expr:
        p=expr.bit_length()-1
        if p not in rows:
            rows[p]=expr
            return 1
        expr^=rows[p]
    return 0


def remainder(rows,expr):
    residual=0
    while expr:
        p=expr.bit_length()-1
        if p in rows:
            expr ^= rows[p]
        else:
            residual ^= 1<<p
            expr ^= 1<<p
    return residual


def scenario(planes,native):
    basis={p:row[0] for p,row in source.rows.items()}
    increase=0
    for stage in gaps:
        fields=mt.get(symbolic,stage)
        if not native:fields=mt.temper(fields)
        for bit in planes:
            increase+=insert(basis,fields[bit])
    target_basis={}
    fixed=[]
    for stage in target:
        fields=mt.get(symbolic,stage)
        if not native:fields=mt.temper(fields)
        fixed_mask=0
        for bit,expr in enumerate(fields):
            rem=remainder(basis,expr)
            if rem==0:fixed_mask|=1<<bit
            insert(target_basis,rem)
        fixed.append(f'{fixed_mask:08X}')
    return {'oracle_new_rank':increase,'K04_quotient_rank':len(target_basis),'fixed_per_native_word_mask':fixed}


results={}
for kind,native in [('native',True),('tempered',False)]:
    for name,planes in [('low1',range(1)),('low2',range(2)),('low12',range(12)),('high12',range(20,32)),('low16',range(16)),('high16',range(16,32)),('all32',range(32))]:
        results[f'{kind}_{name}']=scenario(planes,native)
assert results['native_low1']['K04_quotient_rank']==128
assert results['native_low2']['fixed_per_native_word_mask']==['00000001']*4
assert results['native_low12']['K04_quotient_rank']==84
assert results['native_low12']['fixed_per_native_word_mask']==['000007FF']*4
assert results['native_high12']['K04_quotient_rank']==84
assert results['tempered_low12']['K04_quotient_rank']==128
assert results['tempered_high12']['K04_quotient_rank']==128
assert results['native_all32']['K04_quotient_rank']==0
assert results['tempered_all32']['K04_quotient_rank']==0
print(json.dumps({'spool_source_rank':source.rank,'hidden_nonselected_stages':len(gaps),'selected_stages':[951,952,953,954],'hypothetical_oracle_results':results},indent=2))
