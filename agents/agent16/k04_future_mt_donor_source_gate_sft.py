"""Source-only future MT source-visibility / cross-carrier wholeword scan.

Run in checkout: python agents/agent16/k04_future_mt_donor_source_gate_sft.py
Original selected ACK2 and all acceptance targets are excluded.
"""
from __future__ import annotations
import collections
import re
import struct
import sys
from pathlib import Path
from hashlib import sha256

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from agents.agent49.k04_p951_symbolic_basis import source,ORIGIN,MAG,untemper

RECORDER_SHA='5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
SOURCES={
 'K01':'049AAB2E1CDE7A82CD7C60234303C91A',
 'K02_ACCEPTED':'0D7E3AB56FB75DA3EB0E2E06786D239E',
 'K02_PREHASH':'E1A5E474BAD7E853A2E8C71D3317D507',
 'K03_ACCEPTED':'1384AF96E25D6ADA666209CB55E062FA',
 'K05_SELECTED':'FF8B78200A56E8586DCDA00EF01E4572',
 'K06_AUTHORIZED':'5DBF40EE52FAAED9A536D3326CF0D95A',
 'K07_ACCEPTED':'93495F5E425AB8E592123DABAEB68545',
 'K07_PREHASH':'8947CEDCB9CC73BAB7E87BE63302C5C9',
 'K04_MASK':'8556C8CB6140A7F9A5123AC7571BEE1C',
 'K08_NONCE':'5F933DA6A1BD03C32DA5CBC25344F497',
}


def main():
    basis, words=source(ROOT/'resources')
    evidence=ROOT/'resources/evidence'
    original=collections.defaultdict(list)
    def add(label,raw):
        assert len(raw)==4
        for endian in ('little','big'):
            native=untemper(int.from_bytes(raw,endian))
            original[native].append(label+':'+endian)
    for label,h in SOURCES.items():
        data=bytes.fromhex(h)
        for j in range(0,16,4):add(f'{label}[{j//4}]',data[j:j+4])
    rec=(evidence/'recorder/trip-recorder.raw').read_bytes()
    assert sha256(rec).hexdigest()==RECORDER_SHA
    assert len(rec)==16+88*24
    for j in range(88):
        record=rec[16+j*24:16+(j+1)*24]
        epoch,node,event,latch,seq,control,aux,crc=struct.unpack('<IHBBI4sII',record)
        add(f'REC_n{node}_seq{seq}',control)
    for p in evidence.rglob('*'):
        if not p.is_file() or p.suffix.lower()=='.pdf' or p.name in ('spool-reconstruction.log','trip-recorder.raw'):
            continue
        data=p.read_bytes().decode('utf-8','ignore')
        for m in re.finditer(r'(?<![0-9A-Fa-f])([0-9A-Fa-f]{8})(?![0-9A-Fa-f])',data):
            add(f'HEX_LITERAL_{p.name}:{m.start()}',bytes.fromhex(m.group(1)))
    assert len(original)==352 and sum(map(len,original.values()))==376

    last=20000
    ring=[None]*624
    for i in range(len(words)-624,len(words)):
        ring[i%624]=words[i]
    hist=collections.Counter()
    candidate_stages=0
    checked=0
    matches=[]
    plant_stage=1041
    plant_native=None
    plant_matches=[]
    for i in range(len(words),last-ORIGIN+1):
        t=i-624
        a,x,y=ring[(t+397)%624],ring[t%624],ring[(t+1)%624]
        symbolic=[a[j]^(x[31] if j==30 else (y[j+1] if j<30 else 0))
                  ^(y[0] if (MAG>>j)&1 else 0) for j in range(32)]
        ring[i%624]=symbolic
        q=ORIGIN+i
        mask=value=0
        for bit,expression in enumerate(symbolic):
            known=basis.predict(expression)
            if known is not None:
                mask|=1<<bit
                value|=known<<bit
        n=mask.bit_count()
        hist[n]+=1
        if q==plant_stage:
            assert n==32
            plant_native=value
        if n<24:continue
        candidate_stages+=1
        for native,labels in original.items():
            checked+=1
            if native&mask==value:
                matches.append((q,n,labels))
        if plant_native is not None and (plant_native&mask)==value:
            plant_matches.append(q)
    assert sum(hist.values())==last-1040
    assert candidate_stages==939
    assert checked==939*352
    assert matches==[]
    assert plant_matches==[plant_stage]
    print('SOURCE_ONLY original_printer_rank',basis.rank,'unmodified_recorder_sha256',RECORDER_SHA)
    print('FUTURE_NATIVE_STAGES',last-1040,'prediction_bits_ge24',candidate_stages)
    print('INDEPENDENT_ORIGINAL_NATIVE_DONORS',len(original),'source_labels',sum(map(len,original.values())))
    print('ORIGINAL_FULLWORD_MATCHES',len(matches),'COMPLETE_COMPARISONS',checked)
    print('PLANTED_ORACLE_WHOLEWORD_HITS',len(plant_matches),plant_matches)
    print('KNOWNBIT_HISTOGRAM',dict(sorted(hist.items())))
    print('AUTHENTIC_REC8_STATUS_K04_K08','MISSING')


if __name__=='__main__':main()
