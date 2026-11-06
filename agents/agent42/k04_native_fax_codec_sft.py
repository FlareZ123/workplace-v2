"""Read-only historical H-17 native TIFF/CCITT/PackBits copier hypothesis.
Requires Pillow built with libtiff. Never edits source or acceptance.
"""
from __future__ import annotations
import contextlib
import hashlib
import io
import itertools
import json
import os
import re
import struct
import sys
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "resources"

def original(name):
    if ARCHIVE.is_file():
        with zipfile.ZipFile(ARCHIVE) as z:
            return z.read(name)
    return (ARCHIVE / name).read_bytes()

spool = original("evidence/print/spool-reconstruction.log")
route = json.loads(original("evidence/recovery-routing.json"))
acceptance = json.loads(original("acceptance.json"))
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
selected = [s for s in spool.decode().splitlines()
            if "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in s]
assert len(selected) == 1
copied = bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})", selected[0]).group(1))
assert copied.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
mask = bytes.fromhex(route["K04"]["masked_component"])
target = acceptance["slot_sha256"]["K04"]

# Exactly one 16-byte compressed TIFF strip; the IFD includes 1-bit data tags.
def wrap_tiff(data, width, comp, fill, photo, t4):
    height = 128 // width
    tags = [(256,4,width),(257,4,height),(258,3,1),(259,3,comp),
            (262,3,photo),(266,3,fill),(273,4,0),(277,3,1),
            (278,4,height),(279,4,len(data)),(284,3,1),(292,4,t4),(293,4,0)]
    offset = 8 + 2 + 12 * len(tags) + 4
    out = bytearray(b"II*\\x00".replace(b"\\x00",b"\x00") + struct.pack("<I",8)
                    + struct.pack("<H",len(tags)))
    for tag, kind, value in tags:
        out += struct.pack("<HHII", tag, kind, 1, offset if tag == 273 else value)
    out += b"\x00" * 4 + data
    assert offset + len(data) == len(out)
    return bytes(out)

@contextlib.contextmanager
def quiet_native_errors():
    with open(os.devnull, "wb") as devnull:
        old = os.dup(2)
        try:
            os.dup2(devnull.fileno(), 2)
            yield
        finally:
            os.dup2(old, 2)
            os.close(old)

def decode(data, width, comp, fill, photo, t4):
    with quiet_native_errors():
        try:
            img = Image.open(io.BytesIO(wrap_tiff(data,width,comp,fill,photo,t4)))
            img.load()
            raw = img.tobytes()
            return raw if len(raw) == 16 else None
        except (OSError, ValueError, SyntaxError):
            return None

def encode(raw, width, codec):
    img = Image.frombytes("1", (width,128//width), raw)
    out = io.BytesIO()
    img.save(out, format="TIFF", compression=codec)
    b = out.getvalue()
    tagged = Image.open(io.BytesIO(b))
    start, length = tagged.tag_v2[273][0], tagged.tag_v2[279][0]
    return b[start:start+length]

names = [(2,"tiff_ccitt"),(3,"group3"),(4,"group4"),(32773,"packbits")]
synthetic = bytes.fromhex("FFE00000000000000000000000000000")
for comp, name in names:
    assert decode(encode(synthetic,16,name),16,comp,1,1,0) == synthetic, name
planted = bytes(x for value in (1,35,69,103,137,171,205,239) for x in (value,value))
packed = bytes(x for value in (1,35,69,103,137,171,205,239) for x in (255,value))
assert decode(packed,16,32773,1,1,0) == planted

reverse_bits = bytes(int(f"{i:08b}"[::-1],2) for i in range(256))
variants = lambda b: (b,b[::-1],b.translate(reverse_bits),b[::-1].translate(reverse_bits))
stats = {"tested":0,"decoded":0,"canonical_reencodings":0,"distinct":0,
         "codec_decodes":{},"hits":[]}
seen = set()
for stage, data in (("copied",copied),("mask",mask),
                    ("prexor",bytes(a^b for a,b in zip(copied,mask)))):
    for var_idx, content in enumerate(variants(data)):
        for width in (8,16,32,64,128):
            for comp, name in names:
                for fill, photo, t4 in itertools.product((1,2),(0,1),
                                                         (0,1) if comp == 3 else (0,)):
                    stats["tested"] += 1
                    decoded = decode(content,width,comp,fill,photo,t4)
                    if decoded is None:
                        continue
                    stats["decoded"] += 1
                    stats["codec_decodes"][name] = stats["codec_decodes"].get(name,0)+1
                    if fill == photo == 1 and t4 == 0:
                        try:
                            stats["canonical_reencodings"] += int(encode(decoded,width,name)==content)
                        except (OSError, ValueError):
                            pass
                    if stage == "copied":
                        component = bytes(a^b for a,b in zip(decoded,mask))
                    elif stage == "mask":
                        component = bytes(a^b for a,b in zip(decoded,copied))
                    else:
                        component = decoded
                    if component in seen:
                        continue
                    seen.add(component)
                    if hashlib.sha256(component).hexdigest() == target:
                        stats["hits"].append((stage,var_idx,width,name,fill,photo,t4,component.hex()))
stats["distinct"] = len(seen)
print(json.dumps(stats,indent=2))
assert stats["tested"] == 1200
