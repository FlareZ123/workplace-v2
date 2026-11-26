#!/usr/bin/env python3
"""Literal K08 carrier scan over all non-PDF members of the supplied export."""
import argparse, csv, email.policy, hashlib, hmac, io, json, re
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path

MANIFEST_SHA256 = "225fa828826041fc2dd805ed5055b466a09666dbe32dc7c7f13f546aadba14e3"

def norm(s):
    return " ".join(re.sub(r"[^a-z0-9\\s]", " ", str(s).lower()).split())

class HTMLFields(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.parts=[]
    def handle_data(self, data):
        if data.strip(): self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        self.parts.extend(v for k,v in attrs if v and k.lower() in
                          {"alt","title","aria-label","value","content","label","name","href"})

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]/"resources")
    root=ap.parse_args().root.resolve()
    files=sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower()!=".pdf")
    manifest="\n".join(f"{p.relative_to(root).as_posix()}\t{hashlib.sha256(p.read_bytes()).hexdigest()}"
                       for p in files)+"\n"
    manifest_sha=hashlib.sha256(manifest.encode()).hexdigest()
    if len(files)!=45 or manifest_sha!=MANIFEST_SHA256:
        raise SystemExit(f"source manifest mismatch: files={len(files)} sha256={manifest_sha}")

    fields=[]
    def add(path,label,text):
        if str(text).strip(): fields.append((path,label,str(text)))
    def walk_json(obj,path,rel):
        if isinstance(obj,dict):
            for k,v in obj.items(): add(rel,path+".key",k); walk_json(v,path+"."+str(k),rel)
        elif isinstance(obj,list):
            for i,v in enumerate(obj): walk_json(v,f"{path}[{i}]",rel)
        elif isinstance(obj,str): add(rel,path,obj)

    for p in files:
        rel=p.relative_to(root).as_posix(); raw=p.read_bytes(); add(rel,"filename",rel)
        ext=p.suffix.lower()
        if ext==".eml":
            txt=raw.decode("utf-8",errors="replace"); add(rel,"raw-eml",txt)
            msg=BytesParser(policy=email.policy.default).parsebytes(raw)
            for k,v in msg.items(): add(rel,"header:"+k,v)
            for part in msg.walk():
                if part.get_content_maintype()=="multipart": continue
                try: body=part.get_content()
                except Exception: continue
                if isinstance(body,str): add(rel,"mime:"+part.get_content_type(),body)
        elif ext in {".html",".htm"}:
            txt=raw.decode("utf-8",errors="replace"); add(rel,"raw-html",txt)
            h=HTMLFields(); h.feed(txt); add(rel,"html-text-and-attrs","\\n".join(h.parts))
        elif ext in {".json",".jsonl"}:
            txt=raw.decode("utf-8",errors="replace"); add(rel,"raw-json",txt)
            if ext==".jsonl":
                for i,line in enumerate(txt.splitlines()):
                    try: walk_json(json.loads(line),f"line{i}",rel)
                    except Exception: add(rel,f"line{i}",line)
            else:
                try: walk_json(json.loads(txt),"root",rel)
                except Exception: pass
        elif ext==".csv":
            txt=raw.decode("utf-8",errors="replace"); add(rel,"raw-csv",txt)
            for i,row in enumerate(csv.reader(io.StringIO(txt))):
                add(rel,f"row{i}"," ".join(row))
                for j,cell in enumerate(row): add(rel,f"cell{i}-{j}",cell)
        elif ext==".raw":
            for i,m in enumerate(re.finditer(rb"[\\x20-\\x7e]{4,}",raw)):
                add(rel,f"ascii-run{i}",m.group().decode("ascii"))
        else:
            txt=raw.decode("utf-8",errors="replace"); add(rel,"raw-text",txt)
            for i,line in enumerate(txt.splitlines()): add(rel,f"line{i}",line)
            for i,para in enumerate(re.split(r"\\n\\s*\\n",txt)): add(rel,f"paragraph{i}",para)

    notes=(root/"evidence/crew/noticeboard-and-desk-notes.txt").read_text()
    for m in re.finditer(r"(?ms)^N(\\d{2})\\s*(?:\\[[^\\]]+\\])?\\s*\\n(.*?)(?=^N\\d{2}\\b|\\Z)",notes):
        add("evidence/crew/noticeboard-and-desk-notes.txt","note-N"+m.group(1),m.group(2).strip())

    route=json.loads((root/"evidence/recovery-routing.json").read_text())
    acceptance=json.loads((root/"acceptance.json").read_text())
    nonce=bytes.fromhex(route["K08"]["desk_nonce"])
    target=bytes.fromhex(acceptance["slot_sha256"]["K08"])
    if norm("A—B  C!")!="a b c": raise SystemExit("normalization control failed")
    if hmac.digest(bytes(range(16)),b"synthetic caption control","sha256")[:16].hex().upper()!="19A65FDE6869B98EDE6E366B2115BA46":
        raise SystemExit("HMAC control failed")

    candidates=set()
    for _,_,text in fields:
        words=norm(text).split()
        if words: candidates.add(" ".join(words))
        for i in range(len(words)):
            for j in range(i+1,min(len(words),i+48)+1):
                candidates.add(" ".join(words[i:j]))
    matches=0
    for phrase in candidates:
        component=hmac.digest(nonce,phrase.encode("utf-8"),"sha256")[:16]
        if hashlib.sha256(component).digest()==target: matches+=1
    print(json.dumps({"files_scanned":len(files),"pdf_members_opened":0,
        "fields":len(fields),"unique_contiguous_phrases":len(candidates),
        "max_span_words":48,"manifest_sha256":manifest_sha,
        "normalization_control":"PASS","HMAC_control":"PASS","K08_match_count":matches},indent=2))
if __name__=="__main__": main()
