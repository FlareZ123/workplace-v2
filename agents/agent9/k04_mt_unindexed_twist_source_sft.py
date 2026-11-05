"""Unindexed source-only MT19937 recurrence fingerprint, H-17 K04 ACK2 withheld."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import random
import re
import runpy

ROOT=Path(__file__).resolve().parents[2]
SPOOL=ROOT/'resources/evidence/print/spool-reconstruction.log'
original=SPOOL.read_bytes()
assert hashlib.sha256(original).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
records=[]
for line in original.decode().splitlines():
    m=re.search(r'JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32})',line)
    if m:
        records.append((m[1],int(m[2]),m[3],m[4],bytes.fromhex(m[5])))
assert len(records)==133
assert records[129][:4]==('PS-261003-0417',2,'ACK','RECOVER')
packets=[r[4] for i,r in enumerate(records) if i!=129]
assert len(packets)==132
U32=0xffffffff

def untemper(v:int)->int:
    v^=v>>18
    v^=(v<<15)&0xefc60000
    x=v
    for _ in range(5):v=x^((v<<7)&0x9d2c5680)
    x=v
    for _ in range(3):v=x^(v>>11)
    return v&U32

def temper(v:int)->int:
    v^=v>>11
    v^=(v<<7)&0x9d2c5680
    v^=(v<<15)&0xefc60000
    v^=v>>18
    return v&U32

def mix(a:int,b:int)->int:
    y=(a&0x80000000)|(b&0x7fffffff)
    return (y>>1)^(0x9908b0df if y&1 else 0)

def native(data:list[bytes],endian:str='little',reverse:bool=False,undo:bool=True)->list[int]:
    out=[]
    for packet in data:
        w=[int.from_bytes(packet[i:i+4],endian) for i in range(0,16,4)]
        if reverse:w.reverse()
        out.extend(untemper(x) if undo else x for x in w)
    return out

def links(values:list[int])->list[tuple[int,int,int,int]]:
    # Discover full 32-bit MT relations with no native positions assumed.
    table={}
    n=len(values)
    for k in range(n):
        for l in range(k+32,min(n,k+251)):
            table.setdefault(values[k]^values[l],[]).append((k,l))
    out=[]
    for i in range(n):
        if i%4==3:continue
        for k,l in table.get(mix(values[i],values[i+1]),[]):
            if i+1<k:out.append((i,i+1,k,l))
    return out

r=random.Random(171717)
for _ in range(100):
    x=r.getrandbits(32)
    assert temper(untemper(x))==x

views={}
for endian in ('little','big'):
    for reversed_order in (False,True):
        for inverse in (False,True):
            name=f'{endian}/reverse={reversed_order}/native={inverse}'
            views[name]=len(links(native(packets,endian,reversed_order,inverse)))
assert list(views.values())==[0,25,0,23,0,0,0,0],views
observed=links(native(packets))
assert len(observed)==25
starts=runpy.run_path(str(ROOT/'agents/agent49/k04_p951_symbolic_basis.py'))['STARTS']
assert len(starts)==133
stages=[starts[i+(i>=129)]+j for i in range(len(packets)) for j in range(4)]
def stage_matches(items:list[tuple[int,int,int,int]])->int:
    return sum(stages[k]-stages[i]==397 and stages[l]-stages[i]==624 for i,j,k,l in items)
assert stage_matches(observed)==25

# Independent genuine seeded stream at the same 133 observed packet positions.
stream=random.Random(2610030417)
values=[stream.getrandbits(32) for _ in range(967)]
synthetic=[b''.join(values[t+j].to_bytes(4,'little') for j in range(4))
           for i,t in enumerate(starts) if i!=129]
assert len(links(native(synthetic)))==25

# Placebo: shuffle the four words *within* each actual packet.
# Stage map held fixed; this preserves every actual four-byte value.
placebos=[]
for _ in range(128):
    shuffled=[]
    for data in packets:
        w=[data[i:i+4] for i in range(0,16,4)]
        r.shuffle(w)
        shuffled.append(b''.join(w))
    placebos.append(stage_matches(links(native(shuffled))))
assert max(placebos)<=3,placebos
independent=[]
for _ in range(16):
    independent.append(len(links(native([r.randbytes(16) for _ in packets]))))
assert all(x==0 for x in independent)
print(json.dumps({
    'original_sha256':hashlib.sha256(original).hexdigest(),
    'withheld_selected_spool_row':129,
    'serializer_exact_relation_counts':views,
    'stage_free_source_links':len(observed),
    'prior_p951_stage_map_exact_links':stage_matches(observed),
    'seeded_control_links':len(links(native(synthetic))),
    'within_packet_permutation_stage_link_range':[min(placebos),max(placebos)],
    'within_packet_permutation_stage_link_mean':sum(placebos)/len(placebos),
    'independent_random_link_counts':independent,
    'witnesses_first5':observed[:5],
},indent=2))
