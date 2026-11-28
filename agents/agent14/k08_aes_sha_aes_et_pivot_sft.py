#!/usr/bin/env python3
from hashlib import sha256
import hmac, json, re, sys
from pathlib import Path

CREW_SHA256="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
P20_SHA256="4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c"
N02_HMAC16="bf889359b0303f2b2b2fd96ae841210b"

def words(s): return re.findall(r"[A-Za-z0-9]+",s.lower())
def lowbit(w): return sum((ord(c.lower())&1)<<i for i,c in enumerate(w))

def common_runs(a,b):
    out=[]
    for i in range(len(a)):
        for j in range(len(b)):
            k=0
            while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]:
                k+=1
            if k: out.append((k,i,j,a[i:i+k]))
    m=max(k for k,_,_,_ in out)
    return [x for x in out if x[0]==m]

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

    n20=notes[20]
    payload=n20[6:19]
    assert len(payload)==13
    assert sha256(" ".join(payload).encode()).hexdigest()==P20_SHA256

    assert lowbit("SHA")==5
    runs=common_runs(notes[5],n20)
    assert len(runs)==1 and runs[0][0]==2 and runs[0][2]==13
    _,_,pstart,pivot=runs[0]
    local=pstart-6
    assert local==7 and payload[local:local+2]==pivot

    assert lowbit("AES")==7
    left=payload[:local]
    right=payload[local+len(pivot):]
    assert (len(left),len(pivot),len(right))==(7,2,4)

    candidate=list(reversed(left))+pivot+list(reversed(right))
    assert len(candidate)==13

    route=json.loads((root/"evidence/recovery-routing.json").read_text())
    acceptance=json.loads((root/"acceptance.json").read_text())
    key=bytes.fromhex(route["K08"]["desk_nonce"])
    target=acceptance["slot_sha256"]["K08"]

    def component(ws):
        return hmac.new(key," ".join(ws).encode(),sha256).digest()[:16]

    assert component(notes[2]).hex()==N02_HMAC16
    hit=sha256(component(candidate)).hexdigest()==target
    print({
      "source_pin":"PASS","p20_pin":"PASS","sha_to_n05_et_pivot":"PASS",
      "aes_reversal_selector":"PASS","partition":[7,2,4],
      "complete_candidates":1,"historical_n02_control":"PASS",
      "original_k08_hits":int(hit)
    })
    raise SystemExit(3 if hit else 0)

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: k08_aes_sha_aes_et_pivot_sft.py ROOT")
    main(sys.argv[1])
