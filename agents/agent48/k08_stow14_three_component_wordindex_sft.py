#!/usr/bin/env python3
"""Conditional STOW14 14-word K08 whole-candidate screen, never edits recovery files."""
import hashlib, hmac, itertools, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2] / "resources"
crew = (ROOT/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert hashlib.sha256(crew).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
notes=[]
for no, author, body in re.findall(r"^N(\\d{2}) / (\\w+) \\[censored\\]\\n(.+)",crew.decode(),re.M):
    label,sep,content=body.partition(": ")
    words=re.findall("[a-z0-9]+",(content if sep else body).lower())
    notes.append((int(no),author,words))
assert len(notes)==24 and [row[0] for row in notes]==list(range(1,25))
senders=[]
for n in (10,11,13):
    msg=(ROOT/f"evidence/mail/{n:02d}.eml").read_text()
    senders.append(re.search(r"^From: (\\w+) \\[censored\\]",msg,re.M).group(1))
assert senders==["Simon","Emily","Gabriel"]
selected=[row for row in notes if row[1] in senders]
assert [n for n,_,_ in selected]==[2,5,6,7,10,12,13,14,17,18,20,22,23,24]
bits=[int(author in senders) for _,author,_ in notes]
letters="".join(chr(65+sum(bits[5*j+i]<<i for i in range(5))) for j in range(4))
suffix=sum(bits[20+i]<<i for i in range(4))
assert letters+str(suffix)=="STOW14"
keys={"K05":"FF8B78200A56E8586DCDA00EF01E4572",
      "K06":"5DBF40EE52FAAED9A536D3326CF0D95A",
      "K07":"93495F5E425AB8E592123DABAEB68545"}
accept=json.loads((ROOT/"acceptance.json").read_text())
nonce=bytes.fromhex(json.loads((ROOT/"evidence/recovery-routing.json").read_text())["K08"]["desk_nonce"])
def component(text):
    norm=" ".join(re.findall("[a-z0-9]+",text.lower()))
    return hmac.new(nonce,norm.encode(),hashlib.sha256).digest()[:16],norm
n02,_=component("A good watch leaves the room ready for the next pair of hands")
assert n02.hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
hits=[];seen=set();count=0;first=None
for order in itertools.permutations(keys):
    stream=b"".join(bytes.fromhex(keys[k]) for k in order)
    for offset in range(48):
        for backwards in (False,True):
            bstream=stream[::-1] if backwards else stream
            for mode in ("whole","low4","high4"):
                for origin in (0,1):
                    for reversed_notes in (False,True):
                        seq=selected[::-1] if reversed_notes else selected
                        words=[]
                        for j,(_,_,vocab) in enumerate(seq):
                            byt=bstream[(offset+j)%48]
                            idx={"whole":byt,"low4":byt&15,"high4":byt>>4}[mode]
                            words.append(vocab[(idx-origin)%len(vocab)])
                        derived,normalized=component(" ".join(words))
                        digest=hashlib.sha256(derived).hexdigest()
                        count+=1;seen.add(normalized)
                        if first is None:first=(normalized,derived.hex().upper(),digest)
                        if digest==accept["slot_sha256"]["K08"]:
                            hits.append([order,offset,backwards,mode,origin,reversed_notes,normalized,derived.hex().upper()])
assert count==6912 and len(seen)==2084
assert component(first[0])[0].hex().upper()==first[1]
print(json.dumps({"selector":"STOW14","notes":[n for n,_,_ in selected],
  "tested":count,"unique":len(seen),"original_K08_matches":hits,
  "first_example":first,"source_control":"N02 HMAC16 passes",
  "interpretation":"speculative whole-phrase word-index operator only, no author-final version evidence"},indent=2))
