"""H17: common original copier bit permutation applied to mask AND selected ACK.
Run: python agents/agent31/k04_shared_exporter_prexor_bitplane_sft.py original.zip [transpose|pixel]
Reads only original ZIP. 20,643,840 full K04 checks per geometry. 
"""
import hashlib,itertools,json,re,sys,time,zipfile
SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
FULL=(1<<128)-1
def load(path):
    with zipfile.ZipFile(path) as z:
        raw=z.read("evidence/print/spool-reconstruction.log")
        route=json.loads(z.read("evidence/recovery-routing.json"))
        acceptance=json.loads(z.read("acceptance.json"))
    assert hashlib.sha256(raw).hexdigest()==SPOOL_SHA
    rows=[r for r in raw.decode().splitlines() if "PAYLOAD=" in r]
    assert len(rows)==133 and "ATTEMPT=2 STATE=ACK CLASS=RECOVER" in rows[129]
    copied=bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})",rows[129]).group(1))
    assert copied.hex().upper()=="A9A9DC5731A5E2AE879C47215C2559D5"
    mask=bytes.fromhex(route["K04"]["masked_component"])
    return bytes(x^y for x,y in zip(copied,mask)),bytes.fromhex(acceptance["slot_sha256"]["K04"])
def run(path,family="all"):
    data,target=load(path)
    original=int.from_bytes(data,"big")
    maps=[(a,b,tuple((a*i+b)%16 for i in range(16))) for a in range(1,16,2) for b in range(16)]
    planted=(2,7,0,4,1,6,5,3)
    start=time.monotonic()
    kinds=("transpose","pixel") if family=="all" else (family,)
    for kind in kinds:
        assert kind in ("transpose","pixel")
        count=positive=real=0
        if kind=="transpose":
            for a,b,order in maps:
                source=bytes(data[i] for i in order)
                planes=[sum(((source[j]>>(7-k))&1)<<(15-j) for j in range(16)).to_bytes(2,"big")
                        for k in range(8)]
                for perm in itertools.permutations(range(8)):
                    x=int.from_bytes(b"".join(planes[i] for i in perm),"big")
                    vals=(x,x^FULL,x^original,x^original^FULL)
                    p=(hashlib.sha256(vals[3].to_bytes(16,"big")).digest()
                       if (a,b)==(3,5) and perm==planted else None)
                    for v in vals:
                        d=hashlib.sha256(v.to_bytes(16,"big")).digest()
                        real+=d==target
                        positive+=p is not None and d==p
                        count+=1
        else:
            symbols=sorted(set(data))
            for perm in itertools.permutations(range(8)):
                conversion={v:sum(((v>>(7-perm[k]))&1)<<(7-k) for k in range(8)) for v in symbols}
                modified=bytes(conversion[v] for v in data)
                for a,b,order in maps:
                    x=int.from_bytes(bytes(modified[i] for i in order),"big")
                    vals=(x,x^FULL,x^original,x^original^FULL)
                    p=(hashlib.sha256(vals[3].to_bytes(16,"big")).digest()
                       if (a,b)==(3,5) and perm==planted else None)
                    for v in vals:
                        d=hashlib.sha256(v.to_bytes(16,"big")).digest()
                        real+=d==target
                        positive+=p is not None and d==p
                        count+=1
        assert count==20643840 and positive==1 and real==0
        print("FAMILY",kind,"ORIGINAL_CHECKS",count,"PLANTED_POSITIVE",positive,
              "ORIGINAL_K04_MATCHES",real,"SEC",round(time.monotonic()-start,2),flush=True)
if __name__=="__main__":
    run(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else "all")
