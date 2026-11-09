#!/usr/bin/env python3
"""K08 source-pinned 128-job CLASS/DEST ternary-carrier test; original + planted full-caption control."""
from __future__ import annotations
import argparse
import hashlib
import hmac
import itertools
import json
import re
import zipfile
from pathlib import Path

PINS = {
 "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
 "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
 "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
CLASSES = ("LABEL", "STORES", "RECOVER")
DESTS = ("bench", "desk", "store")
LINE = re.compile(
 r"^2026-10-03T[\d:]+\+00:00 JOB=PS-261003-(\d{4}) ATTEMPT=1 STATE=ACK "
 r"CLASS=(LABEL|STORES|RECOVER) PAYLOAD=[0-9A-F]{32} DEST=(bench|desk|store)$")

def normalized(s):
 return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())

def component(nonce, phrase):
 return hmac.new(nonce, normalized(phrase).encode(), hashlib.sha256).digest()[:16]

def inputs(path, zipped):
 if zipped:
  with zipfile.ZipFile(path) as z:
   data = {name: z.read(name) for name in PINS}
 else:
  data = {name: (path / name).read_bytes() for name in PINS}
 for name, digest in PINS.items():
  assert hashlib.sha256(data[name]).hexdigest() == digest, name
 return data

def original_pairs(spool):
 found = {}
 for line in spool.decode("ascii").splitlines():
  m = LINE.fullmatch(line)
  if m and 300 <= int(m[1]) <= 427:
   k = int(m[1])
   assert k not in found
   found[k] = (m[2], m[3])
 assert sorted(found) == list(range(300, 428))
 return [found[i] for i in range(300, 428)]

def layouts(pairs):
 for ca in itertools.permutations(CLASSES):
  for de in itertools.permutations(DESTS):
   for reverse in (False, True):
    rows = pairs[::-1] if reverse else pairs
    a = [ca.index(x) for x, _ in rows]
    b = [de.index(y) for _, y in rows]
    yield (ca,de,reverse,0), [n for x,y in zip(a,b) for n in (x,y)]
    yield (ca,de,reverse,1), [n for x,y in zip(a,b) for n in (y,x)]
    yield (ca,de,reverse,2), a+b
    yield (ca,de,reverse,3), b+a

def binary_views(t):
 n = 0
 for x in t:
  n = n*3+x
 b = n.to_bytes(51, "big")
 yield "base3-be", b
 yield "base3-le", b[::-1]
 bits = f"{n:0408b}"
 for offset in range(7):
  v = bits[offset:]
  out = bytes(int(v[i:i+7],2) for i in range(0,len(v)-6,7))
  yield f"ascii7-be-phase{offset}", out
  yield f"ascii7-le-phase{offset}", out[::-1]
 for offset in range(5):
  v = bytes(sum(t[i+j]*3**(4-j) for j in range(5))
            for i in range(offset,len(t)-4,5))
  yield f"five-trit-phase{offset}", v
  yield f"five-trit-plus32-phase{offset}", bytes((x+32)%256 for x in v)

def pads(b, nonce):
 yield "literal", b
 yield "nonce-repeat", bytes(x ^ nonce[i%16] for i,x in enumerate(b))
 pad = b"".join(hashlib.sha256(nonce+i.to_bytes(4,"big")).digest()
                for i in range((len(b)+31)//32))
 yield "nonce-sha256-counter", bytes(x^y for x,y in zip(b,pad))

def search(pairs, nonce, target):
 counts = {"source_layouts":0,"decoded_binary_objects":0,
           "printable_exact_strings":0,"unique_normalized_candidates":0,
           "complete_hmac_commitment_checks":0,"original_or_plant_hits":0}
 unique = set()
 hits = []
 for label,trits in layouts(pairs):
  counts["source_layouts"] += 1
  for model,packed in binary_views(trits):
   for mask_name,b in pads(packed,nonce):
    counts["decoded_binary_objects"] += 1
    for mode,v in (("leftzero",b.lstrip(b"\x00")),
                   ("rightzero",b.rstrip(b"\x00")),
                   ("bothzero",b.strip(b"\x00"))):
     if not v or any(x<32 or x>126 for x in v):
      continue
     counts["printable_exact_strings"] += 1
     phrase = v.decode("ascii")
     norm = normalized(phrase)
     if not norm or norm in unique:
      continue
     unique.add(norm)
     counts["complete_hmac_commitment_checks"] += 1
     key = component(nonce,phrase)
     if hashlib.sha256(key).hexdigest() == target:
      hits.append({"phrase":phrase,"component":key.hex().upper(),
                   "layout":str(label),"model":model,"mask":mask_name,"trim":mode})
 counts["unique_normalized_candidates"] = len(unique)
 counts["original_or_plant_hits"] = len(hits)
 return counts,hits

def plant(phrase):
 n = int.from_bytes(phrase.encode("ascii"),"big")
 assert len(phrase.encode("ascii")) <= 50
 digs = []
 for _ in range(128):
  n,r = divmod(n,9)
  digs.append(r)
 assert n == 0
 return [(CLASSES[d//3],DESTS[d%3]) for d in reversed(digs)]

def main():
 parser = argparse.ArgumentParser()
 args = parser.add_mutually_exclusive_group(required=True)
 args.add_argument("--root",type=Path)
 args.add_argument("--archive",type=Path)
 opts = parser.parse_args()
 evidence = inputs(opts.archive or opts.root, bool(opts.archive))
 nonce = bytes.fromhex(json.loads(evidence["evidence/recovery-routing.json"])["K08"]["desk_nonce"])
 target = json.loads(evidence["acceptance.json"])["slot_sha256"]["K08"]
 counts,hits = search(original_pairs(evidence["evidence/print/spool-reconstruction.log"]),nonce,target)
 planted = "we leave a place beside the window for each other"
 positive = hashlib.sha256(component(nonce,planted)).hexdigest()
 ctrl,control_hits = search(plant(planted),nonce,positive)
 assert any(h["phrase"] == planted for h in control_hits)
 print(json.dumps({"original":counts,"original_hits":hits,
                   "control":ctrl,"planted_caption":planted,
                   "planted_component":component(nonce,planted).hex().upper()},indent=2))

if __name__ == "__main__":
 main()
