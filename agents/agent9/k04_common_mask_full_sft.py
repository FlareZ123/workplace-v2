"""Source-pinned H-17 K04 p951/MT common 32-bit recorder-latch XOR mask candidate SFT.

The printer and selected K02/K05 source equations are solved without selected
printer ACK2, K04 mask/commitment in stage/format selection. Once a model is
source compatible, its complete 16-byte candidate keys are tested against
original K04 SHA256. Conditional MT architecture; no hardware attestation.
"""
from collections import Counter
from pathlib import Path
import hashlib
import itertools
import json
import random
import struct
import sys
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'agent49'))
import k04_p951_symbolic_basis as mt

mt.LAST=3000
SOURCE=Path(__file__).resolve().parents[2]/'resources'
assert hashlib.sha256((SOURCE/'evidence/telemetry/freeze-export.jsonl').read_bytes()).hexdigest()=='3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'
assert hashlib.sha256((SOURCE/'evidence/recorder/trip-recorder.raw').read_bytes()).hexdigest()=='5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
raw=(SOURCE/'evidence/recorder/trip-recorder.raw').read_bytes()
k05_controls={}
for i in range(88):
    packet=raw[16+24*i:16+24*(i+1)]
    _,node,event,latch,seq=struct.unpack_from('<IHBBI',packet)
    if node==49 and event==82 and 300<=seq<=303:
        assert zlib.crc32(packet[:20])==struct.unpack_from('<I',packet,20)[0]
        k05_controls[latch]=packet[12:16]
assert sorted(k05_controls)==[0,1,2,3]
k05=b''.join(k05_controls[l] for l in range(4))
assert k05.hex().upper()=='FF8B78200A56E8586DCDA00EF01E4572'
k02=bytes.fromhex('E1A5E474BAD7E853A2E8C71D3317D507')
accepted=json.loads((SOURCE/'acceptance.json').read_text())['slot_sha256']
assert hashlib.sha256(hashlib.sha256(k02).digest()[:16]).hexdigest()==accepted['K02']
assert hashlib.sha256(k05).hexdigest()==accepted['K05']
assert accepted['K04']=='930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
route=json.loads((SOURCE/'evidence/recovery-routing.json').read_text())
mask=bytes.fromhex(route['K04']['masked_component'])
assert mask.hex().upper()=='8556C8CB6140A7F9A5123AC7571BEE1C'
printer,symbolic=mt.source(SOURCE)
assert printer.rank==15365
selected=[e for i in range(951,955) for e in mt.get(symbolic,i)]

def clone(base):
    result=mt.Basis()
    result.rows=base.rows.copy()
    result.rank=base.rank
    return result

def donor_modes():
    for endian in ('big','little'):
        for reverse,swap,native in itertools.product((False,True),repeat=3):
            chunks=[k02[i:i+4] for i in (0,4,8,12)]
            if swap:chunks=[p[2:]+p[:2] for p in chunks]
            if reverse:chunks.reverse()
            values=[int.from_bytes(p,endian) for p in chunks]
            yield (endian,reverse,swap,native),[v if native else mt.untemper(v) for v in values]

def k05_modes(rawword):
    vals=[int.from_bytes(rawword, e) for e in ('little','big')]
    return vals+[mt.untemper(v) for v in vals]

variants=[k05_modes(k05[i:i+4]) for i in (0,4,8,12)]

def residual(base,expression):
    rem=val=0
    while expression:
        p=expression.bit_length()-1
        if p in base.rows:
            eq,bit=base.rows[p]
            expression^=eq
            val^=bit
        else:
            rem^=1<<p
            expression^=1<<p
    return rem,val

def temper_scalar(word):
    word^=word>>11
    word^=(word<<7)&0x9D2C5680
    word^=(word<<15)&0xEFC60000
    word^=word>>18
    return word&0xFFFFFFFF

def make_component(nativebits):
    paper=b''.join(
        temper_scalar(sum(nativebits[32*lane+bit]<<bit for bit in range(32))).to_bytes(4,'little')
        for lane in range(4))
    return bytes(v^m for v,m in zip(paper,mask))

def candidates(base):
    pivots={}
    coefficients=[]
    constants=[]
    for eq in selected:
        rem,const=residual(base,eq)
        coeff=0
        while rem:
            pivot=rem.bit_length()-1
            if pivot in pivots:
                vec,tag=pivots[pivot]
                rem^=vec
                coeff^=tag
            else:
                tag=1<<len(pivots)
                pivots[pivot]=(rem,tag)
                coeff^=tag
                break
        coefficients.append(coeff)
        constants.append(const)
    for value in range(1<<len(pivots)):
        bits=[v^((c&value).bit_count()&1) for c,v in zip(coefficients,constants)]
        yield make_component(bits),len(pivots)

def particular_state(base):
    x=0
    for p,(eq,bit) in sorted(base.rows.items()):
        if bit^((eq&x).bit_count()&1):x|=1<<p
    return x

# Source-only rank selection: choose exactly the five 227-lag lattice stages
# previously discovered by an independent rank-first search, independently
# of K05 observations, copied ACK and original K04 target digest.
starts=(1120,1347,1516,1743,2139)
summary=Counter()
unique=set()
for donor in (1178,1405):
    for donorname,donorwords in donor_modes():
        base=clone(printer)
        for stage,word in zip(range(donor,donor+4),donorwords):
            for bit,eq in enumerate(mt.get(symbolic,stage)):
                base.insert(eq,(word>>bit)&1)
        assert base.rank==15493
        for start in starts:
            stages=[start+227*i for i in range(4)]
            for view in range(4):
                values=[variants[i][view] for i in range(4)]
                summary['assignments']+=1
                joint=clone(base)
                try:
                    for lane,stage in enumerate(stages):
                        for bit,eq in enumerate(mt.get(symbolic,stage)):
                            joint.insert(eq^(1<<(19968+bit)),(values[lane]>>bit)&1)
                except AssertionError:
                    continue
                summary['source_compatible']+=1
                assert joint.rank==15618, (donor,start,view,joint.rank)
                full=list(candidates(joint))
                assert full[0][1]==4, (donor,start,view,full[0][1])
                summary['complete_checks']+=len(full)
                state=particular_state(joint)
                planted=make_component([((e&state).bit_count()&1) for e in selected])
                assert sum(v==planted for v,_ in full)==1
                summary['planted_controls']+=1
                for candidate,_ in full:
                    unique.add(candidate)
                    if hashlib.sha256(candidate).hexdigest()==accepted['K04']:
                        summary['original_hits']+=1
                        print('FOUND ORIGINAL K04',candidate.hex().upper(),donor,donorname,start,view)
                print('COMPATIBLE',donor,donorname,start,view,'FREE_BITS',full[0][1],flush=True)
assert summary['assignments']==640
assert summary['source_compatible']==32
assert summary['complete_checks']==512
assert summary['planted_controls']==32
print('ORIGINAL_K04_TEST',dict(summary),'DISTINCT_COMPONENTS',len(unique),flush=True)

# Independent *genuine* symbolic MT/p951 producer with synthetic masked K05.
# The real source and missing selected row do not enter the planted state.
rng=random.Random(0xA9172026)
syn_state=rng.getrandbits(19968)
syn_shared_mask=rng.getrandbits(32)
syn_printer=mt.Basis()
for row,pos in enumerate(mt.STARTS):
    if row==129:
        continue
    for lane in range(4):
        eqs=mt.get(symbolic,pos+lane)
        native=sum(((eq&syn_state).bit_count()&1)<<bit for bit,eq in enumerate(eqs))
        # Follow actual spool byte serialization and native untempering.
        recorded=temper_scalar(native).to_bytes(4,'little')
        decoded=mt.untemper(int.from_bytes(recorded,'little'))
        assert decoded==native
        for bit,eq in enumerate(eqs):
            syn_printer.insert(eq,(decoded>>bit)&1)
assert syn_printer.rank==15365
syn_withk02=clone(syn_printer)
for stage in range(1178,1182):
    eqs=mt.get(symbolic,stage)
    native=sum(((eq&syn_state).bit_count()&1)<<bit for bit,eq in enumerate(eqs))
    for bit,eq in enumerate(eqs):
        syn_withk02.insert(eq,(native>>bit)&1)
assert syn_withk02.rank==15493
syn_joint=clone(syn_withk02)
for stage in (2139,2366,2593,2820):
    eqs=mt.get(symbolic,stage)
    native=sum(((eq&syn_state).bit_count()&1)<<bit for bit,eq in enumerate(eqs))
    recorded=temper_scalar(native^syn_shared_mask).to_bytes(4,'little')
    whitened=mt.untemper(int.from_bytes(recorded,'little'))
    assert whitened==(native^syn_shared_mask)
    for bit,eq in enumerate(eqs):
        syn_joint.insert(eq^(1<<(19968+bit)),(whitened>>bit)&1)
assert syn_joint.rank==15618
syn_pred=list(candidates(syn_joint))
assert len(syn_pred)==16
syn_true=make_component([((e&syn_state).bit_count()&1) for e in selected])
assert sum(key==syn_true for key,dimension in syn_pred)==1
assert syn_true in [key for key,_ in syn_pred]
print('GENUINE_SYNTHETIC_MASKED_MT_POSITIVE',len(syn_pred),'TRUE_COUPON_FOUND_ONCE',flush=True)
