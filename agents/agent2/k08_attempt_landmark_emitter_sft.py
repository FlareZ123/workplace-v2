#!/usr/bin/env python3
"""Target-blind ATTEMPT-field landmark emitter for the fixed N20 payload."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/"resources"/"evidence"
PINS={
 "crew":"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
 "spool":"7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
 "audit":"32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
}
def load(rel,pin):
 raw=(ROOT/rel).read_bytes();assert hashlib.sha256(raw).hexdigest()==pin;return raw
def words(s):return re.findall(r"[A-Za-z0-9]+",s.lower())
def longest(a,b):
 best=0;runs=set()
 for i in range(len(a)):
  for j in range(len(b)):
   k=0
   while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]:k+=1
   if k>best:best=k;runs={tuple(a[i:i+k])} if k else set()
   elif k and k==best:runs.add(tuple(a[i:i+k]))
 return best,runs
def positions(seq,run):
 return [i for i in range(len(seq)-len(run)+1) if tuple(seq[i:i+len(run)])==tuple(run)]

crew=load("crew/noticeboard-and-desk-notes.txt",PINS["crew"]).decode()
spool=load("print/spool-reconstruction.log",PINS["spool"]).decode()
audit=load("transfers/transfer-audit.jsonl",PINS["audit"]).decode()
notes={}
for m in re.finditer(r"^N(\d{2}) / \w+ \[censored\]\n([^\n]+)$",crew,re.M):
 n=int(m.group(1));line=m.group(2);body=line.split(": ",1)[1] if ": " in line else line
 notes[n]=words(body)
assert set(notes)==set(range(1,25))

# Literal surviving schema vocabulary only.
fields=set(re.findall(r"\b([A-Z][A-Z0-9_]*)=",spool))
for line in audit.splitlines():
 if line.strip():fields.update(k.upper() for k in json.loads(line))
assert "ATTEMPT" in fields

# For each schema field, collect adjacent A..X pairs that address N20 and one
# other note, have a unique >=2-word maximal overlap, and occur uniquely in N20.
def landmarks(field):
 out=[]
 for i in range(len(field)-1):
  pair=field[i:i+2]
  if not all("A"<=c<="X" for c in pair):continue
  a,b=[ord(c)-64 for c in pair]
  if a==b or 20 not in (a,b):continue
  length,runs=longest(notes[a],notes[b])
  if length<2 or len(runs)!=1:continue
  run=next(iter(runs));pos=positions(notes[20],run)
  if len(pos)!=1:continue
  out.append((i,pair,a,b,run,pos[0]))
 return out

census={f:landmarks(f) for f in sorted(fields)}
three=[(f,v) for f,v in census.items() if len({x[5] for x in v})>=3]
assert [f for f,_ in three]==["ATTEMPT"]
lm=census["ATTEMPT"]
# TT is deliberately excluded because it addresses N20 to itself.
assert [(x[1],x[4],x[5]) for x in lm]==[
 ("AT",("the","sea"),6),
 ("TE",("and","the"),13),
 ("PT",("do","not"),19),
]

# The already source-emitted BETWEEN operation makes the field self-delimiting:
# include AT, everything strictly between AT and TE, TE, everything strictly
# between TE and PT; stop at PT.
(_,_,_,_,at,pa),(_,_,_,_,te,pe),(_,_,_,_,pt,pp)=lm
a_end=pa+len(at);e_end=pe+len(te)
payload=tuple(notes[20][pa:pp])
assert payload==at+tuple(notes[20][a_end:pe])+te+tuple(notes[20][e_end:pp])
assert " ".join(payload)=="the sea the end of the night and the voices at the table"
assert tuple(notes[20][pp:pp+len(pt)])==pt==("do","not")

print({
 "source_pins":"PASS","target_or_nonce_read":False,
 "schema_fields":len(fields),"fields_with_three_distinct_N20_landmarks":[f for f,_ in three],
 "ATTEMPT_landmarks":[(x[1]," ".join(x[4]),x[5]) for x in lm],
 "payload":" ".join(payload),"stop":" ".join(pt),
 "transfer_or_crypto_required":False,"heuristic_span_search_required":False,
 "complete_author_final_wording_emitted":False,
})
