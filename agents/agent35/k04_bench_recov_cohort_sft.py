"""H17 source-conditioned same-CLASS same-DEST bench RECOVER ACK interpolation."""
import hashlib
import sys
from collections import Counter
from pathlib import Path
from k04_late_printer_twoanchor_sft import spool, encode, layout, MASK, TARGET
from k04_gf128_label_emitter_sft import mul, power
from k04_late_ring_affine_sft import solutions, MOD

def run(path):
    rows=spool(path)
    cohort=[j for j,r in enumerate(rows)
            if j!=129 and r["state"]=="ACK" and r["cls"]=="RECOVER" and r["dest"]=="bench"]
    assert cohort==[7,20,50,57,65,67,76,87,93,107,116,132]
    anchors=cohort[-2:]
    held=cohort[:-2]
    counts=Counter()
    targets=Counter()
    holdouts=Counter()
    best=Counter()
    for form in range(12):
        for method in range(6):
            x=[encode(rows[j],form,method) for j in anchors]
            selected_x=encode(rows[129],form,method)
            for serializer in range(8):
                y=[int.from_bytes(layout(rows[j]["payload"],serializer),"big") for j in anchors]
                roots={}
                if x[0]!=x[1]:
                    a=mul(y[0]^y[1],power(x[0]^x[1],MOD-2))
                    roots["gf128"]=[(a,y[0]^mul(a,x[0]))]
                roots["z128"]=solutions(*x,*y)
                for model,pairs in roots.items():
                    counts[(model,"layouts")]+=1
                    counts[(model,"roots")]+=len(pairs)
                    for a,b in pairs:
                        if model=="gf128":
                            transform=lambda t:mul(a,t)^b
                        else:
                            transform=lambda t:(a*t+b)%MOD
                        coupon=layout(transform(selected_x).to_bytes(16,"big"),serializer)
                        component=bytes(v^w for v,w in zip(coupon,MASK))
                        targets[model]+=hashlib.sha256(component).digest()==TARGET
                        for j in held:
                            prediction=layout(transform(encode(rows[j],form,method)).to_bytes(16,"big"),serializer)
                            matching=sum(v==w for v,w in zip(prediction,rows[j]["payload"]))
                            holdouts[model]+=matching==16
                            best[model]=max(best[model],matching)
    assert counts==Counter({("gf128","layouts"):552,("gf128","roots"):552,
                           ("z128","layouts"):576,("z128","roots"):356})
    assert all(v==0 for v in targets.values()) and all(v==0 for v in holdouts.values())
    print("SOURCE_TARGET",rows[129]["job"],rows[129]["iso"],"SAME_CLASS_DEST_ANCHORS",anchors,"HOLDOUTS",held)
    print("SOURCE_TRAINED_COUNTS",dict(counts),"ORIGINAL_K04_HITS",dict(targets),
          "FULL_SOURCE_HOLDOUT_HITS",dict(holdouts),"MAX_BYTE_HOLDOUT_OVERLAP",dict(best))
    a0=0x76b0f7189bda0a85778ba0946be568a2
    b0=0x139aba9c72719c329472df449d148051
    coords=[encode(rows[j],7,0) for j in anchors+[129,107]]
    outputs=[mul(a0,t)^b0 for t in coords]
    rec=mul(outputs[0]^outputs[1],power(coords[0]^coords[1],MOD-2))
    pad=outputs[0]^mul(rec,coords[0])
    assert (rec,pad)==(a0,b0)
    assert [mul(rec,t)^pad for t in coords]==outputs
    print("SYNTHETIC_COHORT_HELDOUT_TARGET_FULL_PACKET PASS")

if __name__=="__main__":
    path=sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources/evidence/print/spool-reconstruction.log"
    run(path)
