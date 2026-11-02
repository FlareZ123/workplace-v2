"""K04 p951 seven-hypothetical-donor minimal palette attack.

Uses original 132 untouched printer packets, original 16 AX-7778 halfwords,
withholds selected ACK2, acceptance hash and route mask; implements GF(2)
MT19937 symbolic recurrence and source-consistent target quotient ranks.
"""
import json
import hashlib
import re
import time
from pathlib import Path
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
ROOT=Path(__file__).resolve().parents[2] / 'resources'
M=0xFFFFFFFF


def untemper(x):
    for shift,left,filter_ in ((18,False,M),(15,True,0xEFC60000),(7,True,0x9D2C5680),(11,False,M)):
        y=x
        for _ in range(6):
            y=x^(((y<<shift)&filter_) if left else (y>>shift))
        x=y&M
    return x


def temper(x):
    x^=x>>11
    x^=(x<<7)&0x9D2C5680
    x^=(x<<15)&0xEFC60000
    return (x^(x>>18))&M

MAG=0x9908b0df
ORIGIN=-160


def states(count=3600):
    out=[[1 << (32*i+b) for b in range(32)] for i in range(624)]
    for t in range(count-624):
        a,b,c=out[t],out[t+1],out[t+397]
        nextbits=[c[j]^b[j+1]^(b[0] if MAG>>j&1 else 0) for j in range(30)]
        nextbits.append(c[30]^a[31]^(b[0] if MAG>>30&1 else 0))
        nextbits.append(c[31]^(b[0] if MAG>>31&1 else 0))
        out.append(nextbits)
    return out


def temper_expr(bits):
    x=bits[:]
    for j in range(32):
        if j+11<32: x[j]^=x[j+11]
    for j in range(31,-1,-1):
        if j>=7 and (0x9d2c5680 >> j & 1): x[j]^=x[j-7]
    for j in range(31,-1,-1):
        if j>=15 and (0xefc60000 >> j & 1): x[j]^=x[j-15]
    for j in range(32):
        if j+18<32: x[j]^=x[j+18]
    return x

def reduced(x,pivots):
    while x:
        p=x.bit_length()-1
        if p not in pivots:break
        x^=pivots[p]
    return x


def add(x,pivots):
    x=reduced(x,pivots)
    if x:
        pivots[x.bit_length()-1]=x
        return 1
    return 0


def fit_source(symbols):
    raw=(ROOT/'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
    payloads=[bytes.fromhex(x.decode()) for x in re.findall(rb'PAYLOAD=([A-F0-9]{32})',raw)]
    assert len(payloads)==len(STARTS)==133
    basis={}; affine={}; CURRENT_LABEL='printer'
    def add_eq(expr,value):
        new=add(expr,basis)
        eq=(expr<<1)|(value&1)
        while eq:
            p=eq.bit_length()-1
            if p==0:raise AssertionError(f'original source inconsistency at {CURRENT_LABEL}: value={value}')
            if p not in affine:
                affine[p]=eq
                break
            eq^=affine[p]
        return new
    for row,(at,payload) in enumerate(zip(STARTS,payloads)):
        if row==129:continue
        for j in range(4):
            value=untemper(int.from_bytes(payload[j*4:j*4+4],'little'))
            for b,expr in enumerate(symbols[at+j-ORIGIN]):
                add_eq(expr,(value>>b)&1)
    printer_rank=len(basis)
    assert printer_rank==15365
    print('printer source rank',printer_rank)
    transfer_raw=(ROOT/'evidence/transfers/transfer-audit.jsonl').read_bytes()
    assert hashlib.sha256(transfer_raw).hexdigest()=='32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf'
    transfers=[json.loads(line) for line in transfer_raw.splitlines()]
    rows=sorted([x for x in transfers if x.get('kind')=='CHUNK' and x['transfer']=='AX-7778'],key=lambda x:(x['seq'],x['attempt']))
    assert len(rows)==16
    for i,x in enumerate(rows):
        CURRENT_LABEL=f'AX seq={x["seq"]} attempt={x["attempt"]} index {-157+i}'
        code=int(x['checkpoint'],16)
        high16=(code>>8)|((code&255)<<8) # transfer writes byte-swapped MT high16
        symbolic=temper_expr(symbols[-157+i-ORIGIN])
        for j,expr in enumerate(symbolic[16:]):
            add_eq(expr,(high16>>j)&1)
    assert len(basis)==15495
    print('AX-7778 rank increment',len(basis)-printer_rank,'full source rank',len(basis))
    return basis


def rank_overlap(donors,target,source):
    src_target={};target_rank=sum(add(reduced(x,source),src_target) for x in target)
    donor_vectors=[reduced(x,source) for x in donors]
    donor_basis={};donor_rank=sum(add(x,donor_basis) for x in donor_vectors)
    augmented=src_target.copy()
    extra=sum(add(x,augmented) for x in donor_vectors)
    return target_rank, donor_rank, donor_rank-extra


def synthetic_control(symbols):
    # Independent seeded native MT recurrence and bit-linear temper control.
    import random
    rng=random.Random(7411)
    init=[rng.getrandbits(32) for _ in range(624)]
    secret=sum(x<<(32*i) for i,x in enumerate(init))
    numeric=init[:]
    for t in range(len(symbols)-624):
        mixed=(numeric[t]&0x80000000)|(numeric[t+1]&0x7fffffff)
        numeric.append((numeric[t+397]^((mixed>>1)^(MAG if mixed&1 else 0)))&M)
    for idx in (0,5,463,624,901,1111,1340,1735):
        actual=sum(((secret&v).bit_count()&1)<<bit for bit,v in enumerate(symbols[idx]))
        assert actual==numeric[idx],idx
        out=sum(((secret&v).bit_count()&1)<<bit for bit,v in enumerate(temper_expr(symbols[idx])))
        assert out==temper(numeric[idx]),idx
    for native in (0,1,M,0x12345678,0xCAFEBABE):
        exp=temper(native)
        expr=temper_expr([1<<i for i in range(32)])
        value=sum(((native&x).bit_count()&1)<<j for j,x in enumerate(expr))
        assert value==exp
    print('native seeded-MT recurrence and both symbolic/numeric temper controls PASS')


def test():
    import itertools
    start=time.monotonic()
    sym=states()
    synthetic_control(sym)
    source=fit_source(sym)
    target=[bit for idx in range(951,955) for bit in sym[idx-ORIGIN]]
    assert rank_overlap([],target,source)[0]==128

    # Distinct nearby single-donor family compared with prior 227-step pairs.
    for idx,expected in ((1179,(12,31)),(1180,(16,32)),(1181,(16,32))):
        high=temper_expr(sym[idx-ORIGIN])[16:]
        observed=(rank_overlap(high,target,source)[2],rank_overlap(sym[idx-ORIGIN],target,source)[2])
        assert observed==expected,(idx,observed)
        print('single hypothetical donor',idx,'high16/full32 target gain',*observed)
    full_three=[v for i in (1179,1180,1181) for v in sym[i-ORIGIN]]
    high_three=[v for i in (1179,1180,1181) for v in temper_expr(sym[i-ORIGIN])[16:]]
    assert rank_overlap(full_three,target,source)[2]==95
    assert rank_overlap(high_three,target,source)[2]==44
    print('three full future words remove 95 of 128 selected bits; three upper16 readings remove 44')

    indices=(1179,1180,1181,1347,1348,1349,1350,1351,1574,1575,1576,1577,1578)
    projections={i:[reduced(v,source) for v in sym[i-ORIGIN]] for i in indices}
    target_basis={}
    assert sum(add(reduced(x,source),target_basis) for x in target)==128
    answers=[]
    for size in range(1,8):
        best=-1
        winners=[]
        for subset in itertools.combinations(indices,size):
            d=[v for idx in subset for v in projections[idx]]
            local={}
            rank=sum(add(v,local) for v in d)
            joined=target_basis.copy()
            spill=sum(add(v,joined) for v in d)
            gain=rank-spill
            if gain>best:
                best=gain
                winners=[subset]
            elif gain==best:
                winners.append(subset)
        print(f'donor count={size} maximum selected-bit rank gain={best}; number of best sets={len(winners)}')
        if size==7:
            assert best==128 and winners==[(1179,1180,1181,1347,1348,1574,1575)]
            answers=winners
        else:
            assert best<128
    print('UNIQUE size-seven theoretical complete donor set among the thirteen frozen positions:',answers[0])
    print('Original source target missing. No actual donor values at future indices have been authenticated.')
    print('Original coupon, source masks, K04/K08 commitments and verifier were never read or modified.')
    print('elapsed seconds',round(time.monotonic()-start,3))

if __name__=='__main__':test()
