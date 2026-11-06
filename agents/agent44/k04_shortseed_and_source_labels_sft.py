"""H-17 selected-withheld printer CPython short and source-ID seed emitter SFT."""
import argparse,hashlib,random,re,zipfile
from pathlib import Path,PurePosixPath
PIN="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
FIRST="FBBBC54356483F5864BB3F06794518A5"
EXT=(".txt",".md",".log",".ini",".json",".jsonl",".csv",".eml",".html")
IDENTIFIERS=["H17","H-17","[censored] Energy Group","Energy Group","IR-261003-H17","H17-IR-261003","IR261003","IR-261003","261003","20261003","2026-10-03","2026-10-03T07:00:00+00:00","2026-10-03T18:02:00+00:00","PS-261003-0300","PS-261003-0417","PS-261003-0420","PS-261003-0448","ESC-N","ESC-S","RECOVER","LABEL","STORES","READ_ONLY_RECORDS","REC8/1","K04","K08","AX-7782","WN-14","LT-204","PTW-417","RC-17","8131","BX25/08","FA-17","L-29/N","H17-POL-17/A3","October 2026","3 October 2026","2026","103","17","417","0300","0417","7782","17"]
def load(archive):
    if archive:
        with zipfile.ZipFile(archive) as z:
            names=z.namelist()
            return z.read("evidence/print/spool-reconstruction.log"),names,b"\n".join(z.read(n) for n in names if n.endswith(EXT))
    root=Path(__file__).resolve().parents[2]/"resources"
    names=sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
    named=["START_HERE.md","verify.py","evidence/","acceptance.json","candidate.template.json"]
    named.extend(n for n in names if n.startswith("evidence/"))
    for n in names:
        for parent in PurePosixPath(n).parents:
            s=str(parent)
            if n.startswith("evidence/") and s!="." and s+"/" not in named:named.append(s+"/")
    raw=b"\n".join((root/n).read_bytes() for n in names if n.endswith(EXT))
    return (root/"evidence/print/spool-reconstruction.log").read_bytes(),named,raw
def source_keys(names,all_text):
    tokens={}
    for raw in re.findall(rb"[A-Za-z0-9][A-Za-z0-9_./:|+\-]{2,63}",all_text):
        s=raw.decode("ascii")
        if s.count(":")>4 or len(s)>58 or (len(s)>=9 and all(c in "0123456789ABCDEFabcdef" for c in s)):continue
        tokens[s]=tokens.get(s,0)+1
    base=set(IDENTIFIERS)
    for n in names:
        base.add(n)
        if not n.endswith("/"):
            base.add(PurePosixPath(n).name);base.add(PurePosixPath(n).stem)
    base.update(sorted(tokens,key=lambda s:(-tokens[s],s))[:384])
    keys=set()
    for s in base:
        if s and len(s)<=96:keys.update((s,s.lower(),s.upper(),s.replace("-",""),s.replace("-","_"),s.replace("/","")))
    for a in IDENTIFIERS[:28]:
        for b in IDENTIFIERS[:28]:
            if a!=b:
                for sep in ("","|","-",":","_"):keys.add(a+sep+b)
    return sorted(x for x in keys if x and len(x)<=128),len(base),len(tokens)
def scan(seeds,views,limit):
    n=first_hits=0;matches=[]
    for label,seed in seeds:
        stream=random.Random(seed).randbytes((limit+4)*4)
        n+=limit+1
        for view,payload in views.items():
            pos=stream.find(payload[:4])
            while pos>=0:
                if pos%4==0 and pos<=limit*4:
                    first_hits+=1
                    if stream[pos:pos+16]==payload:matches.append((label,view,pos//4))
                pos=stream.find(payload[:4],pos+1)
    return n,first_hits,matches
def main():
    a=argparse.ArgumentParser();a.add_argument("--archive");a.add_argument("--warmup",type=int,default=8192);a.add_argument("--numeric-stop",type=int,default=65536);args=a.parse_args()
    assert 0<=args.warmup<=8192 and 0<=args.numeric_stop<=65536
    raw,names,all_text=load(args.archive)
    assert hashlib.sha256(raw).hexdigest()==PIN
    rows=[dict(re.findall(r"([A-Z]+)=([^ ]+)",line)) for line in raw.decode().splitlines() if line.startswith("2026")]
    assert len(rows)==133 and rows[0]["JOB"]=="PS-261003-0300" and rows[0]["PAYLOAD"]==FIRST
    b=bytes.fromhex(FIRST);w=[b[i:i+4] for i in range(0,16,4)]
    views={"little":b,"big":b"".join(x[::-1] for x in w),"little_reverse":b"".join(w[::-1]),"big_reverse":b"".join(x[::-1] for x in w[::-1])}
    r=random.Random(42);assert random.Random(42).randbytes(160)==b"".join(r.getrandbits(32).to_bytes(4,"little") for _ in range(40))
    planted=random.Random(2026).randbytes(1024*4)
    assert planted.find(planted[57*4:61*4])==57*4
    for mode in ("integer","decimal_text"):
        seeds=((str(i), i if mode=="integer" else str(i)) for i in range(args.numeric_stop))
        n,first,matches=scan(seeds,views,args.warmup)
        assert matches==[]
        print("NUMERIC",mode,"seeds",args.numeric_stop,"starts",n,"firstword",first,"whole_packet",len(matches))
    keys,base,token_count=source_keys(names,all_text)
    planted=random.Random("IR-261003-H17").randbytes((1234+4)*4)[1234*4:1238*4]
    assert random.Random("IR-261003-H17").randbytes(8196*4).find(planted)==1234*4
    for mode in ("text","sha256_int"):
        seeds=((s,s if mode=="text" else int.from_bytes(hashlib.sha256(s.encode()).digest(),"big")) for s in keys)
        n,first,matches=scan(seeds,views,args.warmup)
        assert matches==[]
        print("IDENTIFIER",mode,"keys",len(keys),"starts",n,"firstword",first,"whole_packet",len(matches))
    if args.archive and args.warmup==8192 and args.numeric_stop==65536:assert (len(keys),base,token_count)==(5149,552,2765)
    print("ORIGINAL_SHA256",PIN,"INTACT_HOLDOUT",FIRST,"SYNTHETIC_STARTUPS_57_1234","PASS","K04","MISSING")
if __name__=="__main__":main()
