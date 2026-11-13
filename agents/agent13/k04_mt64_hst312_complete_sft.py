"""Source-frozen 312-word MT19937-64 HST/print K04 constructor.
No selected ACK2 input. Standard-library single-file reproducibility test.
"""
import hashlib,json,re,struct
from itertools import product
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/"resources"
MASK=(1<<64)-1
A=0xB5026F5AA96619E9
TARGET="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
COUPON_MASK=bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
HST_SHA="3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"

def rr(y,k,m):
    x=y
    for _ in range(5): x=y^((x>>k)&m)
    return x&MASK

def rl(y,k,m):
    x=y
    for _ in range(5): x=y^((x<<k)&m)
    return x&MASK

def temper(x):
    x^=(x>>29)&0x5555555555555555
    x^=(x<<17)&0x71D67FFFEDA60000
    x^=(x<<37)&0xFFF7EEE000000000
    return (x^(x>>43))&MASK

def untemper(x):
    x=rr(x,43,MASK)
    x=rl(x,37,0xFFF7EEE000000000)
    x=rl(x,17,0x71D67FFFEDA60000)
    return rr(x,29,0x5555555555555555)

def twist(a):
    b=a.copy()
    for i in range(312):
        y=(b[i]&(MASK^((1<<31)-1)))|(b[(i+1)%312]&((1<<31)-1))
        b[i]=(b[(i+156)%312]^(y>>1)^(A if y&1 else 0))&MASK
    return b

def predict(words,n=24):
    assert len(words)==312
    s=twist([untemper(w) for w in words])
    out=[]
    while len(out)<n:
        out.extend(map(temper,s))
        s=twist(s)
    return out[:n]

def positive_control():
    init=[5489]
    for i in range(1,312):
        p=init[-1]
        init.append((6364136223846793005*(p^(p>>62))+i)&MASK)
    first=[temper(x) for x in twist(init)]
    second=[temper(x) for x in twist(twist(init))]
    assert first[0]==14514284786278117030
    assert predict(first,312)==second
    for x in (0,1,MASK,0x123456789ABCDEF0):
        assert untemper(temper(x))==x
    print("synthetic native MT64 continuation PASS 312/312")

def sources():
    spool=ROOT/"evidence/print/spool-reconstruction.log"
    hst=ROOT/"evidence/telemetry/freeze-export.jsonl"
    assert hashlib.sha256(spool.read_bytes()).hexdigest()==SPOOL_SHA
    assert hashlib.sha256(hst.read_bytes()).hexdigest()==HST_SHA
    pattern=re.compile(r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)")
    rows=[]
    for line in spool.read_text("utf8").splitlines():
        m=pattern.search(line)
        if m: rows.append((int(m[1]),int(m[2]),m[3],m[4],bytes.fromhex(m[5])))
    assert len(rows)==133
    first,late=rows[:128],rows[128:]
    assert [r[0] for r in first]==list(range(300,428))
    assert [(r[0],r[1],r[2]) for r in late]==[
        (417,1,"REQUESTED"),(417,2,"ACK"),(417,3,"REQUESTED"),
        (448,1,"ACK"),(420,2,"ACK")]
    pv=[json.loads(line) for line in hst.read_text("utf8").splitlines()]
    pv=[x for x in pv if x["field"]=="PV"]
    assert len(pv)==112 and sorted(x["seq"] for x in pv)==list(range(100,212))
    return first,late,pv

def history_words(rows,order,codec):
    if order=="seq": rows=sorted(rows,key=lambda x:x["seq"])
    if order=="ts": rows=sorted(rows,key=lambda x:(datetime.fromisoformat(x["ts"]).timestamp(),x["seq"]))
    if codec=="float":
        return [struct.unpack("<I",struct.pack("<f",float(x["value"])))[0] for x in rows]
    if codec=="milli": return [round(float(x["value"])*1000)&0xffffffff for x in rows]
    return [round(float(x["value"]))&0xffffffff for x in rows]

def layout_words(printer,hist,layout):
    if layout=="h-first": return hist+printer
    if layout=="p-first": return printer+hist
    pos=int(layout)
    out=[]
    for i in range(56):
        block=printer[i*4:i*4+4]
        out+=block[:pos]+[hist[i]]+block[pos:]
    return out+printer[224:]

def coupon(pair,endian,reverse):
    return b"".join(x.to_bytes(8,endian) for x in (pair[::-1] if reverse else pair))

def main():
    positive_control()
    first,late,pv=sources()
    models=checks=hits=0
    best=0
    for order,codec,pair,endian,reverse,layout in product(
        ("seq","raw","ts"),("float","milli","int"),(False,True),
        ("little","big"),(False,True),
        ("h-first","p-first","0","1","2","3","4")):
        x=history_words(pv,order,codec)
        h=[(x[i]<<32|x[i+1]) if pair else (x[i+1]<<32|x[i]) for i in range(0,112,2)]
        printer=[]
        for row in first:
            b=row[4]
            two=[int.from_bytes(b[j:j+8],endian) for j in (0,8)]
            printer.extend(two[::-1] if reverse else two)
        future=predict(layout_words(printer,h,layout))
        models+=1
        for policy in ("all","ack-only"):
            offsets={0:0,1:2,2:4,3:6,4:8} if policy=="all" else {1:0,3:2,4:4}
            controls=(0,2,3,4) if policy=="all" else (3,4)
            matched=sum(coupon(future[offsets[j]:offsets[j]+2],endian,reverse)==late[j][4] for j in controls)
            best=max(best,matched)
            p=coupon(future[offsets[1]:offsets[1]+2],endian,reverse)
            comp=bytes(a^b for a,b in zip(p,COUPON_MASK))
            checks+=1
            if hashlib.sha256(comp).hexdigest()==TARGET:
                hits+=1
                print("K04 ORIGINAL MATCH",comp.hex().upper(),order,codec,pair,endian,reverse,layout,policy)
    assert (models,checks)==(504,1008)
    print("models",models,"complete K04 checks",checks,"hits",hits,"best heldout whole-packet controls",best)

if __name__=="__main__":
    main()
