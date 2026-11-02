"""Source-only SFT: test p951 node50 all-field Python randrange producer.
Run: python agents/agent23/k04_node50_stage_sft.py resources
Does not read row129 selected payload, route mask, acceptance, K04 or K08.
"""
import functools
import hashlib
import importlib.util
import random
import struct
import sys
import zlib
from pathlib import Path

MAX_REJECT_DRAWS = 10
REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
BASE_EPOCH = 1791061740  # 2026-10-03 21:09:00 UTC, hypothesis
ANCHORS = {7:-810, 12:-775, 13:-769, 24:-683, 25:-677, 41:-568, 45:-540, 70:-339}


def native_sampler_controls():
    """Synthetic live CPython controls, preserving each 32-bit draw."""
    for seed in (0, 1, 20261003, 314159, 417, 20261102):
        rng = random.Random(seed)
        state = []
        def draw(k):
            x = rng.getrandbits(32)
            state.append(x)
            return x >> (32-k)
        def rr(n):
            bits = n.bit_length()
            while True:
                x = draw(bits)
                if x < n:
                    return x
        rows=[]
        for _ in range(24):
            ts=rr(400); event=rr(39); latch=rr(4)
            ctrl=draw(32)
            ctrl_at=len(state)-1
            aux=rr(6000)
            rows.append((ts,event,latch,ctrl,aux,ctrl_at))
        for i in range(len(rows)-1):
            a=rows[i]; b=rows[i+1]
            start,end=a[-1],b[-1]
            arr=state[start+1:end]
            observed=(a[4],b[0],b[1],b[2])
            sizes=(13,9,6,3)
            upper=(6000,400,39,4)
            offset=0
            for wanted,k,n in zip(observed,sizes,upper):
                consumed=0
                while True:
                    v=arr[offset+consumed]>>(32-k)
                    consumed+=1
                    if v<n:break
                assert v==wanted, (seed,i,wanted,v)
                assert consumed<=MAX_REJECT_DRAWS, (seed,i,consumed)
                offset+=consumed
            assert offset == len(arr), (seed,i,offset,len(arr))
    print("PASS 6 genuine CPython seeded streams, 23 per-stream transitions")


def recover(root):
    source = Path(__file__).resolve().parents[1] / 'agent2' / '20261102_k04_multicarrier_p951_sft.py'
    module_spec=importlib.util.spec_from_file_location('source_p951', source)
    source_module=importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(source_module)
    val, known, offset=source_module.source_closure(root)
    assert all(known[offset+951+j]==0 for j in range(4))
    raw=(root/'evidence/recorder/trip-recorder.raw').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==REC_SHA
    rows=[]
    for idx in range(88):
        at=16+24*idx
        ts,node,event,latch,seq,word,aux,crc=struct.unpack_from('<IHBBI4sII',raw,at)
        if node!=50:continue
        assert zlib.crc32(raw[at:at+20])==crc
        rows.append(dict(seq=seq,ts=ts-BASE_EPOCH,event=event-1,latch=latch,
                         ctrl=source_module.untemper(int.from_bytes(word,'little')),aux=aux-2000))
    rows.sort(key=lambda r:r['seq'])
    assert len(rows)==72 and [r['seq'] for r in rows]==list(range(72))
    assert all(0<=r['ts']<400 and 0<=r['event']<39 and 0<=r['latch']<4
               and 0<=r['aux']<6000 for r in rows)

    @functools.lru_cache(maxsize=None)
    def codes(pos,bits):
        idx=offset+pos
        if not 0<=idx<len(val):return None
        m=known[idx]; v=val[idx]
        if m==0xffffffff:return (source_module.temper(v)>>(32-bits),)
        if m==0x7fffffff:
            return (source_module.temper(v)>>(32-bits),
                    source_module.temper(v|0x80000000)>>(32-bits))
        return None

    @functools.lru_cache(maxsize=None)
    def accepts(pos,length,bits,limit,target):
        for j in range(length):
            c=codes(pos+j,bits)
            if c is None:continue
            if j<length-1 and not any(v>=limit for v in c):return False
            if j==length-1 and target not in c:return False
        return True

    @functools.lru_cache(maxsize=None)
    def matches_ctrl(seq,pos):
        idx=offset+pos
        if not 0<=idx<len(val):return False
        if seq in ANCHORS and ANCHORS[seq]!=pos:return False
        return ((rows[seq]['ctrl']^val[idx])&known[idx])==0

    @functools.lru_cache(maxsize=None)
    def successors(seq,start):
        if not matches_ctrl(seq,start):return ()
        curr,nxt=rows[seq],rows[seq+1]
        accepted={}
        for a in range(1,MAX_REJECT_DRAWS+1):
            if not accepts(start+1,a,13,6000,curr['aux']):continue
            t=start+1+a
            for time in range(1,MAX_REJECT_DRAWS+1):
                if not accepts(t,time,9,400,nxt['ts']):continue
                e=t+time
                for event in range(1,MAX_REJECT_DRAWS+1):
                    if not accepts(e,event,6,39,nxt['event']):continue
                    l=e+event
                    for latch in range(1,MAX_REJECT_DRAWS+1):
                        if not accepts(l,latch,3,4,nxt['latch']):continue
                        dest=l+latch
                        if matches_ctrl(seq+1,dest):accepted[dest]=(a,time,event,latch)
        return tuple(sorted(accepted.items()))

    cases=[(12,13,True), (24,25,True), (13,16,False), (25,27,False), (45,49,False)]
    for start,end,expected in cases:
        path={ANCHORS[start]:()}
        traces=[]
        for seq in range(start,end):
            out={}
            for at,history in path.items():
                for dest,stages in successors(seq,at):
                    out[dest]=history+((seq,at,dest,stages),)
            path=out
            traces.append((seq+1,len(path),tuple(sorted(path))))
            if not path:break
        found=bool(path) and (end not in ANCHORS or ANCHORS[end] in path)
        print(f"seq{start}->{end}: {'FEASIBLE' if found else 'NO PATH'}, control states {traces}")
        assert found is expected
    @functools.lru_cache(maxsize=None)
    def latent_successors(seq,start,maxskip):
        """AUX, latent omitted stage, EVENT, LATCH, CONTROL."""
        curr,nxt=rows[seq],rows[seq+1]
        found=set()
        for a in range(1,9):
            if not accepts(start+1,a,13,6000,curr['aux']):continue
            end_aux=start+1+a
            for skip in range(maxskip+1):
                e=end_aux+skip
                for event in range(1,9):
                    if not accepts(e,event,6,39,nxt['event']):continue
                    l=e+event
                    for latch in range(1,9):
                        if not accepts(l,latch,3,4,nxt['latch']):continue
                        q=l+latch
                        if matches_ctrl(seq+1,q):found.add(q)
        return tuple(sorted(found))

    def connects_late(maxskip, anchor63=False):
        active={ANCHORS[45]}
        for seq in range(45,70):
            newer={q for p in active for q in latent_successors(seq,p,maxskip)}
            if seq==62 and anchor63:newer &= {-397}
            active=newer
            if not active:break
        return ANCHORS[70] in active

    assert not connects_late(22)
    assert connects_late(23)
    assert not connects_late(50,anchor63=True)
    print("PASS latent-stage boundary: late seq45->70 needs >=23 omitted draws")
    print("PASS seq63=-397 optional anchor incompatible with seq70=-339 under same law and 50-draw latent allowance")
    @functools.lru_cache(maxsize=None)
    def shifted_successors(seq,start):
        """The exact proposed five-field stage with epoch 21:09:02 UTC."""
        curr,nxt=rows[seq],rows[seq+1]
        out=set()
        for a in range(1,11):
            if not accepts(start+1,a,13,6000,curr['aux']):continue
            t=start+1+a
            for tim in range(1,11):
                if not accepts(t,tim,9,400,nxt['ts']-2):continue
                e=t+tim
                for evt in range(1,11):
                    if not accepts(e,evt,6,39,nxt['event']):continue
                    l=e+evt
                    for lat in range(1,11):
                        if not accepts(l,lat,3,4,nxt['latch']):continue
                        q=l+lat
                        if matches_ctrl(seq+1,q):out.add(q)
        return tuple(sorted(out))

    # Candidate seq55 was selected by its own AUX; this is not a blind anchor.
    assert -452 in shifted_successors(54,-459)
    assert shifted_successors(55,-452)==(-446,)
    assert shifted_successors(56,-446)==()
    assert codes(-444,13)==(2624,) and rows[56]['aux']==4362
    assert codes(-444,9)==(164,) and rows[57]['ts']-2==81
    print("PASS new heldout seq57 contradiction: model predicts time code164, original requires81")
    # Retrospectively AUX-selected 54/55 control candidates; new original fields.
    assert matches_ctrl(54,-459) and matches_ctrl(55,-452)
    assert codes(-458,13)==(876,) and rows[54]['aux']==876
    assert codes(-457,9)==(169,) and rows[55]['ts']-2==169
    assert codes(-456,6)==(35,1) and rows[55]['event']==35
    assert codes(-451,13)==(4663,) and rows[55]['aux']==4663
    assert codes(-450,9)==(444,)  # First timestamp56 draw rejects 444>=400
    assert codes(-449,9)==(117,357) and rows[56]['ts']-2==357
    print("PASS conditional AUX54->TS55(+2 epoch)->EVENT55 / AUX55->reject444->TS56(+2 epoch)")
    word,mask=val[:],known[:]
    for pos,high in ((-456,0),(-449,0x80000000)):
        at=offset+pos
        assert mask[at]==0x7fffffff
        mask[at]|=0x80000000
        word[at]|=high
    original_bits=sum(k.bit_count() for k in known)
    for _ in range(30):
        before=sum(k.bit_count() for k in mask)
        for i in range(len(word)-624):
            left=(mask[i]&0x80000000)|(mask[i+1]&0x7fffffff)
            value=(word[i]&0x80000000)|(word[i+1]&0x7fffffff)
            def add(j,v,m):
                assert ((word[j]^v)&mask[j]&m)==0
                fresh=m&~mask[j]
                word[j]=(word[j]&~fresh)|(v&fresh)
                mask[j]|=fresh
            if mask[i+397]==0xffffffff and mask[i+624]==0xffffffff:
                inv=source_module.inverse_twist(word[i+397]^word[i+624])
                add(i,inv,0x80000000)
                add(i+1,inv,0x7fffffff)
            if left==0xffffffff:
                if mask[i+397]==0xffffffff:
                    add(i+624,word[i+397]^source_module.twist(value),0xffffffff)
                if mask[i+624]==0xffffffff:
                    add(i+397,word[i+624]^source_module.twist(value),0xffffffff)
        if sum(k.bit_count() for k in mask)==before:break
    gained=sum(k.bit_count() for k in mask)-original_bits
    assert gained==34 and sum(k==0xffffffff for k in mask)==971
    assert all(mask[offset+951+j]==0 for j in range(4))
    print("PASS conditional two original source MSB completions: +34 fixed state bits, +3 full state words, selected four masks zero")
    print("PASS source-only bounded-order falsifier; selected coupon remains unconstrained")


if __name__ == '__main__':
    native_sampler_controls()
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'
    recover(root)
