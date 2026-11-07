"""H-17 conditional postspool MT/PV fixed-stride screen.

Source-only fit: all 132 retained intact printer payloads in the p951
symbolic MT chronology. The selected 18:02 row129 is always excluded.

Hypothesis: historian PVs are rounded 12+76*random.random() outputs after
printer stages, at fixed native-word stride 2..16 in acquisition-time order.
Ties are allowed to permute. This is a necessary source filter, not a claim
that this producer is historically correct. Never consult K04 hashes/coupons.

Run with an original ZIP argument or from the repository root without args.
Uses Python 3 stdlib on Windows 11.
"""
from __future__ import annotations

from collections import Counter
import hashlib
from itertools import groupby, permutations
import json
from pathlib import Path
import random
import re
import sys
import zipfile

STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
assert len(STARTS)==133 and STARTS[129]==951
MAG = 0x9908b0df
MASK32 = 0xffffffff
MAX_STAGE=4780
SOURCE_SPOOL_SHA='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
SOURCE_HST_SHA='3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'

class Basis:
    def __init__(self) -> None:
        self.rows: dict[int,tuple[int,int]]={}
    def insert(self, v: int, bit: int) -> None:
        while v:
            p=v.bit_length()-1
            if p not in self.rows:
                self.rows[p]=(v,bit)
                return
            w,c=self.rows[p]
            v^=w
            bit^=c
        assert bit==0,'source-inconsistent symbolic MT packet'
    def predict(self,v:int)->int|None:
        bit=0
        while v:
            p=v.bit_length()-1
            if p not in self.rows:return None
            w,c=self.rows[p]
            v^=w
            bit^=c
        return bit

def untemper(x:int)->int:
    for k,left,m in ((18,False,MASK32),(15,True,0xefc60000),(7,True,0x9d2c5680),(11,False,MASK32)):
        y=x
        for _ in range(6):y=x^(((y<<k)&m) if left else y>>k)
        x=y&MASK32
    return x

def temper(v:list[int])->list[int]:
    a=[v[j]^(v[j+11] if j+11<32 else 0) for j in range(32)]
    b=[a[j]^(a[j-7] if j>=7 and (0x9d2c5680>>j)&1 else 0) for j in range(32)]
    c=[b[j]^(b[j-15] if j>=15 and (0xefc60000>>j)&1 else 0) for j in range(32)]
    return [c[j]^(c[j+18] if j+18<32 else 0) for j in range(32)]

def symbolic_words()->list[list[int]]:
    words=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
    for i in range(624,MAX_STAGE+1):
        k=i-624
        words.append([words[k+397][j]^
                      (words[k][31] if j==30 else (words[k+1][j+1] if j<30 else 0))^
                      (words[k+1][0] if (MAG>>j)&1 else 0) for j in range(32)])
    return words

def src_data()->tuple[list[bytes],list[dict]]:
    path=Path(sys.argv[1]) if len(sys.argv)==2 else None
    if path is not None:
        with zipfile.ZipFile(path) as z:
            spool=z.read('evidence/print/spool-reconstruction.log')
            historian=z.read('evidence/telemetry/freeze-export.jsonl')
    else:
        base=Path(__file__).resolve().parents[2]/'resources'/'evidence'
        spool=(base/'print'/'spool-reconstruction.log').read_bytes()
        historian=(base/'telemetry'/'freeze-export.jsonl').read_bytes()
    assert hashlib.sha256(spool).hexdigest()==SOURCE_SPOOL_SHA
    assert hashlib.sha256(historian).hexdigest()==SOURCE_HST_SHA
    rows=[bytes.fromhex(x.decode('ascii')) for x in re.findall(rb'PAYLOAD=([0-9A-F]{32})',spool)]
    assert len(rows)==len(STARTS)
    data=[json.loads(line) for line in historian.splitlines() if b'"field": "PV"' in line]
    assert len(data)==112 and {r['seq'] for r in data}==set(range(100,212))
    data.sort(key=lambda x:(x['ts'],x['seq']))
    return rows,data

def model_basis(words:list[list[int]],packets:list[bytes])->Basis:
    basis=Basis()
    for index,start in enumerate(STARTS):
        if index==129:continue
        for lane in range(4):
            native=untemper(int.from_bytes(packets[index][4*lane:4*lane+4],'little'))
            for bit,v in enumerate(words[start+lane]):
                basis.insert(v,(native>>bit)&1)
    assert len(basis.rows)==15365
    return basis

def predicted_first15(words:list[list[int]],basis:Basis)->list[tuple[int,int]]:
    result=[]
    for stage in range(967,MAX_STAGE+1):
        value=mask=0
        for bit,v in enumerate(temper(words[stage])[17:32]):
            actual=basis.predict(v)
            if actual is not None:
                mask|=1<<bit
                value|=actual<<bit
        result.append((value,mask))
    return result

def pv_prefixes(value:float)->tuple[int,...]:
    lo=max(0.,(value-.0005-12.)/76.)
    hi=min(1.,(value+.0005-12.)/76.)
    assert 0. <= lo < hi <= 1.
    # Include the two immediate adjacent 15-bit bins for any tie/float
    # rounding implementation difference. This weakens exclusions.
    return tuple(range(max(0,int(lo*32768)-1),min(32767,int(hi*32768)+1)+1))

def source_match(prediction:tuple[int,int],pv_bins:tuple[int,...])->bool:
    value,mask=prediction
    return any((v&mask)==value for v in pv_bins)

def tie_groups(pv:list[dict])->list[tuple[int,tuple[tuple[int,...],...]]]:
    groups=[]
    for timestamp,group in groupby(pv,key=lambda row:row['ts']):
        records=tuple(group)
        groups.append((len(records),tuple(pv_prefixes(row['value']) for row in records)))
    assert sum(n for n,_ in groups)==112
    return groups

def score_schedule(predictions:list[tuple[int,int]],groups,first:int,stride:int)->tuple[int,int,int,int]:
    # Maximum possible matches by permuting all same-second records.
    # Each informative native-word position needs an independently matching
    # printed numeric value. Uninformative positions accept any value.
    position=0
    good_train=good_held=eligible_train=eligible_held=0
    for group_number,(size,prefixes) in enumerate(groups):
        indices=[first+stride*(position+j)-967 for j in range(size)]
        position+=size
        info=[j for j,k in enumerate(indices)
              if predictions[k][1].bit_count()>=10]
        if not info:continue
        potential=0
        for perm in permutations(range(size)):
            hits=sum(source_match(predictions[indices[j]],prefixes[perm[j]]) for j in info)
            if hits>potential:potential=hits
            if potential==len(info):break
        if group_number<20:
            good_train+=potential
            eligible_train+=len(info)
        else:
            good_held+=potential
            eligible_held+=len(info)
    return good_train,good_held,eligible_train,eligible_held

def synthetic_positive(words:list[list[int]])->None:
    rng=random.Random(0x5C3E7)
    native_packets=[rng.getrandbits(32) for _ in range(MAX_STAGE+1)]
    source=[untemper(x) for x in native_packets]
    for i in range(624,650):
        w0=source[i-624]; w1=source[i-623]; w397=source[i-227]
        next_ = w397 ^ (((w0&0x80000000)|(w1&0x7fffffff))>>1) ^ (MAG if w1&1 else 0)
        assert source[i]==next_
    packets=[b''.join(native_packets[start+j].to_bytes(4,'little') for j in range(4))
             for start in STARTS]
    planted_basis=model_basis(words,packets)
    projected=predicted_first15(words,planted_basis)
    true_first,true_stride=1011,7
    # Use original actual tie pattern, not an invented chronology.
    _,hist=src_data()
    actual_ties=[n for n,_ in tie_groups(hist)]
    out=[]
    for i in range(112):
        stage=true_first+true_stride*i
        u=((native_packets[stage]>>5)*(2**26)+(native_packets[stage+1]>>6))/(2**53)
        out.append(round(12+76*u,3))
    shuffled=[];start=0
    for count in actual_ties:
        seq=out[start:start+count]
        shuffled.extend(reversed(seq))
        start+=count
    fake_hist=[{'ts':record['ts'],'value':v} for record,v in zip(hist,shuffled)]
    groups=tie_groups(fake_hist)
    score=score_schedule(projected,groups,true_first,true_stride)
    assert score[0]+score[1]==score[2]+score[3] and score[2]+score[3]>=20,score
    print('Genuine MT seeded 112/112 PV pair with reversed within-second ties: PASS',score)

def main()->None:
    packets,pv=src_data()
    words=symbolic_words()
    source=model_basis(words,packets)
    for index,start in enumerate(STARTS):
        if index==129:continue
        for lane in range(4):
            word=temper(words[start+lane])
            original=int.from_bytes(packets[index][4*lane:4*lane+4],'little')
            assert all(source.predict(v)==(original>>bit)&1 for bit,v in enumerate(word))
    synthetic_positive(words)
    predictions=predicted_first15(words,source)
    histogram=Counter(mask.bit_count() for _,mask in predictions)
    print('Source-heldout genuine printer rank 15365; 132/132 complete packet controls PASS')
    print('Unseen postspool 15-bit known-count histogram',dict(sorted(histogram.items())))
    groups=tie_groups(pv)
    print('HST unique-second groups',len(groups),'tie-size distribution',dict(Counter(n for n,_ in groups)))
    scores=[]
    for stride in range(2,17):
        for first in range(967,3001):
            if first+111*stride>MAX_STAGE:continue
            train,held,obs_train,obs_held=score_schedule(predictions,groups,first,stride)
            scores.append((train,held,obs_train,obs_held,first,stride))
    assert len(scores)==30510
    genuine_coverage=[t for t in scores if t[2]>=4 and t[3]>=15]
    assert genuine_coverage
    best=max(genuine_coverage,key=lambda x:(x[0]+x[1],x[0],x[1]))
    fully_consistent=sum(t[0]==t[2] and t[1]==t[3] and t[2]+t[3]>=20 for t in scores)
    print('Tested exact fixed-stride schedules',len(scores))
    print('>=4 training / >=15 heldout source-informative stages',len(genuine_coverage))
    print('Highest informative matched schedule',best)
    print('Fully consistent schedules with >=20 independently source-predicted PVs',fully_consistent)
    assert fully_consistent==0
    print('ORIGINAL_FIXED_STRIDE_PV_MODEL: REJECTED; selected coupon/phrase UNKNOWN')

if __name__=='__main__':main()
