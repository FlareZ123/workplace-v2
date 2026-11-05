"""H17 K04: 2D differential raster-copy candidate SFT, original source only.
Usage: python agents/agent31/k04_fax_2d_differential_sft.py original.zip [2|4|8|16|32|64]
Historical copier codec is hypothetical; original source and commitments read-only.
"""
import hashlib,json,re,sys,time,zipfile
SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
FULL=(1<<128)-1
PLANTED_COMPONENT=bytes.fromhex("7B68DAAA4C2AE2D6A2C042B921315267")
PLANTED_HASH=bytes.fromhex("4e1b5884d0260954fdc6918a4cff646179d9e0ea16f5d2f5fff7d60b117ed3dc")
assert hashlib.sha256(PLANTED_COMPONENT).digest()==PLANTED_HASH
def original(path):
    with zipfile.ZipFile(path) as z:
        spool=z.read("evidence/print/spool-reconstruction.log")
        route=json.loads(z.read("evidence/recovery-routing.json"))
        acceptance=json.loads(z.read("acceptance.json"))
    assert hashlib.sha256(spool).hexdigest()==SPOOL_SHA
    lines=[x for x in spool.decode().splitlines() if "PAYLOAD=" in x]
    assert len(lines)==133 and "ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
    payload=bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})",lines[129]).group(1))
    mask=bytes.fromhex(route["K04"]["masked_component"])
    assert payload.hex().upper()=="A9A9DC5731A5E2AE879C47215C2559D5"
    return payload,mask,bytes.fromhex(acceptance["slot_sha256"]["K04"])
def scan_map(h,w,rowshift,colshift,major,serp,reflectr,reflectc):
    result=[]
    for r in range(h):
        for c in range(w):
            rr=((h-1-r if reflectr else r)+rowshift)%h
            cc=((w-1-c if reflectc else c)+colshift)%w
            if major==0:
                j=rr*w+(w-1-cc if serp and rr%2 else cc)
            else:
                j=cc*h+(h-1-rr if serp and cc%2 else rr)
            result.append(j)
    assert len(result)==128 and len(set(result))==128
    return result
def two_dimensional(grid,h,w,mode):
    out=[0]*128
    for r in range(h):
        for c in range(w):
            j=r*w+c
            above=j-w if r else -1
            left=j-1 if c else -1
            if mode==0:
                out[j]=grid[j]^(grid[above] if above>=0 else 0)
            elif mode==1:
                out[j]=grid[j]^(out[above] if above>=0 else 0)
            elif mode==2:
                out[j]=grid[j]^(grid[left] if left>=0 else 0)
            elif mode==3:
                out[j]=grid[j]^(out[left] if left>=0 else 0)
            elif mode==4:
                out[j]=grid[j]^(grid[above] if above>=0 else 0)^(grid[left] if left>=0 else 0)
            else:
                out[j]=grid[j]^(out[above] if above>=0 else 0)^(out[left] if left>=0 else 0)
    x=0
    for bit in out:
        x=(x<<1)|bit
    return x
def run(path,only_shape=None):
    p,m,target=original(path)
    sources=(p,m,bytes(a^b for a,b in zip(p,m)))
    bitviews=(
        [tuple((v[i>>3]>>(7-(i&7)))&1 for i in range(128)) for v in sources],
        [tuple((v[i>>3]>>(i&7))&1 for i in range(128)) for v in sources],
    )
    p_int=int.from_bytes(p,"big")
    m_int=int.from_bytes(m,"big")
    checks=hits=positives=0
    started=time.monotonic()
    for h in (2,4,8,16,32,64):
        if only_shape is not None and h!=only_shape:
            continue
        w=128//h
        subtotal=0
        for rowshift in range(h):
            for colshift in range(w):
                for major in range(2):
                    for serp in range(2):
                        for reflectr in range(2):
                            for reflectc in range(2):
                                order=scan_map(h,w,rowshift,colshift,major,serp,reflectr,reflectc)
                                for bitorder,views in enumerate(bitviews):
                                    grids=[tuple(view[j] for j in order) for view in views]
                                    for mode in range(6):
                                        for stage in range(3):
                                            x=two_dimensional(grids[stage],h,w,mode)
                                            component=x^(m_int if stage==0 else p_int if stage==1 else 0)
                                            for invert in (0,1):
                                                coupon=(component^(FULL if invert else 0)).to_bytes(16,"big")
                                                digest=hashlib.sha256(coupon).digest()
                                                checks+=1
                                                subtotal+=1
                                                hits+=digest==target
                                                positives+=digest==PLANTED_HASH
                                                if (h,rowshift,colshift,major,serp,reflectr,reflectc,bitorder,mode,stage,invert)==(
                                                    8,3,5,1,1,1,0,1,5,2,1):
                                                    assert coupon==PLANTED_COMPONENT
        assert subtotal==147456
        print("GRID",h,w,"ORIGINAL_CHECKS",subtotal,"ORIGINAL_K04_HITS",hits,
              "elapsed",round(time.monotonic()-started,2),flush=True)
    if only_shape is None:
        assert checks==884736 and positives>=1 and hits==0
    print("FINAL",checks,"ORIGINAL_HITS",hits,"PLANTED_POSITIVES",positives)
if __name__=="__main__":
    run(sys.argv[1],int(sys.argv[2]) if len(sys.argv)>2 else None)
