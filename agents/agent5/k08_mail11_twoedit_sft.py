"""K08 MAIL-11 quoted-semantic-ancestor, two separated source literal replacements."""
import hashlib
import hmac
import json
import re
from collections import Counter
from pathlib import Path

root=Path(__file__).resolve().parents[2]/"resources"
mail=(root/"evidence/mail/11.eml").read_text()
raw=(root/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert hashlib.sha256(raw).hexdigest()=="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
base=tuple(re.findall(r"[a-z0-9]+",("people making room"+mail.split("people making room",1)[1].split(".",1)[0]).lower()))
notes=dict(re.findall(r"(?m)^N(\d\d) / [^\n]+\n(.+?)(?=\n\n|\Z)",raw.decode(),re.S))
n13=tuple(re.findall(r"[a-z0-9]+",notes["13"].lower()))
n20=tuple(re.findall(r"[a-z0-9]+",notes["20"].split(".",1)[0].lower()))
assert len(base)==19 and len(n13)==22 and len(n20)==19
def spans(w,anchors):
    return sorted({w[i:j] for i in range(len(w)) for j in range(i+2,min(i+5,len(w))+1)
                   if not set(w[i:j]).isdisjoint(anchors)})
sea=spans(n20,{"sea","voices","table"})
lamps=spans(n13,{"mugs","window","lamp"})
windows=[(i,j,k,l) for i in range(2,len(base)-7) for j in range(i+1,min(i+5,len(base)-5))
         for k in range(j+2,len(base)-2) for l in range(k+1,min(k+5,len(base)-1))
         if len(base[j:k])>=2 and len(base[l:])>=2]
assert len(sea)==29 and len(lamps)==35 and len(windows)==733
route=json.loads((root/"evidence/recovery-routing.json").read_text())
accept=json.loads((root/"acceptance.json").read_text())
nonce=bytes.fromhex(route["K08"]["desk_nonce"])
target=bytes.fromhex(accept["slot_sha256"]["K08"])
def digest(words):
    return hashlib.sha256(hmac.new(nonce," ".join(words).encode(),hashlib.sha256).digest()[:16]).digest()
q=windows[len(windows)//2]
positive=digest(base[:q[0]]+sea[0]+base[q[1]:q[2]]+lamps[0]+base[q[3]:])
control=0;hits=[];count=Counter()
for label,left,right in (("sea-lamp",sea,lamps),("lamp-sea",lamps,sea)):
    for i,j,k,l in windows:
        front,middle,back=base[:i],base[j:k],base[l:]
        for a in left:
            for b in right:
                text=front+a+middle+b+back
                outcome=digest(text)
                count[label]+=1
                if outcome==positive:control+=1
                if outcome==target:hits.append((label," ".join(text)))
assert dict(count)=={"sea-lamp":743995,"lamp-sea":743995} and control>0
print(json.dumps({"tested":dict(count),"synthetic_hits":control,"original_hits":hits},indent=2))
