"""K08: source-authored N13, all 2^22-1 word-order-preserving pure deletions.

Run: python agents/agent25/k08_n13_full_ordered_subsequence_sft.py resources
Read-only, using original source and original K08 target.
"""
from pathlib import Path
import hashlib,hmac,json,re,sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('resources')
source=(root/'evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
assert hashlib.sha256(source).hexdigest()=='13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
s=source.decode().split('N13 / Emily [censored]\n',1)[1].split('\n\nN14 /',1)[0]
words=re.findall(r'[a-z0-9]+',s.lower());assert len(words)==22
r=json.loads((root/'evidence/recovery-routing.json').read_text())['K08'];key=bytes.fromhex(r['desk_nonce'])
original=bytes.fromhex(json.loads((root/'acceptance.json').read_text())['slot_sha256']['K08'])
def digest(s):return hashlib.sha256(hmac.new(key,s.encode(),hashlib.sha256).digest()[:16]).digest()
assert hmac.new(key,b'a good watch leaves the room ready for the next pair of hands',hashlib.sha256).digest()[:16].hex().upper()=='BF889359B0303F2B2B2FD96AE841210B'
plant=' '.join(words[:4]);planted=digest(plant);plantcount=0;matches=[]
for mask in range(1,1<<len(words)):
 candidate=' '.join(w for i,w in enumerate(words) if mask>>i&1)
 d=digest(candidate)
 if d==original:matches.append((mask,candidate))
 if d==planted:plantcount+=1
print('N13_words',len(words),'all_nonempty_subsequences',(1<<len(words))-1,'original_matches',matches,'plant_matches',plantcount)
assert plantcount==1
