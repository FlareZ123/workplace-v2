#!/usr/bin/env python3
"""Bounded K08 test of Wilson's 1934/1938 Pilot's Guide page-word hypothesis.

The physical-profile candidate is W. Eric Wilson's Pilot's Guide to the Thames
Estuary and the Norfolk Broads for Yachtsmen. This script does not identify the
physical H-17 book; it tests only whether the frozen WN-14 byte-pair coordinates
select the committed K08 phrase from an accessible exact Google Books copy.
"""
from __future__ import annotations
import hashlib, hmac, json, re, sys
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from PIL import Image
import pytesseract

COORDINATES=[(4,154),(171,46),(28,222),(122,130),(205,124),(96,35),(67,3),(201,26)]
NONCE=bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
CONTROL="a good watch leaves the room ready for the next pair of hands"
CONTROL_HMAC=hmac.new(NONCE,CONTROL.encode(),hashlib.sha256).digest()[:16].hex().upper()
EXPECTED_CONTROL="BF889359B0303F2B2B2FD96AE841210B"
OUT=Path("wilson-pageword-probe"); (OUT/"images").mkdir(parents=True,exist_ok=True); (OUT/"ocr").mkdir(parents=True,exist_ok=True)

def get(url,accept="*/*",timeout=60):
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; H17-Archive-Research/1.0)","Accept":accept})
    with urlopen(req,timeout=timeout) as r:
        return r.read(),r.headers.get("Content-Type",""),r.geturl()

def normalize(s):
    return re.sub(r"\\s+"," ",re.sub(r"[^a-z0-9\\s]"," ",s.lower())).strip()

def clean_body(text):
    kept=[]
    for raw in text.splitlines():
        line=re.sub(r"\\s+"," ",raw).strip()
        if not line: continue
        u=line.upper().strip(" .:-—'\"")
        if re.fullmatch(r"\\d{1,3}",u): continue
        if re.fullmatch(r"(?:CHAPTER\\s+)?[IVXLCDM]+",u): continue
        if line==line.upper() and len(line)<=80 and re.search(r"[A-Z]",line): continue
        kept.append(line)
    return "\\n".join(kept)

def margin_tokens(image):
    w,h=image.size; bh=max(32,int(h*.16)); bw=max(32,int(w*.12))
    zones={"top":(0,0,w,bh),"bottom":(0,h-bh,w,h),"left":(0,0,bw,h),"right":(w-bw,0,w,h)}
    out={}
    for name,b in zones.items():
        t=pytesseract.image_to_string(image.crop(b),lang="eng",config="--psm 6 -c tessedit_char_whitelist=0123456789")
        out[name]=re.findall(r"(?<!\\d)\\d{1,3}(?!\\d)",t)
    return out

def fetch_scan(volume_id,scan_index,zoom=3):
    last=None
    for host in ("books.google.com","books.google.es"):
        url=f"https://{host}/books/content?id={volume_id}&pg=PA{scan_index}&img=1&zoom={zoom}&edge=curl&source=gbs_api"
        try:
            data,ctype,final=get(url,"image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8")
            if not ctype.startswith("image/"): raise RuntimeError(f"not image: {ctype}")
            return data,final
        except Exception as e: last=e
    raise RuntimeError(f"page fetch failed PA{scan_index}: {last}")

def resolve_folio(volume_id,page,page_count,window=12):
    hits=[]
    rows=[]
    for scan in range(max(0,page-window),min(page_count-1,page+window)+1):
        try:
            data,url=fetch_scan(volume_id,scan,zoom=2)
            im=Image.open(BytesIO(data)).convert("RGB")
            m=margin_tokens(im)
            zones=[z for z,v in m.items() if v==[str(page)]]
            row={"scan":scan,"zones":zones,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
            rows.append(row)
            if zones: hits.append(row)
        except Exception as e:
            rows.append({"scan":scan,"error":f"{type(e).__name__}: {e}"})
    return (hits[0]["scan"] if len(hits)==1 else None),{"requested_printed_page":page,"unique_match_count":len(hits),"matches":hits,"scanned":rows}

def phrase_check(words):
    phrase=normalize(" ".join(words))
    comp=hmac.new(NONCE,phrase.encode(),hashlib.sha256).digest()[:16]
    return {"words":words,"normalized_phrase":phrase,"component_hex":comp.hex().upper(),"slot_sha256":hashlib.sha256(comp).hexdigest(),"match":hashlib.sha256(comp).hexdigest()==TARGET}

def search_books():
    q=quote('intitle:"The Pilot's Guide to the Thames Estuary and the Norfolk Broads" inauthor:"W. Eric Wilson"')
    raw,_,_=get(f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=40&printType=books")
    data=json.loads(raw.decode())
    cands=[]
    for item in data.get("items",[]):
        info=item.get("volumeInfo",{})
        title=info.get("title",""); authors=" ".join(info.get("authors",[]))
        pub=info.get("publisher",""); year=str(info.get("publishedDate",""))
        pc=info.get("pageCount")
        if "Pilot" in title and "Wilson" in authors and pc and pc>=206:
            cands.append({"id":item["id"],"title":title,"authors":authors,"publisher":pub,"publishedDate":year,"pageCount":pc})
    return cands

def main():
    if CONTROL_HMAC!=EXPECTED_CONTROL: raise SystemExit("known-answer control failed")
    report={"hypothesis":"Wilson 1934/1938 Pilot's Guide frozen WN-14 page-word coordinates","coordinates":COORDINATES,"candidates":[]}
    try:
        candidates=search_books()
    except Exception as e:
        report["status"]="INCOMPLETE"; report["error"]=f"{type(e).__name__}: {e}"
        print(json.dumps(report,indent=2)); return 2
    for meta in candidates[:8]:
        row={"metadata":meta,"status":"INCOMPLETE","folios":[]}
        try:
            page_tokens={}
            for page in sorted({p for p,_ in COORDINATES}):
                scan,mapping=resolve_folio(meta["id"],page,int(meta["pageCount"]))
                row["folios"].append(mapping)
                if scan is None: raise RuntimeError(f"printed page {page} not uniquely resolved")
                data,url=fetch_scan(meta["id"],scan,zoom=3)
                im=Image.open(BytesIO(data)).convert("RGB")
                ocr=pytesseract.image_to_string(im,lang="eng",config="--psm 4")
                (OUT/"ocr"/f"{meta['id']}-page-{page}-scan-{scan}.txt").write_text(ocr,encoding="utf-8")
                (OUT/"images"/f"{meta['id']}-page-{page}-scan-{scan}.png").write_bytes(data)
                toks=re.findall(r"[A-Za-z0-9]+",clean_body(ocr).lower())
                page_tokens[page]=toks
                row.setdefault("pages",[]).append({"page":page,"scan":scan,"word_count":len(toks),"first_tokens":toks[:15]})
            words=[]
            for page,pos in COORDINATES:
                toks=page_tokens[page]
                if not 1<=pos<=len(toks): raise RuntimeError(f"page {page} has {len(toks)} body words; requested {pos}")
                words.append(toks[pos-1])
            row["candidate"]=phrase_check(words); row["status"]="MATCH" if row["candidate"]["match"] else "NO_MATCH"
        except Exception as e:
            row["error"]=f"{type(e).__name__}: {e}"
        report["candidates"].append(row)
        if row.get("status")=="MATCH":
            report["status"]="MATCH"; break
    else:
        report["status"]="NO_MATCH_OR_INCOMPLETE"
    (OUT/"summary.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0 if report["status"]=="MATCH" else 1

if __name__=="__main__":
    raise SystemExit(main())
