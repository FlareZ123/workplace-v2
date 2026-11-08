"""H-17 K08: note-to-printer affine transport with whole-note holdouts.

Read-only source-pin single-file test. The note/job ID pairing is a hypothesis.
"""
from pathlib import Path
import hashlib,hmac,re,itertools

ROOT=Path(__file__).resolve().parents[2]/'resources'
NOTES=ROOT/'evidence/crew/noticeboard-and-desk-notes.txt'
SPOOL=ROOT/'evidence/print/spool-reconstruction.log'
ROUTE=ROOT/'evidence/recovery-routing.json'
ACCEPT=ROOT/'acceptance.json'
PIN={
 NOTES:'13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb',
 SPOOL:'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
 ROUTE:'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
 ACCEPT:'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f',
}
for file,hashval in PIN.items():
 assert hashlib.sha256(file.read_bytes()).hexdigest()==hashval,(file,hashval)
KEY=bytes.fromhex('5F933DA6A1BD03C32DA5CBC25344F497')
TARGET='285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747'
raw_notes=NOTES.read_text()
notes={int(k):text.strip() for k,text in re.findall(r'^N(\d\d) / Emily \[censored\]\n(.*?)(?=\n\n|\Z)',raw_notes,re.M|re.S)}
notes={k:(v.split(':',1)[1].strip() if ':' in v else v) for k,v in notes.items()}
raw=SPOOL.read_text().splitlines()
payload={int(j):bytes.fromhex(p) for j,p in [re.search(r'JOB=PS-261003-(\d\d\d\d).*?PAYLOAD=([A-F0-9]{32})',line).groups() for line in raw if 'JOB=' in line]}
names=[2,6,13,17,18]
N=1<<128

def norm(s): return ' '.join(re.sub('[^a-z0-9\\s]', ' ',s.lower()).split())
def hash16(s): return hmac.new(KEY,norm(s).encode(),hashlib.sha256).digest()[:16]
assert hash16(notes[18]).hex().upper()=='A3100AE1ABB9C8D58315D9EBF326978B'
source={n:(hash16(notes[n]),payload[300+n]) for n in names}

def view(bs,i):
 words=[bs[p:p+4] for p in range(0,16,4)]
 if i&1:words=[w[::-1] for w in words]
 if i&2:words=words[::-1]
 return b''.join(words)

def affine_base(vals,start,end,kind):
 def pad(i):
  hm,packet=vals[i]
  if kind.startswith('xor'): return int.from_bytes(bytes(a^b for a,b in zip(hm,packet)),'big')
  endian='big' if 'big' in kind else 'little'
  return (int.from_bytes(packet,endian)-int.from_bytes(hm,endian))%N
 a,b=pad(start),pad(end)
 if kind=='xor-parity':
  if (start&1)==(end&1):return None
  odd=a if start&1 else b
  even=b if start&1 else a
  return lambda j:odd if j&1 else even
 diff=end-start
 if diff&1==0:return None
 slope=((b-a)*pow(diff,-1,N))%N
 intercept=(a-slope*start)%N
 return lambda j:(intercept+slope*j)%N

def predict_hmac(packet,pad,kind):
 if kind.startswith('xor'):
  x=pad.to_bytes(16,'big')
  return bytes(a^b for a,b in zip(packet,x))
 endian='big' if 'big' in kind else 'little'
 return ((int.from_bytes(packet,endian)-pad)%N).to_bytes(16,endian)

def synthetic_controls():
    phrase='as the night ends the water keeps company with the late watch'
    expected=hash16(phrase)
    for v in range(4):
        for kind in ('xor-parity','add-big','add-little'):
            if kind=='xor-parity':
                pad=lambda j:0x112233445566778899AABBCCDDEEFF00 if j&1 else 0xAABBCCDDEEFF00112233445566778899
            else:
                pad=lambda j:(0x112233445566778899AABBCCDDEEFF00+j*0x102030405060708090A0B0C0D0E0F0F1)%N
            endian='big' if kind=='add-big' else 'little'
            def produce(hm,j):
                if kind=='xor-parity':
                    pp=pad(j).to_bytes(16,'big')
                    return bytes(a^b for a,b in zip(hm,pp))
                return ((int.from_bytes(hm,endian)+pad(j))%N).to_bytes(16,endian)
            simulated={j:(source[j][0],view(view(produce(source[j][0],j),v),v)) for j in names}
            fit=affine_base(simulated,17,18,kind)
            assert fit is not None
            for j in names:
                assert predict_hmac(simulated[j][1],fit(j),kind)==source[j][0],(v,kind,j)
            decoded=predict_hmac(produce(expected,23),fit(23),kind)
            assert decoded==expected,(v,kind)
    print('Genuine synthetic full-transport controls: 12/12 PASS')

synthetic_controls()
fits=[]; checks=0
for v in range(4):
 vals={j:(source[j][0],view(source[j][1],v)) for j in names}
 for kind in ['xor-parity','add-big','add-little']:
  for a,b in itertools.permutations(names,2):
   f=affine_base(vals,a,b,kind)
   if f is None:continue
   held=[k for k in names if k not in (a,b)]
   counts=sum(predict_hmac(vals[k][1],f(k),kind)==vals[k][0] for k in held)
   checks+=len(held)
   if counts>0:
    fits.append((v,kind,a,b,counts,held))
   if counts==len(held):
    candidate=predict_hmac(view(payload[323],v),f(23),kind)
    print('FULL_SOURCE_HOLDOUT',v,kind,a,b,'K08',candidate.hex().upper(),'hit',hashlib.sha256(candidate).hexdigest()==TARGET)
print('SOURCE_NOTES',names)
print('AUTHENTIC_WHOLE_CAPTION_HOLDOUT_CHECKS',checks)
print('PARTIAL_HOLDOUT_MATCHES',fits)
