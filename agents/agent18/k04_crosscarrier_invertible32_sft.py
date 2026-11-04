"""Read-only 32-bit invertible mixer state-gap probe over H-17 sources."""
from __future__ import annotations
import re
import json
import hashlib
import sys
from pathlib import Path

BASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
E = BASE / "evidence"
P = (E / "print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(P).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
V = []
for line in P.decode().splitlines():
    m = re.search(r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32})",line)
    if m:
        V.append((f"spool/{m[1]}/{m[2]}/{m[3]}/{m[4]}/{line[:20]}",bytes.fromhex(m[5])))
r = json.loads((E / "recovery-routing.json").read_text())
V.extend([("K04_mask",bytes.fromhex(r["K04"]["masked_component"])),("K08_nonce",bytes.fromhex(r["K08"]["desk_nonce"]))])
for k,s in [
    ("K01","049AAB2E1CDE7A82CD7C60234303C91A"),
    ("K02","0D7E3AB56FB75DA3EB0E2E06786D239E"),
    ("K02_source","E1A5E474BAD7E853A2E8C71D3317D507"),
    ("K03","1384AF96E25D6ADA666209CB55E062FA"),
    ("K05","FF8B78200A56E8586DCDA00EF01E4572"),
    ("K06","5DBF40EE52FAAED9A536D3326CF0D95A"),
    ("K07","93495F5E425AB8E592123DABAEB68545"),
    ("K07_source","8947CEDCB9CC73BAB7E87BE63302C5C9")
]:
    V.append((k,bytes.fromhex(s)))
assert len(V) == 143
MASK = (1 << 32) - 1

def undo(y,n):
    x=y
    while n < 32:
        x ^= x >> n
        n *= 2
    return x & MASK

def mixer(x,c1,c2,s1,s2,s3):
    x ^= x >> s1
    x = x*c1 & MASK
    x ^= x >> s2
    x = x*c2 & MASK
    return x ^ (x >> s3)

def invert(x,c1,c2,s1,s2,s3):
    x=undo(x,s3)
    x=x*pow(c2,-1,1<<32)&MASK
    x=undo(x,s2)
    x=x*pow(c1,-1,1<<32)&MASK
    return undo(x,s1)

models={
    "murmur3_fmix":(0x85EBCA6B,0xC2B2AE35,16,13,16,0x9E3779B9),
    "lowbias32":(0x7FEB352D,0x846CA68B,16,15,16,0x9E3779B9)
}
summary={}
for model,(c1,c2,s1,s2,s3,gamma) in models.items():
    invg=pow(gamma,-1,1<<32)
    for i in range(1000):
        state=(0x12345678+i*gamma)&MASK
        assert invert(mixer(state,c1,c2,s1,s2,s3),c1,c2,s1,s2,s3)==state
    obs=[]
    for name,payload in V:
        for endian in ("big","little"):
            for index in range(4):
                value=int.from_bytes(payload[index*4:index*4+4],endian)
                obs.append((name,endian,index,invert(value,c1,c2,s1,s2,s3)))
    limit=16
    hits=[]
    for a in range(len(obs)):
        aa=obs[a]
        for b in range(a+1,len(obs)):
            bb=obs[b]
            gap=(bb[3]-aa[3])*invg & MASK
            signed=gap if gap<(1<<31) else gap-(1<<32)
            if 0<abs(signed)<=limit:
                hits.append((signed,aa[:3],bb[:3]))
    state=0xCAFEBABE
    xx=mixer((state+gamma)&MASK,c1,c2,s1,s2,s3)
    yy=mixer((state+5*gamma)&MASK,c1,c2,s1,s2,s3)
    delta=(invert(yy,c1,c2,s1,s2,s3)-invert(xx,c1,c2,s1,s2,s3))*invg & MASK
    assert delta==4
    summary[model]={
        "views":len(obs),"pairs":len(obs)*(len(obs)-1)//2,
        "signed_gap_limit":limit,"hits":len(hits),"sample":hits[:15],
        "intra_packet_gap1":sum(a[0]==b[0] and abs(n)==1 for n,a,b in hits)
    }
print(json.dumps(summary,indent=2))
