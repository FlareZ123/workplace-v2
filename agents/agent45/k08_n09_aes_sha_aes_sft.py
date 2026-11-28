#!/usr/bin/env python3
"""Target-blind N09 AES/SHA/AES emitter census."""
from hashlib import sha256
from pathlib import Path
import re

CREW_SHA256="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"

def lowbit(word):
    return sum((ord(c.lower())&1)<<i for i,c in enumerate(word))

def lower_if_even(value):
    return value+1 if value%2==0 else value

def main():
    root=Path(__file__).resolve().parents[2]
    raw=(root/"resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest()==CREW_SHA256
    notes={}
    for m in re.finditer(r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",raw.decode(),re.M):
        n=int(m.group(1)); line=m.group(3)
        body=line.split(": ",1)[1] if ": " in line else line
        notes[n]=re.findall(r"[A-Za-z0-9]+",body.lower())
    assert set(notes)==set(range(1,25))

    def transform(window):
        selectors=[lower_if_even(lowbit(w)) for w in window]
        if not all(1<=v<=24 for v in selectors):
            return None
        token="".join(notes[v][0][0].upper() for v in selectors)
        return token,tuple(selectors)

    eligible=[]
    special=[]
    for n,body in notes.items():
        for i in range(len(body)-2):
            got=transform(body[i:i+3])
            if got is None: continue
            token,selectors=got
            eligible.append((n,i+1,token))
            if token in {"AES","SHA"}:
                special.append((n,i+1,token,selectors))
    assert len(eligible)==125
    assert [(n,pos,tok) for n,pos,tok,_ in special]==[
        (9,2,"AES"),(9,4,"SHA"),(9,6,"AES")
    ]

    sequences=[]
    for n,body in notes.items():
        for start in range(1,len(body)-6+1):
            outputs=[]
            for pos in (start,start+2,start+4):
                got=transform(body[pos-1:pos+2])
                if got is None:
                    outputs=[]; break
                outputs.append(got[0])
            if outputs==["AES","SHA","AES"]:
                sequences.append((n,start))
    assert sequences==[(9,2)]

    print({
      "source_pin":"PASS","target_or_nonce_read":False,
      "eligible_triplet_windows":len(eligible),
      "AES_or_SHA_windows":[(n,p,t) for n,p,t,_ in special],
      "unique_stride2_AES_SHA_AES":sequences,
      "complete_author_final_wording_emitted":False,
    })

if __name__=="__main__":
    main()
