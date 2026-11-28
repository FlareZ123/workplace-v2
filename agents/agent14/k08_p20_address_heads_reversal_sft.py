#!/usr/bin/env python3
from hashlib import sha256
import hmac,json,re,sys
from pathlib import Path

CREW_SHA256="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
P20_SHA256="4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c"
N02_HMAC16="bf889359b0303f2b2b2fd96ae841210b"
ADDRESSES=("AT","MT","ET","PT")

def words(s): return re.findall(r"[A-Za-z0-9]+",s.lower())
def lowbit(s): return sum((ord(c.lower())&1)<<i for i,c in enumerate(s))

def common(a,b):
    best=(0,None,None,None)
    count=0
    for i in range(len(a)):
        for j in range(len(b)):
            k=0
            while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]:
                k+=1
            if k>best[0]:
                best=(k,i,j,a[i:i+k]);count=1
            elif k==best[0] and k:
                count+=1
    return best,count

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

    expected=[(2,6),(5,8),(2,13),(2,19)]
    for addr,(want_len,want_j) in zip(ADDRESSES,expected):
        a=ord(addr[0])-64
        t=ord(addr[1])-64
        assert t==20
        (ln,_,j,_), multiplicity=common(notes[a],notes[t])
        assert ln==want_len and j==want_j and multiplicity==1

    heads="".join(a[0] for a in ADDRESSES)
    tails="".join(a[1] for a in ADDRESSES)
    assert heads=="AMEP" and tails=="TTTT"
    assert lowbit(heads)==7
    assert lowbit(tails)==0
    assert 7 in notes and 0 not in notes

    payload=notes[20][6:19]
    assert len(payload)==13
    assert sha256(" ".join(payload).encode()).hexdigest()==P20_SHA256
    candidate=list(reversed(payload))

    route=json.loads((root/"evidence/recovery-routing.json").read_text())
    acceptance=json.loads((root/"acceptance.json").read_text())
    key=bytes.fromhex(route["K08"]["desk_nonce"])
    target=acceptance["slot_sha256"]["K08"]

    def component(ws):
        return hmac.new(key," ".join(ws).encode(),sha256).digest()[:16]

    assert component(notes[2]).hex()==N02_HMAC16
    hit=sha256(component(candidate)).hexdigest()==target
    print({
      "source_pin":"PASS","addresses":ADDRESSES,"varying_column":"AMEP",
      "varying_column_lowbit":7,"invariant_column_lowbit":0,
      "selected_note":7,"p20_pin":"PASS","complete_candidates":1,
      "historical_n02_control":"PASS","original_k08_hits":int(hit)
    })
    raise SystemExit(3 if hit else 0)

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: k08_p20_address_heads_reversal_sft.py ROOT")
    main(sys.argv[1])
