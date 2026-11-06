"""H17 selected K04: original late-five-event ring/GF(2^128) whole-coupon test."""
import hashlib, itertools, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPOOL=ROOT/'resources/evidence/print/spool-reconstruction.log'
SPOOL_SHA='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK=bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
TARGET='930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
MOD=1<<128
LAYOUTS=list(itertools.product(itertools.permutations(range(4)),(False,True),(False,True)))

def view(raw,perm,revword,revbit):
    w=[raw[i:i+4] for i in range(0,16,4)]
    raw=b''.join(w[i][::-1] if revword else w[i] for i in perm)
    if revbit:raw=bytes(int(f'{x:08b}'[::-1],2) for x in raw)
    return int.from_bytes(raw,'big')

def unview(x,perm,revword,revbit):
    raw=x.to_bytes(16,'big')
    if revbit:raw=bytes(int(f'{v:08b}'[::-1],2) for v in raw)
    w=[raw[i:i+4] for i in range(0,16,4)]
    out=[b'']*4
    for j,i in enumerate(perm):out[i]=w[j][::-1] if revword else w[j]
    return b''.join(out)

def mul(a,b):
    z=0
    for _ in range(128):
        if b&1:z^=a
        b>>=1
        a=((a<<1)^(0x87 if a>>127 else 0))%MOD
    return z

def power(a,n):
    z=1
    while n:
        if n&1:z=mul(z,a)
        a=mul(a,a);n>>=1
    return z

def model(observations,kind):
    pred=set();holdout=0;roots=0;ambiguous=0
    for perm,rw,rb in LAYOUTS:
        p0,p2,p3,p4=[view(v,perm,rw,rb) for v in observations]
        if kind=='ring':
            x=(p3-p2)%MOD;y=(p4-p3)%MOD
            if x==0:ambiguous+=1;continue
            n=(x&-x).bit_length()-1
            if y%(1<<n):continue
            if n>12:ambiguous+=1;continue
            m=MOD>>n
            start=((y>>n)*pow(x>>n,-1,m))%m
            alist=(start+t*m for t in range(1<<n))
            for a in alist:
                b=(p3-a*p2)%MOD
                p1=(a*p0+b)%MOD
                roots+=1
                if (a*p1+b)%MOD==p2:holdout+=1
                pred.add(unview(p1,perm,rw,rb))
        elif kind=='field':
            x=p2^p3
            if not x:ambiguous+=1;continue
            a=mul(p3^p4,power(x,MOD-2))
            b=p3^mul(a,p2)
            assert mul(a,p2)^b==p3 and mul(a,p3)^b==p4
            roots+=1;p1=mul(a,p0)^b
            if mul(a,p1)^b==p2:holdout+=1
            pred.add(unview(p1,perm,rw,rb))
    return pred,holdout,roots,ambiguous

def target_hash(coupon):
    return hashlib.sha256(bytes(x^y for x,y in zip(coupon,MASK))).hexdigest()

def originals():
    assert hashlib.sha256(SPOOL.read_bytes()).hexdigest()==SPOOL_SHA
    lines=SPOOL.read_text().splitlines()
    rows=[dict(re.findall(r'(\w+)=([^\s]+)',line)) for line in lines[1:]]
    assert len(rows)==133
    specs=[(128,'0417','1','REQUESTED'),(130,'0417','3','REQUESTED'),
           (131,'0448','1','ACK'),(132,'0420','2','ACK')]
    out=[]
    for i,job,attempt,state in specs:
        r=rows[i]
        assert r['JOB'].endswith(job) and r['ATTEMPT']==attempt and r['STATE']==state
        out.append(bytes.fromhex(r['PAYLOAD']))
    assert json.loads((ROOT/'resources/acceptance.json').read_text())['slot_sha256']['K04']==TARGET
    return out

def synthetic(kind):
    for seed in (65,117,257,4951,11259375):
        a=seed*2+1;b=seed*2+3
        states=[(seed*0x123456789ABCDEF987654321)%MOD]
        for _ in range(4):
            x=(a*states[-1]+b)%MOD if kind=='ring' else mul(a,states[-1])^b
            states.append(x)
        obs=[states[i].to_bytes(16,'big') for i in (0,2,3,4)]
        outputs,holdout,_,_=model(obs,kind)
        assert holdout>0 and states[1].to_bytes(16,'big') in outputs
    return 5

def main():
    observed=originals()
    union=set()
    for kind in ('ring','field'):
        options,holdout,roots,ambiguous=model(observed,kind)
        hits=[x.hex().upper() for x in options if target_hash(x)==TARGET]
        union.update(options)
        print(json.dumps(dict(model=kind,layouts=len(LAYOUTS),roots=roots,
          whole_value_holdout=holdout,distinct_candidates=len(options),
          original_k04_hits=hits,ambiguous=ambiguous,synthetic_pass=synthetic(kind)),sort_keys=True))
    print('UNION',len(union),hashlib.sha256(b''.join(sorted(union))).hexdigest())

if __name__=='__main__':main()
