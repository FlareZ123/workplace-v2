"""Hypothetical complete K04 coupon producer from AX-7782 cyclic CRC16.

Run only on a local original resources extraction. Source checkpoint values,
receipt bytes and original commitment/candidate values are never logged.
The generator polynomial and printer/transfer coupling are hypotheses, not
historical facts. Source-independent synthetic 128-bit controls are mandatory.
"""
import argparse,json,hashlib,itertools,random,time,sys,os
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source_root',type=Path,help='local extracted evidence root')
parser.add_argument('--poly-start',type=int,default=1)
parser.add_argument('--poly-end',type=int,default=65536)
parser.add_argument('--local-hit-output',type=Path,default=None)
args=parser.parse_args()
if os.getenv('GITHUB_ACTIONS')=='true':
 raise SystemExit('Source-bearing original checks must run locally, not in public CI')
if not 1<=args.poly_start<=args.poly_end<=65536:
 raise SystemExit('Invalid polynomial interval')
R=args.source_root
# Pin the untouched preservation extract before accepting a historical no-hit.
PINS={
 'evidence/transfers/transfer-audit.jsonl':'32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf',
 'evidence/recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
 'acceptance.json':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f',
}
for rel,want in PINS.items():
 if hashlib.sha256((R/rel).read_bytes()).hexdigest()!=want:
  raise SystemExit('Local source integrity mismatch: '+rel)
L=[json.loads(x) for x in (R/'evidence/transfers/transfer-audit.jsonl').read_text().splitlines()]
rows={}
for o in L:
 if o.get('kind')=='CHUNK' and o.get('transfer')=='AX-7782' and (o['seq'] not in rows or o['attempt']>rows[o['seq']]['attempt']):rows[o['seq']]=o
assert len(rows)==8 and list(sorted(rows))==list(range(8))
source_ck=[bytes.fromhex(rows[i]['checkpoint']) for i in range(8)]
route=json.loads((R/'evidence/recovery-routing.json').read_text())
mask=bytes.fromhex(route['K04']['masked_component'])
target=bytes.fromhex(json.loads((R/'acceptance.json').read_text())['slot_sha256']['K04'])

def mul_mod(a,b,poly):
 # 16-bit polynomial multiplication and modular reduction.
 prod=0
 while b:
  if b&1:prod^=a
  a<<=1;b>>=1
 mod=0x10000|poly
 for i in range(prod.bit_length()-1,15,-1):
  if (prod>>i)&1:prod ^= mod<<(i-16)
 return prod

def pow_mod(a,ex,poly):
 x=1
 while ex:
  if ex&1:x=mul_mod(x,a,poly)
  ex>>=1
  if ex:a=mul_mod(a,a,poly)
 return x

def inv_mod(a,poly):
 u=a;v=0x10000|poly;g1=1;g2=0
 if u==0:return None
 while u!=1:
  if u==0:return None
  d=u.bit_length()-v.bit_length()
  if d<0:u,v=v,u;g1,g2=g2,g1;d=-d
  u ^= v<<d;g1 ^= g2<<d
 return mul_mod(g1,1,poly)

def crc(data,poly,init=0):
 c=init
 for val in data:
  c ^= val<<8
  for _ in range(8):c=((c<<1)^(poly if c&0x8000 else 0))&0xffff
 return c

def derive(checkpoints,poly,init=0,xorout=0):
 x128=pow_mod(2,128,poly)
 invQ=inv_mod(1^x128,poly)
 invX16=inv_mod(poly,poly)
 if invQ is None or invX16 is None:return None
 salt=crc(bytes(16),poly,init)^xorout
 c=[v^salt for v in checkpoints]
 B=[]
 for i in range(8):
  # C_{i+1} xor update_2_zero_bytes(C_i) = (1+Z^8) * CRC16(B_i).
  zero2=crc(bytes(2),poly,c[i]);q=c[(i+1)%8]^zero2
  D=mul_mod(q,invQ,poly)
  word=mul_mod(D,invX16,poly)
  B.append(word)
 P=b''.join(word.to_bytes(2,'big') for word in B)
 # It must replay both full CRC16 words and their byte position schedule.
 for i in range(8):
  part=P[2*i:]+P[:2*i]
  if crc(part,poly,init)^xorout != checkpoints[i]:
   raise AssertionError(('invalid formula',hex(poly),i))
 return P

# independent all-forward planted output inversion at nontrivial CRC polynomials
rng=random.Random(20261128)
for poly in (0xc867,0x8bb7,0x5935,0x1023,0x0003,0xfff9):
 P=rng.randbytes(16)
 for init in (0,0xffff):
  for xorout in (0,0xffff):
   cs=[crc(P[2*i:]+P[:2*i],poly,init)^xorout for i in range(8)]
   assert derive(cs,poly,init,xorout)==P
print('synthetic exact 128-bit inversion controls: 24/24 PASS',flush=True)

stats={'polys_tested':0,'model_reductions':0,'distinct_sha_checks':0,'original_matches':0,'collisions':0}
seen=set(); start=time.monotonic()
for poly in range(args.poly_start|1,args.poly_end,2):
 if poly.bit_count()&1:continue  # p(x) must be coprime with (x+1)^128
 stats['polys_tested']+=1
 for source_endian,source_direction,init,xorout in itertools.product((0,1),(0,1),(0,65535),(0,65535)):
  chunks=[(c[::-1] if source_endian else c) for c in source_ck]
  c=[int.from_bytes(chunk,'big') for chunk in chunks]
  if source_direction: c=[c[(-i)%8] for i in range(8)]
  base=derive(c,poly,init,xorout)
  stats['model_reductions']+=1
  assert base is not None
  for output_reverse,offset in itertools.product((False,True),range(8)):
   P=base[2*offset:]+base[:2*offset]
   if output_reverse:P=P[::-1]
   if P in seen:stats['collisions']+=1;continue
   seen.add(P)
   stats['distinct_sha_checks']+=1
   component=bytes(x^y for x,y in zip(P,mask))
   if hashlib.sha256(component).digest()==target:
    stats['original_matches']+=1
    if args.local_hit_output is not None:
     args.local_hit_output.write_text(component.hex().upper()+'\n')
    print('AUTHENTIC K04 HIT (value suppressed from stdout)',flush=True)
 if stats['polys_tested']%2048==0:
  print('progress polynomials',stats['polys_tested'],'seconds',round(time.monotonic()-start,1),flush=True)
print('RESULT',stats,'elapsed_s',round(time.monotonic()-start,2))
