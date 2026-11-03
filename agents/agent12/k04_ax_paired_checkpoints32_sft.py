"""H-17 K04 source-only AX attempt-pair-to-32bit producer test.

Execute from workplace-v2 root:
 python agents/agent12/k04_ax_paired_checkpoints32_sft.py

Original selected printer row129 and original target hashes are never used.
Model: for each seq0..7, its attempt1/2 checkpoint halfwords are packed as
one tempered 32-bit MT output. Try both half orders, independently selected
endian views for each attempt, and uniform native strides1..8.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'agents'/'agent49'))
from k04_p951_symbolic_basis import Basis, STARTS, get, source, temper, untemper

TRANSFER_SHA='32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf'
TRANSFERS=('AX-7778','AX-7781','AX-7782','AX-7783')


def checks():
    raw=(ROOT/'resources/evidence/transfers/transfer-audit.jsonl').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==TRANSFER_SHA
    hits={}
    for line in raw.splitlines():
        item=json.loads(line)
        if item['kind']=='CHUNK':
            hits[item['transfer'],item['seq'],item['attempt']]=int(item['checkpoint'],16)
    assert len(hits)==64
    return hits


def source_words(basis,symbolic):
    result=[]
    for stage in range(-1100,1041):
        mask=value=0
        for bit,equation in enumerate(temper(get(symbolic,stage))):
            fixed=basis.predict(equation)
            if fixed is not None:
                mask|=1<<bit
                value|=fixed<<bit
        result.append((mask,value))
    return result


def packed(hits,transfer,swapped0,swapped1,upper_attempt):
    assembled=[]
    for seq in range(8):
        a=hits[transfer,seq,1]
        b=hits[transfer,seq,2]
        if swapped0:a=(a>>8)|((a&255)<<8)
        if swapped1:b=(b>>8)|((b&255)<<8)
        assembled.append(((a<<16)|b) if upper_attempt==1 else ((b<<16)|a))
    return assembled


def score(stages,observed,start,stride):
    fixed=bad=0
    for j,v in enumerate(observed):
        mask,expected=stages[start+j*stride]
        fixed+=mask.bit_count()
        bad+=((v^expected)&mask).bit_count()
    return fixed,bad


def positive(symbolic):
    # Truly seeded Python-MT 2141-word stream, with selected packet withheld.
    rng=random.Random(20261103)
    raw=[rng.getrandbits(32) for _ in range(2141)]
    planted=Basis()
    for row,stage in enumerate(STARTS):
        if row==129:continue
        for lane in range(4):
            native=untemper(raw[stage+lane+1100])
            for bit,equation in enumerate(get(symbolic,stage+lane)):
                planted.insert(equation,(native>>bit)&1)
    assert planted.rank==15365
    source_stages=source_words(planted,symbolic)
    eight=raw[1100:1108]
    fixed,bad=score(source_stages,eight,1100,1)
    assert fixed>=128 and bad==0
    mutated=eight.copy()
    mutated[0]^=1
    # Original stage0 is a fully pinned 32-bit printer word.
    assert score(source_stages,mutated,1100,1)[1]==1
    return fixed


def main():
    hits=checks()
    basis,symbolic=source(ROOT/'resources')
    assert basis.rank==15365
    stages=source_words(basis,symbolic)
    seeded_control_fixed=positive(symbolic)
    tested=0
    informative=0
    informative_hits=0
    maximum_consistent=0
    for transfer in TRANSFERS:
        for swap0 in (False,True):
            for swap1 in (False,True):
                for high in (1,2):
                    observed=packed(hits,transfer,swap0,swap1,high)
                    for stride in range(1,9):
                        for start in range(len(stages)-7*stride):
                            fixed,bad=score(stages,observed,start,stride)
                            tested+=1
                            informative+=int(fixed>=32)
                            informative_hits+=int(fixed>=32 and bad==0)
                            if bad==0:maximum_consistent=max(maximum_consistent,fixed)
    assert tested==540032
    assert informative_hits==0
    assert maximum_consistent==10
    print(json.dumps({'original_printer_rank':basis.rank,
                      'original_checkpoints':len(hits),
                      'whole_32bit_attempt_pair_views':32,
                      'source_stage_stride_assignments':tested,
                      'informative_32bit_or_more_assignments':informative,
                      'informative_original_consistent':informative_hits,
                      'most_source_fixed_bits_of_any_consistent_stage':maximum_consistent,
                      'seeded_real_MT_positive_fixed_bits':seeded_control_fixed,
                      'true_selected_K04_coupon_bits':0,
                      'archive_status':'INCOMPLETE'},sort_keys=True))


if __name__=='__main__':
    main()
