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
    experiment(rows,mask,digest)
