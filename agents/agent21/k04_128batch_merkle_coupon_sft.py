"""Source-pinned K04 128-leaf binary Merkle-root producer test with late ACK holdouts.

Run: Python 3 k04_128batch_merkle_coupon_sft.py [path-to-evidence-directory]
Read-only original source and commitment check.
"""
from __future__ import annotations
import hashlib
import hmac
import itertools
import re
import sys
from pathlib import Path

ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources/evidence'
SPOOL=ROOT/'print/spool-reconstruction.log'
SPOOL_SHA='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK=bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
K04_SHA=bytes.fromhex('930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0')

def digest32(name:str,data:bytes)->bytes:
    return getattr(hashlib,name)(data).digest()[:32]

def original_records():
    source=SPOOL.read_bytes()
    assert hashlib.sha256(source).hexdigest()==SPOOL_SHA
    lines=[s for s in source.decode('ascii').splitlines() if 'PAYLOAD=' in s]
    assert len(lines)==133
    rows=[]
    for j in range(300,428):
        matches=[line for line in lines if f'JOB=PS-261003-{j:04d} ' in line and 'STATE=ACK' in line and 'ATTEMPT=1' in line]
        assert len(matches)==1
        line=matches[0]
        rows.append(dict(job=f'PS-261003-{j:04d}',body=line.encode('ascii'),
                        payload=bytes.fromhex(re.search(r'PAYLOAD=([A-F0-9]{32})',line).group(1)),
                        klass=re.search(r'CLASS=(\w+)',line).group(1),dest=re.search(r'DEST=(\w+)',line).group(1)))
    selected={}
    for job,attempt in [('0417',2),('0420',2),('0448',1)]:
        matches=[line for line in lines if f'JOB=PS-261003-{job} ' in line and f'ATTEMPT={attempt} ' in line and 'STATE=ACK' in line and 'CLASS=RECOVER' in line]
        assert len(matches)==1
        line=matches[0]
        selected[job]=dict(job=f'PS-261003-{job}',suffix=job,
                           payload=bytes.fromhex(re.search(r'PAYLOAD=([A-F0-9]{32})',line).group(1)),
                           timestamp=line.split()[0],
                           klass=re.search(r'CLASS=(\w+)',line).group(1),dest=re.search(r'DEST=(\w+)',line).group(1),attempt=attempt)
    assert selected['0417']['payload'].hex().upper()=='A9A9DC5731A5E2AE879C47215C2559D5'
    return rows,selected

def leaves(rows:list[dict],view:int)->list[bytes]:
    if view==0:return [r['payload'] for r in rows]
    if view==1:return [hashlib.sha256(r['payload']).digest() for r in rows]
    if view==2:return [hashlib.sha256(r['payload'].hex().upper().encode()).digest() for r in rows]
    if view==3:return [hashlib.sha256(r['job'].encode()+r['payload']).digest() for r in rows]
    if view==4:return [hashlib.sha256(r['payload']+r['job'].encode()).digest() for r in rows]
    return [hashlib.sha256(r['body']).digest() for r in rows]

def merkle(items:list[bytes],algorithm:str,flip:bool,prefix:bytes)->bytes:
    layer=items
    for _ in range(7):
        assert len(layer)%2==0
        nxt=[]
        for a,b in zip(layer[::2],layer[1::2]):
            nxt.append(digest32(algorithm,prefix+(b+a if flip else a+b)))
        layer=nxt
    assert len(layer)==1
    return layer[0]

def labels(r:dict)->tuple[bytes,...]:
    return (b'',r['job'].encode(),r['suffix'].encode(),r['timestamp'].encode(),
            f'{r["job"]}|RECOVER|ACK|{r["attempt"]}'.encode(),
            f'{r["job"]}|{r["klass"]}|{r["dest"]}'.encode())

def emit(root:bytes,label:bytes,mode:int)->bytes:
    if mode==0:return root
    if mode==1:return hashlib.sha256(root+label).digest()
    if mode==2:return hashlib.sha256(label+root).digest()
    if mode==3:return hmac.digest(root,label,'sha256')
    if mode==4:return hmac.digest(label,root,'sha256')
    return hashlib.sha256(root+hashlib.sha256(label).digest()).digest()

def run()->None:
    rows,selected=original_records()
    assert len(rows)==128
    plant_digest=None
    checks=real_hits=holdout_hits=plant_hits=0
    for sort in range(4):
        if sort==0:ordrows=rows
        elif sort==1:ordrows=list(reversed(rows))
        elif sort==2:ordrows=sorted(rows,key=lambda r:(r['klass'],r['job']))
        else:ordrows=sorted(rows,key=lambda r:(r['dest'],r['job']))
        for view,alg,flip,prefix in itertools.product(range(6),('sha256','sha3_256','blake2s','sha512'),
                                                    (False,True),(b'',b'\x00',b'\x01',b'H17')):
            root=merkle(leaves(ordrows,view),alg,flip,prefix)
            if (sort,view,alg,flip,prefix)==(0,0,'sha256',False,b'\x01'):
                planted=emit(root,selected['0417']['job'].encode(),1)[:16]
                plant_digest=hashlib.sha256(bytes(a^b for a,b in zip(planted,MASK))).digest()
            for job in ('0417','0420','0448'):
                target_record=selected[job]
                for lab,mode,end in itertools.product(labels(target_record),range(6),(False,True)):
                    output=emit(root,lab,mode)
                    coupon=output[-16:] if end else output[:16]
                    checks+=1
                    if job=='0417':
                        component=bytes(a^b for a,b in zip(coupon,MASK))
                        if hashlib.sha256(component).digest()==K04_SHA:
                            real_hits+=1;print('K04_ORIGINAL_HIT',sort,view,alg,flip,prefix,lab,mode,end,coupon.hex(),flush=True)
                        if plant_digest is not None and hashlib.sha256(component).digest()==plant_digest:
                            plant_hits+=1
                    elif coupon==target_record['payload']:
                        holdout_hits+=1;print('FULL_HOLDOUT_MATCH',job,sort,view,alg,flip,prefix,lab,mode,end,flush=True)
    assert checks==4*6*4*2*4*3*6*6*2
    assert plant_digest is not None
    assert plant_hits==2
    print(f'K04_MERKLE original={real_hits} holdout_full16={holdout_hits} planted={plant_hits} checks={checks}')

if __name__=='__main__':run()
