"""H17 Z/(2^128) affine-counter issuer with two genuine late ACK anchors."""
import hashlib
import sys
from collections import Counter
from pathlib import Path
from k04_late_printer_twoanchor_sft import spool, encode, layout, MASK, TARGET

MOD = 1 << 128

def solutions(x0,x1,y0,y1,max_v=8):
    difference = (x0-x1) % MOD
    residue = (y0-y1) % MOD
    if not difference:
        return []
    v = (difference & -difference).bit_length()-1
    if v > max_v or residue % (1<<v):
        return []
    modulus = MOD >> v
    root = (residue >> v) * pow(difference >> v,-1,modulus) % modulus
    return [((root+k*modulus)%MOD,(y0-(root+k*modulus)*x0)%MOD)
            for k in range(1<<v)]

def run(path):
    rows=spool(path)
    held=[j for j,row in enumerate(rows[:128]) if row["state"]=="ACK" and row["cls"]=="RECOVER"]
    assert len(held)==35
    models=source=target=max_bytes=0
    types=Counter()
    for form in range(12):
        for method in range(6):
            x0,x1=(encode(rows[j],form,method) for j in (131,132))
            selected_x=encode(rows[129],form,method)
            for serializer in range(8):
                y0,y1=(int.from_bytes(layout(rows[j]["payload"],serializer),"big") for j in (131,132))
                roots=solutions(x0,x1,y0,y1)
                models+=1
                types[len(roots)]+=1
                for a,b in roots:
                    packet=layout(((a*selected_x+b)%MOD).to_bytes(16,"big"),serializer)
                    component=bytes(x^y for x,y in zip(packet,MASK))
                    target += hashlib.sha256(component).digest()==TARGET
                    for j in held:
                        out=layout(((a*encode(rows[j],form,method)+b)%MOD).to_bytes(16,"big"),serializer)
                        matching=sum(x==y for x,y in zip(out,rows[j]["payload"]))
                        max_bytes=max(max_bytes,matching)
                        source += matching==16
    total=sum(k*v for k,v in types.items())
    print("ORIGINAL_ANCHOR_LAYOUTS",models,"CONSISTENT_LAYOUTS",models-types[0],
          "FULL_CANDIDATES",total,"SOURCE_HOLDOUT_EXACT",source,
          "BEST_BYTE_OVERLAP",max_bytes,"ORIGINAL_K04_HITS",target,"ROOT_HIST",dict(types))
    assert models==576 and total==496 and source==0 and target==0
    for a,b in ((0x8c1549033bcd17740189456a3ecbcc51,0x8be1f25402ed9a089bbc06d88341f201),
                (0x101c5182a1c44098badff54f0e622abc,0x41bd3)):
        x0,x1=(encode(rows[j],7,0) for j in (131,132))
        y0,y1=((a*x+b)%MOD for x in (x0,x1))
        roots=solutions(x0,x1,y0,y1)
        assert (a,b) in roots
        selected_x=encode(rows[129],7,0)
        assert any((aa*selected_x+bb)%MOD==(a*selected_x+b)%MOD for aa,bb in roots)
    print("SYNTHETIC_LATE_AFFINE_INT128_COMPLETE_COUPON_POSITIVES PASS")

if __name__=="__main__":
    path=sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources/evidence/print/spool-reconstruction.log"
    run(path)
