"""All 532 surviving 16-byte carrier groups: exact seven-output MT donor sieve.

Run from a checkout with resources/: python agents/agent22/k04_all_original_future_donor_pairs_sft.py
The original selected attempt-2 ACK is excluded from candidate donor extraction.
"""
from __future__ import annotations
import hashlib,json,re,struct,collections,random,itertools,os
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('s',ROOT/'agents/agent22/k04_future_donor_source_syndrome_sft.py')
s=importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
class Resources:
 def __init__(self,root):self.root=root
 def namelist(self):
  return [(Path(root)/name).relative_to(self.root).as_posix()
          for root,_,names in os.walk(self.root,followlinks=True) for name in names]
 def read(self,name):return (self.root/name).read_bytes()
z=Resources(ROOT/'resources')
assert hashlib.sha256(z.read('evidence/print/spool-reconstruction.log')).hexdigest()==s.PINS['print/spool-reconstruction.log']
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
for k,b in s.groups().items():add('SELECTED:'+k,b)
assert bytes.fromhex('A9A9DC5731A5E2AE879C47215C2559D5') not in src
assert len(src)==532,len(src)
print('SOURCE_CARRIERS',len(src),flush=True)

x556,x557,x558=s.source_words()
source_opts={}
for b,label in src.items():
 for little,tempered,reverse in itertools.product((False,True),repeat=3):
  vs=tuple(s.decode(b,little,tempered,reverse,'all'))
  source_opts.setdefault(vs,[]).append((label,little,tempered,reverse))
assert len(source_opts)==4256,len(source_opts)
print('UNIQUE_4WORD_VIEWS',len(source_opts),flush=True)

# Right block: native donors 1347,1348,1574,1575. The source
# prefilter uses only X1575 XOR X1348, indexed in a constant-time hash.
blookup=collections.defaultdict(list)
for v,meta in source_opts.items():blookup[v[3]^v[1]].append((v,meta[0]))
hits=[]
for a,asrc in source_opts.items():
 for pick in ('first','last'):
  left=a[:3] if pick=='first' else a[1:]
  for h555,h951 in itertools.product((0,0x80000000),repeat=2):
   delta=s.twist(h951,left[0]^s.twist(h555,x556))
   for b,bsource in blookup.get(delta,[]):
    coupons=s.native_coupon(left+b,x556,x557,x558)
    if coupons:hits.append((left,b,h555,h951,asrc[0],bsource,len(coupons)))
assert len(source_opts)*len(source_opts)*2==36227072
assert hits==[],hits
print('SOURCE_PAIRS_TOTAL',len(source_opts)*len(source_opts)*2,
      'SOURCE_SYNDROME_SURVIVORS',len(hits),'COUPONS',sum(h[-1] for h in hits))

# Genuine nonzero cross-index controls from an independently seeded full stream.
rng=random.Random(1983)
native=[s.untemper(rng.getrandbits(32)) for _ in range(1580)]
donor=[native[i] for i in (1179,1180,1181,1347,1348,1574,1575)]
assert s.native_coupon(donor,*native[556:559])==[tuple(native[951:955])]
print('SYNTHETIC_SEVEN_DONOR_FULL_COUPON_PASS')
