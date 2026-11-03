"""SFT: fixed-five-field MT19937 recorder emission order, original H-17 source.

Run: python agents/agent1/k04_node50_fivefield_order_sft.py [resources-path]
Original source/verifier/commitment/candidate read-only; selected spool row129 excluded.
Conditional p951 printer chronology and recorder CONTROL anchors are inherited prior art.
This experiment tests all 120 fixed orders, with exact rejection semantics and no hidden draws.
"""
import hashlib
import itertools
import random
import re
import struct
import sys
import zlib
from functools import lru_cache
from pathlib import Path

U = 0xFFFFFFFF
MAG = 0x9908B0DF
OFF = 2000
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
REC_SHA = '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
ANCHORS = {7:-810,12:-775,13:-769,24:-683,25:-677,41:-568,44:-545,45:-540}
FIELDS = ('time','event','latch','control','aux')

def temper(v):
    v ^= v >> 11
    v ^= (v << 7) & 0x9D2C5680
    v ^= (v << 15) & 0xEFC60000
    return (v ^ (v >> 18)) & U

def untemper(v):
    for n,left,mask in ((18,False,U),(15,True,0xEFC60000),(7,True,0x9D2C5680),(11,False,U)):
        x=v
        for _ in range(6):
            x=v^(((x<<n)&mask) if left else x>>n)
        v=x&U
    return v

def twist(v):
    return (v>>1) ^ (MAG if v&1 else 0)

def inverse_twist(v):
    bit=v>>31
    return (((v^(MAG if bit else 0))<<1)|bit)&U

def printer(root):
    raw=(root/'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SPOOL_SHA
    packets=[bytes.fromhex(x.decode()) for x in re.findall(rb'PAYLOAD=([0-9A-F]{32})',raw)]
    assert len(packets)==len(STARTS)==133 and STARTS[129]==951
    data=[0]*6000
    known=[0]*6000
    def add(i,v,mask):
        if not 0<=i<len(data):return False
        assert ((data[i]^v)&known[i]&mask)==0
        new=mask&~known[i]
        if new:
            data[i]=(data[i]&~new)|(v&new)
            known[i]|=new
        return bool(new)
    for row,(packet,start) in enumerate(zip(packets,STARTS)):
        if row==129:continue
        for lane in range(4):
            add(OFF+start+lane,untemper(int.from_bytes(packet[4*lane:4*lane+4],'little')),U)
    for _ in range(30):
        changed=False
        for i in range(len(data)-624):
            mask=(known[i]&0x80000000)|(known[i+1]&0x7FFFFFFF)
            value=(data[i]&0x80000000)|(data[i+1]&0x7FFFFFFF)
            if known[i+397]==U and known[i+624]==U:
                inv=inverse_twist(data[i+397]^data[i+624])
                changed |= add(i,inv,0x80000000)
                changed |= add(i+1,inv,0x7FFFFFFF)
            if mask==U:
                if known[i+397]==U:changed |= add(i+624,data[i+397]^twist(value),U)
                if known[i+624]==U:changed |= add(i+397,data[i+624]^twist(value),U)
        if not changed:break
    assert sum(m==U for m in known)==968
    assert all(known[OFF+951+k]==0 for k in range(4))
    return data,known,OFF

def recorder(root):
    raw=(root/'evidence/recorder/trip-recorder.raw').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==REC_SHA
    rows={}
    for i in range(88):
        pos=16+i*24
        ts,node,event,latch,seq,ctrl,aux,crc=struct.unpack_from('<IHBBI4sII',raw,pos)
        if node==50:
            assert zlib.crc32(raw[pos:pos+20])==crc
            rows[seq]={
                'time':(ts-1791061742,9,400),
                'event':(event-1,6,39),
                'latch':(latch,3,4),
                'control':(ctrl,32,1<<32),
                'aux':(aux-2000,13,6000)
            }
    assert set(rows)==set(range(72))
    return rows

def search(rows,anchors,word,known,offset,max_rejects=10):
    @lru_cache(maxsize=None)
    def codes(pos,k):
        at=pos+offset
        if not 0<=at<len(word):return ()
        available=known[at]
        missing=U&~available
        # Source-unknown bits are freely compatible: a sound relaxation for no-path results.
        if missing.bit_count()>2 or available.bit_count()<=1:return None
        bits=[b for b in range(32) if missing&(1<<b)]
        return frozenset(temper(word[at]|sum(((choice>>j)&1)<<bit for j,bit in enumerate(bits)))>>(32-k)
                         for choice in range(1<<len(bits)))
    @lru_cache(maxsize=None)
    def choices(seq,field,pos):
        if field=='control':
            at=pos+offset
            if not 0<=at<len(word):return ()
            ctrl=untemper(int.from_bytes(rows[seq]['control'][0],'little'))
            return (pos+1,) if ((word[at]^ctrl)&known[at])==0 else ()
        val,k,limit=rows[seq][field]
        out=[]
        for n in range(max_rejects+1):
            p=pos+n
            valid=codes(p,k)
            if valid==() or (valid is not None and val not in valid):continue
            if all((c:=codes(j,k)) is None or any(x>=limit for x in c) for j in range(pos,p)):
                out.append(p+1)
        return tuple(out)
    assert 7 in anchors and 45 in anchors
    def test(order):
        positions={anchors[7]+1}
        stages=[(7,field) for field in order[order.index('control')+1:]]
        for seq in range(8,46):
            for field in order:
                stages.append((seq,field))
                if seq==45 and field=='control':break
        for seq,field in stages:
            following=set()
            for pos in positions:
                for newpos in choices(seq,field,pos):
                    if newpos<=anchors[45]+1 and (field!='control' or seq not in anchors or newpos==anchors[seq]+1):
                        following.add(newpos)
            positions=following
            if not positions:return None,(seq,field)
        return (anchors[45]+1 in positions),None
    return [(order,*test(order)) for order in itertools.permutations(FIELDS)]

def synthetic_positive():
    seed=random.Random(791)
    outputs=[]
    def next32():
        v=seed.getrandbits(32)
        outputs.append(v)
        return v
    def sample(limit):
        width=limit.bit_length()
        while True:
            x=next32()>>(32-width)
            if x<limit:return x
    rows={}
    anchors={}
    order=('time','event','latch','control','aux')
    for seq in range(7,46):
        row={}
        for name in order:
            if name=='control':
                anchors[seq]=len(outputs)
                row[name]=(next32().to_bytes(4,'little'),32,1<<32)
            else:
                limit={'time':400,'event':39,'latch':4,'aux':6000}[name]
                row[name]=(sample(limit),limit.bit_length(),limit)
        rows[seq]=row
    word=[untemper(v) for v in outputs]
    known=[U]*len(outputs)
    outcomes=search(rows,anchors,word,known,0)
    assert any(perm==order and success for perm,success,_ in outcomes)
    print('SYNTHETIC_ALL_FIELDS_ORIGINAL_ORDER_PASS',len(outputs),'native MT outputs')

def original(root):
    word,known,offset=printer(root)
    rows=recorder(root)
    for seq,stage in ANCHORS.items():
        ctrl=untemper(int.from_bytes(rows[seq]['control'][0],'little'))
        assert ((word[stage+offset]^ctrl)&known[stage+offset])==0
    failures={}
    for shift in (-2,-1,0,1):
        shifted={seq:{**record,'time':(record['time'][0]-shift,9,400)} for seq,record in rows.items()}
        outcomes=search(shifted,ANCHORS,word,known,offset)
        winners=[order for order,success,_ in outcomes if success]
        assert not winners
        reached=max(failed[0] for _,success,failed in outcomes if not success)
        failures[shift]=reached
        print('ORIGINAL_BASE_SHIFT',shift,'ORDERS',len(outcomes),'COMPATIBLE',len(winners),'FARTHEST_FAILED_SEQ',reached)
    assert failures=={-2:24,-1:24,0:24,1:24}
    print('PASS: 480 five-field source-sampler orders rejected, no extra draws, <=10 retries each.')
    print('No claim of true producer identity; selected K04 and K08 remain unrecovered.')

if __name__=='__main__':
    synthetic_positive()
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'
    original(root)
