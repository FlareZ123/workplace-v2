"""H17: exact source-only K02(stage1406) + K05 donor to K04 quotient audit.

Use: python agents/agent25/k04_stage1406_k05_target_rank_sft.py resources
Read-only. The speculative shared MT19937 publisher and cross-record stages are
not authenticated historical causes; this computes only conditional GF(2) ranks.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import struct
import sys
import zlib

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'agent49'))
import k04_p951_symbolic_basis as mt

ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path('resources')
mt.LAST=3500

def selected():
    acceptance=json.loads((ROOT/'acceptance.json').read_text())['slot_sha256']
    raw=(ROOT/'evidence/telemetry/freeze-export.jsonl').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'
    best={}
    for line in raw.splitlines():
        x=json.loads(line)
        if x.get('tag')!='LT-204' or x.get('field')!='DIAG_WORD' or x.get('quality')!='GOOD' or x.get('state')!='HOLD' or x.get('seq') not in range(8):continue
        if not datetime(2026,10,3,21,13,40,tzinfo=timezone.utc)<=datetime.fromisoformat(x['ts'])<datetime(2026,10,3,21,13,48,tzinfo=timezone.utc):continue
        i=x['seq']
        if i not in best or x['revision']>best[i]['revision']:best[i]=x
    assert sorted(best)==list(range(8))
    k02=b''.join(int(best[i]['value']).to_bytes(2,'big') for i in range(8))
    assert k02.hex().upper()=='E1A5E474BAD7E853A2E8C71D3317D507'
    assert hashlib.sha256(hashlib.sha256(k02).digest()[:16]).hexdigest()==acceptance['K02']
    raw=(ROOT/'evidence/recorder/trip-recorder.raw').read_bytes()
    assert raw[:8]==b'TRP2DUMP'
    ver,size,count=struct.unpack_from('<HHI',raw,8)
    assert ver==2 and size==24 and len(raw)==16+size*count
    best={}
    for i in range(count):
        b=raw[16+24*i:16+24*(i+1)]
        epoch,node,event,latch,seq=struct.unpack_from('<IHBBI',b)
        if zlib.crc32(b[:20])!=struct.unpack_from('<I',b,20)[0]:continue
        if node==49 and event==82 and 1791062040<=epoch<1791062048 and latch in range(4):
            if latch not in best or seq>best[latch][0]:best[latch]=(seq,b[12:16])
    assert sorted(best)==[0,1,2,3]
    k05=b''.join(best[i][1] for i in range(4))
    assert k05.hex().upper()=='FF8B78200A56E8586DCDA00EF01E4572'
    assert hashlib.sha256(k05).hexdigest()==acceptance['K05']
    return k02,k05

def views(raw):
    for endian in ('big','little'):
        for reverse in (False,True):
            for halves in (False,True):
                chunks=[raw[i:i+4] for i in (0,4,8,12)]
                if halves:chunks=[p[2:]+p[:2] for p in chunks]
                if reverse:chunks.reverse()
                vals=[int.from_bytes(c,endian) for c in chunks]
                for native in (False,True):
                    yield (endian,reverse,halves,native),[v if native else mt.untemper(v) for v in vals]

def expr(rows,v):
    rem=const=0
    while v:
        p=v.bit_length()-1
        if p in rows:
            w,c=rows[p];v^=w;const^=c
        else:rem|=1<<p;v^=1<<p
    return rem,const

def donor(rows,bank,start):
    """128 source-equation vectors; zero residual is a predicted source parity."""
    independent={};conditions=[]
    for j in range(128):
        lane,bit=divmod(j,32)
        v,c=expr(rows,mt.get(bank,start+lane)[bit]);tag=1<<j
        while v:
            p=v.bit_length()-1
            if p in independent:
                w,d,t=independent[p];v^=w;c^=d;tag^=t
            else:independent[p]=(v,c,tag);break
        if not v:conditions.append((tag,c))
    assert len(independent)+len(conditions)==128
    return independent,conditions

def target_dimension(target,independent):
    seen={}
    for res,_ in target:
        while res:
            p=res.bit_length()-1
            if p in independent:res^=independent[p][0]
            elif p in seen:res^=seen[p]
            else:seen[p]=res;break
    return len(seen)

def main():
    k02,k05=selected()
    source,bank=mt.source(ROOT)
    assert source.rank==15365
    models=[]
    for mode,values in views(k02):
        b=mt.Basis();b.rows=source.rows.copy();b.rank=source.rank
        try:
            for lane,w in enumerate(values):
                for bit,v in enumerate(mt.get(bank,1406+lane)):b.insert(v,(w>>bit)&1)
        except AssertionError:continue
        assert b.rank==15492
        models.append((mode,b))
    assert len(models)==10
    # Every K02 view changes observed constants, but the ten equation row
    # spaces coincide; a representative suffices for structural quotient rank.
    rowforms=[{p:v[0] for p,v in b.rows.items()} for _,b in models]
    assert all(forms==rowforms[0] for forms in rowforms)
    target=[expr(models[0][1].rows,v) for q in range(951,955) for v in mt.get(bank,q)]
    assert sum(r==0 for r,c in target)==95
    counts=Counter();interesting=[];high=0
    for q in range(-1100,3497):
        independent,conditions=donor(models[0][1].rows,bank,q)
        left=target_dimension(target,independent)
        if q<=1040:counts[left]+=1
        else:
            assert left==33
            if len(conditions)>=32:high+=1
        if left<33:interesting.append((q,len(conditions),left))
    assert counts=={33:2116,32:21,1:1,0:3}
    assert len(interesting)==25 and high==1264
    assert target_dimension(target,donor(models[0][1].rows,bank,951)[0])==0
    k05_views=[sum(w<<(32*i) for i,w in enumerate(words)) for _,words in views(k05)]
    usable=[];trivial=Counter()
    for mode,b in models:
        for q,pred,remaining in interesting:
            _,conditions=donor(b.rows,bank,q)
            for packed in k05_views:
                if all((tag&packed).bit_count()%2==c for tag,c in conditions):
                    trivial[(q,pred,remaining)]+=1
                    if pred>=2:usable.append((mode,q,pred,remaining))
    assert not usable
    assert trivial=={(-523,1,32):90,(724,0,32):160}
    print('SOURCE_PINS spool_rank=15365 k02_k05_acceptance=PASS k02_stage1406_compatible=10/16')
    print('EARLY_K05_DONOR target_dim',dict(sorted(counts.items())),'informative_stages',interesting)
    print('LATE_K05_DONOR q1041..3496=2456 target_dim33_each predicted_ge32_per_model',high)
    print('REAL_K05 informative_4000_assignments only_trivial_source_matches',dict(trivial),'usable=0')
    print('SYNTHETIC same_selected_stage_q951 target_dimension_zero=PASS')
    print('K04 selected physical coupon unresolved; conditional model only')

if __name__=='__main__':main()
