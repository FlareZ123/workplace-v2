#!/usr/bin/env python3
"""Read-only XLS/XLSX intake for missing H-17 property/galley sources.

Scans visible and hidden sheets, formulas, cached values, comments, defined
names, individual cells, and row-joined text for direct K04 hex and K08 HMAC hits.
Legacy .xls files are converted to a temporary .xlsx by local LibreOffice;
the original is never modified. No URLs or external services are accessed.
"""
from __future__ import annotations
import argparse, hashlib, hmac, json, re, subprocess, tempfile
from pathlib import Path
import openpyxl

K04_MASK=bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
K04_COMMIT="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
K08_NONCE=bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
K08_COMMIT="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
TOKEN=re.compile(r"[a-z0-9]+")
HEX32=re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def normalize(text: str) -> str:
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9\s]"," ",text.lower())).strip()

def tokens(text: str) -> list[str]:
    return TOKEN.findall(normalize(text))

def hmac_hit(text: str) -> bool:
    phrase=normalize(text)
    digest=hmac.new(K08_NONCE,phrase.encode("utf-8"),"sha256").digest()[:16]
    return sha(digest)==K08_COMMIT

def scan_hex(text: str, source: dict, hits: list[dict]):
    for match in HEX32.finditer(text):
        payload=bytes.fromhex(match.group(0))
        component=bytes(a^b for a,b in zip(payload,K04_MASK))
        component_sha=sha(component)
        hits.append({**source,"payload_hex":match.group(0).upper(),"component_hex":component.hex().upper(),
                     "component_sha256":component_sha,"matches_K04":component_sha==K04_COMMIT})

def scan_windows(text: str, max_words: int, source: dict, hits: list[dict]):
    ts=tokens(text)
    for i in range(len(ts)):
        for n in range(1,min(max_words,len(ts)-i)+1):
            phrase=" ".join(ts[i:i+n])
            if hmac_hit(phrase):
                hits.append({**source,"start_word":i+1,"word_count":n,"phrase":phrase})

def workbook_path(path: Path, temp: Path) -> Path:
    if path.suffix.lower() in {".xlsx",".xlsm"}:
        return path
    if path.suffix.lower()!=".xls":
        raise ValueError(f"unsupported workbook type: {path.suffix}")
    profile=temp/"lo-profile"
    cmd=["libreoffice",f"-env:UserInstallation=file://{profile}","--headless","--norestore","--nodefault","--nofirststartwizard",
         "--convert-to","xlsx","--outdir",str(temp),str(path)]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    converted=temp/(path.stem+".xlsx")
    if proc.returncode!=0 or not converted.exists():
        raise RuntimeError(f"LibreOffice conversion failed for {path}: {proc.stderr[-1000:]} {proc.stdout[-1000:]}")
    return converted

def extract_one(path: Path, max_words: int, dump_cells: bool) -> dict:
    original=path.read_bytes()
    meta={"path":str(path),"sha256":sha(original),"size_bytes":len(original),"format":path.suffix.lower()}
    k08_hits=[]; k04_hex_candidates=[]; cells=[]; sheet_meta=[]
    with tempfile.TemporaryDirectory(prefix="h17-office-") as td:
        converted=workbook_path(path,Path(td))
        wb_formula=openpyxl.load_workbook(converted,data_only=False,read_only=False,keep_links=True)
        wb_values=openpyxl.load_workbook(converted,data_only=True,read_only=False,keep_links=True)
        for ws in wb_formula.worksheets:
            wsv=wb_values[ws.title]
            sheet_meta.append({"sheet":ws.title,"state":ws.sheet_state,"max_row":ws.max_row,"max_column":ws.max_column})
            for row in ws.iter_rows():
                row_values=[]
                for cell in row:
                    if cell.value is None and cell.comment is None:
                        continue
                    coord=cell.coordinate
                    values=[]
                    if cell.value is not None:
                        values.append(("formula_or_value",str(cell.value)))
                    cached=wsv[coord].value
                    if cached is not None and str(cached)!=str(cell.value):
                        values.append(("cached_value",str(cached)))
                    if cell.comment is not None and cell.comment.text:
                        values.append(("comment",cell.comment.text))
                    for kind,value in values:
                        source={"sheet":ws.title,"cell":coord,"kind":kind}
                        scan_windows(value,max_words,source,k08_hits)
                        scan_hex(value,source,k04_hex_candidates)
                        if dump_cells:
                            cells.append({**source,"text":value})
                        if kind in {"formula_or_value","cached_value"}:
                            row_values.append(value)
                if row_values:
                    row_text=" ".join(row_values)
                    source={"sheet":ws.title,"row":row[0].row,"kind":"row_join"}
                    scan_windows(row_text,max_words,source,k08_hits)
                    scan_hex(row_text,source,k04_hex_candidates)
        for name,defined in wb_formula.defined_names.items():
            value=str(defined.attr_text or "")
            if value:
                source={"defined_name":name,"kind":"defined_name"}
                scan_windows(value,max_words,source,k08_hits)
                scan_hex(value,source,k04_hex_candidates)
                if dump_cells:
                    cells.append({**source,"text":value})
        wb_formula.close()
        wb_values.close()
    return {**meta,"sheets":sheet_meta,"cell_text_count":len(cells) if dump_cells else None,
            "K08_commitment_hits":k08_hits,"K04_hex_candidates":k04_hex_candidates,
            "K04_matching_candidates":[x for x in k04_hex_candidates if x["matches_K04"]],
            "cells":cells if dump_cells else None}

def main():
    ap=argparse.ArgumentParser(description="Read-only local XLS/XLSX intake for H-17 missing source files")
    ap.add_argument("paths",nargs="+",type=Path,help="local workbook files or directories")
    ap.add_argument("--max-words",type=int,default=64)
    ap.add_argument("--dump-cells",action="store_true",help="include extracted cell/comment text in output")
    args=ap.parse_args()
    files=[]
    for p in args.paths:
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(x for x in p.rglob("*") if x.is_file() and x.suffix.lower() in {".xls",".xlsx",".xlsm"})
        else:
            raise SystemExit(f"missing local path: {p}")
    files=sorted(set(files))
    if not files:
        raise SystemExit("no XLS/XLSX/XLSM files found")
    results=[]
    for p in files:
        try:
            results.append(extract_one(p,args.max_words,args.dump_cells))
        except Exception as exc:
            results.append({"path":str(p),"error":f"{type(exc).__name__}: {exc}"})
    print(json.dumps({"source_files":len(files),"K04_commitment":K04_COMMIT,"K08_commitment":K08_COMMIT,
                      "results":results},indent=2,sort_keys=True))
    if any("error" in r for r in results):
        raise SystemExit(2)

if __name__=="__main__":
    main()
