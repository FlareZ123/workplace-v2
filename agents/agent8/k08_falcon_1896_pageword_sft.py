#!/usr/bin/env python3
"""Frozen K08 page/word complete-object test on the accessible 1896 Falcon scan.

This is a distinct EDITION from the 1889 Google Books object. It cannot
falsify the 1889 test if negative. Treat its full text as a hypothesis only.

Reads public-domain 1896 Wikimedia/Internet Archive scan; reads only
canonical six-PASS candidate, untouched acceptance, nonce and source words.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
PDF_URL = "https://archive.org/download/falcononbalticco00knig/falcononbalticco00knig.pdf"
OUT = ROOT / "work/agent8-falcon-1896"
PDF_PAGE_COUNT = 370
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K08_TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
K01_COORDS = [(4,154), (171,46), (28,222), (122,130),
              (205,124), (96,35), (67,3), (201,26)]
P0323_COORDS = [(30,81), (239,210), (229,202), (143,78),
                (31,200), (180,146), (151,179), (215,79)]
N02 = "a good watch leaves the room ready for the next pair of hands"
N02_HMAC = "BF889359B0303F2B2B2FD96AE841210B"
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[.'’/-][A-Za-z0-9]+)*")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_report(obj: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(obj, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    fd, temp = tempfile.mkstemp(prefix="summary-", suffix=".json.tmp", dir=OUT)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, OUT / "summary.json")


def control() -> bytes:
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text("utf-8"))
    candidate = json.loads((ROOT / "resources/candidate.json").read_text("utf-8"))
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text("utf-8"))
    if acceptance["slot_sha256"]["K08"] != K08_TARGET:
        raise RuntimeError("original K08 acceptance commitment drift")
    k01 = bytes.fromhex(candidate["K01"])
    if sha(k01) != acceptance["slot_sha256"]["K01"]:
        raise RuntimeError("original K01 candidate no longer accepted")
    if [(k01[i], k01[i+1]) for i in range(0,16,2)] != K01_COORDS:
        raise RuntimeError("K01 coordinate derivation differs from original accepted bytes")
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    if hmac.new(nonce, N02.encode(), hashlib.sha256).digest()[:16].hex().upper() != N02_HMAC:
        raise RuntimeError("source-pinned known N02 HMAC control failed")
    return nonce


def load_p0323() -> None:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    if sha(raw) != SPOOL_SHA:
        raise RuntimeError("original print spool source digest drift")
    matching = []
    for line in raw.decode("ascii").splitlines():
        if "JOB=PS-261003-0323 " in line:
            fields = dict(t.split("=",1) for t in line.split() if "=" in t)
            matching.append(fields)
    if len(matching) != 1:
        raise RuntimeError("PS-0323 is not a unique complete original row")
    row = matching[0]
    if (row["ATTEMPT"],row["STATE"],row["CLASS"],row["DEST"]) != ("1","ACK","RECOVER","store"):
        raise RuntimeError("PS-0323 source role changed")
    buf=bytes.fromhex(row["PAYLOAD"])
    if [(buf[i],buf[i+1]) for i in range(0,16,2)] != P0323_COORDS:
        raise RuntimeError("PS-0323 frozen coordinates changed")


def source_pdf() -> bytes:
    req=Request(PDF_URL,headers={
        "User-Agent": "H17-preservation-research/1.0 (public-domain book study)",
        "Accept": "application/pdf",
    })
    with urlopen(req, timeout=90) as resp:
        if "pdf" not in resp.headers.get("Content-Type","").lower():
            raise RuntimeError("original public archive did not send a PDF")
        data=resp.read(21*1024*1024)
    if len(data)>=21*1024*1024 or not data.startswith(b"%PDF"):
        raise RuntimeError("public PDF download invalid or oversized")
    return data


def normalize(words: list[str]) -> str:
    phrase=" ".join(words).lower()
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9\s]"," ",phrase)).strip()


def tokens_of_page(text: str, folio: int) -> list[str]:
    lines = text.splitlines()
    keep=[]
    for index,original in enumerate(lines):
        line=re.sub(r"\s+"," ",original).strip()
        if not line:
            continue
        if index<=8 and line==str(folio):
            continue
        upper=line.upper().strip(" .:-—'\"")
        if upper in ("THE FALCON ON THE BALTIC","THE \"FALCON\" ON THE BALTIC",
                     "THE 'FALCON' ON THE BALTIC","E. F. KNIGHT"):
            continue
        if re.fullmatch(r"(?:CHAPTER\s+)?[IVXLCDM]+",upper):
            continue
        if len(line)<=72 and line==line.upper() and re.search(r"[A-Z]",line):
            continue
        keep.append(line)
    return WORD_PATTERN.findall(re.sub(r"(?<=[A-Za-z0-9])-\s*\n\s*(?=[A-Za-z0-9])", "", "\n".join(keep)))


def perform() -> dict:
    nonce=control()
    load_p0323()
    data=source_pdf()
    report={
        "status":"INCOMPLETE",
        "original_K08_commitment":K08_TARGET,
        "edition":"1896 new edition / Longmans Green and Co; separate from pinned 1889 W. H. Allen edition",
        "pdf_url":PDF_URL,
        "pdf_sha256":sha(data),
        "pdf_bytes":len(data),
        "coordinate_sets":{"K01":K01_COORDS,"PS0323":P0323_COORDS},
        "pages":{},
        "candidates":{},
    }
    atomic_report(report)
    with pymupdf.open(stream=data,filetype="pdf") as doc:
        if doc.page_count!=PDF_PAGE_COUNT:
            raise RuntimeError(f"unexpected PDF page count {doc.page_count}, expected {PDF_PAGE_COUNT}")
        header = " ".join(doc[i].get_text("text",sort=True) for i in range(3,15))
        if "1896" not in header or "FALCON" not in header.upper():
            raise RuntimeError("source book title/date not validated")
        wanted={p for pairlist in (K01_COORDS,P0323_COORDS) for p,_ in pairlist}
        matches={p:[] for p in wanted}
        for pdf_index,page in enumerate(doc):
            text=page.get_text("text",sort=True)
            lines=[line.strip() for line in text.splitlines() if line.strip()]
            # Must be an identified printed folio, and an adjacent running title.
            top=lines[:8]
            if pdf_index in (20, 30, 45, 60, 85, 110, 145, 180, 220, 255):
                print("PRINT_FOLIO_PROBE",json.dumps({
                    "pdf_index":pdf_index,
                    "first_eight_lines":top,
                    "text_length":len(text),
                    "block_first":page.get_text("blocks")[:2],
                },default=str),flush=True)
            for num in wanted:
                if str(num) not in top:
                    continue
                if not any("FALCON" in s.upper() for s in top):
                    continue
                tokens=tokens_of_page(text,num)
                matches[num].append({
                    "pdf_zero_index":pdf_index,
                    "source_text_sha256":sha(text.encode("utf-8")),
                    "body_word_count":len(tokens),
                    "first_12_words":tokens[:12],
                    "required_positions":sorted({w for pairlist in (K01_COORDS,P0323_COORDS) for p,w in pairlist if p==num}),
                    "tokens":tokens,
                })
        for folio,found in sorted(matches.items()):
            report["pages"][str(folio)]=[
                {k:v for k,v in rec.items() if k!="tokens"} for rec in found
            ]
        atomic_report(report)
        unresolved={p:len(m) for p,m in matches.items() if len(m)!=1}
        if unresolved:
            raise RuntimeError(f"printed folios not uniquely mapped in alternate 1896 edition: {unresolved}")
        for name,coords in (("K01",K01_COORDS),("PS0323",P0323_COORDS)):
            words=[]
            for p,w in coords:
                tokens=matches[p][0]["tokens"]
                if not 1<=w<=len(tokens):
                    raise RuntimeError(f"{name} 1896 printed folio {p} has {len(tokens)} body words, wants {w}")
                words.append(tokens[w-1])
            phrase=normalize(words)
            component=hmac.new(nonce,phrase.encode("utf-8"),hashlib.sha256).digest()[:16]
            result={
                "words":words,
                "normalized_phrase":phrase,
                "k08_component_hex":component.hex().upper(),
                "k08_sha256":sha(component),
                "original_commitment_pass":sha(component)==K08_TARGET,
            }
            report["candidates"][name]=result
            print(f"COMPLETE_ALT_EDITION_CANDIDATE {name} {json.dumps(result,sort_keys=True)}",flush=True)
            atomic_report(report)
    report["status"]="COMPLETE"
    atomic_report(report)
    return report


def main() -> int:
    try:
        result=perform()
        print("ALTERNATE_EDITION_TEST_COMPLETE",json.dumps({
            key:val["original_commitment_pass"] for key,val in result["candidates"].items()
        },sort_keys=True),flush=True)
        return 0
    except Exception as exc:
        partial={}
        path=OUT/"summary.json"
        if path.exists():
            partial=json.loads(path.read_text("utf-8"))
        partial["status"]="INCOMPLETE"
        partial["error"]=f"{type(exc).__name__}: {exc}"
        atomic_report(partial)
        print("ALTERNATE_EDITION_INCOMPLETE",partial["error"],flush=True)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
