#!/usr/bin/env python3
"""Target-blind K08 AES/SEA closed-loop calibration. Aggregate/hash output only."""
from hashlib import sha256
from pathlib import Path
import itertools
import re

CREW_SHA256="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
N07_FIRST3_SHA256="439b4ed8ebfb401883fd56bee755e7f95b822422e1f10d543e1b9e71326bede3"

def addr(token):
    ids=tuple(ord(c)-64 for c in token.upper())
    assert all(1<=n<=24 for n in ids)
    return ids

def lowbit(token):
    return sum((ord(c.lower())&1)<<i for i,c in enumerate(token))

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

    def count_letters(token):
        values=[len(notes[n]) for n in addr(token)]
        assert all(0<=v<=25 for v in values)
        return "".join(chr(65+v) for v in values),values

    aes="AES"; sea=aes[::-1]
    low,counts_aes=count_letters(aes)
    wol,counts_sea=count_letters(sea)
    assert low=="LOW" and wol=="WOL" and wol==low[::-1]
    assert counts_aes==[11,14,22] and counts_sea==[22,14,11]
    assert lowbit(aes)==lowbit(sea)==7
    first3=notes[7][:3]
    assert sha256(" ".join(first3).encode()).hexdigest()==N07_FIRST3_SHA256

    occurrences=[n for n,w in notes.items() if "sea" in w]
    assert occurrences==[1,20]
    occurrence_token="".join(chr(64+n) for n in occurrences)
    assert occurrence_token=="AT"

    low_triples=wol_triples=0
    for a,b,c in itertools.product(range(1,25),repeat=3):
        values=(len(notes[a]),len(notes[b]),len(notes[c]))
        low_triples+=values==(11,14,22)
        wol_triples+=values==(22,14,11)
    assert low_triples==wol_triples==36

    print({
      "source_pin":"PASS","target_or_nonce_read":False,
      "AES_address_ids":addr(aes),"AES_count_letters":low,
      "SEA_address_ids":addr(sea),"SEA_count_letters":wol,
      "AES_LOW_BIT":lowbit(aes),"SEA_LOW_BIT":lowbit(sea),
      "selected_note":7,"selected_note_first3_sha256":N07_FIRST3_SHA256,
      "SEA_literal_note_occurrences":occurrences,
      "occurrence_ids_token":occurrence_token,
      "LOW_count_triples":low_triples,"WOL_count_triples":wol_triples,
      "closed_loop":True,"complete_author_final_wording_emitted":False,
    })

if __name__=="__main__":
    main()
