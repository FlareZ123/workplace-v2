"""Source-only exact CPython MT initial register masks at selected true output origins.

Reuses the p951 native packet chronology. Original selected ACK2 row129 withheld.
Run: python agents/agent3/k04_cpython_k2494_source_projector_sft.py 2494
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2] / "resources"
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
U=0xffffffff
MAG=0x9908b0df

def untemper(x: int) -> int:
    for shift,left,mask in ((18,False,U),(15,True,0xefc60000),(7,True,0x9d2c5680),(11,False,U)):
        old=x
        for _ in range(6):
            old=x^(((old<<shift)&mask) if left else (old>>shift))
        x=old&U
    return x

def words(n: int) -> list[list[int]]:
    out=[[1<<(i*32+b) for b in range(32)] for i in range(624)]
    for i in range(624,n):
        p,q,r=out[i-624],out[i-623],out[i-227]
        out.append([r[b]^(p[31] if b==30 else q[b+1] if b<30 else 0)^(q[0] if (MAG>>b)&1 else 0) for b in range(32)])
    return out

def basis_build(arr: list[list[int]], packets: list[bytes], offset: int) -> dict[int,int]:
    basis={}
    for i,(p,block) in enumerate(zip(STARTS,packets)):
        if i==129:
            continue
        for lane in range(4):
            original=untemper(int.from_bytes(block[4*lane:4*(lane+1)],"little"))
            for bit,expr in enumerate(arr[624+offset+p+lane]):
                row=(expr<<1)|((original>>bit)&1)
                while row:
                    pivot=row.bit_length()-1
                    prev=basis.get(pivot)
                    if prev is None:
                        basis[pivot]=row
                        break
                    row^=prev
                assert row != 1, "Original intact printer record contradicts the given chronology"
    assert len(basis)==15365
    return basis

def recover(arr: list[list[int]], basis: dict[int,int]) -> list[tuple[int,int]]:
    out=[]
    for i in range(624):
        mask=value=0
        for bit,expr in enumerate(arr[i]):
            row=expr<<1
            while row:
                pivot=row.bit_length()-1
                prev=basis.get(pivot)
                if prev is None:
                    break
                row^=prev
            if row in (0,1):
                mask|=1<<bit
                value|=row<<bit
        out.append((mask,value))
    return out

def main(offsets: list[int]) -> None:
    raw=(ROOT/"evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(raw).hexdigest()==SHA
    packets=[bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)]
    assert len(packets)==len(STARTS)==133 and STARTS[129]==951
    now=time.monotonic()
    arr=words(624+max(offsets)+max(STARTS)+4)
    for offset in offsets:
        basis=basis_build(arr,packets,offset)
        state=recover(arr,basis)
        print("OFFSET",offset,"TOTAL_FIXED",sum(mask.bit_count() for mask,_ in state),
              "FULL",[(i,f"{v:08X}") for i,(mask,v) in enumerate(state) if mask==U],
              "FIRST35",[(i,f"{m:08X}",f"{v:08X}")
                         for i,(m,v) in enumerate(state[:35]) if m],
              "ELAPSED",round(time.monotonic()-now,1),flush=True)
        if offset==2494:
            assert sum(m.bit_count() for m,_ in state)==693
            for i,m,v in (
                (3,0x8000001f,0x00000011),
                (4,U,0xe403bb7d),(5,U,0x1f7b301f),
                (6,0x09cc1c00,0x008c1000),
                (13,0x000000ff,0x000000b6),
                (14,0x5398ba7d,0x4010a820),
                (15,0x01800800,0x00000800),
            ):
                assert state[i]==(m,v),(i,state[i],m,v)
            print("PINNED_K2494_ORIGINAL_MASKS=PASS",flush=True)

if __name__=="__main__":
    main([int(x) for x in sys.argv[1:]] or [2494])
