#!/usr/bin/env python3
"""Original K08 complete editor: arbitrary P20 ordered deletion plus fixed ordered
N02 ROOM / N06 LAMP / N01 TEA lexical insertions (2 or 3). Local source only.

The role-conditioned source tokens and their order are frozen before reading
K08 acceptance. No candidate source text, phrase or component is printed.
"""
from hashlib import sha256
import itertools, json, hmac, re,sys,math
from pathlib import Path
RAW_SHA='13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
P20_SHA='4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c'
N02_HMAC='bf889359b0303f2b2b2fd96ae841210b'
def main(root):
 root=Path(root)
 raw=(root/'evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
 assert sha256(raw).hexdigest()==RAW_SHA
 notes={}
 for match in re.finditer(r'^N(\d\d) / [^\n]+\n([^\n]+)',raw.decode(),re.M):
  noteid=int(match.group(1))
  body=match.group(2).split(':',1)[-1].lstrip()
  notes[noteid]=re.findall(r'[a-z0-9]+',body.lower())
 assert set(notes)==set(range(1,25))
 p20=notes[20][6:19]
 assert len(p20)==13 and sha256(' '.join(p20).encode()).hexdigest()==P20_SHA
 extras=['room','lamp','tea']
 for word,n in zip(extras,[2,6,1]):
  assert notes[n].count(word)==1 and word not in p20
 route=json.loads((root/'evidence/recovery-routing.json').read_text())
 acc=json.loads((root/'acceptance.json').read_text())
 key=bytes.fromhex(route['K08']['desk_nonce'])
 target=acc['slot_sha256']['K08']
 def hashed(words):
  return sha256(hmac.new(key,' '.join(words).encode(),'sha256').digest()[:16]).hexdigest()
 assert hmac.new(key,' '.join(notes[2]).encode(),'sha256').digest()[:16].hex()==N02_HMAC
 for m in (2,3):
  append=extras[:m]
  planted_digest=hashed(p20+append)
  checked=0;original_hits=0;plant=0;seen=set();assignments=0
  for mask in range(1<<13):
   retained=[w for i,w in enumerate(p20) if (mask>>i)&1]
   k=len(retained)
   for positions in itertools.combinations(range(k+m),m):
    assignments+=1
    ii=jj=0;candidate=[]
    marker=set(positions)
    for pos in range(k+m):
     if pos in marker:candidate.append(append[ii]);ii+=1
     else:candidate.append(retained[jj]);jj+=1
    msg=' '.join(candidate)
    if msg in seen:continue
    seen.add(msg)
    got=hashed(candidate)
    checked+=1
    original_hits+=(got==target)
    plant+=(got==planted_digest)
  assert assignments==sum(math.comb(13,k)*math.comb(k+m,m) for k in range(14))
  assert plant==1
  print(json.dumps(dict(added_source_roles=2 if m==2 else 3,
      source_sha='PASS',p20_sha='PASS',n02_hmac='PASS',
      assignment_checks=assignments,unique_complete_candidates=checked,
      duplicate_assignments=assignments-checked,
      original_commitment_hits=original_hits,planted_positive_hits=plant),
      sort_keys=True),flush=True)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: SCRIPT extracted-original-archive-root')
 main(sys.argv[1])
