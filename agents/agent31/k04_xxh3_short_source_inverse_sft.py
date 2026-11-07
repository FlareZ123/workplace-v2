"""Invert a seeded XXH3-128 short-metadata issuer from intact print packets.
Original K04 selected row129 and late RECOVER rows131/132 are withheld.
Pure Python 3 stdlib; original full 128-bit output, no seed enumeration.
"""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re

MASK = (1 << 64) - 1
P1, P2, P3 = 0x9E3779B185EBCA87, 0xC2B2AE3D27D4EB4F, 0x165667B19E3779F9
MX1, MX2, P32 = 0x165667919E3779F9, 0x9FB21C651E98DF25, 0x85EBCA77
SEC = bytes.fromhex(
    "b8fe6c3923a44bbe7c01812cf721ad1c"
    "ded46de9839097db7240a4a4b7b3671f"
    "cb79e64eccc0e578825ad07dccff7221"
    "b8084674f743248ee03590e6813a264c"
)
def word(i: int, n: int = 8) -> int:
    return int.from_bytes(SEC[i:i+n], "little")
B1 = word(0, 4) ^ word(4, 4)
B2 = word(8, 4) ^ word(12, 4)
B4 = word(16) ^ word(24)
B9 = word(32) ^ word(40)
B10 = word(48) ^ word(56)

def ux(x: int, shift: int) -> int:
    p = shift
    while p < 64:
        x ^= x >> p
        p *= 2
    return x & MASK

def avalanche3(x: int) -> int:
    x ^= x >> 37
    x = x * MX1 & MASK
    return (x ^ (x >> 32)) & MASK

def avalanche64(x: int) -> int:
    x ^= x >> 33
    x = x * P2 & MASK
    x ^= x >> 29
    x = x * P3 & MASK
    return (x ^ (x >> 32)) & MASK

def inv3(y: int) -> int:
    return ux(ux(y, 32) * pow(MX1, -1, 1 << 64) & MASK, 37)

def inv64(y: int) -> int:
    a = ux(y, 32) * pow(P3, -1, 1 << 64) & MASK
    b = ux(a, 29) * pow(P2, -1, 1 << 64) & MASK
    return ux(b, 33)

def swap(x: int, n: int) -> int:
    return int.from_bytes(x.to_bytes(n, "little"), "big")

def emit(msg: bytes, seed: int) -> tuple[int,int]:
    n = len(msg)
    assert 1 <= n <= 16
    if n <= 3:
        a,b,c = msg[0], msg[n // 2], msg[-1]
        co = (a << 16) | (b << 24) | c | (n << 8)
        ch = ((swap(co,4) << 13) | (swap(co,4) >> 19)) & 0xFFFFFFFF
        return (avalanche64(co ^ ((B1 + seed) & MASK)),
                avalanche64(ch ^ ((B2 - seed) & MASK)))
    if n <= 8:
        flipped = seed ^ (swap(seed & 0xFFFFFFFF,4) << 32)
        v = int.from_bytes(msg[:4], "little") | (int.from_bytes(msg[-4:], "little") << 32)
        z = v ^ ((B4 + flipped) & MASK)
        prod = z * (P1 + (n << 2))
        lo,hi = prod & MASK, (prod >> 64) & MASK
        hi = (hi + 2 * lo) & MASK
        lo ^= hi >> 3
        lo ^= lo >> 35
        lo = lo * MX2 & MASK
        return ((lo ^ (lo >> 28)) & MASK, avalanche3(hi))
    il,ih = int.from_bytes(msg[:8], "little"), int.from_bytes(msg[-8:], "little")
    z = ih ^ ((B10 + seed) & MASK)
    prod = (il ^ ih ^ ((B9 - seed) & MASK)) * P1
    lo = ((prod & MASK) + ((n-1) << 54)) & MASK
    hi = ((prod >> 64) + z + (z & 0xFFFFFFFF) * (P32-1)) & MASK
    lo ^= swap(hi,8)
    q = lo * P2
    return (avalanche3(q & MASK), avalanche3(((q >> 64) + hi * P2) & MASK))

def recover(msg: bytes, seen: tuple[int,int]) -> int | None:
    n = len(msg)
    lo,hi = seen
    if n <= 3:
        co = (msg[0] << 16) | (msg[n//2] << 24) | msg[-1] | (n << 8)
        seed = ((inv64(lo) ^ co) - B1) & MASK
    elif n <= 8:
        h = inv3(hi)
        m = ux(ux(lo,28) * pow(MX2,-1,1 << 64) & MASK,35) ^ (h >> 3)
        v = int.from_bytes(msg[:4],"little") | (int.from_bytes(msg[-4:],"little") << 32)
        flipped = ((((m * pow(P1 + (n << 2),-1,1 << 64)) & MASK) ^ v) - B4) & MASK
        lower = flipped & 0xFFFFFFFF
        seed = lower | (((flipped >> 32) ^ swap(lower,4)) << 32)
    else:
        low = inv3(lo) * pow(P2,-1,1 << 64) & MASK
        h = ((inv3(hi) - (low * P2 >> 64)) * pow(P2,-1,1 << 64)) & MASK
        m = ((low ^ swap(h,8)) - ((n-1) << 54)) & MASK
        il,ih = int.from_bytes(msg[:8],"little"),int.from_bytes(msg[-8:],"little")
        seed = (B9 - (((m * pow(P1,-1,1 << 64)) & MASK) ^ il ^ ih)) & MASK
    return seed if emit(msg,seed) == seen else None

def views(raw: bytes):
    a,b = raw[:8],raw[8:]
    return tuple((int.from_bytes(x,endian),int.from_bytes(y,endian))
                 for endian in ("little","big") for x,y in ((a,b),(b,a)))

def message(p: tuple, typ: int) -> bytes:
    timestamp,num,attempt,status,kind,raw,dest = p
    s = f"{int(num):04d}"
    c = {"LABEL":"L","STORES":"S","RECOVER":"R"}[kind]
    d = {"bench":"B","desk":"D","store":"S"}[dest]
    a = {"ACK":"A","REQUESTED":"Q"}[status]
    t = datetime.fromisoformat(timestamp.replace("Z","+00:00"))
    epoch = int(t.timestamp())
    return (
        s.encode(),str(int(num)).encode(),int(num).to_bytes(4,"little"),
        int(num).to_bytes(4,"big"),f"{s}{attempt}".encode(),
        f"{s}:{attempt}".encode(),f"{s}{attempt}{c}".encode(),
        f"{s}{attempt}{d}".encode(),f"{s}{attempt}{c}{d}".encode(),
        f"{s}{attempt}{a}".encode(),f"{s}{attempt}{a}{c}".encode(),
        f"{s}{c}{d}".encode(),f"{s}{c}{a}{d}".encode(),
        f"{s}{t.hour:02d}{t.minute:02d}".encode(),
        epoch.to_bytes(8,"little"),epoch.to_bytes(8,"big"),
        f"PS-261003-{s}".encode(),f"PS-261003-{s}:{attempt}".encode(),
        f"PS-261003-{s}{attempt}{c}".encode(),
        f"{t.year:04d}{t.month:02d}{t.day:02d}{t.hour:02d}{t.minute:02d}{t.second:02d}".encode(),
        f"261003{s}".encode(),f"2026-10-03T{t.hour:02d}{t.minute:02d}".encode(),
        f"{s}{attempt}{kind[:3]}".encode()
    )[typ]

def main():
    vectors = ((1,0,0xFC1537FC103CB7CF,0x4F4A9030B7ABD431),
               (3,0xDEADBEEF,0xD240B6A7A87119F0,0x8D7888AA9FD3860E),
               (4,0xFEDCBA9876543210,0x610EC516B6DF337D,0x60A26DAEBCB3377F),
               (8,0,0x215E49ECDD1D4CC1,0x712007B418C68C23),
               (9,0xDEADBEEF,0xA7680C17C62E36F6,0xA4E09B08DF0484AD),
               (16,0xFEDCBA9876543210,0xB519BCC936CA8F1B,0xDDE3F518F581C328))
    for n,seed,x,y in vectors:
        msg=bytes(range(0x20,0x20+n))
        assert emit(msg,seed)==(x,y)
        assert recover(msg,(x,y))==seed
    for n in range(1,17):
        for seed in (0,1,0xDEADBEEF,0xFEDCBA9876543210,MASK):
            msg=bytes(range(0x20,0x20+n))
            assert recover(msg,emit(msg,seed))==seed
    path=Path(__file__).resolve().parents[2]/"resources/evidence/print/spool-reconstruction.log"
    source=path.read_bytes()
    assert sha256(source).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    pat=re.compile(rb"^(\S+) JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)$")
    rows=tuple((m[1].decode(),m[2].decode(),int(m[3]),m[4].decode(),m[5].decode(),
                bytes.fromhex(m[6].decode()),m[7].decode())
               for line in source.splitlines() if (m:=pat.fullmatch(line)))
    assert len(rows)==133 and [int(r[1]) for r in rows[128:]]==[417,417,417,448,420]
    assert rows[129][5].hex().upper()=="A9A9DC5731A5E2AE879C47215C2559D5"
    source_train=tuple(r for i,r in enumerate(rows) if i not in (129,131,132))
    holdout=(rows[131],rows[132])
    hits=[]
    for group in ("global","LABEL","STORES","RECOVER"):
        train=source_train if group=="global" else tuple(r for r in source_train if r[4]==group)
        anchor=train[0]
        for typ in range(23):
            for presentation,seen in enumerate(views(anchor[5])):
                seed=recover(message(anchor,typ),seen)
                if seed is not None:
                    confirmed=sum(emit(message(r,typ),seed) in views(r[5]) for r in train[1:])
                    withheld=sum(emit(message(r,typ),seed) in views(r[5]) for r in holdout)
                    hits.append((group,typ,presentation,seed,confirmed,len(train)-1,withheld))
    print("LIBXXHASH_REFERENCE=6/6 SYNTHETIC_SOURCE_INVERSES=80/80")
    print("TRAIN=130 TWO_SIMULTANEOUS_LATE_ACKS_WITHHELD=2")
    print("EXACT_SOURCE_ANCHOR_FITS",len(hits),"OF",4*23*4)
    print("VALIDATED_SOURCE_ISSUERS",sum(x[4]==x[5] and x[6]==2 for x in hits))
    for x in hits:
        print("SOURCE_HYPOTHESIS",x)

if __name__=="__main__":
    main()
