"""K08 source-only eight Emily note word selector, read-only acceptance."""
import hashlib,hmac,itertools,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/"resources"
PIN="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
def digest(s,k):return hashlib.sha256(hmac.digest(k,s,"sha256")[:16]).digest()
def run():
 raw=(ROOT/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
 assert hashlib.sha256(raw).hexdigest()==PIN
 blocks=re.findall(r"(N\d+) / ([^\n]+)\n(.*?)(?=\n\nN\d+|\Z)",raw.decode(),re.S)
 notes=[(n,re.findall(r"[a-z0-9]+",t.split(":",1)[-1].lower())) for n,a,t in blocks if a.startswith("Emily ")]
 assert [n for n,_ in notes]==["N02","N06","N10","N13","N17","N18","N20","N23"]
 nonce=bytes.fromhex(json.loads((ROOT/"evidence/recovery-routing.json").read_text())["K08"]["desk_nonce"])
 want=bytes.fromhex(json.loads((ROOT/"acceptance.json").read_text())["slot_sha256"]["K08"])
 assert hmac.digest(nonce,b"a good watch leaves the room ready for the next pair of hands","sha256")[:16].hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
 out=set()
 for col in range(14):
  for d in (-2,-1,0,1,2):
   for reverse in (False,True):
    p=[]
    for i,(n,w) in enumerate(notes):
     a,b=nonce[2*i:2*i+2]
     rawidx=(a,b,(a<<8)|b,(b<<8)|a,a^b,a+b,a&b,a|b,a>>4,b>>4,a&15,b&15,i,int(n[1:]))[col]
     p.append(w[(((-1-rawidx) if reverse else rawidx)+d)%len(w)])
    out.add(("single",tuple(p)))
 for method in range(8):
  for d in (-2,-1,0,1,2):
   p=[]
   for i,(_,w) in enumerate(notes):
    a,b=nonce[2*i:2*i+2]
    v=((a,b),(b,a),(a^b,a),(b,a^b),(a+b,a),(a,a+b),(a>>4,b&15),(a&15,b>>4))[method]
    p.append((w[(v[0]+d)%len(w)],w[(v[1]+d)%len(w)]))
   out.add(("pair",tuple(p)))
 assert len(out)==180
 seen=set();counts=Counter();match=None;positive=False
 k,p=sorted(out)[0]
 planted=(" ".join(p) if k=="single" else " ".join(z for pair in p for z in pair)).encode()
 planted_hash=digest(planted,nonce)
 for k,p in sorted(out):
  for order in itertools.permutations(range(8)):
   phrase=(" ".join(p[i] for i in order) if k=="single" else " ".join(z for i in order for z in p[i])).encode()
   if phrase in seen:counts["duplicate"]+=1;continue
   seen.add(phrase);counts[k]+=1
   x=digest(phrase,nonce)
   if x==want:match=phrase.decode();break
   if x==planted_hash:positive=True
  if match is not None:break
 assert positive and len(seen)==5367600 and counts["single"]==3795120 and counts["pair"]==1572480
 print(json.dumps({"result":"MATCH" if match else "NO_MATCH","candidate":match,
   "rules":len(out),"distinct_candidates":len(seen),"counts":counts,
   "synthetic_positive":positive},sort_keys=True))
if __name__=="__main__":run()
