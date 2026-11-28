#!/usr/bin/env python3
from hashlib import sha256
import re, sys
from pathlib import Path

CREW_SHA256="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
AT_SPAN_SHA256="556713372501bc1d2a113beaf1fe4fe921267d5cd0c9655b2386ec536a6bffa0"

def words(s): return re.findall(r"[A-Za-z0-9]+",s.lower())
def lowbit(w): return sum((ord(c.lower())&1)<<i for i,c in enumerate(w))
def count_letter(n):
    assert 0 <= n < 26
    return chr(ord("A")+n)

def longest_common(a,b):
    best=[]
    longest=0
    for i in range(len(a)):
        for j in range(len(b)):
            k=0
            while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]:
                k+=1
            if k>longest:
                longest=k; best=[a[i:i+k]]
            elif k==longest and k:
                best.append(a[i:i+k])
    uniq=[]
    for x in best:
        if x not in uniq: uniq.append(x)
    return longest,uniq

def main(root):
    root=Path(root)
    raw=(root/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest()==CREW_SHA256
    notes={}
    for m in re.finditer(rb"^N(\\d{2}) / (\\w+) \\[censored\\]\\n([^\\n]+)$",raw,re.M):
        n=int(m.group(1)); line=m.group(3).decode()
        body=line.split(": ",1)[1] if ": " in line else line
        notes[n]=words(body)
    assert set(notes)==set(range(1,25))

    sha_ids=[19,8,1]
    counts=[len(notes[n]) for n in sha_ids]
    assert counts==[22,13,11]
    token="".join(count_letter(x) for x in counts)
    assert token=="WNL"
    assert lowbit(token)==1

    sea_notes=[n for n,body in notes.items() if "sea" in body]
    assert sea_notes==[1,20]
    length,spans=longest_common(notes[1],notes[20])
    assert length==2 and len(spans)==1
    span=spans[0]
    assert sha256(" ".join(span).encode()).hexdigest()==AT_SPAN_SHA256

    print({
      "source_pin":"PASS","sha_a1z26_ids":sha_ids,"counts":counts,
      "count_token":"WNL","lowbit_wnl":1,"selected_note":1,
      "literal_sea_notes":sea_notes,"n01_n20_unique_max_overlap_words":length,
      "at_span_fingerprint":"PASS","target_or_nonce_read":False
    })

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: k08_sha_n01_sea_interlock_sft.py ROOT")
    main(sys.argv[1])
