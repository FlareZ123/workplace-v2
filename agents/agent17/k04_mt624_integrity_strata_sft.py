#!/usr/bin/env python3
"""Original H-17 source-conditioned, synthetic-controlled MT624 512+84+28 test.

Only reports aggregate outcomes; never prints component candidates, source words,
or per-candidate commitment diagnostics. Does not read quarantined PDF content.
Default root is repository/resources; optionally pass source root as argv[1].
"""
import hashlib
import itertools
import json
import random
import re
import struct
import sys
import zlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'
E = ROOT/'evidence'
PIN = {
    'print/spool-reconstruction.log': '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
    'recorder/trip-recorder.raw': '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba',
}
for path, want in PIN.items():
    assert hashlib.sha256((E/path).read_bytes()).hexdigest()==want, path

ordinary=[]
late={}
for line in (E/'print/spool-reconstruction.log').read_text().splitlines():
    if not line.startswith('2026-10-03'):continue
    d=dict(re.findall(r'([A-Z]+)=([^\s]+)',line))
    job=int(d['JOB'].rsplit('-',1)[-1])
    attempt=int(d['ATTEMPT'])
    if 300<=job<=427 and attempt==1 and line[11:16]<'18:00':
        ordinary.append((job,bytes.fromhex(d['PAYLOAD'])))
    if (job,attempt) in {(417,1),(417,3),(448,1),(420,2)} and line[11:16]>='18:00':
        late[(job,attempt)]=bytes.fromhex(d['PAYLOAD'])
assert len(ordinary)==128 and [r[0] for r in ordinary]==list(range(300,428))
assert len(late)==4

raw=(E/'recorder/trip-recorder.raw').read_bytes()
assert len(raw)==16+88*24
valid=[]
for i in range(88):
    b=raw[16+i*24:16+(i+1)*24]
    if (zlib.crc32(b[:20])&0xffffffff)!=int.from_bytes(b[20:24],'little'):
        continue
    ts,node,event,latch,seq=struct.unpack_from('<IHBBI',b)
    valid.append((i,ts,node,event,latch,seq,b[12:16]))
assert len(valid)==84

seals=[json.loads(x) for x in (E/'maintenance/seal-receipts.jsonl').read_text().splitlines() if x]
bypermit=defaultdict(list)
for i,r in enumerate(seals):
    if r['signed'] and r['state']=='CLOSED' and r['fitment']=='AS_LEFT':
        bypermit[r['permit']].append((i,r))
assert set(bypermit)=={f'PTW-{p:03d}' for p in range(390,418)}
assert all(len(bypermit[f'PTW-{p:03d}'])==1 for p in range(390,417))
last={bay:max((r for _,r in bypermit['PTW-417'] if r['bay']==bay),key=lambda r:r['revision']) for bay in 'ABCD'}
assert all(re.fullmatch('SG-[0-9A-F]{8}',r['serial']) for r in last.values())

def unpack(data,big=False,reverse=False):
    w=[data[i:i+4] for i in range(0,len(data),4)]
    if reverse:w.reverse()
    return [int.from_bytes(x,'big' if big else 'little') for x in w]

def reverse_right(y,s):
    v=y
    for _ in range(6):v=y^(v>>s)
    return v&0xffffffff

def reverse_left(y,s,m):
    v=y
    for _ in range(6):v=y^((v<<s)&m)
    return v&0xffffffff

def untemper(y):
    y=reverse_right(y,18)
    y=reverse_left(y,15,0xEFC60000)
    y=reverse_left(y,7,0x9D2C5680)
    return reverse_right(y,11)

def temper(y):
    y^=y>>11;y^=(y<<7)&0x9D2C5680
    y^=(y<<15)&0xEFC60000
    return (y^(y>>18))&0xffffffff

def predict(observed,howmany=1024):
    assert len(observed)==624
    rng=random.Random(0)
    rng.setstate((3,tuple([untemper(x) for x in observed]+[624]),None))
    return [rng.getrandbits(32) for _ in range(howmany)]

# Genuine independent same-producer positive control, 1024 future full words.
rng=random.Random(20261128)
first=[rng.getrandbits(32) for _ in range(624)]
later=[rng.getrandbits(32) for _ in range(1024)]
assert all(temper(untemper(x))==x for x in first)
assert predict(first)==later

route=json.loads((E/'recovery-routing.json').read_text())
mask=bytes.fromhex(route['K04']['masked_component'])
original=json.loads((ROOT/'acceptance.json').read_text())['slot_sha256']['K04']
seen=0
candidate_checks=0
commit_hits=0
late_hits=0
late_set=set(late.values())
perm_orders=tuple(itertools.permutations(('print','recorder','seal')))
for bay,rec_order,seal_order,sp_big,sp_rev,rec_big,seal_big,order in itertools.product(
        'ABCD',('file','stamp'),('permit','file'),
        (False,True),(False,True),(False,True),(False,True),perm_orders):
    pw=[v for _,packet in ordinary for v in unpack(packet,sp_big,sp_rev)]
    rr=valid if rec_order=='file' else sorted(valid,key=lambda r:(r[1],r[2],r[3],r[5],r[4],r[0]))
    rw=[int.from_bytes(r[6],'big' if rec_big else 'little') for r in rr]
    ordered=sorted(bypermit) if seal_order=='permit' else sorted(bypermit,key=lambda p:bypermit[p][0][0])
    sw=[]
    for permit in ordered:
        r=last[bay] if permit=='PTW-417' else bypermit[permit][0][1]
        sw.append(int.from_bytes(bytes.fromhex(r['serial'][3:]),'big' if seal_big else 'little'))
    assert (len(pw),len(rw),len(sw))==(512,84,28)
    source={'print':pw,'recorder':rw,'seal':sw}
    state=[w for group in order for w in source[group]]
    out=predict(state)
    seen+=1
    for endian,reverse in itertools.product(('big','little'),(False,True)):
        words=[w.to_bytes(4,endian) for w in out]
        for at in range(1021):
            coupon=b''.join(words[at:at+4][::-1] if reverse else words[at:at+4])
            if coupon in late_set:late_hits+=1
            component=bytes(a^b for a,b in zip(coupon,mask))
            if hashlib.sha256(component).hexdigest()==original:
                commit_hits+=1
            candidate_checks+=1
assert seen==1536 and candidate_checks==seen*1021*4
print('SYNTHETIC_MT624_PASS')
print('STRATA 512+84+28')
print('STRUCTURED_MODELS',seen)
print('COMPLETE_COUPON_TRIALS',candidate_checks)
print('INTACT_LATE_PACKET_MATCHES',late_hits)
print('K04_ACCEPTED_TRIALS',commit_hits)
