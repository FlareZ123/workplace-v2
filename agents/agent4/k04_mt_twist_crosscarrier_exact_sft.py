"""Source-only complete MT19937 twist cross-carrier fingerprint.
Run: python agents/agent4/k04_mt_twist_crosscarrier_exact_sft.py
No selected ACK2 value, K04 commitment or route mask in model fitting.
"""
import hashlib,importlib.util,json,re,struct,zlib
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RES=ROOT/"resources"
spec=importlib.util.spec_from_file_location("mt",ROOT/"agents/agent49/k04_p951_symbolic_basis.py")
mt=importlib.util.module_from_spec(spec);spec.loader.exec_module(mt)
def pin(path,sha):
 raw=(RES/path).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==sha
 return raw
sp=pin("evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083")
rows=[bytes.fromhex(s.decode()) for s in re.findall(rb"PAYLOAD=([0-9A-F]{32})",sp)]
assert len(rows)==len(mt.STARTS)==133
entries=[]
for row,(start,p) in enumerate(zip(mt.STARTS,rows)):
 if row==129:continue
 for j in range(4):
  n=mt.untemper(int.from_bytes(p[4*j:4*j+4],"little"))
  entries.append((f"PRINT:{row}:{j}","tempered-little",n,start+j))
assert len(entries)==528
carriers=[]
def add(k,b):
 assert len(b)==4
 carriers.append((k,b))
rc=pin("evidence/procedures/RC-17-scans.txt","a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d")
for m in re.finditer(rb"DOCUMENT RC-17 / REV (B|C|D-draft) / SECTION (\w+).*?Footer control strip: ([0-9A-F]{8})",rc,re.S):
 add("RC17:"+m[1].decode()+":"+m[2].decode(),bytes.fromhex(m[3].decode()))
tr=pin("evidence/recorder/trip-recorder.raw","5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba")
for i in range(88):
 off=16+24*i
 ts,node,event,latch,seq,word,aux,crc=struct.unpack_from("<IHBBI4sII",tr,off)
 if zlib.crc32(tr[off:off+20])&0xffffffff==crc:
  add(f"TRP2:{i}:n{node}:e{event}:seq{seq}",word)
for i,line in enumerate((RES/"evidence/maintenance/seal-receipts.jsonl").read_text().splitlines()):
 h=json.loads(line)["serial"].split("-")[-1]
 if re.fullmatch("[A-Fa-f0-9]{8}",h):add(f"SEAL:{i}",bytes.fromhex(h))
for k,v in (("A","049AAB2E"),("B","1CDE7A82"),("C","CD7C6023"),("D","4303C91A")):
 add("WN14:"+k,bytes.fromhex(v))
routes=json.loads((RES/"evidence/recovery-routing.json").read_text())
for k,field in (("K04","masked_component"),("K08","desk_nonce")):
 b=bytes.fromhex(routes[k][field])
 for j in range(4):add(f"ROUTE:{k}:{j}",b[4*j:4*j+4])
assert len(carriers)==152
for k,b in carriers:
 for endian in ("little","big"):
  n=int.from_bytes(b,endian)
  entries.extend(((k,"native-"+endian,n,None),(k,"tempered-"+endian,mt.untemper(n),None)))
assert len(entries)==1136
byvalue=defaultdict(list)
for e in entries:byvalue[e[2]].append(e)
mag=0x9908b0df
def twist(a,b):
 n=((a&0x80000000)|(b&0x7fffffff))
 return ((n>>1)^(mag if b&1 else 0))&0xffffffff
matches=[]
for a in entries:
 for b in entries:
  if a is b:continue
  candidate=b[2]^twist(0,a[2])
  for value in (candidate,candidate^0x40000000):
   for c in byvalue.get(value,()):
    if c is a or c is b or len({a[0],b[0],c[0]})<3:continue
    if a[3] is not None and b[3] is not None and c[3] is not None:continue
    matches.append((a,b,c))
assert len(matches)==16,matches
ordered=[(a,b,c) for a,b,c in matches if b[3] is not None and c[3]==b[3]+227]
assert len(ordered)==8,ordered
rc_pairs=[(a,b,c) for a,b,c in ordered if a[0].startswith("RC17:")]
assert {(a[0],a[2],b[3],c[3]) for a,b,c in rc_pairs}=={
 ("RC17:B:VERIFY",0x20e95399,210,437),
 ("RC17:B:PURGE",0xeddf3ed2,211,438)}
assert sum(a[0].startswith("TRP2:") for a,b,c in ordered)==6
known={idx:n for _,_,n,idx in entries if idx is not None}
assert known[211]^twist(0x20e95399,0xeddf3ed2)==known[438]==0xf9997b00
assert known[211]^twist(0x20e95399^0x80000000,0xeddf3ed2)!=known[438]
print(json.dumps({"printer_source_words":528,"nonprinter_fourbyte_fields":152,
 "ordered_pair_checks":len(entries)*(len(entries)-1),"source_triples":len(matches),
 "ordered_crosscarrier_links":len(ordered),"rc17b_exact_full_twist":"PASS",
 "selected_K04_bits_recovered":0},indent=2))
