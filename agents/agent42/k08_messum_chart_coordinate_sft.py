#!/usr/bin/env python3
"""K08 exploratory 11-chart / eight-coordinate sampler.

Source hypothesis: K01 supplies eight byte pairs as normalized x/y coordinates;
the ATEALBIT note initialism suggests taking one color-derived bit at each
coordinate. Each of the eleven 1903 East Coast Rivers plates then emits one
byte. This script only prints candidate 11-byte decodings; it never edits H-17
sources or verifier state.
"""
from __future__ import annotations
import io
import urllib.request
from PIL import Image

COORDS=[(4,154),(171,46),(28,222),(122,130),(205,124),(96,35),(67,3),(201,26)]
URLS=[f"https://www.antiquemapsandprints.com/cdn/shop/files/P-6-{n}a.jpg?width=1000" for n in range(108821,108832)]

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.read()

def sample(im):
    im=im.convert("RGB")
    w,h=im.size
    return [im.getpixel((round(x*(w-1)/255),round(y*(h-1)/255))) for x,y in COORDS]

def byte_from(bits, msb=True):
    if not msb:
        bits=list(reversed(bits))
    v=0
    for b in bits:
        v=(v<<1)|int(bool(b))
    return v

def printable(bs):
    return sum(32<=b<127 or b in (9,10,13) for b in bs)

ims=[]
for i,u in enumerate(URLS,108821):
    data=get(u)
    im=Image.open(io.BytesIO(data))
    im.load()
    print(f"FETCH {i} bytes={len(data)} size={im.size} mode={im.mode}")
    ims.append(sample(im))

preds=[]
for c,name in enumerate("RGB"):
    for bit in range(8):
        preds.append((f"{name}_bit{bit}",lambda rgb,c=c,bit=bit:(rgb[c]>>bit)&1))
for name,fn in [
    ("G_gt_R",lambda p:p[1]>p[0]),
    ("B_gt_R",lambda p:p[2]>p[0]),
    ("GB_gt_2R",lambda p:p[1]+p[2]>2*p[0]),
    ("G_gt_B",lambda p:p[1]>p[2]),
    ("B_gt_G",lambda p:p[2]>p[1]),
    ("GplusB_gt_256",lambda p:p[1]+p[2]>=256),
    ("teal_dist_lt_yellow",lambda p:(p[0]-0)**2+(p[1]-128)**2+(p[2]-128)**2 < (p[0]-128)**2+(p[1]-128)**2+(p[2]-0)**2),
]:
    preds.append((name,fn))

rows=[]
for pname,pred in preds:
    for msb in (True,False):
        bs=bytes(byte_from([pred(p) for p in plate],msb) for plate in ims)
        rows.append((printable(bs),pname,"msb" if msb else "lsb",bs))
for score,pname,order,bs in sorted(rows,reverse=True)[:40]:
    print(f"DECODE score={score}/11 pred={pname} order={order} hex={bs.hex().upper()} repr={bs!r}")
