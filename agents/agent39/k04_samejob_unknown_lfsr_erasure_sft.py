#!/usr/bin/env python3
"""Selected-job K04 middle-coupon recovery under unknown <=64-tap binary LFSR.
Source-heldout, source-safe; neither candidate, inferred feedback nor source bytes printed.
"""
from __future__ import annotations
import argparse,hashlib,json,re,random
from pathlib import Path

PIN='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'

def bits_from(buf,revbyte,lsb):
 if revbyte:buf=buf[::-1]
 return [(b>>(i if lsb else (7-i)))&1 for b in buf for i in range(8)]

def bytes_from(bits,revbyte,lsb):
 by=bytes(sum(bits[j*8+i]<<(i if lsb else 7-i) for i in range(8)) for j in range(len(bits)//8))
 return by[::-1] if revbyte else by

def bm(bits):
 n=len(bits);c=[1]+[0]*n;b=[1]+[0]*n;L=0;m=1
 for N in range(n):
  delta=bits[N]
  for i in range(1,L+1):delta^=c[i]&bits[N-i]
  if delta:
   t=c[:]
   for j in range(n-m+1):c[m+j]^=b[j]
   if 2*L<=N:L=N+1-L;b=t;m=1
   else:m+=1
  else:m+=1
 return L,c[:L+1]

def feedback_rank(observed,L):
 basis={}
 for i in range(L,len(observed)):
  v=sum(observed[i-j]<<(j-1) for j in range(1,L+1))
  while v:
   p=v.bit_length()-1
   if p in basis:v^=basis[p]
   else:basis[p]=v;break
 return len(basis)

def predict(observed,L,c,extra=256):
 out=list(observed)
 for k in range(extra):
  value=0
  for j in range(1,L+1):value^=c[j]&out[-j]
  out.append(value)
 return out

def synthetic():
 rng=random.Random(20261128)
 cases=0
 for revbyte in (False,True):
  for lsb in (False,True):
   for L,train_len in ((31,128),(47,128),(63,128),(65,256),(95,256),(127,256)):
    # Ensure true linear complexity of seeded 384-bit test is exactly L.
    while True:
     c=[1]+[rng.randrange(2) for _ in range(L-1)]+[1]
     s=[rng.randrange(2) for _ in range(L)]
     stream=predict(s,L,c,train_len+256-L)
     found,cf=bm(stream[:train_len])
     if found==L:break
    original=bytes_from(stream[:train_len],revbyte,lsb)
    later=bytes_from(stream[train_len+128:train_len+256],revbyte,lsb)
    firstbits=bits_from(original,revbyte,lsb)
    count,coeff=bm(firstbits)
    recovered=predict(firstbits,count,coeff)
    assert count==L and feedback_rank(firstbits,L)==L
    assert recovered[train_len:train_len+128]==stream[train_len:train_len+128]
    assert bytes_from(recovered[train_len+128:train_len+256],revbyte,lsb)==later
    cases+=1
 print('SYNTHETIC planted-middle+independent-REQUESTED3-packet 24/24 PASS')

def original(root):
 source=(root/'evidence/print/spool-reconstruction.log').read_bytes()
 assert hashlib.sha256(source).hexdigest()==PIN
 rows=[]
 for line in source.decode().splitlines()[1:]:
  kv=dict(re.findall(r'([A-Z]+)=([^ ]+)',line))
  rows.append(kv)
 assert len(rows)==133
 label=rows[117]
 a,b,c=rows[128:131]
 assert label['JOB']=='PS-261003-0417' and label['STATE']=='ACK' and label['CLASS']=='LABEL'
 assert a['JOB']==b['JOB']==c['JOB']=='PS-261003-0417'
 assert [q['ATTEMPT'] for q in (a,b,c)]==['1','2','3']
 assert [q['STATE'] for q in (a,b,c)]==['REQUESTED','ACK','REQUESTED']
 assert all(q['CLASS']=='RECOVER' for q in (a,b,c))
 route=json.loads((root/'evidence/recovery-routing.json').read_text())
 acc=json.loads((root/'acceptance.json').read_text())
 mask=bytes.fromhex(route['K04']['masked_component']);target=acc['slot_sha256']['K04']
 first=bytes.fromhex(a['PAYLOAD']);late=bytes.fromhex(c['PAYLOAD']);firstlabel=bytes.fromhex(label['PAYLOAD'])
 assert len(firstlabel)==len(first)==len(late)==len(mask)==16
 results=[]
 for training in ('request1_128bits','label_then_request1_256bits'):
  for rb in (False,True):
   for lsb in (False,True):
    prefix=(bits_from(firstlabel,rb,lsb) if training.startswith('label') else [])+bits_from(first,rb,lsb)
    n=len(prefix)
    L,coef=bm(prefix)
    assert L<=n//2 and feedback_rank(prefix,L)==L, 'non-unique short feedback map'
    recovered=predict(prefix,L,coef)
    mid=bytes_from(recovered[n:n+128],rb,lsb)
    follow=bytes_from(recovered[n+128:n+256],rb,lsb)
    comp=bytes(x^y for x,y in zip(mid,mask))
    results.append((training,int(rb),int(lsb),L,int(follow==late),sum((x^y).bit_count() for x,y in zip(follow,late)),int(hashlib.sha256(comp).hexdigest()==target)))
 print('ORIGINAL training,reversible_byte_order,bit_order_lsb,BM_degree,REQUESTED3_full_match,REQUESTED3_bit_differences,K04_original_hit')
 for r in results:print('ORIGINAL',*r,sep='\t')
 assert len(results)==8
 return results

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]/'resources')
 args=parser.parse_args()
 synthetic();original(args.root)