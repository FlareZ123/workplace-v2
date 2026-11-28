#!/usr/bin/env python3
"""Target-blind fixed N20 payload reconstruction with transfer-emitted PT stop."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/"resources"/"evidence"
PINS={"crew":"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
      "audit":"32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"}
def words(s): return re.findall(r"[A-Za-z0-9]+",s.lower())
def pack(bs): return sum((b&1)<<i for i,b in enumerate(bs))
def low_text(s): return pack([ord(c.lower())&1 for c in s])
def longest(a,b):
 best=0;runs=set()
 for i in range(len(a)):
  for j in range(len(b)):
   k=0
   while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]: k+=1
   if k>best: best=k;runs={tuple(a[i:i+k])} if k else set()
   elif k and k==best:runs.add(tuple(a[i:i+k]))
 return best,runs
def locate(seq,run):
 return [i for i in range(len(seq)-len(run)+1) if tuple(seq[i:i+len(run)])==tuple(run)]

crew=(ROOT/"crew/noticeboard-and-desk-notes.txt").read_bytes()
audit=(ROOT/"transfers/transfer-audit.jsonl").read_bytes()
assert hashlib.sha256(crew).hexdigest()==PINS["crew"]
assert hashlib.sha256(audit).hexdigest()==PINS["audit"]
notes={};authors={};bodies={}
for m in re.finditer(r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",crew.decode(),re.M):
 n=int(m.group(1));authors[n]=m.group(2);line=m.group(3)
 body=line.split(": ",1)[1] if ": " in line else line
 bodies[n]=body;notes[n]=words(body)

# Source-selected TAILBIT/LEN emitter -> literal AT.
sel=[n for n in range(1,25) if authors[n] in {"Simon","Emily","Gabriel"}]
heads="".join(notes[n][0][0].upper() for n in sel)
st=heads.index("TAILBIT");tids=sel[st:st+7]
tail=pack([ord(notes[n][-1][-1])&1 for n in tids])
lens=pack([len(bodies[n])&1 for n in tids])
assert (tail,lens)==(0x41,0x74) and bytes([tail,lens]).decode().upper()=="AT"

# AT -> N01/N20 maximal overlap.
la,ra=longest(notes[1],notes[20]);assert la==2 and ra=={("the","sea")}
run_at=next(iter(ra));assert locate(notes[20],run_at)==[6]

# Existing ATEALBIT LOW BIT calibration -> M; preserve T pivot -> MT.
aids=[2,6,11,13,17,18,20,23]
ah="".join(notes[n][0][0].upper() for n in aids)
assert ah=="ATEALBIT" and low_text(ah)==0x4D and chr(low_text(ah))=="M"
lm,rm=longest(notes[13],notes[20])
assert lm==5 and rm=={("the","end","of","the","night")}
run_mt=next(iter(rm));assert locate(notes[20],run_mt)==[8]

# LEN(MT)=5 -> E; preserve T -> ET.
le,re_=longest(notes[5],notes[20]);assert le==2 and re_=={("and","the")}
run_et=next(iter(re_));assert locate(notes[20],run_et)==[13]

# ATTEMPT TAILBIT LOW IF EVEN side-channel independently emits parity-framed PT.
rows=[json.loads(x) for x in audit.decode().splitlines() if x.strip()]
d={(r["seq"],r["attempt"]):bytes.fromhex(r["checkpoint"])
   for r in rows if r.get("kind")=="CHUNK" and r["transfer"]=="AX-7782"}
raw=b"".join(d[(s,1 if s%2==0 else 2)] for s in range(8))
bits=[b&1 for b in raw];packed=bytes(pack(bits[o:o+8]) for o in (0,8))
assert packed==bytes.fromhex("50D4") and all(x.bit_count()%2==0 for x in packed)
pt="".join(chr(x&0x7f) for x in packed);assert pt=="PT"
lp,rp=longest(notes[16],notes[20]);assert lp==2 and rp=={("do","not")}
run_pt=next(iter(rp));assert locate(notes[20],run_pt)==[19]

# PT is now independently supplied: no "earliest downstream repeated span" choice.
start=locate(notes[20],run_at)[0];stop=locate(notes[20],run_pt)[0]
payload=tuple(notes[20][start:stop])
assert payload==run_at+run_mt+run_et+("voices","at","the","table")
assert " ".join(payload)=="the sea the end of the night and the voices at the table"
assert notes[20][stop:stop+2]==["do","not"]

print({"source_pins":"PASS","target_or_nonce_read":False,
 "AT":run_at,"MT":run_mt,"ET":run_et,"PT":run_pt,
 "transfer_bytes":packed.hex().upper(),"transfer_decode":pt,
 "payload":" ".join(payload),"stop_index":stop,
 "heuristic_PT_search_used":False,"complete_author_final_wording_emitted":False})
