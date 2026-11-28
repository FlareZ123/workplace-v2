#!/usr/bin/env python3
"""H-17 source-pinned K08: exhaustive N01/N06 11-word aligned editor plus zero or one
P20-word insertion, deletion or replacement. Only redacted aggregates go to stdout.
Any original commitment hit is kept as a 0600 file OUTSIDE the source root.
"""
import pathlib,sys,hashlib,hmac,json,re,os
SOURCE_SHA = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
N02_FIXTURE = 'bf889359b0303f2b2b2fd96ae841210b'

def normalized(s):
 return ' '.join(re.sub(r'[^a-z0-9\s]', ' ', s.lower()).split())

def parse_notes(raw):
 notes={}
 for m in re.finditer(r'^N(\d\d) / (.+?)\n(.+?)(?=\n\nN\d\d /|\Z)',raw,re.M|re.S):
  i=int(m.group(1))
  notes[i]={'heading':m.group(2).strip(),'body':m.group(3).strip().split(': ',1)[-1]}
 assert list(notes)==list(range(1,25))
 return notes

def main(root):
 src=(root/'evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
 assert hashlib.sha256(src).hexdigest()==SOURCE_SHA
 n=parse_notes(src.decode())
 route=json.loads((root/'evidence/recovery-routing.json').read_text())
 accept=json.loads((root/'acceptance.json').read_text())
 key=bytes.fromhex(route['K08']['desk_nonce'])
 target=accept['slot_sha256']['K08']
 def reduce(words):
  return hashlib.sha256(hmac.new(key,' '.join(words).encode(),hashlib.sha256).digest()[:16]).hexdigest()
 assert hmac.new(key,normalized(n[2]['body']).encode(),hashlib.sha256).digest()[:16].hex()==N02_FIXTURE
 n20=normalized(n[20]['body']).split()
 p20=n20[6:19]
 assert len(p20)==13
 assert hashlib.sha256(' '.join(p20).encode()).hexdigest()=='4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c'
 a0=normalized(n[1]['body']).split()
 b0=normalized(n[6]['body']).split()
 assert len(a0)==len(b0)==11
 # Original source-only selectors, as reported by Agents 10 and 42.
 head=n[20]['body'][:24]
 assert len(head)==24
 assert bytes(sum((ord(head[k*8+i])&1)<<i for i in range(8)) for k in range(3))==b'MHI'
 triplet=[n[i]['body'] for i in (13,8,9)]
 assert tuple(len(normalized(x).split())&1 for x in triplet)==(0,1,1)
 assert ''.join(normalized(x)[0] for x in triplet)=='abn'
 orientations=[(a0,b0),(a0[::-1],b0),(a0,b0[::-1]),(a0[::-1],b0[::-1])]
 positive={}
 for kind,m in zip(('replacement','insertion','deletion'),(0x559,0x569,0x579)):
  words=[(b0 if m>>i&1 else a0)[i] for i in range(11)]
  if kind=='replacement':words[3]=p20[1]
  elif kind=='insertion':words.insert(7,p20[2])
  else:words.pop(5)
  positive[kind]=reduce(words)
 count=0
 matches=0
 plant={kind:0 for kind in positive}
 by_kind={}
 fd=None
 for a,b in orientations:
  for mask in range(2048):
   words=[(b if mask>>i&1 else a)[i] for i in range(11)]
   for kind in ('identity','replacement','insertion','deletion'):
    if kind=='identity':variants=(words,)
    elif kind=='replacement':variants=(words[:i]+[term]+words[i+1:] for i in range(11) for term in p20)
    elif kind=='insertion':variants=(words[:i]+[term]+words[i:] for i in range(12) for term in p20)
    else:variants=(words[:i]+words[i+1:] for i in range(11))
    for v in variants:
     dig=reduce(v)
     count+=1
     by_kind[kind]=by_kind.get(kind,0)+1
     if dig==target:
      matches+=1
      if fd is None:
       fd=os.open(root.parent/'k08_n01_n06_P20_real_hit_0600.jsonl',os.O_CREAT|os.O_WRONLY|os.O_EXCL,0o600)
      with os.fdopen(os.dup(fd),'a') as f:
       f.write(json.dumps({'phrase':' '.join(v),'k08':hmac.new(key,' '.join(v).encode(),hashlib.sha256).digest()[:16].hex()})+'\n')
     for k,val in positive.items():plant[k]+=dig==val
 if fd is not None:os.close(fd)
 assert count==2048*4*(1+11*13+12*13+11),count
 assert all(x>0 for x in plant.values())
 print(json.dumps({
  'model':'N01N06_literal_aligned_full_plus_0_or_1_P20_word_edit',
  'complete_assignments':count,'counts_by_operation':by_kind,
  'original_matches':matches,'planted_full_output_positive_counts':plant,
  'n02_hmac16_fixture':'PASS','source_sha':'PASS','p20_digest':'PASS'
 },sort_keys=True))

if __name__=='__main__':
 main(pathlib.Path(sys.argv[1]))
