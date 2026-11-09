"""Threefry4x32-20 source-keyed H-17 K04 issuer test (read-only)."""
from __future__ import annotations
import hashlib
import json
import re
import struct
from pathlib import Path
from datetime import datetime

ROT = [(10,26),(11,21),(13,27),(23,5),(6,20),(17,11),(25,10),(18,20)]
MASK32=(1<<32)-1
KAT=[
 ((0,)*4,(0,)*4,(0x9c6ca96a,0xe17eae66,0xfc10ecd4,0x5256a7d8)),
 ((MASK32,)*4,(MASK32,)*4,(0x2a881696,0x57012287,0xf6c7446e,0xa16a6732)),
 ((0x243f6a88,0x85a308d3,0x13198a2e,0x03707344),(0xa4093822,0x299f31d0,0x082efa98,0xec4e6c89),(0x59cd1dbb,0xb8879579,0x86b5d00c,0xac8b6d84)),
]


def rol(x: int, r: int) -> int:
    return ((x << r) | (x >> (32-r))) & MASK32


def threefry(ctr: tuple[int, ...], key: tuple[int, ...]) -> tuple[int, ...]:
    """Random123 reference Threefry4x32_R<20> (same output word order)."""
    ks=(*key,0x1bd11bda ^ key[0] ^ key[1] ^ key[2] ^ key[3])
    x=[(ctr[i]+ks[i])&MASK32 for i in range(4)]
    for r in range(20):
        a,b=ROT[r%8]
        if r%2==0:
            x[0]=(x[0]+x[1])&MASK32
            x[1]=rol(x[1],a)^x[0]
            x[2]=(x[2]+x[3])&MASK32
            x[3]=rol(x[3],b)^x[2]
        else:
            x[0]=(x[0]+x[3])&MASK32
            x[3]=rol(x[3],a)^x[0]
            x[2]=(x[2]+x[1])&MASK32
            x[1]=rol(x[1],b)^x[2]
        if r%4==3:
            s=(r+1)//4
            for j in range(4):
                x[j]=(x[j]+ks[(s+j)%5])&MASK32
            x[3]=(x[3]+s)&MASK32
    return tuple(x)


def record(line: str) -> dict:
    tokens=line.split()
    p=dict(t.split('=',1) for t in tokens[1:])
    p['time']=datetime.fromisoformat(tokens[0].replace('Z','+00:00'))
    return p


def counters(r: dict, idx: int) -> list[tuple[int,...]]:
    job=int(r['JOB'][-4:])
    att=int(r['ATTEMPT'])
    d=r['time']
    hhmm=d.hour*100+d.minute
    minute=d.hour*60+d.minute
    sec=int(d.timestamp())&MASK32
    cls={'LABEL':0,'STORES':1,'RECOVER':2}[r['CLASS']]
    dst={'store':0,'bench':1,'desk':2}[r['DEST']]
    jid_hash=int.from_bytes(hashlib.sha256(r['JOB'].encode('ascii')).digest()[:4],'little')
    return [
       (job,att,0,0), (job,0,0,0), (job,att,cls,dst),
       (job,att,minute,d.timetuple().tm_yday),
       (job,att,int(d.strftime('%Y%m%d')),hhmm),
       (sec,job,att,0), (sec,att,cls,dst),
       (idx,att,0,0), (idx,0,0,0),
       (jid_hash,att,0,0),
       (job,att,int(d.strftime('%Y%m%d')),0),
       (job,att,hhmm,0),
    ]


def keys(root: Path) -> list[tuple[str,bytes]]:
    route=json.loads((root/'evidence/recovery-routing.json').read_text())
    d=[('route-mask',bytes.fromhex(route['K04']['masked_component'])),('desk-nonce',bytes.fromhex(route['K08']['desk_nonce']))]
    accepted={
      'K01':'049AAB2E1CDE7A82CD7C60234303C91A',
      'K02':'0D7E3AB56FB75DA3EB0E2E06786D239E',
      'K03':'1384AF96E25D6ADA666209CB55E062FA',
      'K05':'FF8B78200A56E8586DCDA00EF01E4572',
      'K06':'5DBF40EE52FAAED9A536D3326CF0D95A',
      'K07':'93495F5E425AB8E592123DABAEB68545',
    }
    commitment=json.loads((root/'acceptance.json').read_text())['slot_sha256']
    for name,s in accepted.items():
        raw=bytes.fromhex(s)
        assert hashlib.sha256(raw).hexdigest()==commitment[name]
        d.append((name,raw))
    return d


def test(root: Path) -> dict:
    for ctr,key,expected in KAT:
        assert threefry(ctr,key)==expected,(ctr,key,threefry(ctr,key))
    spool=(root/'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(spool).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
    rows=[record(line) for line in spool.decode().splitlines() if line and not line.startswith('#')]
    assert len(rows)==133
    target=[(i,r) for i,r in enumerate(rows) if r['JOB']=='PS-261003-0417' and r['ATTEMPT']=='2' and r['STATE']=='ACK' and r['CLASS']=='RECOVER']
    assert len(target)==1 and target[0][1]['time'].isoformat()=='2026-10-03T18:02:00+00:00'
    other=[(i,r) for i,r in enumerate(rows) if (r['JOB'],r['ATTEMPT'],r['CLASS'],r['STATE']) in {
        ('PS-261003-0420','2','RECOVER','ACK'),('PS-261003-0448','1','RECOVER','ACK')}]
    assert len(other)==2
    mask=bytes.fromhex(json.loads((root/'evidence/recovery-routing.json').read_text())['K04']['masked_component'])
    digest=json.loads((root/'acceptance.json').read_text())['slot_sha256']['K04']
    checks=0; control_hits=0; hits=[]
    # All source-defined key words in both native word byte orders,
    # all exact 12 event-counter representations, and four output serializations.
    for name,key_b in keys(root):
        for key_endian in ('<','>'):
            key=struct.unpack(key_endian+'4I',key_b)
            for c in range(12):
                for output_endian in ('<','>'):
                    for rev in (False,True):
                        config=(name,key_endian,c,output_endian,rev)
                        def emit(e):
                            i,r=e
                            ctr=counters(r,i)[c]
                            words=threefry(ctr,key)
                            if rev: words=words[::-1]
                            return struct.pack(output_endian+'4I',*words)
                        control_hits+=sum(emit(e).hex().upper()==e[1]['PAYLOAD'] for e in other)
                        candidate=bytes(a^b for a,b in zip(emit(target[0]),mask))
                        checks+=1
                        if hashlib.sha256(candidate).hexdigest()==digest:
                            hits.append({'config':config,'component':candidate.hex().upper()})
    return {'model':'Random123 Threefry4x32-20 keyed by eight authentic source fields',
            'source_packets':len(rows),'heldout_other_acked':len(other),
            'source_holdout_complete_hits':control_hits,'target_complete_sha_checks':checks,
            'original_K04_hits':hits,'reference_kats':len(KAT)}


if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]/'resources'
    print(json.dumps(test(root),indent=2))
