"""H-17 joint-carrier stage-switch falsifier, original source only.

Train on 132 intact printer packets and independently held AX-7778 high16
checkpoints; predict frozen 16-draw placements for three heldout transfer
chains. Includes genuinely seeded complete synthetic transfer controls.
The disputed printer ACK2, K04/K08 commitments, route mask and verifier
are not parsed or used.
"""
import hashlib
import json
import random
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/'resources/evidence'
ORIGIN=-160
STARTS=[0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
FULL=0xffffffff
MAGIC=0x9908b0df

def states():
    out=[[1<<(32*i+b) for b in range(32)] for i in range(624)]
    for index in range(624,1300):
        p,n,q=out[index-624],out[index-623],out[index-227]
        out.append([q[b]^(p[31] if b==30 else n[b+1] if b<30 else 0)^(n[0] if MAGIC>>b&1 else 0) for b in range(32)])
    return out

def high16(bits):
    x=bits.copy()
    for j in range(32):
        if j+11<32:x[j]^=x[j+11]
    for j in range(31,-1,-1):
        if j>=7 and (0x9d2c5680>>j)&1:x[j]^=x[j-7]
    for j in range(31,-1,-1):
        if j>=15 and (0xefc60000>>j)&1:x[j]^=x[j-15]
    for j in range(32):
        if j+18<32:x[j]^=x[j+18]
    return x[16:]

def untemper(x):
    for shift,left,mask in ((18,False,FULL),(15,True,0xefc60000),(7,True,0x9d2c5680),(11,False,FULL)):
        y=x
        for _ in range(6):y=x^(((y<<shift)&mask) if left else (y>>shift))
        x=y&FULL
    return x

def reduce(row,basis):
    while row:
        pivot=row.bit_length()-1
        if pivot not in basis:break
        row^=basis[pivot]
    return row

def add(basis,expr,value):
    row=reduce((expr<<1)|(value&1),basis)
    assert row!=1,'source contradiction'
    if row>1:basis[row.bit_length()-1]=row

def fit(symbols,packets,anchor):
    basis={}
    for row,(at,packet) in enumerate(zip(STARTS,packets)):
        if row==129:continue
        assert len(packet)==16
        for lane in range(4):
            val=untemper(int.from_bytes(packet[4*lane:4*lane+4],'little'))
            for bit,expr in enumerate(symbols[at+lane-ORIGIN]):
                add(basis,expr,(val>>bit)&1)
    assert len(basis)==15365,len(basis)
    assert len(anchor)==16
    for j,value in enumerate(anchor):
        for bit,expr in enumerate(high16(symbols[-157+j-ORIGIN])):
            add(basis,expr,(value>>bit)&1)
    assert len(basis)==15495,len(basis)
    return basis

def check(symbols,basis,start,seq):
    covered=errors=0
    for j,value in enumerate(seq):
        for bit,expr in enumerate(high16(symbols[start+j-ORIGIN])):
            remainder=reduce(expr<<1,basis)
            if remainder<=1:
                covered+=1
                errors+=((value>>bit)&1)!=(remainder&1)
    return covered,errors

def synthetic(symbols):
    for seed in (202618,202619,202620):
        stream=random.Random(seed)
        draws=[stream.getrandbits(32) for _ in range(1150)]
        packets=[b''.join(draws[at-ORIGIN+lane].to_bytes(4,'little') for lane in range(4)) for at in STARTS]
        packets[129]=b''
        anchor=[draws[-157+j-ORIGIN]>>16 for j in range(16)]
        basis=fit(symbols,packets,anchor)
        for pos,cov in ((-141,116),(-125,103),(-109,104)):
            heldout=[draws[pos+j-ORIGIN]>>16 for j in range(16)]
            assert check(symbols,basis,pos,heldout)==(cov,0),(seed,pos)
    print('Independent genuinely seeded full-stream heldouts: 3/3 PASS')

def original(symbols):
    spool=(ROOT/'print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(spool).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
    fields=re.findall(rb'PAYLOAD=([0-9A-F]{32})',spool)
    assert len(fields)==len(STARTS)==133 and STARTS[129]==951
    packets=[b'' if i==129 else bytes.fromhex(x.decode()) for i,x in enumerate(fields)]
    raw=(ROOT/'transfers/transfer-audit.jsonl').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf'
    rows=[json.loads(x) for x in raw.splitlines()]
    trails={}
    for name in ('AX-7778','AX-7781','AX-7782','AX-7783'):
        entries=sorted((r for r in rows if r.get('kind')=='CHUNK' and r['transfer']==name),key=lambda r:(r['seq'],r['attempt']))
        assert len(entries)==16
        trails[name]=[((v:=int(r['checkpoint'],16))>>8)|((v&255)<<8) for r in entries]
    statuses={r['transfer']:(r['kind'],r.get('dry_run')) for r in rows if r['kind']!='CHUNK'}
    assert statuses=={'AX-7778':('COMMIT',False),'AX-7781':('COMMIT',True),
                      'AX-7782':('COMMIT',False),'AX-7783':('ABORT',False)}
    basis=fit(symbols,packets,trails['AX-7778'])
    # Hypothesis H1, before observing heldout bits: all transfer IDs consume
    # one successive 16-output block in ascending transfer-ID order.
    for name,index,expected in (('AX-7781',-141,(116,56)),('AX-7782',-125,(103,49)),('AX-7783',-109,(104,48))):
        result=check(symbols,basis,index,trails[name])
        assert result==expected,(name,result)
        print('H1 all-transfer sequential stage',name,index,'predicted',result[0],'errors',result[1])
    # Hypothesis H2: dry-run and aborted transfers use a separate stream;
    # the two successful non-dry-run COMMITs use consecutive 16-word blocks.
    result=check(symbols,basis,-141,trails['AX-7782'])
    assert result==(116,57),result
    print('H2 committed-only shared stream AX-7782 -141 predicted',result[0],'errors',result[1])
    print('Both selected-output stage models fail source-heldout tests. Actual printer producer still unauthenticated.')

def main():
    symbols=states()
    synthetic(symbols)
    original(symbols)

if __name__=='__main__':main()
