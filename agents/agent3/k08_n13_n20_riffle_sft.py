"""K08 four-fragment ordered riffle from Emily N13 and N20.

Two nonoverlapping original 1..4-word spans per source note, alternated in
either A1 B1 A2 B2 or B1 A1 B2 A2 order. No invented source words.
Run from repository root: python agents/agent3/k08_n13_n20_riffle_sft.py
"""
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/"resources"
raw=(ROOT/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert hashlib.sha256(raw).hexdigest()=="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
notes={int(n):re.findall(r"[a-z0-9]+",line.lower())
       for n,author,line in re.findall(r"(?m)^N(\\d\\d) / ([^\\n]+)\\n([^\\n]+)",raw.decode())}
a,b=notes[13],notes[20]
assert (len(a),len(b))==(22,30)

def pairs(words,anchors):
    out=[]
    for i in range(len(words)):
        for n in range(1,5):
            j=i+n
            if j>=len(words):continue
            for k in range(j,len(words)):
                for m in range(1,5):
                    l=k+m
                    if l>len(words):continue
                    first,second=words[i:j],words[k:l]
                    if set(first+second).isdisjoint(anchors):continue
                    out.append((" ".join(first)," ".join(second)))
    return out

A=pairs(a,{"mugs","window","lamp","night"})
B=pairs(b,{"sea","night","voices","table"})
assert (len(A),len(B))==(1839,3170)
route=json.loads((ROOT/"evidence/recovery-routing.json").read_text())
accept=json.loads((ROOT/"acceptance.json").read_text())
nonce=bytes.fromhex(route["K08"]["desk_nonce"])
target=bytes.fromhex(accept["slot_sha256"]["K08"])
def digest(text):
    return hashlib.sha256(hmac.digest(nonce,text.encode("ascii"),"sha256")[:16]).digest()

assert hmac.digest(nonce,b"a good watch leaves the room ready for the next pair of hands","sha256")[:16].hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
planted=digest(" ".join((A[0][0],B[0][0],A[0][1],B[0][1])))
positive=total=0
original=[]
for swap in (False,True):
    for x,y in itertools.product(A,B):
        text=" ".join((x[0],y[0],x[1],y[1]) if not swap
                      else (y[0],x[0],y[1],x[1]))
        got=digest(text)
        if got==planted:positive+=1
        if got==target:original.append(text)
        total+=1
assert total==11659260 and positive==1
print(json.dumps({"complete_candidates":total,"synthetic_hits":positive,"original_hits":original},indent=2))
assert not original
