"""Whole-coupon K04 inverse: 8 CRC16 checkpoints of eight rotated 16-byte views.

Exploratory hypothetical transport, not asserted by the original queue note.
Reads the original archive without changing evidence, acceptance, or candidates.
"""
from __future__ import annotations
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from itertools import product

ROOT = Path(__file__).resolve().parent
if not (ROOT / 'evidence').is_dir():
    ROOT = ROOT.parent.parent
DATA = ROOT / 'evidence' if (ROOT / 'evidence').exists() else ROOT / 'resources' / 'evidence'
ACCEPTANCE = ROOT / 'acceptance.json' if (ROOT / 'acceptance.json').exists() else ROOT / 'resources' / 'acceptance.json'
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
POLYS = {
    'CCITT_FALSE':(0x1021,0xffff,0,False,0x29b1),
    'XMODEM':(0x1021,0,0,False,0x31c3),
    'X25':(0x8408,0xffff,0xffff,True,0x906e),
    'KERMIT':(0x8408,0,0,True,0x2189),
    'ARC':(0xa001,0,0,True,0xbb3d),
    'MODBUS':(0xa001,0xffff,0,True,0x4b37),
    'DNP':(0xa6bc,0,0xffff,True,0xea82),
    'T10_DIF':(0x8bb7,0,0,False,0xd0db),
    'OPENSAFETY_A':(0x5935,0,0,False,0x5d38),
    'OPENSAFETY_B':(0x755b,0,0,False,0x20fe),
    'CDMA2000':(0xc867,0xffff,0,False,0x4c06),
    'PROFIBUS':(0x1dcf,0xffff,0xffff,False,0xa819)
}


def crc16(data: bytes, spec: tuple[int,int,int,bool,int]) -> int:
    poly,initial,final,reflected,_ = spec
    c=initial
    for b in data:
        if reflected:
            c ^= b
            for _ in range(8):
                c=(c>>1)^(poly if c&1 else 0)
        else:
            c ^= b<<8
            for _ in range(8):
                c=((c<<1)&65535)^(poly if c&32768 else 0)
    return c^final


def rotate_output(coupon: bytes, spec: tuple[int,int,int,bool,int], direction: int, reverse: bool) -> int:
    value=0
    for seq in range(8):
        step=(direction*2*seq)%16
        segment=coupon[step:]+coupon[:step]
        if reverse:
            segment=segment[::-1]
        value |= crc16(segment,spec) << (16*seq)
    return value


def build_system(spec: tuple[int,int,int,bool,int], direction:int, reverse:bool):
    zero=rotate_output(bytes(16),spec,direction,reverse)
    columns=[]
    for bit in range(128):
        word=1<<bit
        columns.append(rotate_output(word.to_bytes(16,'little'),spec,direction,reverse)^zero)
    rows=[0]*128
    for bit,col in enumerate(columns):
        for j in range(128):
            if (col>>j)&1:
                rows[j]|=1<<bit
    basis={}
    relations=[]
    for j,coef in enumerate(rows):
        rhs=1<<j
        while coef:
            pivot=coef.bit_length()-1
            if pivot in basis:
                a,b=basis[pivot]
                coef^=a;rhs^=b
            else:
                basis[pivot]=(coef,rhs)
                break
        if coef==0:
            relations.append(rhs)
    pivots=set(basis)
    assert (len(pivots), len(relations)) in [(121, 7), (128, 0)]
    def solve(raw_output: int):
        rhs=raw_output^zero
        if any((rhs&relation).bit_count()&1 for relation in relations):
            return None
        state=0
        for k in sorted(pivots):
            coef,bias=basis[k]
            if ((rhs&bias).bit_count()^(coef&state).bit_count())&1:
                state^=1<<k
        assert rotate_output(state.to_bytes(16,'little'),spec,direction,reverse)==raw_output
        return state
    kernel=[]
    for k in range(128):
        if k in pivots:
            continue
        state=1<<k
        for pivot in sorted(pivots):
            coef,_=basis[pivot]
            if (coef&state).bit_count()&1:
                state ^= 1<<pivot
        assert rotate_output(state.to_bytes(16,'little'),spec,direction,reverse)==zero
        kernel.append(state)
    assert len(kernel)==128-len(pivots)
    for needle in [bytes(range(16)), bytes.fromhex('049AAB2E1CDE7A82CD7C60234303C91A')]:
        actual=int.from_bytes(needle,'little')
        observed=rotate_output(needle,spec,direction,reverse)
        baseline=solve(observed)
        assert baseline is not None
        dif=actual^baseline
        # Source encoding and derived 7-dimensional affine span must cover planted source exactly.
        mask=0
        for b,delta in enumerate(kernel):
            if (dif>>[j for j in range(128) if j not in pivots][b])&1:
                mask ^= delta
        assert mask==dif
    return solve,kernel


def main():
    records=(DATA/'transfers'/'transfer-audit.jsonl').read_bytes()
    chunks=defaultdict(lambda:defaultdict(dict))
    for line in records.splitlines():
        obj=json.loads(line)
        if obj['kind']=='CHUNK':
            chunks[obj['transfer']][obj['seq']][obj['attempt']]=int(obj['checkpoint'],16)
    assert len(chunks)==4 and all(set(c)==set(range(8)) for c in chunks.values())
    accepted=json.loads(ACCEPTANCE.read_text())['slot_sha256']
    for name,spec in POLYS.items():
        assert crc16(b'123456789',spec)==spec[4],name
    source_models,source_consistent,attempt2_consistent,full_checks=0,0,0,0
    hits=[]
    for name,spec in POLYS.items():
        for direction,reverse in product([1,-1],[False,True]):
            solve,kernel=build_system(spec,direction,reverse)
            source_models+=1
            for transfer,seqmap in sorted(chunks.items()):
                assert all(set(d)=={1,2} for d in seqmap.values())
                for attempts_mask in range(256):
                    ck=[seqmap[seq][1+((attempts_mask>>seq)&1)] for seq in range(8)]
                    for endian in ['big','little']:
                        field=[v if endian=='big' else int.from_bytes(v.to_bytes(2,'big'),'little') for v in ck]
                        word=sum(v<<(16*seq) for seq,v in enumerate(field))
                        start=solve(word)
                        if start is None:
                            continue
                        source_consistent+=1
                        if transfer=='AX-7782' and attempts_mask==255:
                            attempt2_consistent+=1
                        # Each independent CRC yields a 7-bit coupon ambiguity. Fully enumerate it.
                        for assignment in range(1 << len(kernel)):
                            if assignment:
                                selected=start
                                for j,vec in enumerate(kernel):
                                    if (assignment>>j)&1:
                                        selected ^= vec
                            else:
                                selected=start
                            physical=selected.to_bytes(16,'little')
                            component=bytes(a^b for a,b in zip(physical,MASK))
                            full_checks+=1
                            if hashlib.sha256(component).hexdigest()==accepted['K04']:
                                hits.append((name,direction,reverse,transfer,attempts_mask,endian,assignment,component.hex().upper()))
    print('SOURCE_SHA256',hashlib.sha256(records).hexdigest())
    print('MATRIX_CONTROL',source_models,'models x 2 true coupon controls PASS; rank 121/free7 or rank128/free0')
    print('SOURCE_CONSISTENT',source_consistent,'selected_original_chain_consistent',attempt2_consistent)
    print('COMPLETE_K04_SHA256_CHECKS',full_checks,'ORIGINAL_HITS',len(hits))
    for hit in hits:
        print('ORIGINAL_PASS',hit)


if __name__=='__main__':
    main()
