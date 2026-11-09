"""H17 print CLASS/DEST common-draw publisher, source-only six-MT model falsifier.

Reads the original archive ZIP (arg1) or repository resources/ by default.
Never reads the disputed selected ACK payload, K04 commitment, or key.
"""
import hashlib
import itertools
import re
import zipfile
import random
import sys
from pathlib import Path
from collections import defaultdict

SOURCE = sys.argv[1] if len(sys.argv)>1 else str(Path(__file__).resolve().parents[2] / 'resources')
STAGES=[0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
MAG=0x9908b0df
MASK=(1<<32)-1

def untemper(x):
    for k,left,m in ((18,False,MASK),(15,True,0xefc60000),(7,True,0x9d2c5680),(11,False,MASK)):
        y=x
        for _ in range(6):
            y=x^(((y<<k)&m) if left else y>>k)
        x=y&MASK
    return x

def temper(a):
    b=[a[i]^(a[i+11] if i+11<32 else 0) for i in range(32)]
    c=[b[i]^(b[i-7] if i>=7 and (0x9d2c5680>>i)&1 else 0) for i in range(32)]
    d=[c[i]^(c[i-15] if i>=15 and (0xefc60000>>i)&1 else 0) for i in range(32)]
    return [d[i]^(d[i+18] if i+18<32 else 0) for i in range(32)]

class Basis:
    def __init__(self):
        self.rows={}
    def add(self,v,b):
        while v:
            p=v.bit_length()-1
            if p not in self.rows:
                self.rows[p]=(v,b)
                return
            w,c=self.rows[p]
            v^=w
            b^=c
        if b:
            raise ValueError('Original payloads contradict the source MT chronology')
    def bit(self,v):
        b=0
        while v:
            p=v.bit_length()-1
            if p not in self.rows:
                return None
            w,c=self.rows[p]
            v^=w
            b^=c
        return b

def load():
    if SOURCE.lower().endswith('.zip'):
        with zipfile.ZipFile(SOURCE) as z:
            raw=z.read('evidence/print/spool-reconstruction.log')
    else:
        root=Path(SOURCE)
        folder=root if (root/'evidence').is_dir() else root/'resources'
        raw=(folder/'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
    lines=[x for x in raw.decode().splitlines() if x.startswith('2026-')]
    assert len(lines)==133
    rows=[]
    for line in lines:
        found=re.search(r'CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)',line)
        assert found
        rows.append((found.group(1),found.group(3),bytes.fromhex(found.group(2))))
    assert len(STAGES)==len(rows)
    return rows

def basis(rows):
    # Initial 624 words are unknown binary states. Untwist forward exactly.
    s=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
    for i in range(624,max(STAGES)+4):
        k=i-624
        s.append([s[k+397][j]^(s[k][31] if j==30 else (s[k+1][j+1] if j<30 else 0))^(s[k+1][0] if (MAG>>j)&1 else 0) for j in range(32)])
    b=Basis()
    for i, (_,_,payload) in enumerate(rows):
        if i==129:
            continue
        for t in range(4):
            x=untemper(int.from_bytes(payload[4*t:4*t+4],'little'))
            for j,v in enumerate(s[STAGES[i]+t]):
                b.add(v,(x>>j)&1)
    return s,b

def code_options(vectors,b):
    # If MT source leaves bits unresolved, allow every numeric value in
    # an optimistic min/max interval. Actual compatible outcomes are a subset.
    a,bits=0,0
    for k in range(31,4,-1):
        r=b.bit(vectors[0][k])
        a=a*2+(r or 0)
        bits=bits*2+(1 if r is None else 0)
    c,d=0,0
    for k in range(31,5,-1):
        r=b.bit(vectors[1][k])
        c=c*2+(r or 0)
        d=d*2+(1 if r is None else 0)
    lo=(a<<26)|c
    hi=((a+bits)<<26)|(c+d)
    return frozenset(range((lo*9)>>53,((hi*9)>>53)+1))

def maximum_matching(possibilities):
    ownership={}
    def assign(category,seen):
        for code in sorted(possibilities[category]):
            if code in seen:
                continue
            seen.add(code)
            if code not in ownership or assign(ownership[code],seen):
                ownership[code]=category
                return True
        return False
    return all(assign(c,set()) for c in sorted(possibilities,key=lambda k:len(possibilities[k])))

ALPHABET='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
# Exact delta encoding of the other five archived p950..955 vectors relative
# to the p951 stage vector above. Delta=(ALPHABET.index(character)-13).
DIFFERENCES={
    '950':'DDCDDDDCCCCCCCCCADDDDDDDDHIFFDDDDCDDDCCCCCCCCCCCCCCCCDDCDDDFDCCCCCCCCCGFDCDDDEEFFFDDDDDDDCCCCCCCCCCC66DDDDDD9EFFGDDDDDDCCCCCCCCCCCCCC',
    '952':'DDCDDJHEDEEEEEEECEEEFBBGGGGDDADDDCDJJJEDEEEEEEEEEEEEEDDCDDDD87DEEEEEEEEDB0BB9BDDDDDDDDDDDBCEDDEEEEEEEDBBBBBFBCDDGDDDDDBCBEDDEEEEEEEEE',
    '953':'DDCDDDBGFFFFFFFFDDDDFFFGIIIFFDDDDCDCA9GFFFFFFFFFFFFFFDDCDDDFB9FFFFFFFFHHMEFFDDFFFFDDDDDDFGGGFFFFFFFF9HFFFFFIDEFFGDDDDKIIGGFFFFFFFFFFF',
    '954':'DDEEEDFGGGGGGGGGEEEEEDDDDEFEFDDDEEEPNMGGGGGGGGHHHHHHHDEEEEEFFGGGGGGGGGIIODDDBCFEFFDDEEEEGEGGGGGGGGGGA9BBDDDLFFFFFDDEEECBCGGGGGGGGGGGG',
    '955':'DDBDDMKHHHHHHHHHFFFFFBBBBEIFFDDDDCDCADHHHHHHHHHHHHHHHDDCDDEFIHHHHHHHHHJOMBBB9AA9FFDDDDDDDBEHHHHHHHHHBA888BBE8AAFFDDDDIKJHHHHHHHHHHHHH'
}

def one_word_code(v, basis):
    low=unknown=0
    for k in range(31,-1,-1):
        bit=basis.bit(v[k])
        low=(low<<1)|(bit or 0)
        unknown=(unknown<<1)|int(bit is None)
    return frozenset(range((9*low)>>32,((9*(low+unknown))>>32)+1))

def source_model(rows, vector, basis, kind, position, binding, train=95):
    cats=sorted({(c,d) for c,d,_ in rows[:128]})
    assert len(cats)==9
    domains={x:set(range(9)) for x in cats}
    examples=defaultdict(list)
    def options(i):
        start,end=STAGES[i]+4,STAGES[i+1]
        stages=range(start,end-1) if kind=='float53' else range(start,end)
        if position=='first':
            stages=[start]
        elif position=='last':
            stages=[end-2 if kind=='float53' else end-1]
        opts=set()
        for j in stages:
            opts.update(code_options((vector[j],vector[j+1]),basis) if kind=='float53' else one_word_code(vector[j],basis))
        return opts
    for i in range(train):
        opts=options(i)
        cat=rows[i+(binding=='following')][:2]
        domains[cat]&=opts
        examples[cat].append((i,opts))
    if maximum_matching(domains):
        # Independent 32 original records, never used to select the codebook.
        full={k:set(v) for k,v in domains.items()}
        holdout=[]
        for i in range(train,127):
            opts=options(i)
            cat=rows[i+(binding=='following')][:2]
            full[cat]&=opts
            holdout.append((i,cat,opts))
        best=0
        for codes in itertools.permutations(range(9)):
            mapping=dict(zip(cats,codes))
            if all(mapping[cat] in domain for cat,domain in domains.items()):
                best=max(best,sum(mapping[cat] in opts for _,cat,opts in holdout))
        print('SOURCE_HOLDOUT',kind,position,binding,'best',best,'of 32',
              'all_source_feasible',maximum_matching(full))
        return best<32
    witness=None
    for cat, sightings in examples.items():
        for (i,a),(j,b) in itertools.combinations(sightings,2):
            if a.isdisjoint(b):
                witness=(cat,i,j,sorted(a),sorted(b))
                break
        if witness is not None:
            break
    print('SOURCE_REJECT',kind,position,binding,'empty_groups',sum(not v for v in domains.values()),'pair_witness',witness)
    return True

def planted_random_controls():
    r=random.Random(20261109)
    for _ in range(128):
        a,b=r.getrandbits(32),r.getrandbits(32)
        direct=(((a>>5)<<26)|(b>>6))*9>>53
        base=Basis()
        v=[[1<<j for j in range(32)],[1<<(32+j) for j in range(32)]]
        for lane,word in enumerate((a,b)):
            for j in range(32):
                base.add(v[lane][j],(word>>j)&1)
        assert code_options(v,base)==frozenset((direct,))
        assert one_word_code(v[0],base)==frozenset(((a*9)>>32,))
    print('SYNTHETIC_PUBLISHER_CONTROLS_PASS 128 float53 128 scaled32')

def run():
    planted_random_controls()
    rows=load()
    starts_951=STAGES[:]
    rejects=0
    for chronology in ('950','951','952','953','954','955'):
        delta=DIFFERENCES.get(chronology)
        starts=[v+ALPHABET.index(x)-13 for v,x in zip(starts_951,delta)] if delta else starts_951[:]
        assert len(starts)==133
        STAGES[:]=starts
        assert STAGES[129]==int(chronology)
        native,b=basis(rows)
        assert len(b.rows)=={950:15366,951:15365,952:15367,953:15368,954:15365,955:15369}[int(chronology)]
        output=[temper(w) for w in native]
        print('CHRONOLOGY',chronology,'source_rank',len(b.rows))
        for kind in ('float53','scaled32'):
            for pos in ('first','last','any'):
                for binding in ('previous','following'):
                    rejects+=int(source_model(rows,output,b,kind,pos,binding))
    assert rejects==72,('source-surviving model requires investigation',rejects)
    print('FINAL chronologies=6 publishers=2 positions=3 bindings=2 rejected=72 key_recovered=0')

if __name__=='__main__':
    run()
