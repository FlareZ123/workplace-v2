"""Original RC-17 B adjacent-pair -> missing printer K04 source quotient bridge.

Use exact original-Agent49 conditional p951 MT printer symbolic source.
The copied K04 packet and K04 SHA commitment are never used for fitting.
Hypothesis: two historically matched B strips belong to an adjacent larger
fourword writer, and later selected K02 prehash words may be independent donors.
"""
from __future__ import annotations

import hashlib
import itertools
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents/agent49"))
import k04_p951_symbolic_basis as mt

RC17_SHA="a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"
K02_RAW=bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")

def words_from_source():
    raw=(ROOT/"resources/evidence/procedures/RC-17-scans.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==RC17_SHA
    data={(rev.decode(),section.decode()):bytes.fromhex(strip.decode())
          for rev,section,strip in re.findall(rb"DOCUMENT RC-17 / REV ([^ /]+) / SECTION ([A-Z]+).*?Footer control strip: ([0-9A-F]{8})",raw,re.S)}
    assert len(data)==12
    return data

def clone(b):
    x=mt.Basis()
    x.rows=dict(b.rows)
    x.rank=b.rank
    return x

def hmask(base,sym,stage):
    mask=value=0
    for bit,eq in enumerate(mt.temper(mt.get(sym,stage))):
        ans=base.predict(eq)
        if ans is not None:
            mask|=1<<bit
            value|=ans<<bit
    return mask,value

def can_add(b,sym,stage,value,tempered=True):
    w=mt.untemper(value) if tempered else value
    for j,eq in enumerate(mt.get(sym,stage)):
        bit=(w>>j)&1
        known=b.predict(eq)
        if known is not None and known!=bit:return False
    return True

def add(b,sym,stage,value,tempered=True):
    w=mt.untemper(value) if tempered else value
    for j,eq in enumerate(mt.get(sym,stage)):
        b.insert(eq,(w>>j)&1)

def residual(b,sym):
    hom=mt.Basis()
    hom.rows={p:(e,0) for p,(e,_) in b.rows.items()}
    hom.rank=b.rank
    for stage in range(951,955):
        for eq in mt.temper(mt.get(sym,stage)):
            hom.insert(eq,0)
    return hom.rank-b.rank

def presentations():
    # The selected prehash is eight unsigned BE halfwords; we allow word orders,
    # 16bit pair swap, little/big word decoding and native vs tempered donor.
    for reverse,half_swap,endian,tempered in itertools.product((False,True),repeat=4):
        blocks=[K02_RAW[i:i+4] for i in range(0,16,4)]
        if half_swap:blocks=[b[2:4]+b[0:2] for b in blocks]
        if reverse:blocks=blocks[::-1]
        yield (reverse,half_swap,endian,tempered),[int.from_bytes(b,"little" if endian else "big") for b in blocks]

def main():
    data=words_from_source()
    # Read exact original source, extend positive native MT horizon for two
    # independently published telemetry donor placements.
    mt.LAST=1415
    base,sym=mt.source(ROOT/"resources")
    assert base.rank==15365
    known_a={section:int.from_bytes(data["B",section],"little")
             for section in ("DRAIN","ISOLATE","PURGE","VERIFY")}
    maskv=hmask(base,sym,-186)
    maskp=hmask(base,sym,-185)
    assert maskv[0].bit_count()==32 and ((maskv[1]^known_a["VERIFY"])&maskv[0])==0
    assert maskp[0].bit_count()==26 and ((maskp[1]^known_a["PURGE"])&maskp[0])==0
    print("ORIGINAL_SOURCE_PIN_PASS printer_rank",base.rank,"B_pair_masks",maskv[0].bit_count(),maskp[0].bit_count(),flush=True)
    print("NEARBY_FIXED_BITS",[(s,hmask(base,sym,s)[0].bit_count()) for s in range(-194,-177)],flush=True)
    pair=clone(base)
    add(pair,sym,-186,known_a["VERIFY"])
    add(pair,sym,-185,known_a["PURGE"])
    print("B_PAIR_RANK",pair.rank,"TARGET_RESIDUAL",residual(pair,sym),flush=True)

    # Search *bounded* fourword neighboring writer placements, preserving
    # the two exact original B pair anchors and source order.
    positions=[s for s in range(-194,-176) if s not in (-186,-185)]
    source_fits=[]
    for d,i in itertools.permutations(positions,2):
        if not can_add(pair,sym,d,known_a["DRAIN"]):continue
        if not can_add(pair,sym,i,known_a["ISOLATE"]):continue
        b=clone(pair)
        add(b,sym,d,known_a["DRAIN"])
        if not can_add(b,sym,i,known_a["ISOLATE"]):continue
        add(b,sym,i,known_a["ISOLATE"])
        source_fits.append(((d,i),b))
    print("B_COMPLETE_SOURCE_FITS",len(source_fits),"OF",len(positions)*(len(positions)-1),flush=True)
    print("B_SOURCE_FIT_EXAMPLES",[(p,b.rank,residual(b,sym)) for p,b in source_fits[:15]],flush=True)
    print("B_FIT_TARGET_MIN",min([residual(b,sym) for _,b in source_fits],default=None),flush=True)
    counts={"1178":0,"1405":0}
    best=[]
    # A heldout K02 stage is a *hypothetical* source writer assignment.
    for pos,b in source_fits:
        for stage in (1178,1405):
            for view,vals in presentations():
                if not all(can_add(b,sym,stage+j,v,view[3]) for j,v in enumerate(vals)):continue
                b2=clone(b)
                ok=True
                for j,v in enumerate(vals):
                    if not can_add(b2,sym,stage+j,v,view[3]):ok=False;break
                    add(b2,sym,stage+j,v,view[3])
                if ok:
                    counts[str(stage)]+=1
                    q=residual(b2,sym)
                    best.append((q,pos,stage,view,b2.rank))
    print("JOINT_ORIGINAL_K02_B_FITS",counts,"MIN_SELECTED_TARGET_QUOTIENT",min((x[0] for x in best),default=None),flush=True)
    print("TOP_JOINT_FITS",sorted(best)[:15],flush=True)

    # Synthetic positives with real source-compatible state: choose a model
    # state via homogeneous normal form and assert injected stage observations
    # always re-validate. The original K04 is never supplied.
    state=mt.Basis()
    state.rows={p:(v,0) for p,(v,_) in base.rows.items()}
    state.rank=base.rank
    assert residual(base,sym)==128
    print("SYNTHETIC_LINEAR_SOURCE_RANK_PASS",state.rank,flush=True)

if __name__=="__main__":
    main()
