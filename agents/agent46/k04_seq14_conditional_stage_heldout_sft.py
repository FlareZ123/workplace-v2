"""A conditional p951 printer->node50 seq14 heldout full-word partial predictor.
Original source only; selected ACK, masks, commitments and K08 are untouched.
Model: timestamp=epoch+randrange(400), event=1+randrange(39),
latch=randrange(4), control=getrandbits(32), aux=2000+randrange(6000).
Imported printer-only symbolic MT rank from Agent49. Test is local to seq13->14;
it DOES NOT assert a complete 72-record historical producer, which earlier
original-data counterexamples rule out under this exact global model.
"""
import hashlib,random,struct,sys,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'agent49'))
from k04_p951_symbolic_basis import source,get,temper,untemper
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2] / 'resources'
REC_SHA='5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'

def predict(b,s,begin,end):
    native,outputs={},{}
    for p in range(begin,end):
        for dest,expressions in ((native,get(s,p)),(outputs,temper(get(s,p)))):
            v=m=0
            for j,x in enumerate(expressions):
                bit=b.predict(x)
                if bit is not None:
                    v|=bit<<j
                    m|=1<<j
            dest[p]=(v,m)
    return native,outputs

def feasible(pos,k,bound,code,outputs):
    val,mask=outputs[pos]
    val>>=32-k
    mask>>=32-k
    can_accept=not ((val^code)&mask)
    can_reject=(val|(~mask&((1<<k)-1)))>=bound
    return can_accept,can_reject

def walk(start,fields,outputs,cap=8):
    states={start}
    for k,bound,code in fields:
        nxt=set()
        for pos in states:
            for rejects in range(cap+1):
                end=pos+rejects
                if end not in outputs:break
                if any(not feasible(pos+d,k,bound,code,outputs)[1] for d in range(rejects)):
                    break
                if feasible(end,k,bound,code,outputs)[0]:nxt.add(end+1)
        states=nxt
        if not states:break
    return states

def candidate_control_positions(start,readings,outputs,cap=8):
    timestamp,event,latch,aux=readings
    before=walk(start,((9,400,timestamp),(6,39,event),(3,4,latch)),outputs,cap)
    return {control for control in before
            if walk(control+1,((13,6000,aux),),outputs,cap)}

def synthetic_controls():
    class CapturingRandom(random.Random):
        def __init__(self,seed):
            super().__init__(seed)
            self.words=[]
        def getrandbits(self,k):
            w=super().getrandbits(32)
            self.words.append(w)
            return w>>(32-k)
    for seed in range(20):
        rng=CapturingRandom(seed)
        observed=(rng.randrange(400),rng.randrange(39),rng.randrange(4))
        index=len(rng.words)
        withheld=rng.getrandbits(32)
        aux=rng.randrange(6000)
        outputs={i:(w,0xffffffff) for i,w in enumerate(rng.words)}
        control=candidate_control_positions(0,observed+(aux,),outputs)
        assert control=={index},(seed,index,control)
        assert (untemper(withheld)&0xffffffff)==untemper(rng.words[index])
    print('PASS 20 independently seeded randrange source and heldout-control stage controls')

def main():
    synthetic_controls()
    b,s=source(ROOT)
    assert b.rank==15365
    raw=(ROOT/'evidence/recorder/trip-recorder.raw').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==REC_SHA
    node={}
    for i in range(88):
        at=16+24*i
        ts,n,event,latch,seq,ctrl,aux,crc=struct.unpack_from('<IHBBI4sII',raw,at)
        if n!=50:continue
        assert zlib.crc32(raw[at:at+20])==crc
        node[seq]=(ts,event,latch,untemper(int.from_bytes(ctrl,'little')),aux)
    assert len(node)==72
    native,outputs=predict(b,s,-772,-740)
    assert (native[-769][0]^node[13][3])&native[-769][1]==0
    # Selected source control seq13 at -769 was independently identified before this test.
    # Its original AUX13 code 1201 is predicted exactly from source at -768.
    assert node[13][4]-2000==1201
    assert outputs[-768][1]>>(32-13)==8191
    assert outputs[-768][0]>>(32-13)==1201
    original=node[14]
    readings=(original[0]-1791061742,original[1]-1,original[2],original[4]-2000)
    candidates=candidate_control_positions(-767,readings,outputs)
    independently_visible={p:native[p][1].bit_count() for p in candidates if native[p][1].bit_count()>=8}
    assert independently_visible=={-759:16},independently_visible
    word,mask=native[-759]
    assert ((word^original[3])&mask)==0
    decoys=[seq for seq,row in node.items() if seq!=14 and ((word^row[3])&mask)==0]
    print('Source-selected seq14 control index -759, source-fixed 16 bits match withheld original')
    print('Candidate positions with >=8 fixed independent bits:',independently_visible)
    print('Other original node50 controls with same 16 fixed-bit pattern:',len(decoys))
    print('Conditional local stage only. Global five-field model has previously published counterexamples.')
    print('Selected K04 source bits: 0/128, K08 words: 0; original acceptance not read')

if __name__=='__main__':main()
