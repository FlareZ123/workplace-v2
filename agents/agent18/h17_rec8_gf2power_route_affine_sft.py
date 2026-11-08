"""H-17: affine GF(2^w) REC8 erasure model using original route constants.

Fit X3 and X5 from X1,X2 with unknown (a,b), known route offset c.
Reconstruct K04 and K08, check complete independent K06/K07 holdouts.
"""
import hashlib
import itertools
import json
import random

from h17_rec8_gf2power_squaregap_sft import FIELDS, KNOWN, ROOT, TARGET, mul, power, split, join

ROUTE = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
OFFSETS = (("mask",ROUTE["K04"]["masked_component"]),
           ("nonce",ROUTE["K08"]["desk_nonce"]))


def artin_schreier(value, bits, poly):
    """Solve t^2 + t=value by GF2 elimination, returning up to two roots."""
    basis = {}
    for col in range(bits):
        t = 1 << col
        image = mul(t,t,bits,poly) ^ t
        witness = t
        while image:
            pivot = image.bit_length()-1
            if pivot in basis:
                old_image,old_witness = basis[pivot]
                image ^= old_image
                witness ^= old_witness
            else:
                basis[pivot]=(image,witness)
                break
    image = value
    witness = 0
    while image:
        pivot = image.bit_length()-1
        if pivot not in basis:
            return ()
        old_image,old_witness = basis[pivot]
        image ^= old_image
        witness ^= old_witness
    assert mul(witness,witness,bits,poly)^witness == value
    return witness,witness^1


def candidates(x1,x2,x3,x5,c,bits,poly):
    """Quadratic in a; derive b via genuine known X3."""
    m = lambda x,y:mul(x,y,bits,poly)
    d = m(x1,x3)^m(x2,x2)
    e = m(c,x1^x2)
    f = m(x3^c,x3)^m(x1,x5^c)
    if d == 0:
        if e == 0:
            assert f != 0, "unbounded source-degenerate coefficient"
            return ()
        return (m(f,power(e,(1<<bits)-2,bits,poly)),)
    denominator_inverse = power(d,(1<<bits)-2,bits,poly)
    p,q = m(e,denominator_inverse),m(f,denominator_inverse)
    if p == 0:
        return (power(q,1<<(bits-1),bits,poly),)
    v=m(q,power(m(p,p),(1<<bits)-2,bits,poly))
    return tuple(m(p,t) for t in artin_schreier(v,bits,poly))


def series(x1,x2,coeff,offset,bits,poly):
    result={1:tuple(x1),2:tuple(x2)}
    for i in range(3,9):
        result[i]=tuple(
            mul(coeff[j][0],result[i-1][j],bits,poly)^
            mul(coeff[j][1],result[i-2][j],bits,poly)^offset[j]
            for j in range(len(offset))
        )
    return result


def main():
    assert all(hashlib.sha256(bytes.fromhex(value)).hexdigest()==TARGET[f"K{i:02d}"]
               for i,value in KNOWN.items())
    rng=random.Random(20261108)
    controls=0
    for bits,poly in FIELDS:
        lanes=128//bits
        for label,offset in OFFSETS:
            for endian,reverse in itertools.product(("big","little"),(False,True)):
                c=split(offset,bits,endian,reverse)
                coeff=tuple((rng.getrandbits(bits),rng.getrandbits(bits)) for _ in range(lanes))
                initial=(tuple(rng.getrandbits(bits) for _ in range(lanes)),
                         tuple(rng.getrandbits(bits) for _ in range(lanes)))
                truth=series(*initial,coeff,c,bits,poly)
                for j in range(lanes):
                    x1,x2,x3,x5=(truth[i][j] for i in (1,2,3,5))
                    assert coeff[j][0] in candidates(x1,x2,x3,x5,c[j],bits,poly)
                controls+=1

    count=dict(complete=0,rejected=0,full_holdout=0,k04=0,k08=0)
    for bits,poly in FIELDS:
        lanes=128//bits
        for label,offset in OFFSETS:
            for endian,reverse in itertools.product(("big","little"),(False,True)):
                known={i:split(value,bits,endian,reverse) for i,value in KNOWN.items()}
                c=split(offset,bits,endian,reverse)
                choices=[]
                for j in range(lanes):
                    x1,x2,x3,x5=(known[i][j] for i in (1,2,3,5))
                    assert x1!=0, "underdetermined original source fit"
                    coeff=[]
                    for a in candidates(x1,x2,x3,x5,c[j],bits,poly):
                        inv=power(x1,(1<<bits)-2,bits,poly)
                        b=mul(x3^mul(a,x2,bits,poly)^c[j],inv,bits,poly)
                        coeff.append((a,b))
                    if not coeff:
                        choices=[]
                        break
                    choices.append(coeff)
                if not choices:
                    count["rejected"]+=1
                    continue
                for coeff in itertools.product(*choices):
                    predicted=series(known[1],known[2],coeff,c,bits,poly)
                    assert predicted[3]==known[3] and predicted[5]==known[5]
                    count["complete"]+=1
                    count["full_holdout"]+=int(predicted[6]==known[6] and predicted[7]==known[7])
                    for slot,key in ((4,"k04"),(8,"k08")):
                        block=join(predicted[slot],bits,endian,reverse)
                        count[key]+=int(hashlib.sha256(block).hexdigest()==TARGET[f"K{slot:02d}"])
    print("SIX_SOURCE_PINS_PASS=6 SYNTHETIC_AFFINE_ROUTE_CONTROLS=",controls,
          "ORIGINAL_RESULTS=",count)
    assert controls==72 and count==dict(complete=24,rejected=64,full_holdout=0,k04=0,k08=0)


if __name__=="__main__":
    main()
