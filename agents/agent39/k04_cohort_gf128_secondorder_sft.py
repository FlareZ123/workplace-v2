#!/usr/bin/env python3
"""K04: independent CLASS / DEST / pair GF(2^128) order-two source emitters.

Read the exact original spool, withhold copied ACK2, calibrate coefficients
only on each category's first four ordinary packets, predict complete
unfitted original packets, then test a full hypothesized selected coupon.
No candidate/secret bytes are printed.
"""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,random,re

SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
FULL=(1<<128)-1

def gf_mul(x,y):
    z=0
    while y:
        if y&1:z^=x
        y>>=1
        x=((x<<1)&FULL)^(0x87 if (x>>127) else 0)
    return z

def gf_inv(x):
    if not x:raise ZeroDivisionError
    e=(1<<128)-2;r=1
    while e:
        if e&1:r=gf_mul(r,x)
        x=gf_mul(x,x);e>>=1
    return r

def view(buf,reverse_words,reverse_within_words):
    words=[buf[i:i+4] for i in range(0,16,4)]
    if reverse_words:words.reverse()
    if reverse_within_words:words=[w[::-1] for w in words]
    return b"".join(words)

def field(buf,rw,rb):
    return int.from_bytes(view(buf,rw,rb),"big")

def packet(value,rw,rb):
    return view(value.to_bytes(16,"big"),rw,rb)

def coeff(s):
    x0,x1,x2,x3=s[:4]
    determinant=gf_mul(x1,x1)^gf_mul(x0,x2)
    if determinant==0:return None
    inverse=gf_inv(determinant)
    a=gf_mul(gf_mul(x1,x2)^gf_mul(x0,x3),inverse)
    b=gf_mul(gf_mul(x1,x3)^gf_mul(x2,x2),inverse)
    assert gf_mul(a,x1)^gf_mul(b,x0)==x2
    assert gf_mul(a,x2)^gf_mul(b,x1)==x3
    return a,b

def step(ab,u,v):
    a,b=ab
    return gf_mul(a,v)^gf_mul(b,u)

def group(row,method):
    if method=="class":return row["CLASS"]
    if method=="dest":return row["DEST"]
    return row["CLASS"]+"|"+row["DEST"]

def control():
    rng=random.Random(20261128)
    assert gf_mul(1,7)==7
    for i in range(16):
        value=rng.getrandbits(128) or 1
        assert gf_mul(value,gf_inv(value))==1
    models=0
    for method in ("class","dest","pair"):
        for rw in (False,True):
            for rb in (False,True):
                for _ in range(9 if method=="pair" else 3):
                    a=rng.getrandbits(128);b=rng.getrandbits(128)
                    x=rng.getrandbits(128);y=rng.getrandbits(128)
                    values=[x,y]
                    for i in range(14):
                        x,y=y,step((a,b),x,y)
                        values.append(y)
                    read=[field(packet(q,rw,rb),rw,rb) for q in values]
                    fitted=coeff(read[:4])
                    assert fitted==(a,b)
                    for i in range(4,16):
                        assert step(fitted,read[i-2],read[i-1])==read[i]
                models+=1
    print("SYNTHETIC 12/12 complete group emitter controls PASS; 16/16 GF inverse")

def run(root):
    raw=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SPOOL_SHA
    records=[dict(re.findall(r"([A-Z]+)=([^ ]+)",line)) for line in raw.decode().splitlines()[1:]]
    assert len(records)==133
    normal=records[:128]
    assert [int(r["JOB"][-4:]) for r in normal]==list(range(300,428))
    earlier,selected,later=records[128:131]
    assert [(r["JOB"],r["ATTEMPT"],r["STATE"],r["CLASS"],r["DEST"]) for r in (earlier,selected,later)]==[
        ("PS-261003-0417","1","REQUESTED","RECOVER","bench"),
        ("PS-261003-0417","2","ACK","RECOVER","bench"),
        ("PS-261003-0417","3","REQUESTED","RECOVER","bench")]
    route=json.loads((root/"evidence/recovery-routing.json").read_text())
    commitments=json.loads((root/"acceptance.json").read_text())
    mask=bytes.fromhex(route["K04"]["masked_component"])
    target=commitments["slot_sha256"]["K04"]
    assert len(mask)==16 and len(target)==64
    totals=[]
    for method in ("class","dest","pair"):
        for rw in (False,True):
            for rb in (False,True):
                groups=defaultdict(list)
                for row in normal:
                    groups[group(row,method)].append(field(bytes.fromhex(row["PAYLOAD"]),rw,rb))
                assert len(groups)==(9 if method=="pair" else 3)
                fitted={}
                for name,values in groups.items():
                    assert len(values)>=5
                    fitted[name]=coeff(values[:4])
                    assert fitted[name] is not None
                checks=matches=error=0
                for name,values in groups.items():
                    for i in range(4,len(values)):
                        expected=step(fitted[name],values[i-2],values[i-1])
                        matches+=int(expected==values[i]);error+=(expected^values[i]).bit_count()
                        checks+=1
                name=group(earlier,method);values=groups[name]
                first=field(bytes.fromhex(earlier["PAYLOAD"]),rw,rb)
                last=field(bytes.fromhex(later["PAYLOAD"]),rw,rb)
                predicted_first=step(fitted[name],values[-2],values[-1])
                coupon=step(fitted[name],values[-1],first)
                predicted_last=step(fitted[name],first,coupon)
                coupon_bytes=packet(coupon,rw,rb)
                component=bytes(a^b for a,b in zip(coupon_bytes,mask))
                hit=hashlib.sha256(component).hexdigest()==target
                totals.append((method,int(rw),int(rb),len(groups),checks,matches,error,
                               int(predicted_first==first),(predicted_first^first).bit_count(),
                               int(predicted_last==last),(predicted_last^last).bit_count(),int(hit)))
    print("ORIGINAL method,rw,rb,groups,heldout_packets,exact_matches,total_bit_errors,REQUEST1_match,REQUEST1_bit_errors,REQUEST3_match,REQUEST3_bit_errors,K04_full_hash_hits")
    for t in totals:print("ORIGINAL",*t,sep="\t")
    assert len(totals)==12
    assert all(t[5]==0 and t[7]==0 and t[9]==0 and t[11]==0 for t in totals)
    print("FINAL complete_models=12 intact_holdouts=1296 exact_packet_matches=0 K04_original_hits=0")
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]/"resources")
    args=ap.parse_args()
    control();run(args.root)
