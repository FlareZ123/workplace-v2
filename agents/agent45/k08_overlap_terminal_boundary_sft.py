#!/usr/bin/env python3
"""Target-blind K08 overlap-chain terminal-boundary SFT. Aggregate/hash output only."""
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import re

CREW_SHA256="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
HASH_AT="556713372501bc1d2a113beaf1fe4fe921267d5cd0c9655b2386ec536a6bffa0"
HASH_MT="a9bb20e02706cf2079ed0a11b3fededd1c9325edeea5925734f7592ca7c943c9"
HASH_ET="44359e21492d788147966d8c0bc5beb2f4f4d0d05dd36f3ff36a0cd36a349907"
HASH_PT="9ad80878ed715fd6a1b1bf2b353e344a3dda762a4f3f5c713ccb2dad3d01d88f"
HASH_BETWEEN="1c142a3af93b7bf154aa022daf9431d6d38599c9e880e043a7b5185ca5142401"
HASH_PAYLOAD="4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c"

def words(s): return re.findall(r"[A-Za-z0-9]+",s.lower())
def h(run): return sha256(" ".join(run).encode("ascii")).hexdigest()
def locate(seq,run):
    out=[]
    for i in range(len(seq)-len(run)+1):
        if tuple(seq[i:i+len(run)])==tuple(run): out.append(i)
    return out
def longest(a,b):
    best=0;runs=set()
    for i in range(len(a)):
        for j in range(len(b)):
            k=0
            while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]: k+=1
            if k>best:
                best=k;runs={tuple(a[i:i+k])} if k else set()
            elif k and k==best:runs.add(tuple(a[i:i+k]))
    return best,runs
def addr(token):
    ids=tuple(ord(c)-64 for c in token.upper())
    assert all(1<=n<=24 for n in ids)
    return ids

def main():
    root=Path(__file__).resolve().parents[2]
    raw=(root/"resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest()==CREW_SHA256
    text=raw.decode()
    notes={}
    rawbodies={}
    for m in re.finditer(r"^N(\d{2}) / \w+ \[censored\]\n([^\n]+)$",text,re.M):
        n=int(m.group(1)); line=m.group(2)
        body=line.split(": ",1)[1] if ": " in line else line
        rawbodies[n]=body; notes[n]=words(body)
    assert set(notes)==set(range(1,25))

    # Existing source-emitted addresses.
    at=addr("AT"); mt=addr("MT")
    la,ra=longest(notes[at[0]],notes[at[1]])
    lm,rm=longest(notes[mt[0]],notes[mt[1]])
    assert la==2 and len(ra)==1 and lm==5 and len(rm)==1
    run_at=next(iter(ra)); run_mt=next(iter(rm))
    assert h(run_at)==HASH_AT and h(run_mt)==HASH_MT
    p_at=locate(notes[20],run_at); p_mt=locate(notes[20],run_mt)
    assert p_at==[6] and p_mt==[8]

    # Existing LEN operator: MT's exact five-word span -> E; preserve T pivot.
    et=addr(chr(64+lm)+"T")
    assert et==(5,20)
    le,re_=longest(notes[et[0]],notes[et[1]])
    assert le==2 and len(re_)==1
    run_et=next(iter(re_)); assert h(run_et)==HASH_ET
    p_et=locate(notes[20],run_et); assert p_et==[13]
    assert p_mt[0]+lm==p_et[0]

    # Enumerate every downstream repeated >=2-word N20 span; choose the earliest
    # one after ET without consulting target semantics.
    et_end=p_et[0]+le
    candidates=[]
    for other in range(1,25):
        if other==20: continue
        for k,i,j,run in common_runs(notes[other],notes[20]):
            if k>=2 and j>=et_end:
                candidates.append((j,other,k,run))
    min_start=min(c[0] for c in candidates)
    earliest=[c for c in candidates if c[0]==min_start]
    assert len(earliest)==1
    p_pt,partner,lpt,run_pt=earliest[0]
    assert partner==16 and lpt==2 and h(run_pt)==HASH_PT
    assert addr("PT")==((partner,20))

    between=tuple(notes[20][et_end:p_pt])
    assert len(between)==4 and h(between)==HASH_BETWEEN

    # PT is the normalized prefix of N20 sentence two: source-visible stop.
    sentences=[s.strip() for s in re.split(r"[.!?]+",rawbodies[20]) if s.strip()]
    assert len(sentences)==2
    sentence2=tuple(words(sentences[1]))
    assert tuple(run_pt)==sentence2[:2]

    payload=tuple(notes[20][p_at[0]:p_pt])
    assert len(payload)==13 and h(payload)==HASH_PAYLOAD
    assert payload==run_at+run_mt+run_et+between

    # Corpus controls retained from the earlier stage.
    pair_bigram=0;ge5=[]
    for a,b in combinations(range(1,25),2):
        ll,_=longest(notes[a],notes[b])
        pair_bigram+=ll>=2
        if ll>=5:ge5.append((a,b,ll))
    assert pair_bigram==12 and ge5==[(13,20,5)]

    print({
      "source_pin":"PASS","target_or_nonce_read":False,
      "AT":{"ids":at,"words":la,"n20_start":p_at[0],"sha256":HASH_AT},
      "MT":{"ids":mt,"words":lm,"n20_start":p_mt[0],"sha256":HASH_MT},
      "ET":{"ids":et,"words":le,"n20_start":p_et[0],"sha256":HASH_ET},
      "PT_stop":{"ids":(partner,20),"words":lpt,"n20_start":p_pt,"sha256":HASH_PT},
      "between_words":len(between),"between_sha256":HASH_BETWEEN,
      "reconstructed_payload_words":len(payload),"payload_sha256":HASH_PAYLOAD,
      "pairs_with_any_shared_bigram":pair_bigram,"pairs_with_run_ge5":ge5,
      "complete_author_final_wording_emitted":False,
    })

def common_runs(a,b):
    out=[]
    for i in range(len(a)):
        for j in range(len(b)):
            k=0
            while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]: k+=1
            if k>=2: out.append((k,i,j,tuple(a[i:i+k])))
    return out

if __name__=="__main__": main()
