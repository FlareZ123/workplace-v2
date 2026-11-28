#!/usr/bin/env python3
"""K04: broad source-heldout native 32-bit GF(2)-affine issuer falsifier.

Test an arbitrary 32-bit affine transform x->M*x xor c (not merely named
PRNG seeds) in either globally interleaved or per-native-word lanes, with
original CLASS/DEST/pair stream multiplexing. Never fit selected ACK2.
"""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,random,re

SPOOL="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

class GF2Affine32:
    def __init__(self):
        self.b={};self.conflicts=0;self.closed=None;self.steps=0
    def add(self,x,y):
        self.steps+=1
        v=(1<<32)|x;w=y
        while v:
            p=v.bit_length()-1
            if p not in self.b:
                self.b[p]=(v,w)
                break
            vv,ww=self.b[p]
            v^=vv;w^=ww
        if not v and w:self.conflicts+=1
        if len(self.b)==33 and self.closed is None:self.closed=self.steps-1
    def predict(self,x):
        v=(1<<32)|x;w=0
        while v:
            p=v.bit_length()-1
            if p not in self.b:return None
            vv,ww=self.b[p]
            v^=vv;w^=ww
        return w

def group(r,selector):
    if selector=="global":return "ALL"
    if selector=="class":return r["CLASS"]
    if selector=="dest":return r["DEST"]
    return r["CLASS"]+"|"+r["DEST"]

def words(r,reverse=False):
    b=bytes.fromhex(r["PAYLOAD"])
    w=[int.from_bytes(b[i:i+4],"big") for i in range(0,16,4)]
    return w[::-1] if reverse else w

def encoded(w,reverse=False):
    return b"".join(x.to_bytes(4,"big") for x in (w[::-1] if reverse else w))

def source(root):
    raw=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SPOOL
    r=[dict(re.findall(r"([A-Z]+)=([^ ]+)",t)) for t in raw.decode().splitlines()[1:]]
    assert len(r)==133 and [int(x["JOB"][-4:]) for x in r[:128]]==list(range(300,428))
    a,b,c=r[128:131]
    assert [(x["JOB"],x["ATTEMPT"],x["STATE"],x["CLASS"],x["DEST"]) for x in (a,b,c)]==[
        ("PS-261003-0417","1","REQUESTED","RECOVER","bench"),
        ("PS-261003-0417","2","ACK","RECOVER","bench"),
        ("PS-261003-0417","3","REQUESTED","RECOVER","bench")]
    route=json.loads((root/"evidence/recovery-routing.json").read_text())
    check=json.loads((root/"acceptance.json").read_text())
    mask=bytes.fromhex(route["K04"]["masked_component"])
    target=check["slot_sha256"]["K04"]
    assert len(mask)==16 and len(target)==64
    return r,mask,target

def plant():
    rng=random.Random(20261128)
    cases=0
    for mode in ("serial","lanes"):
        for group_count in (1,3,9):
            for _ in range(2):
                for lane in range(1 if mode=="serial" else 4):
                    for retry in range(100):
                        matrix=[rng.getrandbits(32) for _ in range(32)]
                        bias=rng.getrandbits(32)
                        def f(x):
                            y=bias
                            for k in range(32):
                                if (x>>k)&1:y^=matrix[k]
                            return y
                        values=[rng.getrandbits(32)]
                        for t in range(199):values.append(f(values[-1]))
                        trained=GF2Affine32()
                        for u,v in zip(values,values[1:]):trained.add(u,v)
                        if len(trained.b)==33 and not trained.conflicts:break
                    else:raise AssertionError("synthetic full-rank failed")
                    assert trained.closed is not None
                    for u,v in zip(values,values[1:]):assert trained.predict(u)==v
                cases+=1
    assert cases==12
    print("SYNTHETIC 12/12 source-fit full 32-bit affine stream controls PASS")

def experiment(root):
    r,mask,target=source(root)
    real=r[:128];attempt1=r[128];attempt3=r[130]
    results=[]
    for mode in ("serial","lanes"):
        selectors=("global","class","dest","pair") if mode=="serial" else ("global","class","dest")
        for selector in selectors:
            for reverse in ((False,True) if mode=="serial" else (False,)):
                cohorts=defaultdict(list)
                for row in real:cohorts[group(row,selector)].append(words(row,reverse))
                assert len(cohorts)==(9 if selector=="pair" else 1 if selector=="global" else 3)
                trained={}
                transitions=source_contradictions=packet_checks=packet_hits=0
                for k,records in cohorts.items():
                    if mode=="serial":
                        seq=[v for packet in records for v in packet]
                        m=GF2Affine32()
                        for x,y in zip(seq,seq[1:]):m.add(x,y)
                        trained[k]=[m]
                        transitions+=len(seq)-1;source_contradictions+=m.conflicts
                        for i in range(1,len(records)):
                            if m.closed is None or 4*i<m.closed+1:continue
                            q=records[i-1][-1];predict=[]
                            for z in range(4):
                                q=m.predict(q)
                                if q is None:break
                                predict.append(q)
                            if len(predict)==4:
                                packet_checks+=1;packet_hits+=int(predict==records[i])
                    else:
                        maps=[]
                        for lane in range(4):
                            seq=[p[lane] for p in records]
                            m=GF2Affine32()
                            for x,y in zip(seq,seq[1:]):m.add(x,y)
                            maps.append(m)
                            transitions+=len(seq)-1;source_contradictions+=m.conflicts
                        trained[k]=maps
                        for i in range(1,len(records)):
                            if not all(m.closed is not None and i>=m.closed+1 for m in maps):continue
                            q=[m.predict(records[i-1][j]) for j,m in enumerate(maps)]
                            if all(v is not None for v in q):
                                packet_checks+=1;packet_hits+=int(q==records[i])
                route=group(attempt1,selector)
                req=words(attempt1,reverse);late=words(attempt3,reverse)
                maps=trained[route];ordinary=cohorts[route]
                first=last=None;candidate=None
                if mode=="serial":
                    f=maps[0].predict
                    def four(state):
                        out=[]
                        for _ in range(4):
                            state=f(state)
                            if state is None:return None
                            out.append(state)
                        return out
                    guess_req=four(ordinary[-1][-1])
                    first=None if guess_req is None else int(guess_req==req)
                    candidate=four(req[-1])
                    guess_late=None if candidate is None else four(candidate[-1])
                    last=None if guess_late is None else int(guess_late==late)
                else:
                    guess_req=[m.predict(ordinary[-1][i]) for i,m in enumerate(maps)]
                    if all(v is not None for v in guess_req):first=int(guess_req==req)
                    guess=[m.predict(req[i]) for i,m in enumerate(maps)]
                    if all(v is not None for v in guess):
                        candidate=guess
                        guess_late=[m.predict(guess[i]) for i,m in enumerate(maps)]
                        if all(v is not None for v in guess_late):last=int(guess_late==late)
                hit=None
                if candidate is not None:
                    comp=bytes(x^y for x,y in zip(encoded(candidate,reverse),mask))
                    hit=int(hashlib.sha256(comp).hexdigest()==target)
                results.append((mode,selector,int(reverse),len(cohorts),transitions,
                                source_contradictions,packet_checks,packet_hits,
                                int(candidate is not None),first,last,hit))
    print("ORIGINAL mode,selector,reverse,cohorts,transitions,source_contradictions,whole_packet_holdouts,whole_matches,coupon_complete,REQUEST1_match,REQUEST3_match,K04_full_hash_hit")
    for row in results:print("ORIGINAL",*[(x if x is not None else "NA") for x in row],sep="\t")
    assert len(results)==11
    assert sum(x[6] for x in results)==(119+119+101+101+99+99+44+44+93+16+20)
    assert all(x[7]==0 and x[11] in (None,0) for x in results)
    assert sum(x[8] for x in results)==10
    print("FINAL models=11 complete_original_k04_checks=10 original_hits=0")
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]/"resources")
    arg=a.parse_args();plant();experiment(arg.root)
