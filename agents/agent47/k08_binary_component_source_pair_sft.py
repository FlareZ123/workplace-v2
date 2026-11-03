"""H-17 exploratory K08 full-component binary-source bypass SFT.
Construct 16-byte K08 components from 16-byte archival carrier pairs using
nine finite rules, rather than assuming exact terminal caption wording.
Original selected PS-261003-0417 ACK2 is excluded. The model is speculative.
The original verifier, source files, candidate and commitments stay untouched.
Source-carrier construction adapts Agent22's original 532-carrier reproducible
source builder; no source-indexed historical K08 binary producer is claimed.
Run from a full workplace-v2 checkout with Python standard library only.
"""
import hashlib, hmac, itertools, json, re, struct, collections, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Resources:
 def __init__(self,root):self.root=root
 def namelist(self):
  return [(Path(root)/name).relative_to(self.root).as_posix()
          for root,_,names in os.walk(self.root,followlinks=True) for name in names]
 def read(self,name):return (self.root/name).read_bytes()
z=Resources(ROOT/'resources')
assert hashlib.sha256(z.read('evidence/print/spool-reconstruction.log')).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
src={}
def add(label,b):
 if len(b)==16:src.setdefault(b,label)
for name in z.namelist():
 if name.endswith('/') or name in ('acceptance.json','verify.py','candidate.template.json'):continue
 data=z.read(name)
 if name=='evidence/print/spool-reconstruction.log':
  data=b'\n'.join(line for line in data.splitlines() if not (b'JOB=PS-261003-0417' in line and b'ATTEMPT=2 STATE=ACK' in line))
 for m in re.finditer(rb'(?<![0-9A-Fa-f])([0-9A-Fa-f]{32})(?![0-9A-Fa-f])',data):
  add(f'HEX32:{name}:{m.start()}',bytes.fromhex(m.group(1).decode()))
tr=z.read('evidence/recorder/trip-recorder.raw')
controls=[];recs=[]
for i in range(88):
 rec=tr[16+i*24:16+(i+1)*24]
 _,node,ev,latch,seq,control,aux,crc=struct.unpack('<IHBBI4sII',rec)
 controls.append(control);recs.append((node,ev,latch,seq,control))
for i in range(85):add(f'TRP2:physical:{i}',b''.join(controls[i:i+4]))
rr=sorted(recs,key=lambda x:(x[0],x[1],x[3],x[2]))
for i in range(85):add(f'TRP2:sorted:{i}',b''.join(x[4] for x in rr[i:i+4]))
for node,ev in sorted(set((x[0],x[1]) for x in recs)):
 group=sorted((x for x in recs if (x[0],x[1])==(node,ev)),key=lambda x:x[3])
 for i in range(len(group)-3):add(f'TRP2:node{node}ev{ev}:{i}',b''.join(x[4] for x in group[i:i+4]))
trans=[json.loads(l) for l in z.read('evidence/transfers/transfer-audit.jsonl').splitlines()]
for name in ['AX-7778','AX-7781','AX-7782','AX-7783']:
 rows=sorted([x for x in trans if x['kind']=='CHUNK' and x['transfer']==name],key=lambda x:(x['seq'],x['attempt']))
 cp=[bytes.fromhex(x['checkpoint']) for x in rows]
 for i in range(len(cp)-7):add(f'{name}:sorted8:{i}',b''.join(cp[i:i+8]))
 for attempt in (1,2):add(f'{name}:attempt{attempt}',b''.join(bytes.fromhex(x['checkpoint']) for x in rows if x['attempt']==attempt))
 vals=[bytes.fromhex(max((x for x in rows if x['seq']==j),key=lambda x:x['attempt'])['checkpoint']) for j in range(8)]
 add(f'{name}:greatest',b''.join(vals))
pages=z.read('evidence/procedures/RC-17-scans.txt').decode().split('\f')
foot=[]
for p in pages:
 m=re.search(r'Footer control strip:\s*([0-9A-F]{8})',p)
 if m:
  rev=re.search(r'DOCUMENT RC-17 / REV ([^/]+) / SECTION ([^\n]+)',p)
  foot.append((rev.group(1).strip(),rev.group(2).strip(),bytes.fromhex(m[1])))
for i in range(len(foot)-3):add(f'RC17:scan:{i}',b''.join(x[2] for x in foot[i:i+4]))
for rev in sorted(set(t[0] for t in foot)):
 g={section:b for r,section,b in foot if r==rev}
 if len(g)==4:
  add(f'RC17:{rev}:service',b''.join(g[k] for k in ['DRAIN','ISOLATE','PURGE','VERIFY']))
  add(f'RC17:{rev}:alphabet',b''.join(g[k] for k in sorted(g)))
tele=[json.loads(l) for l in z.read('evidence/telemetry/freeze-export.jsonl').splitlines()]
for key,sub in {'ALL':[x for x in tele if x.get('field')=='DIAG_WORD'],
                'LT204':[x for x in tele if x.get('tag')=='LT-204' and x.get('field')=='DIAG_WORD'],
                'GOODHOLD':[x for x in tele if x.get('tag')=='LT-204' and x.get('field')=='DIAG_WORD' and x.get('quality')=='GOOD' and x.get('state')=='HOLD']}.items():
 for order,arr in [('source',sub),('seq',sorted(sub,key=lambda x:(x['seq'],x['revision']))),
                   ('time',sorted(sub,key=lambda x:x['ts']))]:
  words=[int(x['value']).to_bytes(2,'big') for x in arr if isinstance(x.get('value'),int) and 0<=x['value']<=65535]
  for i in range(len(words)-7):add(f'TELEMETRY:{key}:{order}:{i}',b''.join(words[i:i+8]))
seals=[json.loads(l) for l in z.read('evidence/maintenance/seal-receipts.jsonl').splitlines()]
ss=[(x['permit'],x['bay'],x['serial'].split('-')[-1]) for x in seals]
for i in range(len(ss)-3):add(f'SEAL:source:{i}',b''.join(bytes.fromhex(x[2]) for x in ss[i:i+4]))
for permit in sorted(set(x[0] for x in ss)):
 vals=sorted((x for x in ss if x[0]==permit),key=lambda x:x[1])
 for i in range(len(vals)-3):add(f'SEAL:{permit}:{i}',b''.join(bytes.fromhex(x[2]) for x in vals[i:i+4]))
for k,h in {'K01':'049AAB2E1CDE7A82CD7C60234303C91A','K02':'0D7E3AB56FB75DA3EB0E2E06786D239E',
            'K03':'1384AF96E25D6ADA666209CB55E062FA','K05':'FF8B78200A56E8586DCDA00EF01E4572',
            'K06':'5DBF40EE52FAAED9A536D3326CF0D95A','K07':'93495F5E425AB8E592123DABAEB68545'}.items():
 add('DERIVED:'+k,bytes.fromhex(h))
for k,v in {'K02_PREHASH':'E1A5E474BAD7E853A2E8C71D3317D507','K03_PREHASH':'D7DAD6BC9714519B7DAD0AD4BE8E87FD','K07_PREHASH':'8947CEDCB9CC73BAB7E87BE63302C5C9'}.items():add('PREHASH:'+k,bytes.fromhex(v))
assert bytes.fromhex('A9A9DC5731A5E2AE879C47215C2559D5') not in src
assert len(src)>=500,len(src)



ROUTE=json.loads((ROOT/'resources/evidence/recovery-routing.json').read_text())
NONCE=bytes.fromhex(ROUTE['K08']['desk_nonce'])
NOTES=(ROOT/'resources/evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
assert hashlib.sha256(NOTES).hexdigest()=='13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
KNOWN={
  'N02':'A good watch leaves the room ready for the next pair of hands.',
  'N06':'The little lamp stays on until the corridor has gone quiet.',
  'N17':'Leave the light on for the next watch.',
  'N18':'Back before the first boat.',
}
def norm(s):
 return ' '.join(re.sub(r'[^a-z0-9\s]',' ',s.lower()).split())
for k,line in KNOWN.items():add('EMILY_HMAC_'+k,hmac.digest(NONCE,norm(line).encode(),'sha256')[:16])
assert hmac.digest(NONCE,norm(KNOWN['N02']).encode(),'sha256')[:16].hex().upper()=='BF889359B0303F2B2B2FD96AE841210B'
assert bytes.fromhex('A9A9DC5731A5E2AE879C47215C2559D5') not in src
vals=list(src.items())
def sha(x):return hashlib.sha256(x).digest()
def xor(a,b):return bytes(i^j for i,j in zip(a,b))
def add128(a,b):
 return ((int.from_bytes(a,'big')+int.from_bytes(b,'big'))&((1<<128)-1)).to_bytes(16,'big')
def sub128(a,b):
 return ((int.from_bytes(a,'big')-int.from_bytes(b,'big'))&((1<<128)-1)).to_bytes(16,'big')
def variants(a,b):
 x=xor(a,b)
 return {
  'xor':x,'sum128':add128(a,b),'sub128_ab':sub128(a,b),
  'sub128_ba':sub128(b,a),'sha_xor_first16':sha(x)[:16],
  'sha_concat_ab_first16':sha(a+b)[:16],
  'sha_concat_ba_first16':sha(b+a)[:16],
  'hmac_nonce_concat_ab_first16':hmac.digest(NONCE,a+b,'sha256')[:16],
  'hmac_nonce_concat_ba_first16':hmac.digest(NONCE,b+a,'sha256')[:16],
 }
target=bytes.fromhex(json.loads((ROOT/'resources/acceptance.json').read_text())['slot_sha256']['K08'])
planted=xor(vals[0][0],vals[1][0])
assert planted not in (vals[0][0],vals[1][0])
planted_digest=sha(planted)
real=[];control=[]
counts=collections.Counter()
for i,(a,alabel) in enumerate(vals):
 for b,blabel in vals[i:]:
  for method,c in variants(a,b).items():
   counts[method]+=1
   if sha(c)==target:real.append((alabel,blabel,method,c.hex()))
   if sha(c)==planted_digest:control.append((alabel,blabel,method,c.hex()))
assert sum(counts.values())==9*(len(vals)*(len(vals)+1)//2)
assert len(control)>=1 and any(x[2]=='xor' and x[3]==planted.hex() for x in control)
print(json.dumps({'source_fields':len(vals),'complete_component_checks':sum(counts.values()),'method_counts':counts,
 'original_K08_matches':real,'planted_control_hits':len(control)},indent=2))
