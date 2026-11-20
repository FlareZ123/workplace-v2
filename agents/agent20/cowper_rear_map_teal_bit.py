#!/usr/bin/env python3
"""Bounded, hypothesis-only Cowper rear-chart K08 test.

Uses the eight K01 byte pairs as normalized chart coordinates and samples
teal/green/blue low-bit predicates across Google Books pages 360-390 of the
1893 Cowper Part II scan. A matching K08 HMAC would be a candidate hit only;
the physical-book identity still requires custody evidence.
"""
from __future__ import annotations
import hashlib, hmac, json, re
from pathlib import Path
from PIL import Image
import colorsys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path("out/cowper-rear-map")
PAGES = []
candidate = json.loads((ROOT / "candidate.json").read_text())
routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
raw = bytes.fromhex(candidate["K01"])
COORDS = [(raw[i], raw[i+1]) for i in range(0, 16, 2)]
NONCE = bytes.fromhex(routing["K08"]["desk_nonce"])
TARGET = acceptance["slot_sha256"]["K08"]

def norm(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())

def bbox(im: Image.Image):
    rgb = im.convert("RGB")
    w, h = rgb.size
    # Ignore only a narrow scan border; retain the full image as a control.
    return (0, 0, w, h)

def transform(x, y, t):
    return [
        (x,y),(255-x,y),(x,255-y),(255-x,255-y),
        (y,x),(255-y,x),(y,255-x),(255-y,255-x)
    ][t]

def map_point(x, y, box, t):
    x,y = transform(x,y,t)
    x0,y0,x1,y1 = box
    return (x0 + round(x * max(0,x1-x0-1)/255),
            y0 + round(y * max(0,y1-y0-1)/255))

def teal(rgb):
    r,g,b = rgb
    hh,ss,vv = colorsys.rgb_to_hsv(r/255,g/255,b/255)
    return (110 <= hh*360 <= 180 and ss*255 >= 64 and vv*255 >= 32)

def pack(bits, reverse):
    if reverse: bits = bits[::-1]
    v=0
    for bit in bits: v=(v<<1)|int(bit)
    return v

manifest_path = OUT / "manifest.json"
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
images=[]
for item in manifest:
    if not item.get("file"): continue
    p=OUT/item["file"]
    try:
        im=Image.open(p).convert("RGB")
        im.load()
        images.append((item["printedPage"], im, item["sha256"], p.name))
    except Exception as e:
        print(f"IMAGE_SKIP page={item.get('printedPage')} error={e}")
images.sort(key=lambda x:x[0])
if not images:
    raise SystemExit("NO_IMAGES_CAPTURED")

# Per-page color evidence; this distinguishes actual chart pages from text scans.
for page,im,digest,name in images:
    sample=im.copy()
    sample.thumbnail((180,180))
    pix=list(sample.getdata())
    chroma=sum(1 for r,g,b in pix if max(r,g,b)-min(r,g,b)>32)
    teal_count=sum(1 for rgb in pix if teal(rgb))
    print(f"PAGE_COLOR page={page} file={name} size={im.size} chroma={chroma}/{len(pix)} teal={teal_count}/{len(pix)} sha256={digest}")

# Candidate predicates: literal teal membership and G/B low bits, plus unmasked
# G/B low bits as controls. No source claim is made by this finite screen.
variants=[]
for sym in range(8):
  for reverse_bits in (False, True):
    for pred in ("teal-membership","teal-G-low","teal-B-low","G-low","B-low"):
      for order in ("asc","desc"):
        seq=images if order=="asc" else list(reversed(images))
        out=[]
        for page,im,digest,name in seq:
          bits=[]
          for x,y in COORDS:
            px,py=map_point(x,y,(0,0,im.width,im.height),sym)
            rgb=im.getpixel((px,py))
            is_teal=teal(rgb)
            if pred=="teal-membership": bit=int(is_teal)
            elif pred=="teal-G-low": bit=(rgb[1]&1) if is_teal else 0
            elif pred=="teal-B-low": bit=(rgb[2]&1) if is_teal else 0
            elif pred=="G-low": bit=rgb[1]&1
            else: bit=rgb[2]&1
            bits.append(bit)
          out.append(pack(bits,reverse_bits))
        bs=bytes(out)
        letters=sum(b==32 or 65<=b<=90 or 97<=b<=122 for b in bs)
        printable=sum(32<=b<127 for b in bs)
        variants.append(((letters,printable),f"{pred}/sym{sym}/{order}/{'revbits' if reverse_bits else 'fwdbits'}",bs))

        # Also test even- and odd-numbered printed pages separately.
        for parity in (0,1):
          chosen=[x for x in seq if x[0]%2==parity]
          if not chosen: continue
          out2=[]
          for page,im,digest,name in chosen:
            bits=[]
            for x,y in COORDS:
              px,py=map_point(x,y,(0,0,im.width,im.height),sym)
              rgb=im.getpixel((px,py)); is_teal=teal(rgb)
              if pred=="teal-membership": bit=int(is_teal)
              elif pred=="teal-G-low": bit=(rgb[1]&1) if is_teal else 0
              elif pred=="teal-B-low": bit=(rgb[2]&1) if is_teal else 0
              elif pred=="G-low": bit=rgb[1]&1
              else: bit=rgb[2]&1
              bits.append(bit)
            out2.append(pack(bits,reverse_bits))
          bs2=bytes(out2)
          letters2=sum(b==32 or 65<=b<=90 or 97<=b<=122 for b in bs2)
          printable2=sum(32<=b<127 for b in bs2)
          variants.append(((letters2,printable2),f"{pred}/sym{sym}/{order}/{'revbits' if reverse_bits else 'fwdbits'}/page-parity-{parity}",bs2))

hits=[]
for score,label,bs in variants:
    # Search contiguous byte spans for a printable ASCII caption (8-96 chars).
    for start in range(len(bs)):
      for end in range(start+8,min(len(bs),96)+1):
        raw=bs[start:end]
        if any(b<32 or b>126 for b in raw): continue
        text=raw.decode("ascii")
        normalized=norm(text)
        if not normalized: continue
        comp=hmac.new(NONCE,normalized.encode("utf-8"),hashlib.sha256).digest()[:16]
        if hashlib.sha256(comp).hexdigest()==TARGET:
          hits.append((label,start,end,text,normalized,comp.hex().upper()))

print(f"SUMMARY captured={len(images)} variants={len(variants)} hmac_hits={len(hits)} target={TARGET}")
for hit in hits:
    print("HMAC_HIT "+json.dumps({"variant":hit[0],"start":hit[1],"end":hit[2],"raw":hit[3],"normalized":hit[4],"component":hit[5]}))
for score,label,bs in sorted(variants,key=lambda x:(x[0][0],x[0][1]),reverse=True)[:30]:
    print(f"DECODE score={score} variant={label} hex={bs.hex().upper()} repr={bs!r}")
print("INTERPRETATION=HYPOTHESIS_ONLY; no K08 assignment without authenticated physical-book/source join.")
