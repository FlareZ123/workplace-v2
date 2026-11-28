#!/usr/bin/env python3
"""K04: exact original source-only binary/ASCII job metadata affine issuer tests.

An arbitrary GF(2)-affine map from the original job number, CLASS, DEST to a
whole 128-bit printer coupon is learned from independent intact ordinary rows.
The disputed copied 18:02 ACK2 is never fitted or used as a donor.
"""
from pathlib import Path
import argparse,hashlib,json,random,re

PIN="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def feature(r,form):
    assert r["JOB"].startswith("PS-261003-")
    job=int(r["JOB"][-4:])
    assert 0<=job<1000
    cls={"LABEL":0,"STORES":1,"RECOVER":2}[r["CLASS"]]
    dest={"bench":0,"desk":1,"store":2}[r["DEST"]]
    x=1
    if form=="numeric":
        x|=job<<1
        base=11
    elif form=="ascii":
        for i,b in enumerate(r["JOB"][-4:].encode("ascii")):
            x|=b<<(1+8*i)
        base=33
    else:raise ValueError(form)
    return x|(1<<(base+cls))|(1<<(base+3+dest))

class GF2Affine128:
    def __init__(self):
        self.b={};self.independent=[];self.conflicts=[]
    def add(self,x,y,i):
        v=x;w=y;relation=1<<i
        while v:
            p=v.bit_length()-1
            if p not in self.b:
                self.b[p]=(v,w,relation)
                self.independent.append(i)
                return
            bv,bw,br=self.b[p]
            v^=bv;w^=bw;relation^=br
        if w:self.conflicts.append((i,relation,w))
    def predict(self,x):
        v=x;w=0
        while v:
            p=v.bit_length()-1
            if p not in self.b:return None
            bv,bw,_=self.b[p]
            v^=bv;w^=bw
        return w

def source(root):
    raw=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN
    rows=[dict(re.findall(r"([A-Z]+)=([^ ]+)",line)) for line in raw.decode().splitlines()[1:]]
    assert len(rows)==133
    assert [int(x["JOB"][-4:]) for x in rows[:128]]==list(range(300,428))
    req,missing,late=rows[128:131]
    assert (missing["JOB"],missing["ATTEMPT"],missing["STATE"],missing["CLASS"],missing["DEST"])==(
        "PS-261003-0417","2","ACK","RECOVER","bench")
    assert rows[131]["JOB"]=="PS-261003-0448" and rows[132]["JOB"]=="PS-261003-0420"
    assert rows[132]["ATTEMPT"]=="2" and rows[132]["STATE"]=="ACK"
    mask=bytes.fromhex(json.loads((root/"evidence/recovery-routing.json").read_text())["K04"]["masked_component"])
    target=json.loads((root/"acceptance.json").read_text())["slot_sha256"]["K04"]
    assert len(mask)==16 and len(target)==64
    return rows,mask,target

def reduction(value,mask):
    return bytes(x^y for x,y in zip(value.to_bytes(16,"big"),mask))

def planted(rows,mask):
    rng=random.Random(20261128)
    for form in ("numeric","ascii"):
        coeff=[rng.getrandbits(128) for _ in range(40)]
        def transform(x):
            y=0
            for i,c in enumerate(coeff):
                if (x>>i)&1:y^=c
            return y
        f=GF2Affine128()
        for i,r in enumerate(rows[:128]):
            x=feature(r,form)
            f.add(x,transform(x),i)
        assert not f.conflicts
        for r in rows:
            x=feature(r,form)
            assert f.predict(x)==transform(x)
        selected=f.predict(feature(rows[129],form))
        expected=hashlib.sha256(reduction(transform(feature(rows[129],form)),mask)).hexdigest()
        assert hashlib.sha256(reduction(selected,mask)).hexdigest()==expected
    print("SYNTHETIC 2/2 full 128-bit metadata-publisher and K04 route/hash controls PASS")

def original(rows,mask,target):
    for form in ("numeric","ascii"):
        m=GF2Affine128()
        for i,r in enumerate(rows[:128]):
            m.add(feature(r,form),int(r["PAYLOAD"],16),i)
        heldout=[i for i in range(128) if i not in m.independent]
        assert all(m.predict(feature(rows[i],form)) is not None for i in heldout)
        matches=sum(m.predict(feature(rows[i],form))==int(rows[i]["PAYLOAD"],16) for i in heldout)
        later=[m.predict(feature(rows[i],form)) for i in (131,132)]
        assert all(x is not None for x in later)
        full_later=[int(x==int(rows[i]["PAYLOAD"],16)) for i,x in zip((131,132),later)]
        mid=m.predict(feature(rows[129],form))
        assert mid is not None
        hit=int(hashlib.sha256(reduction(mid,mask)).hexdigest()==target)
        cidx,maskids,residual=m.conflicts[0]
        ids=[i for i in range(128) if (maskids>>i)&1]
        assert ids==[0,3,5,6] and residual.bit_count()==55
        # Mathematically complete four-source-word contradiction:
        assert (feature(rows[0],form)^feature(rows[3],form)^feature(rows[5],form)^feature(rows[6],form))==0
        assert (int(rows[0]["PAYLOAD"],16)^int(rows[3]["PAYLOAD"],16)^int(rows[5]["PAYLOAD"],16)^int(rows[6]["PAYLOAD"],16)).bit_count()==55
        print("ORIGINAL",form,"source_rank",len(m.independent),
              "heldout_128bit_original_packets",len(heldout),"full_matches",matches,
              "source_affine_inconsistencies",len(m.conflicts),
              "first_witness_original_job_ordinals",ids,"witness_output_bitcount",55,
              "independent_later_ACK1_ACK2_matches",full_later,"K04_original_hit",hit)
        assert matches==0 and full_later==[0,0] and hit==0

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]/"resources")
    arg=a.parse_args()
    rows,mask,target=source(arg.root)
    planted(rows,mask)
    original(rows,mask,target)
