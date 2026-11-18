"""Source-pinned 1896 Falcon printed-page OCR candidate builder, independent of 1889 Google edition."""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
import re
import sys
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

BASENAME = "falcononbalticco00knig"
SOURCE = f"https://archive.org/download/{BASENAME}/{BASENAME}_djvu.xml"
RAW_SHA256 = None
COORDINATES = [(4,154),(171,46),(28,222),(122,130),(205,124),(96,35),(67,3),(201,26)]
K08_EXPECTED="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
DESK_NONCE="5F933DA6A1BD03C32DA5CBC25344F497"


def acquire() -> tuple[bytes,ET.Element]:
    req=Request(SOURCE,headers={"User-Agent":"H17-source-study/1.0","Accept":"application/xml,text/xml,*/*"})
    with urlopen(req,timeout=60) as h:
        raw=h.read(35_000_000)
        status=h.status
        ctype=h.headers.get("Content-Type")
    root=ET.fromstring(raw)
    print("SOURCE",json.dumps({"url":SOURCE,"status":status,"content_type":ctype,"bytes":len(raw),
        "sha256":hashlib.sha256(raw).hexdigest(),"root":root.tag,
        "objects":len(root.findall(".//OBJECT")),
        "pages":len(root.findall(".//page")),
        "word_tags":len(root.findall(".//WORD"))},sort_keys=True),flush=True)
    return raw,root


def text_for_object(obj:ET.Element)->str:
    return " ".join((w.text or "") for w in obj.iter() if w.tag.upper()=="WORD")


def main()->None:
    raw,root=acquire()
    obj=root.findall(".//OBJECT")
    if not obj:
        print("STRUCTURE","no OBJECT, first tags", [e.tag for e in list(root)[:20]],flush=True)
        return
    for i in (0,1,2,10,16,18,20,28,29,30,40,100,171,172,205,206,209,220,230,240,250,300,350):
        if i>=len(obj):continue
        page=text_for_object(obj[i]);w=re.findall(r"[a-z0-9]+",page.lower())
        print("PAGE_SAMPLE",json.dumps({"scan":i,"num_tokens":len(w),"first":w[:25],
            "last":w[-20:],"raw_head":page[:160]},sort_keys=True),flush=True)
    if "--acquire-only" in sys.argv: return
    if not RAW_SHA256 or hashlib.sha256(raw).hexdigest()!=RAW_SHA256:raise RuntimeError("Source digest unpinned")
    # Authentic folios must be independently assigned before acceptance.
    raise RuntimeError("Printed folio-to-scan mapping has not been frozen")


if __name__=="__main__":
    main()
