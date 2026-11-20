#!/usr/bin/env python3
"""Hypothesis-only Cowper rear-chart K08 test.

The 1893 Cowper Part II scan is a candidate for MAIL-09's map-back book.
This bounded pass captures pages 360-390, runs the existing frozen K08
teal-mask/low-if-even image decoder on each page, and separately tests K01's
eight byte-pairs as normalized chart coordinates. A hit is not historical
authentication: the physical-book identity and image-to-Emily caption link
remain unproven.
"""
from __future__ import annotations
import hashlib, hmac, json, sys
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path("out/cowper-rear-map")
sys.path.insert(0, str(ROOT / "work"))
from h17_k08_teal_bit_image_scan import scan_image, load_commitment, normalize_phrase, k08_matches

candidate = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))
raw = bytes.fromhex(candidate["K01"])
COORDS = [(raw[i], raw[i+1]) for i in range(0, 16, 2)]
NONCE, TARGET = load_commitment(ROOT / "resources")

manifest_path = OUT / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
images=[]
for item in manifest:
    if not item.get("file"): continue
    path=OUT/item["file"]
    try:
        with Image.open(path) as opened:
            im=opened.convert("RGB")
            im.load()
        images.append((int(item["printedPage"]), path, im, item["sha256"]))
    except Exception as exc:
        print(f"IMAGE_SKIP page={item.get('printedPage')} error={exc}")
images.sort(key=lambda x:x[0])
if not images:
    raise SystemExit("NO_IMAGES_CAPTURED")

def ink_bbox(im: Image.Image):
    rgb=im.convert("RGB")
    scale=min(1.0,450.0/max(rgb.size))
    small=rgb.resize((max(1,round(rgb.width*scale)),max(1,round(rgb.height*scale))))
    pix=small.load()
    xs=[]; ys=[]
    for y in range(small.height):
        for x in range(small.width):
            r,g,b=pix[x,y]
            if (r+g+b)/3 < 225 or max(r,g,b)-min(r,g,b) > 28:
                xs.append(x); ys.append(y)
    if not xs: return (0,0,rgb.width,rgb.height)
    inv=1.0/scale
    return (max(0,int(min(xs)*inv)),max(0,int(min(ys)*inv)),
            min(rgb.width,int((max(xs)+1)*inv)),min(rgb.height,int((max(ys)+1)*inv)))

def transform(x,y,t):
    return [(x,y),(255-x,y),(x,255-y),(255-x,255-y),
            (y,x),(255-y,x),(y,255-x),(255-y,255-x)][t]

def map_point(x,y,box,t):
    x,y=transform(x,y,t)
    x0,y0,x1,y1=box
    return (x0+round(x*max(0,x1-x0-1)/255),
            y0+round(y*max(0,y1-y0-1)/255))

def pack(bits, reverse):
    if reverse: bits=bits[::-1]
    v=0
    for bit in bits: v=(v<<1)|int(bit)
    return v

def hmac_hits(bs, label):
    hits=[]
    for start in range(len(bs)):
        for end in range(start+8,min(len(bs),96)+1):
            raw=bs[start:end]
            if any(b<32 or b>126 for b in raw): continue
            text=raw.decode("ascii")
            normalized=normalize_phrase(text)
            if normalized and k08_matches(normalized,NONCE,TARGET):
                hits.append({"variant":label,"start":start,"end":end,
                             "raw":text,"normalized":normalized})
    return hits

# First, apply the already-frozen K08 decoder to each page, with no changes to
# its two source-literal layouts or bit packing.
bitplane_hits=[]
for page,path,im,digest in images:
    matches=scan_image(path,NONCE,TARGET)
    for match in matches:
        bitplane_hits.append({"page":page,**match})
    print(f"BITPLANE page={page} sha256={digest} matches={len(matches)}")
for hit in bitplane_hits:
    print("BITPLANE_HMAC_HIT "+json.dumps(hit,sort_keys=True))

# Then test the source-linked K01 coordinate interpretation. The teal mask and
# absolute-pixel parity are identical to the frozen decoder:
# HSV 110..150, S>=64, V>=32; bit 0 at even flat indices, bit 1 at odd.
hmac_results=[]
variants=[]
for sym in range(8):
  for frame in ("full","ink"):
    for channel_name,channel_idx in (("green",1),("blue",2)):
      for reverse_bits in (False,True):
        for order in ("asc","desc"):
          seq=images if order=="asc" else list(reversed(images))
          for parity in ("all","even-pages","odd-pages","teal-pages"):
            chosen=[]
            for page,path,im,digest in seq:
                if parity=="even-pages" and page%2: continue
                if parity=="odd-pages" and page%2==0: continue
                if parity=="teal-pages":
                    hsv=im.convert("HSV")
                    hp=hsv.load()
                    w,h=im.size
                    teal_count=0
                    # A sparse grid is sufficient for page inclusion, not decoding.
                    for yy in range(0,h,max(1,h//80)):
                        for xx in range(0,w,max(1,w//80)):
                            hh,ss,vv=hp[xx,yy]
                            if 110<=hh<=150 and ss>=64 and vv>=32: teal_count+=1
                    if teal_count<2: continue
                chosen.append((page,path,im,digest))
            if not chosen: continue
            out=[]
            for page,path,im,digest in chosen:
                hsv=im.convert("HSV")
                hp=hsv.load(); rgb=im.load()
                box=(0,0,im.width,im.height) if frame=="full" else ink_bbox(im)
                bits=[]
                for x,y in COORDS:
                    px,py=map_point(x,y,box,sym)
                    hh,ss,vv=hp[px,py]
                    is_teal=(110<=hh<=150 and ss>=64 and vv>=32)
                    idx=py*im.width+px
                    bit=((rgb[px,py][channel_idx] >> (idx&1)) & 1) if is_teal else 0
                    bits.append(bit)
                out.append(pack(bits,reverse_bits))
            bs=bytes(out)
            label=f"{channel_name}/{frame}/sym{sym}/{order}/{parity}/{'revbits' if reverse_bits else 'fwdbits'}"
            letters=sum(b==32 or 65<=b<=90 or 97<=b<=122 for b in bs)
            printable=sum(32<=b<127 for b in bs)
            variants.append(((letters,printable),label,bs))
            hmac_results.extend(hmac_hits(bs,label))

print(f"SUMMARY captured={len(images)} bitplane_hits={len(bitplane_hits)} coordinate_variants={len(variants)} coordinate_hmac_hits={len(hmac_results)} target={TARGET}")
for hit in hmac_results:
    print("COORDINATE_HMAC_HIT "+json.dumps(hit,sort_keys=True))
for score,label,bs in sorted(variants,key=lambda x:(x[0][0],x[0][1]),reverse=True)[:30]:
    print(f"COORDINATE_DECODE score={score} variant={label} hex={bs.hex().upper()} repr={bs!r}")
print("INTERPRETATION=HYPOTHESIS_ONLY; no K08 assignment without authenticated physical-book/source join.")
