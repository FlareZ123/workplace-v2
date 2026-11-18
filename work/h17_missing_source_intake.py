#!/usr/bin/env python3
from pathlib import Path
import hashlib, hmac, re, argparse

K04_MASK=bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
K08_NONCE=bytes.fromhex('5F933DA6A1BD03C32DA5CBC25344F497')
K04_COMMIT='930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
K08_COMMIT='285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747'

def norm(s):
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9\s]',' ',s.lower())).strip()

def sha(b): return hashlib.sha256(b).hexdigest()

def print_rows(p):
    try: text=p.read_text(errors='ignore')
    except Exception: return []
    out=[]
    for line in text.splitlines():
        if 'JOB=PS-261003-0417' not in line or 'PAYLOAD=' not in line: continue
        f={k:v for k,v in (tok.split('=',1) for tok in line.split() if '=' in tok)}
        try: attempt=int(f['ATTEMPT'])
        except (KeyError,ValueError): continue
        payload=f.get('PAYLOAD','')
        if re.fullmatch(r'[0-9A-Fa-f]{32}',payload): out.append((f.get('CLASS',''),attempt,f.get('STATE',f.get('STATUS','')),payload))
    return out

def k04(root):
    rows=[]
    for p in root.rglob('*'):
        if p.is_file() and ('0417' in p.name.upper() or p.name.lower() in {'spool-reconstruction.log','queue.log','queue.journal','queue-export.txt'}):
            rows += [(p,)+r for r in print_rows(p)]
    acks=[r for r in rows if r[3]=='ACK']
    print('K04 carriers:',len(rows),'ACKs:',len(acks))
    if not acks: return
    p,cls,attempt,state,payload=max(acks,key=lambda r:r[2])
    if cls and cls!='RECOVER':
        print('Last ACK is not RECOVER:',p,cls,attempt); return
    c=bytes(a^b for a,b in zip(bytes.fromhex(payload),K04_MASK))
    print('K04 last ACK:',p,'attempt',attempt,'payload',payload)
    print('component',c.hex().upper(),'commit',sha(c),'match',sha(c)==K04_COMMIT)

def k08(root):
    hits=[]; files=0
    for p in root.rglob('*'):
        if not p.is_file(): continue
        low=str(p).lower()
        if not any(x in low for x in ('wn-14','desk','caption','galley','noticeboard','crew')): continue
        try: words=re.findall(r'[a-z0-9]+',p.read_text(errors='ignore').lower())
        except Exception: continue
        files+=1
        for i in range(len(words)):
            s=''
            for n in range(1,min(64,len(words)-i)+1):
                s=words[i] if n==1 else s+' '+words[i+n-1]
                h=hmac.new(K08_NONCE,s.encode(),hashlib.sha256).digest()[:16]
                if sha(h)==K08_COMMIT: hits.append((p,s))
    print('K08 text carriers:',files,'contiguous commitment hits:',len(hits))
    for p,s in hits: print(p,repr(s))

ap=argparse.ArgumentParser(description='H-17 K04/K08 missing-source intake; implements only the route-sheet rules.')
ap.add_argument('root',type=Path)
a=ap.parse_args(); root=a.root.resolve()
if not root.is_dir(): ap.error('root must be a directory')
k04(root); k08(root)