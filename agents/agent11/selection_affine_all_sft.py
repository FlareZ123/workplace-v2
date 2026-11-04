"""Cross-domain source-selected affine holdout; read-only H-17 original ZIP SFT."""
from __future__ import annotations
import hashlib, itertools, json, re, struct, zipfile, zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ZIP=Path('/mnt/data/h17-archive-dump.zip')
M=(1<<128)-1

def read(path):
    direct=ROOT/'resources'/path
    if direct.exists():return direct.read_bytes()
    with zipfile.ZipFile(ZIP) as z:return z.read(path)

def recorder():
    raw=read('evidence/recorder/trip-recorder.raw')
    ver,size,n=struct.unpack('<HHI',raw[8:16])
    assert (ver,size)==(2,24) and len(raw)==16+n*24
    groups={k:{} for k in (200,300,900,990)}
    for k in range(n):
        r=raw[16+24*k:16+24*(k+1)]
        _,node,event,latch,seq=struct.unpack('<IHBBI',r[:12])
        if node!=49 or event!=82:continue
        for start,grp in groups.items():
            if start<=seq<start+4:
                assert latch==seq-start
                grp[latch]=(r[12:16],zlib.crc32(r[:20])==int.from_bytes(r[20:],'little'))
    assert all(len(g)==4 for g in groups.values())
    assert all(ok for grp in (groups[200],groups[300],groups[990]) for _,ok in grp.values())
    assert all(not ok for _,ok in groups[900].values())
    ans={f'seq{k}':b''.join(g[i][0] for i in range(4)) for k,g in groups.items()}
    assert ans['seq300'].hex().upper()=='FF8B78200A56E8586DCDA00EF01E4572'
    return ans

def procedures():
    txt=read('evidence/procedures/RC-17-scans.txt').decode()
    groups={}
    for chunk in txt.split('\f'):
        header=re.search(r'DOCUMENT RC-17 / REV ([^/]+) / SECTION (\w+)',chunk)
        if header:
            strip=re.search(r'Footer control strip: ([0-9A-F]{8})',chunk)
            groups.setdefault(header[1].strip(),{})[header[2]]=bytes.fromhex(strip[1])
    return {v:b''.join(d[p] for p in ('DRAIN','ISOLATE','PURGE','VERIFY')) for v,d in groups.items()}

def transfers():
    groups={}
    for line in read('evidence/transfers/transfer-audit.jsonl').decode().splitlines():
        j=json.loads(line)
        if j['kind']!='CHUNK':continue
        grp=groups.setdefault(j['transfer'],{})
        seq=j['seq'];a=j['attempt']
        if seq not in grp or a>grp[seq][0]:
            grp[seq]=(a,bytes.fromhex(j['checkpoint']))
    return {k:b''.join(d[i][1] for i in range(8)) for k,d in groups.items()}

def mul(a,b):
    result=0
    for _ in range(128):
        if b&1:result^=a
        b>>=1
        a=((a<<1)&M)^(0x87 if a>>127 else 0)
    return result

def inv(x):
    assert x
    exponent=(1<<128)-2
    result=1
    while exponent:
        if exponent&1:result=mul(result,x)
        x=mul(x,x);exponent>>=1
    return result

def view(b,v):
    if v&4:b=b[::-1]
    chunks=[b[i:i+4] for i in range(0,16,4)]
    if v&2:chunks.reverse()
    if v&1:chunks=[chunk[::-1] for chunk in chunks]
    return b''.join(chunks)

def modpredict(t,x,bits):
    m=1<<bits
    (a,b),(c,d)=t
    delta=(a-c)%m;out=(b-d)%m
    if not delta:return ()
    k=(delta&-delta).bit_length()-1
    if out%(1<<k) or k>8:return ()
    reduced=m>>k
    slope=(out>>k)*pow(delta>>k,-1,reduced)%reduced
    return tuple(((slope+j*reduced)*(x-a)+b)%m for j in range(1<<k))

def main():
    raw=read('evidence/print/spool-reconstruction.log')
    assert hashlib.sha256(raw).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
    r,p,t=recorder(),procedures(),transfers()
    selected={'K05':r['seq300'],'K06':p['C'],'K07':t['AX-7782']}
    other={
        'K05':{k:v for k,v in r.items() if k!='seq300'},
        'K06':{k:v for k,v in p.items() if k!='C'},
        'K07':{k:v for k,v in t.items() if k!='AX-7782'}
    }
    keys=list(other)
    counts=dict(gf128=0,mod128=0,per32=0,xor=0)
    hits=[]
    for choice in itertools.product(*(list(other[k]) for k in keys)):
        prior={k:other[k][c] for k,c in zip(keys,choice)}
        for v in range(8):
            history={k:(int.from_bytes(view(prior[k],v),'big'),int.from_bytes(view(selected[k],v),'big')) for k in keys}
            for held in keys:
                train=[history[k] for k in keys if k!=held]
                x,y=history[held]
                counts['xor']+=1
                if (x^(train[0][0]^train[0][1]))==y:hits.append(('xor',choice,v,held))
                dx=train[0][0]^train[1][0]
                if dx:
                    a=mul(train[0][1]^train[1][1],inv(dx))
                    b=train[0][1]^mul(a,train[0][0])
                    counts['gf128']+=1
                    if mul(a,x)^b==y:hits.append(('gf128',choice,v,held))
                for q in modpredict(train,x,128):
                    counts['mod128']+=1
                    if q==y:hits.append(('mod128',choice,v,held))
                lanes=[]
                for j in range(4):
                    shift=96-32*j
                    tt=[((a>>shift)&0xffffffff,(b>>shift)&0xffffffff) for a,b in train]
                    lanes.append(modpredict(tt,(x>>shift)&0xffffffff,32))
                for words in itertools.product(*lanes):
                    counts['per32']+=1
                    if sum(q<<(96-32*j) for j,q in enumerate(words))==y:
                        hits.append(('per32',choice,v,held))
    assert counts=={'gf128':432,'mod128':448,'per32':396,'xor':432} and not hits
    # Known planted affine transformation; train two old-source blocks, recover third full output.
    xx=[int.from_bytes(list(other[k].values())[0],'big') for k in keys]
    A=int('D53281E664A9FC5070D98A0B32EC142D',16)
    B=int('5C3F45A0E7D8B39241B628A986C5F013',16)
    yy=[mul(A,x)^B for x in xx]
    aa=mul(yy[0]^yy[1],inv(xx[0]^xx[1]))
    bb=yy[0]^mul(aa,xx[0])
    assert (aa,bb)==(A,B) and mul(aa,xx[2])^bb==yy[2]
    print('Source alternatives:',{k:list(v) for k,v in other.items()})
    print('Original complete holdout checks:',counts)
    print('Exact original selected predictions:',hits)
    print('Planted full 128-bit affine holdout: PASS')

if __name__=='__main__':main()
