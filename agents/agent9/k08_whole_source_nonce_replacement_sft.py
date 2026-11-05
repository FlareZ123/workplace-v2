"""Original H-17 K08: full 16-byte source-key replacement and preserved text."""
import hashlib as H,hmac,json,re,sys
from pathlib import Path
r=Path(sys.argv[1] if len(sys.argv)>1 else "resources")
sp=(r/"evidence/print/spool-reconstruction.log").read_bytes()
no=(r/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
ro=(r/"evidence/recovery-routing.json").read_bytes()
assert H.sha256(sp).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert H.sha256(no).hexdigest()=="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
assert H.sha256(ro).hexdigest()=="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
route=json.loads(ro);nonce=bytes.fromhex(route["K08"]["desk_nonce"])
target="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
norm=lambda s:" ".join(re.findall("[a-z0-9]+",s.lower()))
def dig(k,s):return H.sha256(hmac.new(k,norm(s).encode(),H.sha256).digest()[:16]).hexdigest()
n02="A good watch leaves the room ready for the next pair of hands."
assert hmac.new(nonce,norm(n02).encode(),H.sha256).digest()[:16].hex()=="bf889359b0303f2b2b2fd96ae841210b"
texts={}
lines=no.decode().splitlines()
for i,line in enumerate(lines):
 m=re.match(r"N(\d{2}) /",line)
 if m:
  body=lines[i+1].strip();texts["N"+m.group(1)]=body
  if ":" in body:texts["N"+m.group(1)+" caption"]=body.split(":",1)[1].strip()
for p in sorted((r/"evidence/mail").glob("*.eml")):
 body=p.read_text().split("\n\n",1)[-1].strip();texts[p.stem]=body
 for j,x in enumerate(re.split(r"\n\s*\n",body)):
  if len(x.strip())>15:texts[f"{p.stem}p{j}"]=" ".join(x.split())
 for j,x in enumerate(re.split(r"(?<=[.!?])\s+",body.replace("\n"," "))):
  if len(x.strip())>18:texts[f"{p.stem}s{j}"]=x.strip()
phrases=set(map(norm,texts.values()));phrases.discard("")
keys={nonce}
files=[x for x in (r/"evidence").rglob("*") if x.is_file()]
files += [r/x for x in ("START_HERE.md","acceptance.json","candidate.template.json","verify.py")]
for p in files:
 data=p.read_bytes()
 keys.update(bytes.fromhex(x.decode()) for x in re.findall(rb"(?<![a-fA-F0-9])[0-9A-Fa-f]{32}(?![a-fA-F0-9])",data))
 if p.suffix.lower() not in (".pdf",".raw"):
  d=H.sha256(data).digest();keys.update((d[:16],d[-16:],H.md5(data).digest()))
known=("049AAB2E1CDE7A82CD7C60234303C91A","0D7E3AB56FB75DA3EB0E2E06786D239E","1384AF96E25D6ADA666209CB55E062FA","FF8B78200A56E8586DCDA00EF01E4572","5DBF40EE52FAAED9A536D3326CF0D95A","93495F5E425AB8E592123DABAEB68545")
keys.update(bytes.fromhex(x) for x in known)
plant=dig(bytes.fromhex(route["K04"]["masked_component"]),"Leave the light on for the next watch.")
assert plant!=target
hit=0;positive=0
for key in keys:
 forms=(key,key[::-1],b"".join(key[i:i+4][::-1] for i in range(0,16,4)),b"".join(reversed([key[i:i+4] for i in range(0,16,4)])))
 for k in forms:
  for phrase in phrases:
   h=dig(k,phrase)
   hit+=h==target;positive+=h==plant
assert len(keys)==276 and len(phrases)==281 and hit==0 and positive==1
print(json.dumps({"source_keys":len(keys),"original_texts":len(phrases),"checks":len(keys)*4*len(phrases),"original_hits":hit,"planted_hits":positive}))
