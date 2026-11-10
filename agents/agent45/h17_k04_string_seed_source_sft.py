"""Original H17 printer source-first text-seed search; selected coupon withheld."""
import argparse
import hashlib
import random
import re
import zipfile
from pathlib import Path

SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
N=8192
ANCHORS=[
"H-17","H17","IR-261003-H17","H17-IR-261003","REC8/1",
"PS-261003-0417","PS-261003-0300","ESC-N","ESC-S",
"2026-10-03","261003","20261003","2026","Oct03",
"RECOVER","ACK","WN-14","RC-17","AX-7782","PTW-417",
"K01","K02","K03","K04","K05","K06","K07","K08",
"CEG","CEG-ARCHIVE-RECOVERY","CEG-ARCHIVE-RECOVERY/v1",
"archive","recovery","coupon","printer","north","escrow",
"incident","watch","paper","envelope","mask","Emily",
]

def originals(archive):
    if archive:
        with zipfile.ZipFile(archive) as z:
            paths=[n for n in z.namelist() if n.startswith("evidence/") and not n.endswith(".pdf")]
            data=[z.read(n) for n in paths]
            spool=z.read("evidence/print/spool-reconstruction.log")
    else:
        root=Path(__file__).resolve().parents[2]/"resources"/"evidence"
        data=[p.read_bytes() for p in root.rglob("*") if p.is_file() and p.suffix!=".pdf"]
        spool=(root/"print"/"spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest()==SPOOL_SHA
    lines=[s for s in spool.decode("ascii").splitlines() if s.startswith("2026-")]
    assert len(lines)==133 and "ATTEMPT=2 STATE=ACK" in lines[129] and "PS-261003-0417" in lines[129]
    assert "PS-261003-0300" in lines[0]
    packet=bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})",lines[0]).group(1))
    return data,packet

def seeds(data):
    tokens=set(ANCHORS)
    for raw in data:
        for v in re.findall(r"(?<![\w])(?:[A-Za-z][A-Za-z0-9-]{1,60}|[0-9]{4,16})(?![\w])",raw.decode("utf-8","ignore")):
            if len(v)<=60:
                tokens.add(v)
    root={v for v in tokens if len(v)<=45}
    vals=set(root)
    for v in root:
        vals.update((v.lower(),v.upper()))
    for a in ANCHORS:
        for b in root:
            if len(a)+len(b)>70:
                continue
            for sep in ("","-","_",":","/"," "):
                vals.update((a+sep+b,b+sep+a))
    out=sorted(v for v in vals if len(v)<100 and "FBBBC543" not in v)
    assert len(tokens)==2105 and len(out)==1078631
    return out

def positions(data,packet):
    words=[packet[i:i+4] for i in range(0,16,4)]
    needles={w for v in words for w in (v,v[::-1])}
    found=set()
    for needle in needles:
        at=data.find(needle)
        while at>=0:
            if at%4==0:
                ix=at//4
                for p in range(max(0,ix-3),min(N-4,ix)+1):
                    native=[data[4*q:4*q+4] for q in range(p,p+4)]
                    if all(any(w in (v,v[::-1]) for v in native) for w in words):
                        found.add(p)
            at=data.find(needle,at+1)
    return found

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path,default=None)
    parser.add_argument("--start",type=int,default=0)
    parser.add_argument("--end",type=int,default=1078631)
    args=parser.parse_args()
    data,packet=originals(args.archive)
    dictionary=seeds(data)
    assert 0<=args.start<args.end<=len(dictionary)
    synthetic=random.Random("H17-original-source-positive-control").randbytes(N*4)
    original=synthetic[4*431:4*435]
    planted=original[12:16][::-1]+original[:4]+original[8:12][::-1]+original[4:8]
    assert 431 in positions(synthetic,planted)
    assert 431 not in positions(synthetic,bytes([planted[0]^1])+planted[1:])
    hits=[]
    for i in range(args.start,args.end):
        sample=random.Random(dictionary[i]).randbytes(N*4)
        for stage in positions(sample,packet):
            hits.append((i,dictionary[i],stage))
    print("SEEDS",len(dictionary),"TESTED",args.end-args.start,
          "WORDS_PER_SEED",N,"HISTORICAL_WHOLE_PACKET_HITS",len(hits))
    for item in hits:
        print("MATCH",item)
    assert not hits

if __name__=="__main__":
    main()
