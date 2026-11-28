#!/usr/bin/env python3
"""K04 complete quadratic job-metadata publisher and cubic observability gate.

Fit all binary degree<=2 monomials of source job suffix, CLASS, DEST to
complete 128-bit ordinary printer packets. Fit only basis-independent intact
ACKs, withhold the selected copied ACK2 from all learning. Predict complete
target and independent whole intact packets; check original masked K04 SHA.
A degree<=3 source-rank test shows when coupon is unidentifiable.
"""
from pathlib import Path
from itertools import combinations
import argparse,hashlib,json,random,re

PIN="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
C={"LABEL":0,"STORES":1,"RECOVER":2}
D={"bench":0,"desk":1,"store":2}

def fields(row,view):
    job=row["JOB"][-4:]
    if view=="numeric":z=[(int(job)>>i)&1 for i in range(10)]
    elif view=="ascii":z=[(ord(ch)>>i)&1 for ch in job for i in range(7)]
    else:raise ValueError(view)
    return z+[int(C[row["CLASS"]]==i) for i in range(3)]+[int(D[row["DEST"]]==i) for i in range(3)]

def monomials(row,view,degree=2):
    f=fields(row,view)
    v=1;bit=1
    for order in range(1,degree+1):
        for subset in combinations(range(len(f)),order):
            if all(f[i] for i in subset):v|=1<<bit
            bit+=1
    return v,bit

class GF2Basis128:
    def __init__(self):
        self.b={};self.pivots=[];self.contradictions=[]
    def add(self,x,y,i):
        v=x;w=y;source=1<<i
        while v:
            bit=v.bit_length()-1
            if bit in self.b:
                a,b,s=self.b[bit]
                v^=a;w^=b;source^=s
            else:
                self.b[bit]=(v,w,source);self.pivots.append(i)
                return
        if w:self.contradictions.append((i,source,w))
    def predict(self,x):
        v=x;w=0;source=0
        while v:
            bit=v.bit_length()-1
            if bit not in self.b:return None,None
            a,b,s=self.b[bit]
            v^=a;w^=b;source^=s
        return w,source

def read(root):
    src=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(src).hexdigest()==PIN
    rows=[dict(re.findall(r"([A-Z]+)=([^ ]+)",line)) for line in src.decode().splitlines()[1:]]
    assert len(rows)==133 and [int(x["JOB"][-4:]) for x in rows[:128]]==list(range(300,428))
    assert [(x["JOB"],x["ATTEMPT"],x["STATE"],x["CLASS"],x["DEST"]) for x in rows[128:131]]==[
        ("PS-261003-0417","1","REQUESTED","RECOVER","bench"),
        ("PS-261003-0417","2","ACK","RECOVER","bench"),
        ("PS-261003-0417","3","REQUESTED","RECOVER","bench")]
    route=json.loads((root/"evidence/recovery-routing.json").read_text())
    acceptance=json.loads((root/"acceptance.json").read_text())
    mask=bytes.fromhex(route["K04"]["masked_component"])
    digest=acceptance["slot_sha256"]["K04"]
    assert len(mask)==16 and len(digest)==64
    return rows,mask,digest

def component(value,mask):
    return bytes(a^b for a,b in zip(value.to_bytes(16,"big"),mask))

def synthetic(rows,mask):
    rng=random.Random(20261128)
    for view in ("numeric","ascii"):
        dimension=monomials(rows[0],view,2)[1]
        coeff=[rng.getrandbits(128) for _ in range(dimension)]
        def f(x):
            y=0
            while x:
                bit=(x&-x).bit_length()-1
                y^=coeff[bit]
                x&=x-1
            return y
        b=GF2Basis128()
        for i,row in enumerate(rows[:128]):
            x,_=monomials(row,view,2);b.add(x,f(x),i)
        assert not b.contradictions
        for row in rows:
            x,_=monomials(row,view,2)
            actual,_=b.predict(x)
            if actual is not None:assert actual==f(x)
        selected,_=monomials(rows[129],view,2)
        actual,_=b.predict(selected)
        assert actual==f(selected)
        assert hashlib.sha256(component(actual,mask)).digest()==hashlib.sha256(component(f(selected),mask)).digest()
    print("SYNTHETIC 2/2 complete 128-bit quadratic source/coupon and K04 masked commitment controls PASS")



def original_affine_threecubes(rows,view):
    """Exhaustive source-input affine 3-flats; no printer payload or target read."""
    originals=[sum(z<<j for j,z in enumerate(fields(row,view))) for row in rows[:128]]
    locator={value:i for i,value in enumerate(originals)}
    assert len(locator)==128
    planes=set()
    for p in range(128):
        for q in range(p+1,128):
            delta=originals[p]^originals[q]
            for t in range(q+1,128):
                u=locator.get(originals[t]^delta,-1)
                if u>t:planes.add((p,q,t,u))
    cubes=set()
    for plane in planes:
        pp=[originals[i] for i in plane]
        for idx in range(128):
            if idx in plane:continue
            delta=pp[0]^originals[idx]
            partners=tuple(locator.get(value^delta,-1) for value in pp)
            if -1 in partners or len(set(partners))!=4:continue
            cubes.add(tuple(sorted(plane+partners)))
    expected={(52,64,68,80,86,98,102,114)} if view=="numeric" else set()
    assert cubes==expected
    print("SOURCE_ONLY",view,"affine2_source_planes",len(planes),
          "affine3_source_cubes",len(cubes),
          "unique_weight8_numeric_certificate",int(view=="numeric"))
    return cubes



def cubic_constructive_ambiguous_coupons(rows):
    """Build two real-data-exact cubic issuers with different entire selected coupons.

    This does not use any acceptance target, mask or copied 18:02 payload.
    The arbitrary selected values are a mathematical counterexample, not
    historical candidates. Do not disclose historical fitted coefficients.
    """
    for view in ("numeric","ascii"):
        counts=[]
        for selected_value in (0,1<<127):
            basis={}
            for i,row in enumerate(rows[:128]+[rows[129]]):
                x,dimension=monomials(row,view,3)
                y=int(row["PAYLOAD"],16) if i<128 else selected_value
                while x:
                    p=x.bit_length()-1
                    if p in basis:
                        vx,vy=basis[p]
                        x^=vx;y^=vy
                    else:
                        basis[p]=(x,y)
                        break
                else:
                    assert y==0
            assert len(basis)==129
            coefficients=[0]*dimension
            for pivot in sorted(basis):
                x,y=basis[pivot]
                x&=(1<<pivot)-1
                while x:
                    j=(x&-x).bit_length()-1
                    y^=coefficients[j]
                    x&=x-1
                coefficients[pivot]=y
            def evaluate(row):
                x,_=monomials(row,view,3)
                y=0
                while x:
                    j=(x&-x).bit_length()-1
                    y^=coefficients[j]
                    x&=x-1
                return y
            assert all(evaluate(row)==int(row["PAYLOAD"],16) for row in rows[:128])
            assert evaluate(rows[129])==selected_value
            counts.append(sum(v!=0 for v in coefficients))
        print("SOURCE_ONLY_CUBIC_WITNESS",view,
              "distinct_entire_selected_coupon_models",2,
              "both_replay_all_128_original_packets",1,
              "selected_coupons_disagree",1,
              "sparse_nonzero_coefficients_per_model",counts)


def sparse_original_quadratic_certificates(rows):
    """Small original-source exact null relations for *every* quadratic issuer."""
    certificates=(
        ("numeric",(52,64,68,80,86,98,102,114),63),
        ("ascii",(12,14,15,17,31,35,41,45,60,61,63,66),58),
    )
    for view,indices,expected_bits in certificates:
        original_affine_threecubes(rows,view)
        inputs=output=0
        for i in indices:
            assert i<128
            x,_=monomials(rows[i],view,2)
            inputs^=x
            output^=int(rows[i]["PAYLOAD"],16)
        assert inputs==0
        assert output.bit_count()==expected_bits
        # Independent planted random matrices show every valid quadratic map
        # obeys the same zero-output XOR for precisely these original inputs.
        rng=random.Random(20261128+len(indices))
        dim=monomials(rows[indices[0]],view,2)[1]
        for trial in range(8):
            coefficients=[rng.getrandbits(128) for _ in range(dim)]
            actual=0
            for i in indices:
                x,_=monomials(rows[i],view,2)
                y=0
                while x:
                    p=(x&-x).bit_length()-1
                    y^=coefficients[p]
                    x&=x-1
                actual^=y
            assert actual==0
        print("SOURCE_CERT",view,"source_record_count",len(indices),
              "source_indices",','.join(map(str,indices)),
              "quadratic_input_XOR_zero",1,
              "real_full128bit_output_XOR_setbits",expected_bits,
              "synthetic_arbitrary_quadratic_controls","8/8 PASS")



def full_packet_output_rank(rows):
    """Exact linear algebra on original whole 128-bit printer packet values."""
    pivots={}
    for row in rows[:128]:
        vector=int(row["PAYLOAD"],16)
        while vector:
            bit=vector.bit_length()-1
            if bit in pivots:vector^=pivots[bit]
            else:pivots[bit]=vector;break
    assert len(pivots)==128
    print("ORIGINAL_OUTPUT entire_128bit_packet_row_rank",len(pivots),
          "source_rows",128,"required_input_feature_rank_for_any_Gf2_linear_output_map",128)
    return len(pivots)


def experiment(rows,mask,digest):
    for view,rank_target,late_expected in (("numeric",75,("NA","MISS")),("ascii",84,("NA","MISS"))):
        b=GF2Basis128()
        for i,row in enumerate(rows[:128]):
            x,_=monomials(row,view,2)
            b.add(x,int(row["PAYLOAD"],16),i)
        assert len(b.b)==rank_target
        heldout=[i for i in range(128) if i not in b.pivots]
        assert len(heldout)==128-rank_target
        full=0
        for i in heldout:
            x,_=monomials(rows[i],view,2)
            prediction,_=b.predict(x)
            assert prediction is not None
            full+=int(prediction==int(rows[i]["PAYLOAD"],16))
        late=[]
        for idx in (131,132):
            x,_=monomials(rows[idx],view,2)
            predicted,_=b.predict(x)
            late.append("NA" if predicted is None else "HIT" if predicted==int(rows[idx]["PAYLOAD"],16) else "MISS")
        assert tuple(late)==late_expected
        target_x,_=monomials(rows[129],view,2)
        coupon,source_mask=b.predict(target_x)
        assert coupon is not None
        actual=hashlib.sha256(component(coupon,mask)).hexdigest()==digest
        assert len(b.contradictions)==len(heldout)
        assert full==0 and not actual
        conflict_idx,provenance,residual=b.contradictions[0]
        print("ORIGINAL degree2",view,"rank",len(b.b),"whole_source_holdouts",len(heldout),
              "whole_source_matches",full,"source_contradictions",len(b.contradictions),
              "source_coefficient_rows",source_mask.bit_count(),
              "first_contradiction_row",conflict_idx,
              "first_contradiction_support",provenance.bit_count(),
              "first_contradiction_wrong_output_bits",residual.bit_count(),
              "later_intact_ACK",late,"complete_original_K04_hits",int(actual))
        # Next-degree identifiability is computed strictly on original metadata,
        # without reading any original output or acceptance.
        basis={}
        for row in rows[:128]:
            x,dim=monomials(row,view,3)
            while x:
                p=x.bit_length()-1
                if p in basis:x^=basis[p]
                else:basis[p]=x;break
        assert len(basis)==128
        indep=[]
        for idx in (129,131,132):
            x,_=monomials(rows[idx],view,3)
            while x:
                p=x.bit_length()-1
                if p in basis:x^=basis[p]
                else:break
            indep.append(x!=0)
        assert indep==[True,True,True]
        print("SOURCE_ONLY degree3",view,"feature_dimension",dim,
              "original_training_rank",len(basis),
              "selected_coupon_outside_original_training_span",int(indep[0]),
              "two_later_ACKs_outside_original_training_span",sum(indep[1:]))
    print("FINAL degree2 complete_original_K04_checks=2 accepted=0; degree3 coupon NOT identified from the original source")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]/"resources")
    arg=p.parse_args()
    rows,mask,digest=read(arg.root)
    synthetic(rows,mask)
    full_packet_output_rank(rows)
    sparse_original_quadratic_certificates(rows)
    experiment(rows,mask,digest)
    cubic_constructive_ambiguous_coupons(rows)
