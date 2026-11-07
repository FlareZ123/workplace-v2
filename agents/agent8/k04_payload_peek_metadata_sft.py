"""Original H17 printer source-only direct payload-peek CATEGORY issuer test.

Tests whether printer CLASS/DEST derive deterministically from payload itself,
without consuming unknown interjob generator draws. Candidate functions and
96/36 source-only calibration split are fixed before any target use.
No selected 18:02 payload, K04 digest or mask is used. Standard library only.
"""
import collections
import hashlib
import itertools
import random
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
CATEGORIES = {'CLASS': ('LABEL', 'STORES', 'RECOVER'), 'DEST': ('bench', 'desk', 'store')}
TRAIN = 96


def untemper(x):
    for k,left,mask in ((18,False,0xffffffff),(15,True,0xefc60000),
                         (7,True,0x9d2c5680),(11,False,0xffffffff)):
        y=x
        for _ in range(6):
            y=x^(((y<<k)&mask) if left else (y>>k))
        x=y&0xffffffff
    return x


def source():
    data=(ROOT/'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(data).hexdigest()==SPOOL_SHA
    pattern=re.compile(r'^\S+ JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)$')
    raw=[]
    for line in data.decode().splitlines():
        m=pattern.fullmatch(line)
        if m:
            job,attempt,state,cls,payload,dest=m.groups()
            raw.append((job,int(attempt),state,cls,bytes.fromhex(payload),dest))
    assert len(raw)==133
    assert raw[129][:4]==('PS-261003-0417',2,'ACK','RECOVER')
    assert len(raw[129][4])==16
    original=[r for i,r in enumerate(raw) if i!=129]
    assert len(original)==132
    assert all(r[2]=='ACK' and r[1]==1 for r in original[:128])
    return original


def features(packet):
    """Finite, named deterministic candidate source-to-category functions."""
    out={}
    crc=zlib.crc32(packet)
    adler=zlib.adler32(packet)
    hashes={'crc':crc,'adler':adler}
    for algo in ('md5','sha1','sha256','sha512','sha3_256','blake2s','blake2b'):
        digest=hashlib.new(algo,packet).digest()
        for i in (0,1,2,3,len(digest)-4,len(digest)-3,len(digest)-2,len(digest)-1):
            out[f'{algo}:byte{i}:mod3']=digest[i]%3
        hashes[algo+':headbe']=int.from_bytes(digest[:4],'big')
        hashes[algo+':headle']=int.from_bytes(digest[:4],'little')
        hashes[algo+':tailbe']=int.from_bytes(digest[-4:],'big')
        hashes[algo+':taille']=int.from_bytes(digest[-4:],'little')
    for key,num in hashes.items():
        out[f'{key}:mod3']=num%3
        out[f'{key}:popcount3']=num.bit_count()%3
        out[f'{key}:top2mod3']=((num>>max(0,num.bit_length()-2))&3)%3
    for key,num in hashes.items():
        out[f'{key}:jointmod9']=num%9
    out['bytes:sum9']=sum(packet)%9
    out['bytes:sum3']=sum(packet)%3
    out['bytes:xor3']=__import__('functools').reduce(lambda a,b:a^b,packet,0)%3
    for byte in range(16):
        b=packet[byte]
        out[f'byte{byte}:jointmod9']=b%9
        for name,v in (('raw',b),('bitrev',int(f'{b:08b}'[::-1],2)),
                       ('low4',b&15),('high4',b>>4)):
            out[f'byte{byte}:{name}:mod3']=v%3
            out[f'byte{byte}:{name}:popcount3']=v.bit_count()%3
    for order in ('little','big'):
        for i in range(4):
            word=int.from_bytes(packet[4*i:4*i+4],order)
            for view,x in (('tempered',word),('native',untemper(word))):
                out[f'{order}:w{i}:{view}:jointmod9']=x%9
                out[f'{order}:w{i}:{view}:top8jointmod9']=(x>>24)%9
                for name,v in (('word',x),('top16',x>>16),('low16',x&65535),
                               ('top8',x>>24),('low8',x&255),('top2',x>>30),
                               ('low2',x&3)):
                    out[f'{order}:w{i}:{view}:{name}:mod3']=v%3
                    out[f'{order}:w{i}:{view}:{name}:popcount3']=v.bit_count()%3
    return out


def score(codes,labels,first,stop):
    best=(-1,None)
    for perm in itertools.permutations(range(3)):
        match=sum(perm[codes[i]]==labels[i] for i in range(first,stop))
        if match>best[0]:best=(match,perm)
    return best


def check_planted(feature_rows):
    chosen=list(feature_rows)[17]
    values=feature_rows[chosen]
    synthetic=[(v+1)%3 for v in values]
    train,perm=score(values,synthetic,0,TRAIN)
    assert train==TRAIN and all(perm[values[i]]==synthetic[i] for i in range(TRAIN,len(synthetic)))
    return chosen


def main():
    rows=source()
    label_indices={name:[CATEGORIES[name].index(row[3 if name=='CLASS' else 5]) for row in rows]
                   for name in CATEGORIES}
    features_by_row=[features(row[4]) for row in rows]
    spec=tuple(features_by_row[0])
    assert all(tuple(x)==spec for x in features_by_row)
    col={name:tuple(f[name] for f in features_by_row) for name in spec}
    planted=check_planted(col)
    print('SOURCE_PIN_PASS',len(rows),'source_rows',len(spec),'finite_peek_features',
          'training_rows',TRAIN,'untouched_holdout',len(rows)-TRAIN,'synthetic_positive',planted)
    for field,labels in label_indices.items():
        scored=[]
        for name,values in col.items():
            if "jointmod9" in name or name.endswith("sum9"):
                continue
            train,perm=score(values,labels,0,TRAIN)
            holdout=sum(perm[values[i]]==labels[i] for i in range(TRAIN,len(rows)))
            scored.append((train,holdout,name,perm))
        print(field,'TOP_FULL_CALIBRATION',sorted(scored,reverse=True)[:10])
        print(field,'ALL_TRAIN_PERFECT',sum(x[0]==TRAIN for x in scored))
        print(field,'ALL_36_HOLDOUT_PERFECT',sum(x[1]==len(rows)-TRAIN for x in scored))
        print(field,'TRAIN_MAX',max(x[0] for x in scored),'HOLDOUT_MAX_ANY',max(x[1] for x in scored))
        if max(x[0] for x in scored)==TRAIN:
            print('SOURCE_WITNESS',field,[x for x in scored if x[0]==TRAIN])
    pairs=[(a,b) for a,b in zip(label_indices['CLASS'],label_indices['DEST'])]
    controls=[]
    for name,values in col.items():
        if 'jointmod9' not in name:
            continue
        codebook={code:collections.Counter(pairs[i] for i in range(TRAIN)
                                          if values[i]==code).most_common(1)[0][0]
                  for code in set(values[:TRAIN])}
        train=sum(codebook[values[i]]==pairs[i] for i in range(TRAIN))
        hold=sum(codebook.get(values[i])==pairs[i] for i in range(TRAIN,len(rows)))
        controls.append((train,hold,name))
    assert controls
    print('JOINT_PAIR_ANY_9CODE_MAPPING',len(controls),'best_training_96',
          max(x[0] for x in controls),'best_holdout_36',max(x[1] for x in controls),
          'top',sorted(controls,reverse=True)[:10])
    assert all(x[0]<TRAIN for x in controls)
    print('NO_ORIGINAL_SELECTED_COUPON_OR_COMMITMENT_READ')

if __name__=='__main__': main()
