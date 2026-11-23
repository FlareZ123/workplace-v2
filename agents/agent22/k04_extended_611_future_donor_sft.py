#!/usr/bin/env python3
"""H-17 K04: original-source fourfresh future donor, extended carrier classes.

Run: python agents/agent22/k04_extended_611_future_donor_sft.py [resources]
Requires the existing Agent10 three read-only MT source modules.
The selected 18:02 attempt2 copied PAYLOAD is excluded before any decoding.
This conditional model does NOT authenticate historical printer firmware.
"""
import collections, hashlib, itertools, json, re, struct, sys, zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents/agent10"))
from k04_all42_wholewindow_sft import ALT_STAGES,SPOOL_SHA,K04_SHA,build_basis,symbolic_words,untemper,temper
from k04_all42_fourfresh_countermodel_sft import GAP_DELTAS,full_state,native_word
from k04_fourfresh_future_source_donor_sft import BLOCKS,donor_mapping,donor_bits_from_block,map_native
import random

res=Path(sys.argv[1]) if len(sys.argv)==2 else ROOT/"resources"
spool=(res/"evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest()==SPOOL_SHA
rows=re.findall(rb'^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$',spool,re.M)
assert len(rows)==133 and rows[129][:5]==(b'2026-10-03T18:02:00Z',b'PS-261003-0417',b'2',b'ACK',b'RECOVER')
native=[None if i==129 else tuple(untemper(int.from_bytes(bytes.fromhex(r[5].decode())[4*j:4*j+4],'little')) for j in range(4)) for i,r in enumerate(rows)]
gaps=[ALT_STAGES[i+1]-ALT_STAGES[i]+GAP_DELTAS.get(i,0) for i in range(132)]
assert min(gaps)>=4 and max(gaps)<=16
starts=[0]
for d in gaps: starts.append(starts[-1]+d)
assert starts[128:133]==[951,955,959,963,968]
ex=symbolic_words(0,1867)
basis=build_basis(native,tuple(starts),ex,0)
assert len(basis)==15434
maps={q:donor_mapping(basis,ex,955,q) for q in (1409,1863)}
assert all(m is not None and len(m)==128 for m in maps.values())

# True positive: a full source-fitted synthetic state has the same coupon
# when the two source-selected future native donor quartets are mapped back.
free=random.Random(20261123).getrandbits(19968)
for p in basis: free&=~(1<<p)
state=full_state(basis,free)
target=b''.join(temper(native_word(state,ex[955+j])).to_bytes(4,'little') for j in range(4))
assert target!=b'\0'*16
for q,m in maps.items():
    bits=sum(native_word(state,ex[q+j])<<(32*j) for j in range(4))
    assert map_native(bits,m)==target
route=json.loads((res/"evidence/recovery-routing.json").read_text())
accept=json.loads((res/"acceptance.json").read_text())
mask=bytes.fromhex(route['K04']['masked_component'])
assert mask.hex().upper()==BLOCKS['K04_route_mask']
assert accept['slot_sha256']['K04']==K04_SHA

sources={}
classes=collections.Counter()
def add(label,buffer):
    if len(buffer)==16 and buffer not in sources:
        sources[buffer]=label
        classes[label.split(':',1)[0]]+=1

for p in (res/"evidence").rglob('*'):
    if not p.is_file() or p.name=='BX25-08.pdf':continue
    data=p.read_bytes()
    if p.name=='spool-reconstruction.log':
        data=b'\n'.join(ln for ln in data.splitlines() if not (b'JOB=PS-261003-0417' in ln and b'ATTEMPT=2 STATE=ACK' in ln))
    for hit in re.finditer(rb'(?<![0-9A-Fa-f])([0-9A-Fa-f]{32})(?![0-9A-Fa-f])',data):
        add('HEX32:'+p.name,bytes.fromhex(hit[1].decode()))

raw=(res/"evidence/recorder/trip-recorder.raw").read_bytes()
assert raw[:8]==b'TRP2DUMP'
recs=[]
for i in range(88):
    packet=raw[16+24*i:16+24*(i+1)]
    _,node,event,latch,seq,control,aux,crc=struct.unpack('<IHBBI4sII',packet)
    recs.append((node,event,latch,seq,control,crc==zlib.crc32(packet[:20])))
for good in (False,True):
    group=[r for r in recs if r[5] or not good]
    for order,arr in (('raw',group),('event',sorted(group,key=lambda r:(r[1],r[0],r[3],r[2]))),('utc',sorted(group,key=lambda r:(r[0],r[1],r[3],r[2])))):
        for i in range(len(arr)-3):add(f'TRP2:{good}:{order}:{i}',b''.join(x[4] for x in arr[i:i+4]))
for node,event in sorted(set((r[0],r[1]) for r in recs)):
    for good in (False,True):
        group=sorted((r for r in recs if r[0]==node and r[1]==event and (r[5] or not good)),key=lambda x:x[3])
        for i in range(len(group)-3):add(f'TRP2:{node}:{event}:{good}:{i}',b''.join(r[4] for r in group[i:i+4]))

transfer=[json.loads(ln) for ln in (res/"evidence/transfers/transfer-audit.jsonl").read_text().splitlines()]
for tx in sorted(set(r['transfer'] for r in transfer if 'transfer' in r)):
    chunks=[r for r in transfer if r.get('kind')=='CHUNK' and r['transfer']==tx]
    for key in ('seq','attempt'):
        chunks=sorted(chunks,key=lambda r:(r[key],r['seq'],r['attempt']))
        cs=[bytes.fromhex(r['checkpoint']) for r in chunks]
        if all(len(w)==2 for w in cs):
            for j in range(len(cs)-7): add(f'AX:{tx}:{key}:{j}',b''.join(cs[j:j+8]))

seals=[json.loads(ln) for ln in (res/"evidence/maintenance/seal-receipts.jsonl").read_text().splitlines()]
for key,rs in (('raw',seals),('bay',sorted(seals,key=lambda r:(r['bay'],r.get('revision',0))))):
    cs=[bytes.fromhex(r['serial'].split('-')[-1]) for r in rs]
    for j in range(len(cs)-3):add(f'SEAL:{key}:{j}',b''.join(cs[j:j+4]))
for permit in sorted(set(r['permit'] for r in seals)):
    rs=sorted([r for r in seals if r['permit']==permit],key=lambda r:(r['bay'],r.get('revision',0)))
    cs=[bytes.fromhex(r['serial'].split('-')[-1]) for r in rs]
    for j in range(len(cs)-3):add(f'SEAL:{permit}:{j}',b''.join(cs[j:j+4]))

strips=[bytes.fromhex(h) for h in re.findall(r'Footer control strip:\s*([0-9A-F]{8})',(res/"evidence/procedures/RC-17-scans.txt").read_text())]
for j in range(len(strips)-3):add(f'RC17:scan:{j}',b''.join(strips[j:j+4]))

tele=[json.loads(ln) for ln in (res/"evidence/telemetry/freeze-export.jsonl").read_text().splitlines()]
groups=(
 ('all',tele),
 ('diag',[r for r in tele if r.get('field')=='DIAG_WORD']),
 ('LT204',[r for r in tele if r.get('tag')=='LT-204' and r.get('field')=='DIAG_WORD']),
 ('GH',[r for r in tele if r.get('tag')=='LT-204' and r.get('field')=='DIAG_WORD' and r.get('quality')=='GOOD' and r.get('state')=='HOLD'])
)
for label,group in groups:
    for order,arr in (('raw',group),('seq',sorted(group,key=lambda r:(r.get('seq',0),r.get('revision',0))))),('time',sorted(group,key=lambda r:r.get('ts','')))):
        cs=[int(r['value']).to_bytes(2,'big') for r in arr if isinstance(r.get('value'),int) and 0<=r['value']<=65535]
        for j in range(len(cs)-7):add(f'TEL:{label}:{order}:{j}',b''.join(cs[j:j+8]))
for name,value in json.loads((res/"candidate.json").read_text()).items():
    if isinstance(value,str) and re.fullmatch(r'[0-9A-F]{32}',value):add('ACCEPTED:'+name,bytes.fromhex(value))
add('K04MASK',mask);add('K08NONCE',bytes.fromhex(route['K08']['desk_nonce']))
assert bytes.fromhex(rows[129][5].decode()) not in sources
assert len(sources)==611,len(sources)
assert sum(classes.values())==611
assert dict(classes)=={'HEX32':134,'TRP2':188,'AX':72,'SEAL':95,'RC17':9,'TEL':108,'ACCEPTED':5},classes

checked=0;hits=[];predictions={q:set() for q in maps}
for value,label in sources.items():
    for order in itertools.permutations(range(4)):
        for endian in ('little','big'):
            for native_input in (False,True):
                b=donor_bits_from_block(value,order,endian,native_input)
                for q,projection in maps.items():
                    raw_coupon=map_native(b,projection)
                    predictions[q].add(raw_coupon)
                    component=bytes(x^y for x,y in zip(raw_coupon,mask))
                    checked+=1
                    if hashlib.sha256(component).hexdigest()==K04_SHA:
                        hits.append({'source':label,'future_stage':q,'order':order,
                                     'endian':endian,'native_input':native_input,
                                     'K04':component.hex().upper()})
assert checked==117312,checked
assert {q:len(predictions[q]) for q in maps}=={1409:58656,1863:58656}
assert len(predictions[1409]&predictions[1863])==0
assert not hits
print(json.dumps({
 'selected_ACK2_payload_decoded':False,
 'source_MT_rank':len(basis),
 'original_16byte_carriers':len(sources),
 'source_class_counts':dict(classes),
 'complete_original_K04_candidates_tested':checked,
 'independent_future_native_donor_sites':sorted(maps),
 'coupon_prediction_count_each_site':{str(q):len(predictions[q]) for q in maps},
 'cross_site_coupon_intersection':0,
 'positive_full_state_coupon_reconstructed_at_both_sites':True,
 'original_K04_hits':hits,
 'actual_K04_recovered':False},indent=2))
