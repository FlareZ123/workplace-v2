"""Original-source gate: arbitrary binary affine 32-bit native-register writer,
all 32 possible short interleavings. Selected physical coupon withheld.

Model S[i+d] = A*S[i] xor c, d=1..32, arbitrary 32x32 binary A
and shared unknown c. For each d, 32 independent fully observed input
vectors span the domain; all additional source-fixed bits are held out.
No commitment hashes are consulted.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent49"))
import k04_p951_symbolic_basis as mt
basis, states = mt.source(ROOT)
assert basis.rank == 15365 and mt.STARTS[129] == 951
U = (1 << 32) - 1
masks = []
vals = []
for i in range(624):
    bits = [basis.predict(1 << (32*i + j)) for j in range(32)]
    masks.append(sum(1 << j for j,v in enumerate(bits) if v is not None))
    vals.append(sum((v or 0) << j for j,v in enumerate(bits)))
assert sum(m==U for m in masks)==166


def analyze_step(values, visible, d):
    full = {i:values[i] for i in range(624) if visible[i]==U}
    paired = [i for i in sorted(full) if i+d in full]
    pivots = {}
    used = set()
    for i in paired:
        x,y=full[i],full[i+d]
        rowcoeff = 1 << i
        parity=1
        while x:
            p=x.bit_length()-1
            if p not in pivots:
                pivots[p]=(x,y,parity,rowcoeff)
                used.add(i)
                break
            a,b,pc,mask=pivots[p]
            x^=a;y^=b;parity^=pc;rowcoeff^=mask
        else:
            # Redundant pairs become independent heldout equations later.
            pass
    if len(pivots)!=32:
        return {"stride":d,"train_rank":len(pivots),"complete_pairs":len(paired),
                "status":"rank_deficient"}
    # Analyze every source-fixed input with at least one output bit visible,
    # including all complete training and redundant pairs.
    odd_contradictions=0
    constraints={}
    pairchecks=0
    heldoutbits=0
    first_bad=None
    for i in sorted(full):
        if i+d>=624 or visible[i+d]==0:
            continue
        pairchecks+=1
        if i not in used:
            heldoutbits+=visible[i+d].bit_count()
        x=full[i]; y=0;par=0
        while x:
            p=x.bit_length()-1
            ax,ay,ap,_=pivots[p]
            x^=ax;y^=ay;par^=ap
        discrepancy=(y^values[i+d])&visible[i+d]
        if par:
            if discrepancy:
                odd_contradictions+=1
                if first_bad is None:first_bad=i
        else:
            for j in range(32):
                if (visible[i+d]>>j)&1:
                    constraints.setdefault(j,set()).add((discrepancy>>j)&1)
    constant_conflicts=sum(len(bs)>1 for bs in constraints.values())
    status="EXCLUDED" if odd_contradictions or constant_conflicts else "survives_source"
    return {"stride":d,"train_rank":32,"complete_pairs":len(paired),
            "pairchecks":pairchecks,"heldoutbits":heldoutbits,
            "odd_failures":odd_contradictions,"constant_conflicts":constant_conflicts,
            "first_bad":first_bad,"status":status}


results=[analyze_step(vals,masks,d) for d in range(1,33)]
for r in results:print("ORIGINAL",r)
complete=[r for r in results if r["train_rank"]==32]
print("SUMMARY", "fullrank",len(complete),
      "excluded",sum(r["status"]=="EXCLUDED" for r in complete),
      "possible", [r["stride"] for r in complete if r["status"]=="survives_source"],
      "rankdeficient", [r["stride"] for r in results if r["status"]=="rank_deficient"])

# Genuine planted independent arbitrary four-lane and single-lane GF2
# affine generators exercised under the SAME original source visibility.
def xs32(x):
    x^=(x<<13)&U;x^=x>>17;x^=(x<<5)&U
    return x&U
for d in (1,2,4,8,16,32):
    for c in (0,0xD6C6C5C0):
        v=list(range(1,d+1))
        for i in range(d,624):v.append(xs32(v[i-d])^c)
        planted=analyze_step(v,masks,d)
        if planted["train_rank"]==32:
            assert planted["status"]=="survives_source",planted
            assert planted["odd_failures"]==planted["constant_conflicts"]==0
        print("POSITIVE",d,hex(c),planted["train_rank"],planted["status"])
print("SOURCE_GATES_COMPLETE SELECTED_K04_WITHHELD")
