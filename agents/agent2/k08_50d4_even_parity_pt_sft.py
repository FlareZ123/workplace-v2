#!/usr/bin/env python3
"""Target-blind parity decode of LOW-IF-EVEN transfer output."""
import hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/"resources"/"evidence"
PINS={
 "crew":"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
 "audit":"32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
}
def pack(bits): return sum((b&1)<<i for i,b in enumerate(bits))
def even(b): return b.bit_count()%2==0
def longest(a,b):
 best=0;runs=set()
 for i in range(len(a)):
  for j in range(len(b)):
   k=0
   while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]: k+=1
   if k>best: best=k;runs={tuple(a[i:i+k])} if k else set()
   elif k and k==best:runs.add(tuple(a[i:i+k]))
 return best,runs

crew=(ROOT/"crew/noticeboard-and-desk-notes.txt").read_bytes()
audit=(ROOT/"transfers/transfer-audit.jsonl").read_bytes()
assert hashlib.sha256(crew).hexdigest()==PINS["crew"]
assert hashlib.sha256(audit).hexdigest()==PINS["audit"]
notes={}
for m in re.finditer(r"^N(\d{2}) / \w+ \[censored\]\n([^\n]+)$",crew.decode(),re.M):
 n=int(m.group(1));line=m.group(2)
 body=line.split(": ",1)[1] if ": " in line else line
 notes[n]=re.findall(r"[a-z0-9]+",body.lower())
rows=[json.loads(x) for x in audit.decode().splitlines() if x.strip()]

outs={}
for tr in sorted({r["transfer"] for r in rows if r.get("kind")=="CHUNK"}):
 d={(r["seq"],r["attempt"]):bytes.fromhex(r["checkpoint"])
    for r in rows if r.get("kind")=="CHUNK" and r["transfer"]==tr}
 raw=b"".join(d[(s,1 if s%2==0 else 2)] for s in range(8))
 bits=[b&1 for b in raw]
 packed=bytes(pack(bits[o:o+8]) for o in (0,8))
 decoded="".join(chr(b&0x7f) for b in packed)
 valid=all(even(b) for b in packed) and all("A"<=c<="X" for c in decoded)
 outs[tr]=(packed.hex().upper(),decoded,[even(b) for b in packed],valid)

assert outs=={
 "AX-7778":("694A","iJ",[True,False],False),
 "AX-7781":("C28A","B\n",[False,False],False),
 "AX-7782":("50D4","PT",[True,True],True),
 "AX-7783":("CF59","OY",[True,True],False),
}
assert (0x50&0x7f,0xD4&0x7f)==(ord("P"),ord("T"))
assert even(0x50) and even(0xD4)

# PT is a valid N01..N24 A1Z26 address and independently lands on the
# source-visible N16/N20 prohibition boundary.
length,runs=longest(notes[16],notes[20])
assert length==2 and runs=={("do","not")}
starts=[i for i in range(len(notes[20])-1) if notes[20][i:i+2]==["do","not"]]
assert starts==[19]
raw20=re.search(r"^N20 / \w+ \[censored\]\n([^\n]+)$",crew.decode(),re.M).group(1)
sentences=[re.findall(r"[a-z0-9]+",s.lower()) for s in re.split(r"[.!?]+",raw20) if s.strip()]
assert sentences[1][:2]==["do","not"]

print({
 "source_pins":"PASS","target_or_nonce_read":False,
 "controls":outs,"selected_decode":"PT","address":[16,20],
 "max_overlap":["do","not"],"n20_start":19,"sentence2_prefix":True,
 "complete_author_final_wording_emitted":False,
})
