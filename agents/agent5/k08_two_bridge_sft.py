"""K08 two-interior-edit source model. Read-only original commitment SFT."""
import hashlib
import hmac
import json
import re
from collections import Counter
from pathlib import Path

case = Path(__file__).resolve().parents[2] / "resources"
raw = (case / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
notes = dict(re.findall(r"(?m)^N(\d\d) / [^\n]+\n(.+?)(?=\n\n|\Z)", raw.decode(), re.S))
words = {n:tuple(re.findall(r"[a-z0-9]+",v.lower())) for n,v in notes.items()}
base, draft1, draft2, desc = words["13"],words["02"][6:],words["06"][3:],words["20"][:19]
assert (len(base),len(draft1),len(draft2),len(desc)) == (22,13,11,19)
route = json.loads((case/"evidence/recovery-routing.json").read_text())
accept = json.loads((case/"acceptance.json").read_text())
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
target = bytes.fromhex(accept["slot_sha256"]["K08"])
def component(w):
    return hmac.new(nonce," ".join(w).encode(),hashlib.sha256).digest()[:16]
assert component(draft1).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
def spans(ws, anchors):
    return sorted({ws[i:j] for i in range(len(ws)) for j in range(i+2,min(len(ws),i+5)+1)
                   if set(ws[i:j]).intersection(anchors)})
sea=spans(desc,{"sea","voices","table"})
room=sorted(set(spans(draft1,{"watch","room","hands"})) |
            set(spans(draft2,{"lamp","corridor","quiet"})))
windows=[(i,j,k,l) for i in range(2,len(base)-8)
         for j in range(i+1,min(i+5,len(base)-6))
         for k in range(j+3,len(base)-3)
         for l in range(k+1,min(k+5,len(base)-1))
         if len(base[:i])>=2 and len(base[j:k])>=3 and len(base[l:])>=2]
assert len(sea)==29 and len(room)==52 and len(windows)==1024
i,j,k,l=windows[len(windows)//2]
synthetic=hashlib.sha256(component(base[:i]+sea[0]+base[j:k]+room[-1]+base[l:])).digest()
count=Counter()
controls=0
matches=[]
for label,first,second in (("sea-room",sea,room),("room-sea",room,sea)):
    for i,j,k,l in windows:
        start,centre,end=base[:i],base[j:k],base[l:]
        for a in first:
            for b in second:
                phrase=start+a+centre+b+end
                digest=hashlib.sha256(component(phrase)).digest()
                count[label]+=1
                if digest==synthetic: controls+=1
                if digest==target: matches.append((label," ".join(phrase),component(phrase).hex()))
assert dict(count)=={"sea-room":1544192,"room-sea":1544192} and controls>=1
print(json.dumps({"spans":[len(sea),len(room)],"two_cut_windows":len(windows),
                  "assignments":dict(count),"synthetic_control_hits":controls,
                  "accepted_matches":matches},indent=2))
