"""SFT: speculative p951 future-stage replay K04 candidates from original intact carriers.

Read-only, no third-party dependencies. From repo root: python agents/agent11/k04_p951_future_replay_sft.py
The selected spool row129 is omitted from source-state construction. Original source
SHA pins and a held-out intact-row positive ensure extraction and algebra correctness.
"""
import hashlib
import importlib.util
import itertools
import json
import re
import struct
import zlib
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "resources"
spec = importlib.util.spec_from_file_location("p951",ROOT / "agents/agent49/k04_p951_symbolic_basis.py")
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
source_basis, words = mt.source(RES)
assert source_basis.rank == 15365
START,END,MAX_RANK=1038,5300,3
for i in range(len(words),END-mt.ORIGIN+4):
    t=i-624
    words.append([words[t+397][j]^(words[t][31] if j==30 else (words[t+1][j+1] if j<30 else 0))^(words[t+1][0] if (0x9908b0df>>j)&1 else 0) for j in range(32)])

def pinned(path, sha):
    raw=(RES/path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==sha,path
    return raw

spool=pinned("evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083")
ax_raw=pinned("evidence/transfers/transfer-audit.jsonl","32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf")
tr_raw=pinned("evidence/recorder/trip-recorder.raw","5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba")
rows=[bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})",spool)]
assert len(rows)==133
ax=sorted((json.loads(line) for line in ax_raw.splitlines() if b'"transfer": "AX-7778"' in line and b'"kind": "CHUNK"' in line),key=lambda x:(x["seq"],x["attempt"]))
assert len(ax)==16 and len({(x["seq"],x["attempt"]) for x in ax})==16
version,record_size,count=struct.unpack_from("<HHI",tr_raw,8)
assert tr_raw[:8]==b"TRP2DUMP" and (version,record_size,count,len(tr_raw))==(2,24,88,2128)
rec=[]
for i in range(count):
    off=16+i*24
    timestamp,node,event,latch,seq,control,aux,crc=struct.unpack_from("<IHBBI4sII",tr_raw,off)
    if node==49 and event==82 and 200<=seq<=203 or node==49 and event==82 and 900<=seq<=903 or node==49 and event==82 and 990<=seq<=993:
        rec.append((seq,latch,control,zlib.crc32(tr_raw[off:off+20])==crc))
assert len(rec)==12
route=json.loads((RES/"evidence/recovery-routing.json").read_text())
acceptance=json.loads((RES/"acceptance.json").read_text())
mask=bytes.fromhex(route["K04"]["masked_component"])
target=acceptance["slot_sha256"]["K04"]

def symbolic_temper(v):
    a=[v[j]^(v[j+11] if j+11<32 else 0) for j in range(32)]
    b=[a[j]^(a[j-7] if j>=7 and (0x9d2c5680>>j)&1 else 0) for j in range(32)]
    c=[b[j]^(b[j-15] if j>=15 and (0xefc60000>>j)&1 else 0) for j in range(32)]
    return [c[j]^(c[j+18] if j+18<32 else 0) for j in range(32)]

def reduce(b,v):
    known=0;residual=0
    while v:
        p=v.bit_length()-1
        if p in b.rows:
            w,rhs=b.rows[p];v^=w;known^=rhs
        else:
            residual |= 1<<p;v ^= 1<<p
    return residual,known

def quotient_labels(window):
    piv={};labels=[]
    for word in window:
        for residual,known in word:
            c=0;v=residual
            while v:
                p=v.bit_length()-1
                if p in piv:
                    w,bit=piv[p];v^=w;c^=bit
                else:
                    new=1<<len(piv);piv[p]=(v,new);c^=new;break
            labels.append((known,c))
    return len(piv),labels

def coupon(labels, assignment):
    pieces=[]
    for lane in range(4):
        native=0
        for bit in range(32):
            known,c=labels[32*lane+bit]
            native|=(known ^ ((c&assignment).bit_count()&1))<<bit
        n=native
        n^=n>>11;n^=(n<<7)&0x9d2c5680;n^=(n<<15)&0xefc60000;n^=n>>18
        pieces.append((n&0xffffffff).to_bytes(4,"little"))
    return pieces

transforms=[(p,r) for p in itertools.permutations(range(4)) for r in itertools.product((False,True),repeat=4)]

def run(ax_on,node_on,bad_on):
    b=mt.Basis()
    b.rows=source_basis.rows.copy();b.rank=source_basis.rank
    if ax_on:
        for i,x in enumerate(ax):
            cp=int.from_bytes(bytes.fromhex(x["checkpoint"]),"little")
            bits=symbolic_temper(words[-157+i-mt.ORIGIN])
            for j in range(16):
                b.insert(bits[j+16],(cp>>j)&1)
    rank_ax=b.rank
    if node_on:
        for seq,latch,control,crc_good in rec:
            if not bad_on and not crc_good:continue
            step=0 if seq<300 else 1 if seq<990 else 2
            idx=-324+3*latch+step
            val=mt.untemper(int.from_bytes(control,"little"))
            for j,v in enumerate(words[idx-mt.ORIGIN]):
                b.insert(v,(val>>j)&1)
    target_q=[[reduce(b,v) for v in words[951+i-mt.ORIGIN]] for i in range(4)]
    assert quotient_labels(target_q)[0]==128
    intact=[[reduce(b,v) for v in words[955+i-mt.ORIGIN]] for i in range(4)]
    r,labels=quotient_labels(intact)
    assert r==0 and b"".join(coupon(labels,0))==rows[130]

    d=deque(maxlen=4);hist=Counter();low=[];native=oriented=0;matches=[];planted=0
    for i in range(START,END+4):
        d.append([reduce(b,v) for v in words[i-mt.ORIGIN]])
        if len(d)<4:continue
        stage=i-3
        rank,labels=quotient_labels(d)
        hist[rank]+=1
        if rank>MAX_RANK:continue
        low.append((stage,rank))
        selected=(1<<rank)-1
        planted_value=b"".join(coupon(labels,selected))
        planted_hash=hashlib.sha256(bytes(x^y for x,y in zip(planted_value,mask))).digest()
        planted_found=False
        for assignment in range(1<<rank):
            original=coupon(labels,assignment)
            v=b"".join(original)
            native+=1
            digest=hashlib.sha256(bytes(x^y for x,y in zip(v,mask))).digest()
            if digest==planted_hash:planted_found=True
            if digest.hex()==target:matches.append((stage,assignment,"direct"))
            for p,reversals in transforms:
                v=b"".join(original[p[j]][::-1] if reversals[j] else original[p[j]] for j in range(4))
                oriented+=1
                if hashlib.sha256(bytes(x^y for x,y in zip(v,mask))).hexdigest()==target:
                    matches.append((stage,assignment,(p,reversals)))
        assert planted_found
        planted+=1
    return {"AX":ax_on,"node":node_on,"bad_CRC_included":bad_on,"final_source_rank":b.rank,
        "source_rank_after_AX":rank_ax,"selected_rank":128,"window_count":sum(hist.values()),
        "lowrank_count":len(low),"native_candidates":native,"layout_assignments":oriented,
        "planted_controls":planted,"lowrank_stages":low,"authentic_matches":matches}

def main():
    tests=((False,False,False),(True,False,False),(False,True,False),
        (True,True,False),(True,True,True))
    results=[run(*t) for t in tests]
    assert [(x["lowrank_count"],x["native_candidates"],x["layout_assignments"]) for x in results]==[
        (52,147,56448),(52,147,56448),(52,147,56448),(52,147,56448),(69,197,75648)]
    assert all(x["window_count"]==4263 and not x["authentic_matches"] for x in results)
    print(json.dumps({"result":"NO_MATCH","source_rows":132,"window_start":START,
        "window_end":END,"max_rank":MAX_RANK,"models":results},indent=2))

if __name__=="__main__":
    main()
