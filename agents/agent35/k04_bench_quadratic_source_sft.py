"""H17 selected K04 packet through full GF128 quadratic same-role printer publisher."""
import hashlib
import sys
from pathlib import Path
from k04_late_printer_twoanchor_sft import spool, encode, layout, MASK, TARGET
from k04_gf128_label_emitter_sft import mul, power

MOD=1<<128
ONE=1<<127

def div(n,d):
    assert d
    return mul(n,power(d,MOD-2))

def denominators(x):
    assert len(x)==3 and len(set(x))==3
    return [div(ONE,mul(x[i]^x[(i+1)%3],x[i]^x[(i+2)%3])) for i in range(3)]

def interpolate(x,y,t,denoms):
    assert len(x)==len(y)==len(denoms)==3
    out=0
    for i in range(3):
        v=mul(y[i],denoms[i])
        for j in range(3):
            if j!=i:
                v=mul(v,t^x[j])
        out ^= v
    return out

def run(path):
    rows=spool(path)
    cohort=[j for j,row in enumerate(rows)
            if j!=129 and row["state"]=="ACK" and row["cls"]=="RECOVER" and row["dest"]=="bench"]
    assert cohort==[7,20,50,57,65,67,76,87,93,107,116,132]
    anchors=cohort[-3:]
    held=cohort[:-3]
    models=target=full=partial=0
    for form in range(12):
        for encoder in range(6):
            x=[encode(rows[j],form,encoder) for j in anchors]
            if len(set(x))!=3:
                continue
            selected_x=encode(rows[129],form,encoder)
            denoms=denominators(x)
            for serializer in range(8):
                y=[int.from_bytes(layout(rows[j]["payload"],serializer),"big") for j in anchors]
                def predict(t):
                    return layout(interpolate(x,y,t,denoms).to_bytes(16,"big"),serializer)
                assert all(predict(t)==rows[j]["payload"] for t,j in zip(x,anchors))
                coupon=predict(selected_x)
                component=bytes(a^b for a,b in zip(coupon,MASK))
                target+=hashlib.sha256(component).digest()==TARGET
                models+=1
                for j in held:
                    got=predict(encode(rows[j],form,encoder))
                    matching=sum(a==b for a,b in zip(got,rows[j]["payload"]))
                    full+=matching==16
                    partial=max(partial,matching)
    print("GF128_QUADRATIC_MODELS",models,"HOLDOUTS",held,
          "FULL_SOURCE_MATCHES",full,"MAX_BYTES_MATCHED",partial,"K04_SHA_HITS",target)
    assert models==552 and full==0 and target==0
    a0=0x76b0f7189bda0a85778ba0946be568a2
    b0=0x139aba9c72719c329472df449d148051
    c0=0xA081287B0ACF7D
    coords=[encode(rows[j],7,0) for j in anchors+[129,93]]
    outputs=[mul(a0,mul(v,v))^mul(b0,v)^c0 for v in coords]
    denoms=denominators(coords[:3])
    assert [interpolate(coords[:3],outputs[:3],v,denoms) for v in coords]==outputs
    print("SYNTHETIC_THREE_SOURCE_ANCHORS_TWO_WITHHELD_FULL_BLOCKS PASS")

if __name__=="__main__":
    path=sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources/evidence/print/spool-reconstruction.log"
    run(path)
