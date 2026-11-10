"""Source-first alternative HST float64 + printer MT 624-word publisher probe.
Original material read-only. No selected source bytes fit the model.
"""
from pathlib import Path
from datetime import datetime
from itertools import product
import math, sys
import hashlib, json, re, struct, random
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'
SPOOL=ROOT/'evidence/print/spool-reconstruction.log'
HST=ROOT/'evidence/telemetry/freeze-export.jsonl'
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
assert hashlib.sha256(HST.read_bytes()).hexdigest()=='3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'
spool=[bytes.fromhex(p) for p in re.findall(r'PAYLOAD=([A-F0-9]{32})',SPOOL.read_text())]
assert len(spool)==133
rec=[json.loads(line) for line in HST.read_text().splitlines()]
pvs=[r for r in rec if r['field']=='PV']
assert len(pvs)==112 and sorted(r['seq'] for r in pvs)==list(range(100,212))
orders={
  'seq':sorted(pvs,key=lambda r:r['seq']),
  'raw':pvs,
  'ts':sorted(pvs,key=lambda r:datetime.fromisoformat(r['ts'])),
}
MASK=bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
TARGET='930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
BITMASK=0xffffffff

def temper(x):
    x^=x>>11
    x^=(x<<7)&0x9d2c5680
    x^=(x<<15)&0xefc60000
    x^=x>>18
    return x&BITMASK

def undo(y,shift,mask,fromleft):
    x=y
    for _ in range(8):
        x=(y^((x<<shift)&mask))&BITMASK if fromleft else (y^(x>>shift))
    return x

def untemper(x):
    x=undo(x,18,BITMASK,False)
    x=undo(x,15,0xefc60000,True)
    x=undo(x,7,0x9d2c5680,True)
    x=undo(x,11,BITMASK,False)
    return x&BITMASK

def future(outputs,count):
    assert len(outputs)==624
    native=[untemper(w) for w in outputs]
    for i in range(624,624+count):
        a=native[i-624];b=native[i-623];x=((a&0x80000000)|(b&0x7fffffff))
        x=native[i-624+397]^(x>>1)^(0x9908b0df if b&1 else 0)
        native.append(x&BITMASK)
    return [temper(x) for x in native[624:]]

for seed in (0,20261003,20261110):
    gen=random.Random(seed)
    xs=[gen.getrandbits(32) for _ in range(624+112)]
    assert future(xs[:624],112)==xs[624:], ('MT true synthetic',seed)
assert all(temper(untemper(x))==x for x in (0,1,0xffffffff,0x55aa1122,0x8f7b9325))

# End-to-end planted HST IEEE754-double plus spool interleave. This is a
# genuine MT-generated 736-word source, *not* a historical source claim.
for seed in range(20261003, 20261020):
    sgen=random.Random(seed)
    emitted=[sgen.getrandbits(32) for _ in range(736)]
    doubles=[struct.unpack('<d',struct.pack('<2I',*emitted[i*6+2:i*6+4]))[0]
             for i in range(112)]
    if all(math.isfinite(v) for v in doubles):break
else:raise AssertionError('synthetic finite-double seed unavailable')
assert len(doubles)==112
synthetic=[]
for i in range(112):
    word=struct.unpack('<2I',struct.pack('<d',doubles[i]))
    assert tuple(emitted[6*i+2:6*i+4])==word
    synthetic.extend(emitted[6*i:6*i+2]+list(word)+emitted[6*i+4:6*i+6])
synthetic.extend(emitted[672:736])
assert synthetic==emitted
assert future(synthetic[:624],112)==synthetic[624:]
print('TRUE_GENERATOR_POSITIVE IEEE754-double and fourword packet, 112 PV and 128 packets, 24 withheld full packets: PASS')


models=0; heldout_full=0; heldout_pv=0; target_hits=0; total_source_matches=0
best=[]
for order_name,view,rev_pv,word_endian,rev_print,mode,pos in product(
        orders, ('<','>'), (False,True), ('<','>'), (False,True), ('interleave','pvfirst','spoolfirst'), range(5)):
    if mode!='interleave' and pos:continue
    rows=orders[order_name]
    def pv_words(r):
        z=struct.unpack(view+'2I',struct.pack(view+'d',r['value']))
        return list(z[::-1] if rev_pv else z)
    def packet_words(packet):
        z=struct.unpack(word_endian+'4I',packet)
        return list(z[::-1] if rev_print else z)
    pv_seq=[pv_words(x) for x in rows]
    packet_seq=[packet_words(x) for x in spool[:128]]
    stream=[]; tags=[]
    if mode=='interleave':
        for i in range(128):
            b=packet_seq[i]
            if i<112:
                b=b[:pos]+pv_seq[i]+b[pos:]
                tags.extend([('job',i)]*pos+[('pv',i)]*2+[('job',i)]*(4-pos))
            else: tags.extend([('job',i)]*4)
            stream.extend(b)
    elif mode=='pvfirst':
        stream=[w for p in pv_seq for w in p]+[w for p in packet_seq for w in p]
        tags=[('pv',i) for i in range(112) for _ in range(2)]+[('job',i) for i in range(128) for _ in range(4)]
    else:
        stream=[w for p in packet_seq for w in p]+[w for p in pv_seq for w in p]
        tags=[('job',i) for i in range(128) for _ in range(4)]+[('pv',i) for i in range(112) for _ in range(2)]
    assert len(stream)==736 and len(tags)==736
    predictions=future(stream[:624],len(stream)-624+20)
    source_matches=sum(a==b for a,b in zip(predictions,stream[624:]))
    # A true original whole object is predicted only when every source word in it matches.
    byobject={}
    for tag,actual,pred in zip(tags[624:],stream[624:],predictions):
        byobject.setdefault(tag,[]).append(pred==actual)
    full_matches=sum(all(v) and len(v)==(4 if tag[0]=='job' else 2) for tag,v in byobject.items())
    pv_matches=sum(all(v) and len(v)==2 for tag,v in byobject.items() if tag[0]=='pv')
    models+=1; heldout_full+=full_matches; heldout_pv+=pv_matches; total_source_matches+=source_matches
    best.append((full_matches,source_matches,order_name,view,rev_pv,word_endian,rev_print,mode,pos))
    # Original hypothetical late rows occupy source stream word positions 736..739 (REQ1)
    # and 740..743 (ACK2), with no hidden draw. Repack the predicted selected raw packet.
    selected_words=predictions[116:120]
    if rev_print: selected_words=selected_words[::-1]
    selected=struct.pack(word_endian+'4I',*selected_words)
    component=bytes(a^b for a,b in zip(selected,MASK))
    if hashlib.sha256(component).hexdigest()==TARGET:
        target_hits+=1;print('ORIGINAL_K04_MATCH',component.hex().upper(),order_name,view,rev_pv,word_endian,rev_print,mode,pos)
assert (models,heldout_full,heldout_pv,total_source_matches,target_hits)==(336,0,0,0,0)
print('original source model_count',models,'whole_holdout_matches',heldout_full,'pv_holdout_matches',heldout_pv,'individual_word_matches',total_source_matches,'selected_K04_hits',target_hits)
print('best source matches',sorted(best,reverse=True)[:7])
