#!/usr/bin/env python3
"""Source-only NumPy SeedSequence(pool4) inversion with AX-7778 high16 bridge.

Conditional model: p951 relative printer schedule; AX-7778 checkpoints are
byte-swapped high16 tempered outputs at relative stages -157..-142. NumPy's
initialized 624-word state is the symbolic origin, so no pre-initialization
MT prehistory is assumed. The selected printer row129 payload is never read
for fitting. Candidate bytes are never printed or persisted.
"""
from __future__ import annotations
import argparse, hashlib, json, re, struct, time
from pathlib import Path
import numpy as np

U=0xffffffff; MAG=0x9908b0df; INIT_B=0x8b51f9dd; MULT_B=0x58f38ded
SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TRANSFER_SHA="32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
ORIGIN=0; LAST=2600
STARTS=[0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]

def untemper(x):
    x &= U
    for shift,mask,left in ((18,U,False),(15,0xefc60000,True),(7,0x9d2c5680,True),(11,U,False)):
        y=x
        for _ in range(6): x=y^(((x<<shift)&mask) if left else (x>>shift))
        x &= U
    return x

def words():
    a=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
    for i in range(624,LAST-ORIGIN+1):
        t=i-624
        a.append([a[t+397][j] ^ (a[t][31] if j==30 else (a[t+1][j+1] if j<30 else 0)) ^ (a[t+1][0] if (MAG>>j)&1 else 0) for j in range(32)])
    return a

def temper(v):
    a=[v[j]^(v[j+11] if j+11<32 else 0) for j in range(32)]
    b=[a[j]^(a[j-7] if j>=7 and (0x9d2c5680>>j)&1 else 0) for j in range(32)]
    c=[b[j]^(b[j-15] if j>=15 and (0xefc60000>>j)&1 else 0) for j in range(32)]
    return [c[j]^(c[j+18] if j+18<32 else 0) for j in range(32)]

class Basis:
    def __init__(self): self.rows={}; self.rank=0
    def insert(self,v,b):
        while v:
            p=v.bit_length()-1
            if p not in self.rows:
                self.rows[p]=(v,b); self.rank+=1; return
            w,c=self.rows[p]; v^=w; b^=c
        if b: raise ValueError("linear source contradiction")
    def predict(self,v):
        b=0
        while v:
            p=v.bit_length()-1
            if p not in self.rows: return None
            w,c=self.rows[p]; v^=w; b^=c
        return b

def load(root):
    spool=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest()==SPOOL_SHA
    lines=[x for x in spool.splitlines() if x.startswith(b"2026-")]
    assert len(lines)==133 and len(STARTS)==133 and STARTS[0]==0 and STARTS[129]==951 and STARTS[-1]==963
    payloads=[]
    for i,line in enumerate(lines):
        if i==129: payloads.append(None); continue
        m=re.search(rb"(?:^|\s)PAYLOAD=([0-9A-F]{32})(?=\s|$)",line); assert m
        payloads.append(bytes.fromhex(m.group(1).decode()))
    transfer=(root/"evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(transfer).hexdigest()==TRANSFER_SHA
    recs=[json.loads(x) for x in transfer.decode().splitlines() if x.strip()]
    ax=sorted((x for x in recs if x.get("kind")=="CHUNK" and x.get("transfer")=="AX-7778"),key=lambda x:(x["seq"],x["attempt"]))
    assert len(ax)==16
    axvals=[int.from_bytes(bytes.fromhex(x["checkpoint"]),"little") for x in ax]
    return payloads,axvals

def pool_state(i,p):
    b=(INIT_B*pow(MULT_B,i,1<<32))&U
    f=(b*MULT_B)&U
    v=((p^b)*f)&U
    return v^(v>>16)

def pool_from_state(i,s):
    b=(INIT_B*pow(MULT_B,i,1<<32))&U
    f=(b*MULT_B)&U
    v=s^(s>>16)
    return ((v*pow(f,-1,1<<32))&U)^b

def recover_pool(basis,seq,phase,threshold=16):
    # The NumPy MT19937 initialized state is S[0..623] at symbolic positions 0..623.
    # S[0] is fixed by NumPy to 0x80000000.
    try:
        for j,v in enumerate(seq[0]): basis.insert(v,(0x80000000>>j)&1)
    except ValueError:
        return "s0-contradiction",None
    groups=[[] for _ in range(4)]
    for i in range(1,624):
        vec=seq[i]
        mask=value=0
        for j,expr in enumerate(vec):
            bit=basis.predict(expr)
            if bit is not None:
                mask|=1<<j; value|=bit<<j
        groups[i%4].append((i,mask,value))
    pool=[None]*4; group_status=[]
    for residue,g in enumerate(groups):
        full=[(i,v) for i,m,v in g if m==U]
        if full:
            candidates={pool_from_state(i,v) for i,v in full}
            if len(candidates)!=1:
                return f"pool-contradiction:res{residue}:full-word-disagreement:{len(candidates)}",None
            cand=next(iter(candidates))
            mismatch=next(((i,m,v) for i,m,v in g if (pool_state(i,cand)&m)!=(v&m)),None)
            if mismatch:
                mi,mm,mv=mismatch
                return f"pool-contradiction:res{residue}:word{mi}:maskbits{mm.bit_count()}",None
            pool[residue]=cand; group_status.append("full")
            continue
        partial=[(i,m,v) for i,m,v in g if m and (32-m.bit_count())<=threshold]
        if not partial:
            group_status.append("underdetermined"); continue
        i0,m0,v0=min(partial,key=lambda x:32-x[1].bit_count())
        unknown=[j for j in range(32) if not (m0>>j)&1]
        base=v0&m0; good=set()
        for bits in range(1<<len(unknown)):
            s=base
            for k,j in enumerate(unknown):
                if (bits>>k)&1: s|=1<<j
            cand=pool_from_state(i0,s)
            if all((pool_state(i,cand)&m)==(v&m) for i,m,v in g):
                good.add(cand)
                if len(good)>1: break
        if not good:
            return f"pool-contradiction:res{residue}:partial-word{i0}:unknown{len(unknown)}",None
        if len(good)==1:
            pool[residue]=next(iter(good)); group_status.append("partial-unique")
        else:
            group_status.append("partial-ambiguous")
    if any(x is None for x in pool):
        return "underdetermined:"+",".join(group_status),None
    return "recovered:"+",".join(group_status),tuple(pool)

def make_basis(seq,payloads,axvals,phase):
    b=Basis()
    # Original printer rows; selected row129 was withheld in load().
    for row,payload in enumerate(payloads):
        if payload is None: continue
        pos=1227+phase+STARTS[row]
        for lane in range(4):
            native=untemper(int.from_bytes(payload[lane*4:lane*4+4],"little"))
            for j,v in enumerate(seq[pos+lane]): b.insert(v,(native>>j)&1)
    # AX-7778 checkpoints: byte-swapped high16 of tempered outputs at relative -157..-142.
    for k,value in enumerate(axvals):
        pos=1070+phase+k
        for bit,v in enumerate(temper(seq[pos])[16:]): b.insert(v,(value>>bit)&1)
    return b

def stream_from_pool(pool,count=2400):
    key=np.empty(624,dtype=np.uint32)
    for i in range(624): key[i]=pool_state(i,pool[i%4])
    key[0]=0x80000000
    rng=np.random.MT19937(0)
    rng.state={"bit_generator":"MT19937","state":{"key":key,"pos":623}}
    return [int(x) for x in rng.random_raw(count)]

def source_gate(pool,phase,payloads,axvals):
    out=stream_from_pool(pool)
    good=0
    for row,payload in enumerate(payloads):
        if payload is None: continue
        start=604+phase+STARTS[row]
        if struct.pack("<4I",*out[start:start+4])==payload: good+=1
    ax_ok=all(((out[604+phase-157+k]>>16)&0xffff)==v for k,v in enumerate(axvals))
    return good,ax_ok,out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",default="/mnt/data/h17-archive")
    ap.add_argument("--phases",default="0-392"); ap.add_argument("--threshold",type=int,default=16)
    ap.add_argument("--synthetic",action="store_true"); ap.add_argument("--seed",type=int,default=1234); ap.add_argument("--phase",type=int,default=13)
    args=ap.parse_args(); root=Path(args.root)
    payloads,axvals=load(root)
    seq=words()
    if args.synthetic:
        phase=args.phase; pool=tuple(int(x) for x in np.random.SeedSequence(args.seed).pool)
        out=stream_from_pool(pool)
        syn=[]
        for row in range(133):
            start=604+phase+STARTS[row]; syn.append(struct.pack("<4I",*out[start:start+4]))
        syn[129]=None
        ax=[(out[604+phase-157+k]>>16)&0xffff for k in range(16)]
        b=make_basis(seq,syn,ax,phase)
        status,recovered=recover_pool(b,seq,phase,args.threshold)
        good=source_gate(recovered,phase,syn,ax)[0] if recovered else None
        print(json.dumps({"synthetic_rank":b.rank,"status":status,"pool_recovered":recovered==pool if recovered else False,"full_packets":good}))
        return
    if args.phases=="0-392": phases=range(393)
    else: phases=[int(x) for x in args.phases.split(",") if x]
    counts={}; hits=[]; t0=time.time()
    for n,phase in enumerate(phases,1):
        try:
            b=make_basis(seq,payloads,axvals,phase)
            rank_before_s0=b.rank
            status,pool=recover_pool(b,seq,phase,args.threshold)
            item={"phase":phase,"rank_before_s0":rank_before_s0,"rank_after_s0":b.rank,"status":status}
            if pool:
                good,ax_ok,out=source_gate(pool,phase,payloads,axvals)
                item["full_intact_packets"]=good; item["ax_match"]=ax_ok
                if good==132 and ax_ok:
                    route=json.loads((root/"evidence/recovery-routing.json").read_text())
                    accepted=json.loads((root/"acceptance.json").read_text())
                    mask=bytes.fromhex(route["K04"]["masked_component"])
                    raw=struct.pack("<4I",*out[604+phase+STARTS[129]:604+phase+STARTS[129]+4])
                    candidate=bytes(a^b for a,b in zip(raw,mask))
                    item["K04_commitment_match"]=hashlib.sha256(candidate).hexdigest()==accepted["slot_sha256"]["K04"]
                    hits.append(item)
            counts[status]=counts.get(status,0)+1
            print(json.dumps(item),flush=True)
        except ValueError as e:
            item={"phase":phase,"status":"source-contradiction","detail":str(e)}
            counts[item["status"]]=counts.get(item["status"],0)+1
            print(json.dumps(item),flush=True)
    print("AGGREGATE",json.dumps({"counts":counts,"candidate_gate_hits":hits,"seconds":round(time.time()-t0,3)}),flush=True)

if __name__=="__main__": main()
