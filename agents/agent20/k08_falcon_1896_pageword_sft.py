"""Acquire exact Commons-hosted 1896 Falcon scan and probe its printed-folio layout."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import Request, urlopen

SOURCE=("https://upload.wikimedia.org/wikipedia/commons/0/0c/"
"The_Falcon_on_the_Baltic%3B_a_coasting_voyage_from_Hammersmith_to_Copenhagen"
"_in_a_three-ton_yacht_%28IA_falcononbalticco00knig%29.pdf")
PATH=Path("falcon-1896.pdf")
RAW_SHA256=None


def run(*args:str)->str:
    p=subprocess.run(args,check=True,text=True,capture_output=True,timeout=90)
    return p.stdout


def main()->None:
    req=Request(SOURCE,headers={"User-Agent":"H17-historical-source-audit/1.0",
        "Accept":"application/pdf"})
    with urlopen(req,timeout=45) as h:
        size=0
        with PATH.open("wb") as output:
            while (block:=h.read(1_000_000)):
                size+=len(block)
                if size>30_000_000: raise RuntimeError("PDF exceeds 30MB bound")
                output.write(block)
    digest=hashlib.sha256(PATH.read_bytes()).hexdigest()
    pages=re.search(r"(?m)^Pages:\s*(\d+)",run("pdfinfo",str(PATH)))
    assert pages, "pdfinfo page count missing"
    count=int(pages.group(1))
    assert count==370,count
    print("SOURCE",json.dumps({"url":SOURCE,"bytes":size,"sha256":digest,"pdf_pages":count}),flush=True)
    for page in [10,11,12,13,14,15,18,29,30,31,35,40,50,90,110,160,190,205,206,220,230,240,250,360]:
        if page>count:continue
        t=run("pdftotext","-f",str(page),"-l",str(page),"-layout",str(PATH),"-")
        print("PAGE_TEXT",json.dumps({"pdf_page":page,"bytes":len(t),
             "head":" ".join(t[:220].split()),"tail":" ".join(t[-120:].split())}),flush=True)
    if "--acquire-only" in sys.argv:return
    assert RAW_SHA256 is not None and digest==RAW_SHA256
    raise RuntimeError("Exact printed folio controls are not yet established")


if __name__=="__main__":
    main()
