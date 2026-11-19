#!/usr/bin/env python3
"""Enumerate contiguous 1+3+3 ALOWBIT splices for the selected Emily +1 edit."""
from __future__ import annotations
import hashlib, itertools, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"resources/evidence/crew/noticeboard-and-desk-notes.txt"
EXPECTED="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
TOKEN=re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?")

def words(s):
    return TOKEN.findall(s)

def main():
    raw=SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==EXPECTED
    text=raw.decode("utf-8")
    notes={}
    for number,author,body in re.findall(r"(?ms)^N(\d\d) / ([^\n]+)\n(.+?)(?=\n\nN\d\d /|\Z)",text):
        body=body.strip()
        body=body.split(":",1)[1].strip() if ":" in body else body
        toks=words(body)
        notes[int(number)]={"author":author.split()[0],"head":toks[0][0].upper(),"count":len(toks)}
    emily=[n for n in range(1,25) if notes[n]["author"]=="Emily"]
    def edit_rows(direction):
        out=[]
        for i,old in enumerate(emily):
            ids=emily.copy()
            ids[i]+=direction
            if ids!=sorted(ids) or len(set(ids))!=len(ids) or any(n not in notes for n in ids):
                continue
            initials="".join(notes[n]["head"] for n in ids)
            count_letters="".join(chr(65+notes[n]["count"]) if notes[n]["count"]<26 else "?" for n in ids)
            fixed=initials[0]+count_letters[1:4]+initials[5:8]
            out.append({"old":old,"new":ids[i],"ids":ids,"initials":initials,
                        "count_letters":count_letters,"fixed_splice":fixed})
        return out
    plus=edit_rows(1)
    minus=edit_rows(-1)
    hits=[r for r in plus if r["initials"]=="ATEALBIT" and r["fixed_splice"]=="ALOWBIT"]
    assert len(plus)==7 and len(minus)==7 and len(hits)==1
    selected=hits[0]
    h=selected["initials"]
    c=selected["count_letters"]
    all_splices=[]
    for hp,cs,ts in itertools.product(range(len(h)),range(len(c)-2),range(len(h)-2)):
        value=h[hp]+c[cs:cs+3]+h[ts:ts+3]
        all_splices.append({"head_position":hp,"count_window_start":cs,
                            "tail_window_start":ts,"value":value})
    matches=[r for r in all_splices if r["value"]=="ALOWBIT"]
    assert len(all_splices)==288 and len(matches)==2
    print(json.dumps({"source_sha256":EXPECTED,"Emily_positions":emily,
                      "valid_plus_one_edits":plus,"valid_minus_one_edits":minus,
                      "selected_edit":selected,"splice_count":len(all_splices),
                      "ALOWBIT_matches":matches,"all_splices":all_splices},
                     indent=2,sort_keys=True))

if __name__=="__main__":
    main()
