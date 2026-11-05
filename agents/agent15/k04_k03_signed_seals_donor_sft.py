"""K03 authentic signed seal serials as speculative early K04 MT donors.

Run from repository: python agents/agent15/k04_k03_signed_seals_donor_sft.py
This reads original printer spool and K03 commitment, without reading K04 data.
"""
from __future__ import annotations
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents' / 'agent49'))
import k04_p951_symbolic_basis as mt

mt.LAST = 3000
printer, symbolic = mt.source(ROOT / 'resources')
assert printer.rank == 15365

serials = ('SG-D7DAD6BC', 'SG-9714519B', 'SG-7DAD0AD4', 'SG-BE8E87FD')
k03_raw = bytes.fromhex(''.join(s[3:] for s in serials))
k03_digest = hashlib.sha256('|'.join(serials).encode('ascii')).digest()[:16].hex().upper()
assert k03_digest == '1384AF96E25D6ADA666209CB55E062FA'

k02_raw = bytes.fromhex('E1A5E474BAD7E853A2E8C71D3317D507')
assert hashlib.sha256(k02_raw).digest()[:16].hex().upper() == '0D7E3AB56FB75DA3EB0E2E06786D239E'


def k02_forms():
    for endian in ('little','big'):
        for backwards,swap_halves,native in itertools.product((False,True), repeat=3):
            words=[k02_raw[i:i+4] for i in range(0,16,4)]
            if swap_halves: words=[w[2:]+w[:2] for w in words]
            if backwards: words.reverse()
            yield [x if native else mt.untemper(x) for x in (int.from_bytes(w,endian) for w in words)]


def k03_forms():
    forms=[]
    for i in range(4):
        w=k03_raw[4*i:4*i+4]
        values=[int.from_bytes(w,endian) for endian in ('little','big')]
        forms.append(values+[mt.untemper(x) for x in values])
    for order in itertools.permutations(range(4)):
        for view in itertools.product(range(4),repeat=4):
            yield sum(forms[order[i]][view[i]] << (32*i) for i in range(4))


def reduce_expression(base,expr):
    rem=rhs=0
    while expr:
        p=expr.bit_length()-1
        if p in base.rows:
            v,b=base.rows[p]
            expr ^= v
            rhs ^= b
        else:
            rem ^= 1<<p
            expr ^= 1<<p
    return rem,rhs


def with_words(base,first,values):
    clone=mt.Basis()
    clone.rows=base.rows.copy()
    clone.rank=base.rank
    for index,native in enumerate(values):
        for bit,expr in enumerate(mt.get(symbolic,first+index)):
            clone.insert(expr,(native>>bit)&1)
    return clone


def checks_for(base,first):
    pivots={}
    checks=[]
    for lane in range(4):
        for bit,expr in enumerate(mt.get(symbolic,first+lane)):
            residual,rhs=reduce_expression(base,expr)
            tag=1<<(32*lane+bit)
            while residual:
                pivot=residual.bit_length()-1
                if pivot not in pivots:
                    pivots[pivot]=(residual,tag,rhs)
                    break
                v,t,b=pivots[pivot]
                residual ^= v
                tag ^= t
                rhs ^= b
            if residual==0:
                checks.append((tag,rhs))
    assert len(checks)+len(pivots)==128
    return checks


def source_consistent_planted(base,first):
    # Construct a genuine source-consistent native state from GF(2) constraints.
    state=0
    for pivot,(expr,rhs) in sorted(base.rows.items()):
        if rhs ^ ((expr&state).bit_count()&1):
            state |= 1<<pivot
    words=[]
    for lane in range(4):
        native=sum(((expr&state).bit_count()&1)<<bit for bit,expr in enumerate(mt.get(symbolic,first+lane)))
        words.append(native)
    return sum(x<<(32*i) for i,x in enumerate(words))


views=list(k03_forms())
assert len(views)==6144
counts=[]
for k02_stage in (1178,1405):
    for k03_stage in (-240,-239,-238,-237):
        count=0
        for k02 in k02_forms():
            base=with_words(printer,k02_stage,k02)
            assert base.rank==15493
            predicates=checks_for(base,k03_stage)
            planted=source_consistent_planted(base,k03_stage)
            assert all(((planted&tag).bit_count()&1)==rhs for tag,rhs in predicates)
            count += sum(all(((packed&tag).bit_count()&1)==rhs for tag,rhs in predicates) for packed in views)
        result={'k02_stage':k02_stage,'k03_stage':k03_stage,'assignments':16*len(views),'checks':len(predicates),'compatible':count,'planted':16}
        counts.append(result)
        print(json.dumps(result),flush=True)
assert all(x['compatible']==0 for x in counts)
assert sum(x['assignments'] for x in counts)==786432
print('ORIGINAL NO_MATCH; synthetic GF2 consistent placements PASS')
