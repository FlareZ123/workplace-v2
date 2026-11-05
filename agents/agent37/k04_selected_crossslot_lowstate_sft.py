"""H-17 selected-source low-state generator bridge (read-only original acceptance).

Hypothesis: five independently accepted raw 16B source blocks were emitted
from one common xorshift128, xoshiro128** or SplitMix64 stream. An anchor
source block specifies an entire source state, which can emit K04 coupons.
The late selected copied printer ACK payload is never used to fit a state.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, re, struct, zlib
from datetime import datetime, timezone
from collections import deque

ROOT=Path(__file__).resolve().parents[2] / 'resources' / 'evidence'
MASK32=(1<<32)-1
MASK64=(1<<64)-1
SPOOL_HASH='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
TRANSFER_HASH='32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf'
EXPECTED={'K01':'049AAB2E1CDE7A82CD7C60234303C91A',
 'K02':'E1A5E474BAD7E853A2E8C71D3317D507',
 'K05':'FF8B78200A56E8586DCDA00EF01E4572',
 'K06':'5DBF40EE52FAAED9A536D3326CF0D95A',
 'K07':'8947CEDCB9CC73BAB7E87BE63302C5C9'}


def source_blocks():
    raw=(ROOT/'print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SPOOL_HASH
    assert b'2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in raw
    emails='\n'.join((ROOT/'mail'/f'{i:02d}.eml').read_text() for i in (3,6))
    ink=dict((n,v) for n,v in re.findall(r'WN-14 / group ([A-D]) / ([0-9A-F]{8})', emails))
    assert sorted(ink)==list('ABCD')
    a=bytes.fromhex(''.join(ink[k] for k in 'ABCD'))

    tele=[json.loads(line) for line in (ROOT/'telemetry/freeze-export.jsonl').read_bytes().splitlines()]
    lo=datetime.fromisoformat('2026-10-03T21:13:40+00:00')
    hi=datetime.fromisoformat('2026-10-03T21:13:48+00:00')
    chosen={}
    for t in tele:
        if t['tag']=='LT-204' and t['field']=='DIAG_WORD' and t['quality']=='GOOD' and t['state']=='HOLD' and lo<=datetime.fromisoformat(t['ts'])<hi:
            k=t['seq']
            if k not in chosen or t['revision']>chosen[k]['revision']:chosen[k]=t
    assert sorted(chosen)==list(range(8))
    b=b''.join(int(chosen[i]['value']).to_bytes(2,'big') for i in range(8))

    rec=(ROOT/'recorder/trip-recorder.raw').read_bytes()
    assert rec[:8]==b'TRP2DUMP' and int.from_bytes(rec[10:12],'little')==24
    assert len(rec)==16+24*int.from_bytes(rec[12:16],'little')
    best={}
    start=int(datetime(2026,10,3,21,14,tzinfo=timezone.utc).timestamp())
    for i in range(16,len(rec),24):
        entry=rec[i:i+24]
        if zlib.crc32(entry[:20])!=int.from_bytes(entry[20:24],'little'):continue
        t,node,event,latch,seq=struct.unpack_from('<IHBBI',entry)
        if node==49 and event==82 and start<=t<start+8:
            if latch not in best or seq>best[latch][0]:best[latch]=(seq,entry[12:16])
    assert sorted(best)==list(range(4))
    c=b''.join(best[i][1] for i in range(4))

    procedures=(ROOT/'procedures/RC-17-scans.txt').read_text()
    pages={}
    for part in procedures.split('\f'):
        head=re.search(r'DOCUMENT RC-17 / REV ([^ /]+) / SECTION ([^\n]+)',part)
        val=re.search(r'Footer control strip:\s*([0-9A-F]{8})',part)
        if head and val:pages[(head.group(1),head.group(2))]=bytes.fromhex(val.group(1))
    d=b''.join(pages[('C',name)] for name in ('DRAIN','ISOLATE','PURGE','VERIFY'))

    trans=(ROOT/'transfers/transfer-audit.jsonl').read_bytes()
    assert hashlib.sha256(trans).hexdigest()==TRANSFER_HASH
    chosen={}
    for r in (json.loads(line) for line in trans.splitlines()):
        if r['kind']=='CHUNK' and r['transfer']=='AX-7782':
            k=r['seq']
            if k not in chosen or r['attempt']>chosen[k]['attempt']:chosen[k]=r
    assert sorted(chosen)==list(range(8))
    e=b''.join(bytes.fromhex(chosen[i]['checkpoint']) for i in range(8))
    result=dict(zip(EXPECTED, (a,b,c,d,e)))
    assert all(value.hex().upper()==EXPECTED[k] for k,value in result.items()), result
    accepted=json.loads((ROOT.parent/'acceptance.json').read_text())['slot_sha256']
    selected={'K01':'049AAB2E1CDE7A82CD7C60234303C91A',
              'K02':hashlib.sha256(b).hexdigest()[:32].upper(),
              'K05':'FF8B78200A56E8586DCDA00EF01E4572',
              'K06':'5DBF40EE52FAAED9A536D3326CF0D95A',
              'K07':hashlib.sha256(e).hexdigest()[:32].upper()}
    for k,component in selected.items():
        assert hashlib.sha256(bytes.fromhex(component)).hexdigest()==accepted[k]
    return result


def layouts(data, wordsize):
    words=[data[i:i+wordsize] for i in range(0,16,wordsize)]
    for endian in ('little','big'):
        vec=tuple(int.from_bytes(w,endian) for w in words)
        yield endian+'-forward',vec
        yield endian+'-reverse',vec[::-1]


def serialize(words, layout, wordsize):
    endian,direction=layout.split('-')
    if direction=='reverse':words=words[::-1]
    return b''.join(w.to_bytes(wordsize,endian) for w in words)


def rotate(x,k):return ((x<<k)|(x>>(32-k)))&MASK32

def xorshift128(state):
    x,y,z,w=state
    t=(x^(x<<11))&MASK32
    nw=(w^(w>>19)^t^(t>>8))&MASK32
    return (y,z,w,nw)


def xoshiro_step(s,version):
    a,b,c,d=s
    v=b if version==11 else a
    out=rotate(v*5&MASK32,7)*9&MASK32
    t=b<<9&MASK32
    c^=a; d^=b; b^=c; a^=d; c^=t;d=rotate(d,11)
    return (a&MASK32,b&MASK32,c&MASK32,d),out


def inv_mix32(z):
    z=z*pow(9,-1,1<<32)&MASK32
    z=((z>>7)|(z<<25))&MASK32
    return z*pow(5,-1,1<<32)&MASK32


def state_from_four_xoshiro(observed,version):
    col=[]
    srcpos=1 if version==11 else 0
    for bit in range(128):
        basis=tuple((1<<(bit%32)) if i==bit//32 else 0 for i in range(4))
        out=0
        for j in range(4):
            out|=basis[srcpos]<<(32*j)
            basis,_=xoshiro_step(basis,version)
        col.append(out)
    rhs=sum(inv_mix32(y)<<(32*i) for i,y in enumerate(observed))
    reduced={}
    for eqbit in range(128):
        row=sum(((col[i]>>eqbit)&1)<<i for i in range(128))
        row|=((rhs>>eqbit)&1)<<128
        while row:
            variable=row&((1<<128)-1)
            assert variable, 'source observations contradict xoshiro linear state equations'
            pivot=variable.bit_length()-1
            if pivot not in reduced:
                reduced[pivot]=row
                break
            row^=reduced[pivot]
    assert len(reduced)==128,('not uniquely invertible',version,len(reduced))
    result=0
    for pivot,row in sorted(reduced.items()):
        if ((row>>128)^((row&result).bit_count()&1))&1:result|=1<<pivot
    state=tuple((result>>(32*i))&MASK32 for i in range(4))
    replay=[];cur=state
    for _ in range(4):
        cur,w=xoshiro_step(cur,version);replay.append(w)
    assert tuple(replay)==observed
    return state


def undo_right64(y,n):
    x=y
    for _ in range(1+64//n):x=y^(x>>n)
    return x&MASK64


def unmix64(v,kind):
    if kind=='stafford':
        v=undo_right64(v,31)
        v=v*pow(0x94D049BB133111EB,-1,1<<64)&MASK64
        v=undo_right64(v,27)
        v=v*pow(0xBF58476D1CE4E5B9,-1,1<<64)&MASK64
        return undo_right64(v,30)
    v=undo_right64(v,33)
    v=v*pow(0xC4CEB9FE1A85EC53,-1,1<<64)&MASK64
    v=undo_right64(v,33)
    v=v*pow(0xFF51AFD7ED558CCD,-1,1<<64)&MASK64
    return undo_right64(v,33)


def mix64(v,kind):
    if kind=='stafford':
        v=(v^(v>>30))*0xBF58476D1CE4E5B9&MASK64
        v=(v^(v>>27))*0x94D049BB133111EB&MASK64
        return v^(v>>31)
    v=(v^(v>>33))*0xFF51AFD7ED558CCD&MASK64
    v=(v^(v>>33))*0xC4CEB9FE1A85EC53&MASK64
    return v^(v>>33)


def search(source,engine,horizon=8192):
    target=json.loads((ROOT.parent/'acceptance.json').read_text())['slot_sha256']['K04']
    mask=bytes.fromhex(json.loads((ROOT/'recovery-routing.json').read_text())['K04']['masked_component'])
    wordsize=8 if engine.startswith('splitmix') else 4
    n=16//wordsize
    destinations={}
    for name,block in source.items():
        for v,words in layouts(block,wordsize):destinations.setdefault(words,[]).append((name,v))
    original=[]
    examined=0;source_hits=0
    kinds={'splitmix-stafford':'stafford','splitmix-murmur':'murmur'}
    for name,block in source.items():
        for layout,observed in layouts(block,wordsize):
            if engine=='xorshift128':
                cur=tuple(observed)
                def forward():
                    nonlocal cur
                    cur=xorshift128(cur)
                    return cur[-1]
            elif engine.startswith('xoshiro'):
                version=11 if engine=='xoshiro11' else 10
                cur=state_from_four_xoshiro(tuple(observed),version)
                for _ in range(4):cur,_=xoshiro_step(cur,version)
                def forward():
                    nonlocal cur
                    cur,out=xoshiro_step(cur,version)
                    return out
            else:
                kind=kinds[engine]
                first,second=map(lambda w:unmix64(w,kind),observed)
                gamma=(second-first)&MASK64
                cur=second
                def forward():
                    nonlocal cur
                    cur=(cur+gamma)&MASK64
                    return mix64(cur,kind)
            window=deque(maxlen=n)
            for offset in range(horizon+n-1):
                window.append(forward())
                if len(window)<n:continue
                words=tuple(window)
                for other,view in destinations.get(words,()):
                    if other!=name:source_hits+=1
                for presentation in (i[0] for i in layouts(bytes(16),wordsize)):
                    coupon=serialize(words,presentation,wordsize)
                    component=bytes(x^y for x,y in zip(coupon,mask))
                    if hashlib.sha256(component).hexdigest()==target:
                        original.append((engine,name,layout,presentation,offset-n+1,coupon.hex(),component.hex()))
                    examined+=1
    print('ORIGINAL',engine,'anchors',len(source)*4,'horizon',horizon,'source_matches',source_hits,'full_candidate_checks',examined,'target_hits',original)
    assert source_hits==0 and original==[]
    assert examined==len(source)*4*horizon*4
    return examined


def planted_controls():
    initial=(0x11223344,0x99AABBCC,0x76543210,0xA5D0C3E7)
    early=serialize(initial,'little-forward',4)
    st=initial
    for _ in range(23):st=xorshift128(st)
    later=serialize(st,'little-forward',4)
    state=tuple(next(layouts(early,4))[1]);
    for _ in range(23):state=xorshift128(state)
    assert serialize(state,'little-forward',4)==later
    for version in (10,11):
        s=initial
        outputs=[]
        for _ in range(53):s,v=xoshiro_step(s,version);outputs.append(v)
        recovered=state_from_four_xoshiro(tuple(outputs[:4]),version)
        assert recovered==initial
        for _ in range(49):recovered,_=xoshiro_step(recovered,version)
        got=[]
        for _ in range(4):recovered,v=xoshiro_step(recovered,version);got.append(v)
        assert got==outputs[49:53]
        assert recovered==s
    for kind in ('stafford','murmur'):
        start=0xDEF0ACE710203040;gamma=0x9e3779b97f4a7c15
        packets=[mix64((start+i*gamma)&MASK64,kind) for i in range(15)]
        assert all(unmix64(x,kind)==(start+i*gamma)&MASK64 for i,x in enumerate(packets))
        recovered=(unmix64(packets[1],kind)-unmix64(packets[0],kind))&MASK64
        assert recovered==gamma
        assert mix64((unmix64(packets[1],kind)+13*recovered)&MASK64,kind)==packets[14]
    print('SYNTHETIC planted xorshift128/xoshiro128-1.0/1.1/SplitMix Stafford/Murmur positives PASS')


def main():
    source=source_blocks(); print('SOURCE_SELECTED',[(k,v.hex().upper()) for k,v in source.items()])
    planted_controls()
    total=0
    for engine in ('xorshift128','xoshiro11','xoshiro10','splitmix-stafford','splitmix-murmur'):
        total+=search(source,engine)
    print('COMPLETE source-only gate and original SHA256 target: assignments',total,'K04=missing K08=missing')

if __name__=='__main__': main()
