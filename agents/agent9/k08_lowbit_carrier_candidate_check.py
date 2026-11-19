#!/usr/bin/env python3
"""Test direct complete-carrier adoption under the LOW BIT route.

The source-stage/accepted-stage component maps select the workshop, shelf and
desk notes; the HMAC/route convergence selects the sunrise-photo note; the
four-note HMAC cycle adds N09/N11/N12/N13. This script tests complete sentences
from exactly those source-selected note carriers, plus the two literal route
instructions and the concatenated cycle. It does not generate paraphrases.
"""
from __future__ import annotations
import hashlib, hmac, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
E=ROOT/"resources/evidence"
NOTES=E/"crew/noticeboard-and-desk-notes.txt"
ROUTING=E/"recovery-routing.json"
ACCEPTANCE=ROOT/"resources/acceptance.json"
PINS={
    NOTES:"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    ROUTING:"f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    ACCEPTANCE:"681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def normalize(s):
    return " ".join(re.sub(r"[^a-z0-9\s]"," ",s.lower()).split())

def parse_notes(s):
    out={}
    for n,author,body in re.findall(r"(?ms)^N(\d\d) / ([^\n]+)\n(.*?)(?=\n\nN\d\d /|\Z)",s):
        body=body.strip()
        body=body.split(":",1)[1].strip() if ":" in body else body
        out[int(n)]={"author":author.split()[0],"body":body}
    assert set(out)==set(range(1,25))
    return out

def main():
    for path,expected in PINS.items():
        assert sha(path.read_bytes())==expected, path
    notes=parse_notes(NOTES.read_text(encoding="utf-8"))
    route=json.loads(ROUTING.read_text(encoding="utf-8"))
    acceptance=json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    nonce=bytes.fromhex(route["K08"]["desk_nonce"])
    target=acceptance["slot_sha256"]["K08"]
    selected=[9,10,11,12,13,14,20,23]
    candidates=[]
    for n in selected:
        candidates.append({"label":f"N{n:02d} {notes[n]['author']} full body","source_ids":[n],"text":notes[n]["body"]})
        sentences=[x.strip() for x in re.split(r"(?<=[.!?])\s+",notes[n]["body"]) if x.strip()]
        for i,sentence in enumerate(sentences,1):
            candidates.append({"label":f"N{n:02d} {notes[n]['author']} sentence {i}","source_ids":[n],"text":sentence})
    candidates.extend([
        {"label":"source-stage component route","source_ids":[12,10,11],"text":"Workshop to shelf"},
        {"label":"accepted-stage component route","source_ids":[12,10],"text":"Workshop to desk"},
        {"label":"four-note HMAC cycle concatenation","source_ids":[12,11,13,9],
         "text":" ".join(notes[n]["body"] for n in [12,11,13,9])},
    ])
    results=[]
    for candidate in candidates:
        normalized=normalize(candidate["text"])
        digest=hmac.new(nonce,normalized.encode("utf-8"),"sha256").digest()[:16]
        component_sha=sha(digest)
        results.append({"label":candidate["label"],"source_ids":candidate["source_ids"],
                        "normalized":normalized,"hmac16":digest.hex().upper(),
                        "component_sha256":component_sha,"matches_K08":component_sha==target})
    assert len(results)==22 and not any(x["matches_K08"] for x in results)
    print(json.dumps({
        "hypothesis":"direct complete-body/sentence adoption from LOW BIT-selected note carriers or literal route instruction",
        "selected_note_ids":selected,"candidate_count":len(results),"K08_target_sha256":target,
        "matches":sum(x["matches_K08"] for x in results),"results":results,
        "scope":"Exact full bodies and complete sentences from N09/N10/N11/N12/N13/N14/N20/N23 plus source-stage/accepted-stage route strings and the full HMAC-cycle concatenation. No paraphrase or phrase grammar; a negative result rejects only direct adoption from these retained text carriers."
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
