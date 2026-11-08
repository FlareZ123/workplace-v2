"""H-17 K08: complete-object indexed PRF transport test.

A conditional Nxx->PS-(0300+xx) note-to-printer issuer is fitted at one real
complete historical note/packet control and must replay four whole heldout
HMAC16 values, before it may predict the final PS-0323 HMAC16.
"""
from pathlib import Path
import hashlib, hmac, itertools, json, re

ROOT=Path(__file__).resolve().parents[2] / 'resources'
EVIDENCE=ROOT/'evidence'
SOURCES={
 'notes': EVIDENCE/'crew/noticeboard-and-desk-notes.txt',
 'spool': EVIDENCE/'print/spool-reconstruction.log',
 'routing': EVIDENCE/'recovery-routing.json',
 'acceptance': ROOT/'acceptance.json',
}
PINS={
 'notes':'13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb',
 'spool':'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
 'routing':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
 'acceptance':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f',
}
for name,p in SOURCES.items():
 assert hashlib.sha256(p.read_bytes()).hexdigest()==PINS[name]
route=json.loads(SOURCES['routing'].read_text())
acceptance=json.loads(SOURCES['acceptance'].read_text())
nonce=bytes.fromhex(route['K08']['desk_nonce'])
mask=bytes.fromhex(route['K04']['masked_component'])
assert len(nonce)==len(mask)==16
known=json.loads((Path(__file__).resolve().parents[2]/'candidate.json').read_text())
slots={k:bytes.fromhex(v) for k,v in known.items() if v is not None}
selected_names=(2,6,13,17,18)
raw_note=SOURCES['notes'].read_text()
note={int(k):v.strip().split(':',1)[-1].strip() for k,v in re.findall(
 r'^N(\d\d) / Emily \[censored\]\n(.*?)(?=\n\n|\Z)',raw_note,re.M|re.S)}
spool={int(j):bytes.fromhex(p) for j,p in re.findall(r'JOB=PS-261003-(\d\d\d\d).*?PAYLOAD=([0-9A-F]{32})',SOURCES['spool'].read_text())}
def normalize(t):return ' '.join(re.sub(r'[^a-z0-9\s]',' ',t.lower()).split())
def note_hash(t):return hmac.digest(nonce,normalize(t).encode(),'sha256')[:16]
assert note_hash(note[18]).hex().upper()=='A3100AE1ABB9C8D58315D9EBF326978B'
source={n:(note_hash(note[n]),spool[300+n]) for n in selected_names}
keys={'nonce':nonce,'mask':mask,**slots,
 'first-six-sha256':hashlib.sha256(b''.join(slots[k] for k in sorted(slots))).digest()[:16],
 'nonce-mask-xor':bytes(x^y for x,y in zip(nonce,mask)),
 'nonce-mask-sha256':hashlib.sha256(nonce+mask).digest()[:16],
}

def transform(x,mode):
 words=[x[i:i+4] for i in range(0,16,4)]
 if mode&1:words=[w[::-1] for w in words]
 if mode&2:words=words[::-1]
 return b''.join(words)
def xor(a,b):return bytes(x^y for x,y in zip(a,b))
def labels(n):
 job=f'PS-261003-{300+n:04d}'
 return [job,f'{300+n:04d}',str(300+n),f'N{n:02d}',str(n),f'{n:02d}',
         f'H17|{job}',f'IR-261003-H17|{job}',f'H17-IR-261003|{job}',
         f'K08|{job}',f'K08|N{n:02d}',f'K08|{n:02d}']
def prf(key,msg,method):
 if method=='sha256-key-message':return hashlib.sha256(key+msg).digest()[:16]
 if method=='sha256-message-key':return hashlib.sha256(msg+key).digest()[:16]
 if method=='hmac-sha256':return hmac.digest(key,msg,'sha256')[:16]
 if method=='blake2s-keyed':return hashlib.blake2s(msg,key=key).digest()[:16]
 raise AssertionError(method)
METHODS=['sha256-key-message','sha256-message-key','hmac-sha256','blake2s-keyed']

def predicted(n,cohort,calibrator,method,key,label_variant,note_view,packet_view):
 def pad(j):return prf(key,labels(j)[label_variant].encode('ascii'),method)
 h0,p0=cohort[calibrator]
 const=xor(xor(transform(h0,note_view),transform(p0,packet_view)),pad(calibrator))
 h,p=cohort[n]
 return transform(xor(xor(transform(p,packet_view),pad(n)),const),note_view)

def synthetic_control():
 key=keys['nonce']
 method='hmac-sha256'
 variant=4
 note_view=2
 packet_view=1
 const=bytes.fromhex('17D57342BB84AD502509B4C739411AA2')
 def pad(n):return prf(key,labels(n)[variant].encode('ascii'),method)
 def forward(h,n):return transform(xor(xor(transform(h,note_view),pad(n)),const),packet_view)
 synthetic={n:(source[n][0],forward(source[n][0],n)) for n in selected_names}
 for baseline in selected_names:
  for j in selected_names:
   assert predicted(j,synthetic,baseline,method,key,variant,note_view,packet_view)==source[j][0]
 planted=note_hash('by the window everyone saved a chair for the next watch')
 synthetic[23]=(planted,forward(planted,23))
 decoded=predicted(23,synthetic,17,method,key,variant,note_view,packet_view)
 assert decoded==planted
 print('SYNTHETIC_NONLINEAR_PRF_FULL_SOURCE_AND_BLIND_FINAL_PASS 5/5 calibrators')

synthetic_control()
checked=0
survived=[]
partial=[]
for method,key_name,label_variant,note_view,packet_view in itertools.product(
 METHODS,keys,range(12),range(4),range(4)):
 key=keys[key_name]
 for calibrator in selected_names:
  held=[j for j in selected_names if j!=calibrator]
  correct=sum(predicted(j,source,calibrator,method,key,label_variant,note_view,packet_view)==source[j][0] for j in held)
  checked+=len(held)
  if correct>0:partial.append((method,key_name,label_variant,note_view,packet_view,calibrator,correct))
  if correct==len(held):
   candidate=predicted(23,{**source,23:(b'',spool[323])},calibrator,method,key,label_variant,note_view,packet_view)
   digest=hashlib.sha256(candidate).hexdigest()
   survived.append((method,key_name,label_variant,note_view,packet_view,calibrator,candidate.hex().upper(),digest==acceptance['slot_sha256']['K08']))
print('ORIGINAL_MODELS',len(METHODS),len(keys),'labels=12 note_views=4 packet_views=4 calibrators=5')
print('ORIGINAL_HELDOUT_WHOLE_128BIT_COMPARISONS',checked)
print('PARTIAL_HELDOUT_HITS',partial)
print('FULL_PREDICTIONS',survived)
