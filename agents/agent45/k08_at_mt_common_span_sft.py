#!/usr/bin/env python3
"""Target-blind K08 AT->MT common-span decoder. Aggregate/hash output only."""
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import re

CREW_SHA256="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ATEALBIT_IDS=(2,6,11,13,17,18,20,23)
TAILBIT_IDS=(12,13,14,17,18,20,22)
AT_SPAN_SHA256="556713372501bc1d2a113beaf1fe4fe921267d5cd0c9655b2386ec536a6bffa0"
MT_SPAN_SHA256="a9bb20e02706cf2079ed0a11b3fededd1c9325edeea5925734f7592ca7c943c9"

def words(text):
    return re.findall(r"[A-Za-z0-9]+",text.lower())

def pack_lsb(bits):
    return sum((b&1)<<i for i,b in enumerate(bits))

def longest_common_runs(a,b):
    best_len=0
    best=set()
    for i in range(len(a)):
        for j in range(len(b)):
            k=0
            while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]:
                k+=1
            if k>best_len:
                best_len=k
                best={tuple(a[i:i+k])} if k else set()
            elif k and k==best_len:
                best.add(tuple(a[i:i+k]))
    return best_len,best

def address_ids(token):
    ids=tuple(ord(c.upper())-64 for c in token if c.isalpha())
    assert all(1<=n<=24 for n in ids)
    return ids

def span_hash(run):
    return sha256(" ".join(run).encode("ascii")).hexdigest()

def first_index(seq,run):
    for i in range(len(seq)-len(run)+1):
        if tuple(seq[i:i+len(run)])==run:
            return i
    raise AssertionError("run absent")

def main():
    path=Path(__file__).resolve().parents[2]/"resources/evidence/crew/noticeboard-and-desk-notes.txt"
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==CREW_SHA256
    text=raw.decode("utf-8")
    notes={}
    authors={}
    for m in re.finditer(r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",text,re.M):
        n=int(m.group(1))
        authors[n]=m.group(2)
        line=m.group(3)
        notes[n]=line.split(": ",1)[1] if ": " in line else line
    assert set(notes)==set(range(1,25))
    tokenized={n:words(body) for n,body in notes.items()}

    selected=[n for n in range(1,25) if authors[n] in {"Simon","Emily","Gabriel"}]
    selected_heads="".join(tokenized[n][0][0].upper() for n in selected)
    start=selected_heads.index("TAILBIT")
    tail_ids=tuple(selected[start:start+7])
    assert tail_ids==TAILBIT_IDS
    tail_value=pack_lsb([ord(tokenized[n][-1][-1])&1 for n in tail_ids])
    len_value=pack_lsb([len(notes[n])&1 for n in tail_ids])
    address1=bytes((tail_value,len_value)).decode("ascii").upper()
    assert address1=="AT"

    ids1=address_ids(address1)
    assert ids1==(1,20)
    len1,runs1=longest_common_runs(tokenized[ids1[0]],tokenized[ids1[1]])
    assert len1==2 and len(runs1)==1
    run1=next(iter(runs1))
    assert span_hash(run1)==AT_SPAN_SHA256
    tail_step=pack_lsb([ord(c)&1 for c in run1[-1]])
    assert tail_step==7

    atealbit="".join(tokenized[n][0][0].upper() for n in ATEALBIT_IDS)
    assert atealbit=="ATEALBIT"
    m_value=pack_lsb([ord(c.lower())&1 for c in atealbit])
    assert m_value==ord("M")
    next_letter=chr(ord("A")+((m_value-ord("A")+tail_step)%26))
    assert next_letter=="T"
    address2=chr(m_value)+next_letter
    assert address2=="MT"

    ids2=address_ids(address2)
    assert ids2==(13,20)
    len2,runs2=longest_common_runs(tokenized[ids2[0]],tokenized[ids2[1]])
    assert len2==5 and len(runs2)==1
    run2=next(iter(runs2))
    assert span_hash(run2)==MT_SPAN_SHA256

    pairs_with_bigram=0
    pairs_with_run_ge5=[]
    pairs_with_span1=[]
    for a,b in combinations(range(1,25),2):
        run_len,runs=longest_common_runs(tokenized[a],tokenized[b])
        pairs_with_bigram+=run_len>=2
        if run_len>=5:
            pairs_with_run_ge5.append((a,b,run_len))
        if any(span_hash(run)==AT_SPAN_SHA256 for run in runs):
            pairs_with_span1.append((a,b))
    assert pairs_with_bigram==12
    assert pairs_with_run_ge5==[(13,20,5)]
    assert pairs_with_span1==[(1,20)]
    assert first_index(tokenized[20],run1)<first_index(tokenized[20],run2)

    print({
        "source_pin":"PASS",
        "address_1":address1,"address_1_ids":ids1,
        "address_1_span_words":len1,"address_1_span_sha256":AT_SPAN_SHA256,
        "address_2":address2,"address_2_ids":ids2,
        "address_2_span_words":len2,"address_2_span_sha256":MT_SPAN_SHA256,
        "all_note_pairs":276,"pairs_with_any_shared_bigram":pairs_with_bigram,
        "pairs_with_run_len_ge_5":pairs_with_run_ge5,
        "spans_occur_in_N20_in_order":True,
        "k08_target_or_nonce_read":False,
        "complete_final_wording_emitted":False,
    })

if __name__=="__main__":
    main()
