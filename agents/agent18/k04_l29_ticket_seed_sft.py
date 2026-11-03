"""Read-only H17 K04 source-joined L29/N ledger seed / direct coupon test.
Run from repository root: python agents/agent18/k04_l29_ticket_seed_sft.py.
Does not modify official source, selected ACK, route, candidate or verifier.
"""
from pathlib import Path
import re, csv, io, json, hashlib, hmac, random

RES=Path(__file__).resolve().parents[2]/'resources'
note=(RES/'evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt').read_text()
csvtxt=(RES/'evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv').read_text()
route=json.loads((RES/'evidence/recovery-routing.json').read_text())
mask=bytes.fromhex(route['K04']['masked_component'])
accept=json.loads((RES/'acceptance.json').read_text())['slot_sha256']['K04']
assert 'PS-261003-0417   ESC-N' in note
part=note[note.index('L-29/N    01'):]
tickets=[]
for line in part.splitlines():
    m=re.match(r'L-29/N\s+(\d{2})\s+(ST-\d{3})\s+(.+)$',line)
    if m: tickets.append((int(m[1]),m[2],m[3]))
    elif len(tickets)>=5:break
assert [(i,t) for i,t,_ in tickets]==[(1,'ST-094'),(2,'ST-081'),(3,'ST-106'),(4,'ST-099'),(5,'ST-112')]
dockets=list(csv.DictReader(io.StringIO('\n'.join(x for x in csvtxt.splitlines() if not x.startswith('#')))))
rows=[]
for _,ticket,part in tickets:
    found=[d for d in dockets if d['line_ref']==ticket and d['run']=='R3' and d['posting']=='POSTED'
           and d['account']=='FA-17' and d['folio_or_jacket']=='H17-POL-17/A3']
    assert len(found)==1
    rows.append((ticket,found[0]['amount_eur'],part))
print('ORIGINAL_CROSS_FILE_TICKET_ROWS',rows)
digit=[t[3:] for t,_,_ in rows]
numer=[str(int(n)) for n in digit]
tag=[t for t,_,_ in rows]
cents=[str(int(round(float(v)*100))) for _,v,_ in rows]
strings=set()
for direction in (1,-1):
    for values in (digit,numer,tag,cents):
        vv=values[::direction]
        for sep in ('','|',',','-',' ',':','/','\n'):
            base=sep.join(vv)
            for form in ('{}','L29/N:{}','PS-261003-0417:{}','FA-17:{}','H17-POL-17/A3:{}','ESC-N:{}','{}:R3','{}:POSTED'):
                strings.add(form.format(base))
assert len(strings)==512
seeds=set()
for st in strings:
    raw=st.encode('ascii')
    for obj in (raw,hashlib.sha256(raw).digest(),hashlib.md5(raw).digest()):
        seeds.add(obj)
        seeds.add(int.from_bytes(obj,'little'))
        seeds.add(int.from_bytes(obj,'big'))
checks=0
hits=[]
for seed in seeds:
    gen=random.Random(seed)
    words=[gen.getrandbits(32) for _ in range(132)]
    for offset in range(129):
        for endian in ('little','big'):
            four=[w.to_bytes(4,endian) for w in words[offset:offset+4]]
            for arrangement in (four,four[::-1]):
                raw=b''.join(arrangement)
                candidate=bytes(x^y for x,y in zip(raw,mask))
                checks+=1
                if hashlib.sha256(candidate).hexdigest()==accept:hits.append((repr(seed),offset,candidate.hex()))
for st in strings:
    raw=st.encode('ascii')
    d=(hashlib.sha256(raw).digest(),hashlib.sha512(raw).digest(),
       hashlib.blake2b(raw).digest(),hashlib.md5(raw).digest(),hmac.digest(mask,raw,'sha256'))
    for item in d:
        for rawcoupon in (item[:16],item[-16:]):
            for cand in (rawcoupon,bytes(x^y for x,y in zip(rawcoupon,mask))):
                checks+=1
                if hashlib.sha256(cand).hexdigest()==accept:hits.append(('DIGEST',st,cand.hex()))
print('SOURCE_STRINGS',len(strings),'SEEDS',len(seeds),'K04_TESTS',checks,'REAL_MATCHES',len(hits))
assert checks==2387968 and not hits
testseed=int(''.join(digit))
gen=random.Random(testseed)
source=[gen.getrandbits(32) for _ in range(20)]
planted=bytes(x^y for x,y in zip(b''.join(w.to_bytes(4,'little') for w in source[7:11]),mask))
replay=random.Random(testseed)
again=[replay.getrandbits(32) for _ in range(20)]
assert bytes(x^y for x,y in zip(b''.join(w.to_bytes(4,'little') for w in again[7:11]),mask))==planted
print('SOURCE_SEED_SYNTHETIC_COUPON_POSITIVE PASS')
