#!/usr/bin/env python3
"""One source-defined K08 candidate: interpret accepted WN-14 K01 bytes as eight
(printed page, 1-based word) coordinates in the public 1903 Riddle scan.

This is a bounded candidate test, not evidence that the physical map-back book
was The Riddle of the Sands. It tests only big-endian byte pairs and the
published PDF/printed-page offset used by the existing scan crosswalk.
"""
from __future__ import annotations
import hashlib, hmac, json, re, urllib.parse, urllib.request
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
CAND=json.loads((ROOT/"resources/candidate.json").read_text())
ROUTE=json.loads((ROOT/"resources/evidence/recovery-routing.json").read_text())
ACCEPT=json.loads((ROOT/"resources/acceptance.json").read_text())
K01=bytes.fromhex(CAND["K01"])
NONCE=bytes.fromhex(ROUTE["K08"]["desk_nonce"])
TARGET=ACCEPT["slot_sha256"]["K08"]
FILE_TITLE="The Riddle of the Sands- A Record of Secret Service (IA dli.granth.107255).pdf"
PDF_PAGE_OFFSET=4
COORDS=[(K01[i],K01[i+1]) for i in range(0,16,2)]
TOKENIZERS={
 "apostrophes-kept": re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*"),
 "punctuation-split": re.compile(r"[A-Za-z0-9]+"),
}
def download_pdf():
 params=urllib.parse.urlencode({"action":"query","titles":f"File:{FILE_TITLE}","prop":"imageinfo","iiprop":"url","format":"json"})
 req=urllib.request.Request(f"https://commons.wikimedia.org/w/api.php?{params}",headers={"User-Agent":"H17-Archive-Research/1.0"})
 with urllib.request.urlopen(req,timeout=60) as r: meta=json.load(r)
 page=next(iter(meta["query"]["pages"].values()))
 url=page["imageinfo"][0]["url"]
 print("PUBLIC_SCAN",page.get("title"),flush=True)
 with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"H17-Archive-Research/1.0"}),timeout=120) as r: data=r.read()
 print("PDF_BYTES",len(data),flush=True)
 return data
def clean(text,printed):
 out=[]
 for raw in text.splitlines():
  line=raw.strip()
  if not line: continue
  if line.casefold() in {"the riddle of the sands","erskine childers"} or line==str(printed): continue
  out.append(line)
 return "\n".join(out)
def norm(words):
 return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9\s]"," "," ".join(words).lower())).strip()
def check(phrase):
 comp=hmac.new(NONCE,phrase.encode("utf-8"),hashlib.sha256).digest()[:16]
 return comp.hex().upper(),hashlib.sha256(comp).hexdigest()
def main():
 assert hashlib.sha256(K01).hexdigest()==ACCEPT["slot_sha256"]["K01"]
 fixture="a good watch leaves the room ready for the next pair of hands"
 assert hmac.new(NONCE,fixture.encode(),hashlib.sha256).digest()[:16].hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
 print("K01_HEX",K01.hex().upper())
 print("BIG_ENDIAN_PAGE_WORD_COORDINATES",COORDS)
 doc=PdfReader(BytesIO(download_pdf()))
 print("PDF_PAGE_COUNT",len(doc.pages))
 pages={}
 for page,word in COORDS:
  pdf_page=page+PDF_PAGE_OFFSET
  if not 1<=pdf_page<=len(doc.pages): raise RuntimeError(f"printed page {page} maps outside PDF")
  txt=clean(doc.pages[pdf_page-1].extract_text() or "",page)
  if not txt.strip(): raise RuntimeError(f"no embedded text on printed page {page}")
  pages[page]=txt
 for name,tokenizer in TOKENIZERS.items():
  words=[]; counts={}
  for page,position in COORDS:
   tokens=tokenizer.findall(pages[page])
   counts[page]=len(tokens)
   if len(tokens)<position: raise RuntimeError(f"printed page {page}: {len(tokens)} tokens < requested {position}")
   words.append(tokens[position-1])
  phrase=norm(words); component,digest=check(phrase)
  print({"tokenizer":name,"page_token_counts":counts,"words_in_K01_byte_order":words,
         "first_letters":"".join(w[0].lower() for w in words),"complete_normalized_phrase":phrase,
         "derived_K08_component":component,"derived_K08_sha256":digest,"acceptance_match":digest==TARGET},flush=True)
 print("TARGET_K08_SHA256",TARGET)
if __name__=="__main__": main()
