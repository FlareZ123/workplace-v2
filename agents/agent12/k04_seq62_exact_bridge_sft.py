"""H-17 source-only exact GF(2) bridge, node50 seq62, synthetic MT positive.

Original printer ACK row129, copied K04 bytes, route mask, acceptance and K08 are
excluded. The hypothesis that node50 CONTROLs share the hypothetical p951 MT
producer and each successive CONTROL gap lies within 2..12 draws is conditional.
Run from workplace-v2 root: python agents/agent12/k04_seq62_exact_bridge_sft.py
"""
import hashlib
import json
import random
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents' / 'agent49'))
from k04_p951_symbolic_basis import Basis, STARTS, get, source, temper, untemper, words

RAW_SHA = '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
ANCHORS = {7:-810,9:-793,12:-775,13:-769,14:-759,24:-683,25:-677,
           41:-568,43:-552,44:-545,45:-540,61:-417,63:-397,64:-390,70:-339}


def read_recorder():
    raw = (ROOT / 'resources' / 'evidence' / 'recorder' / 'trip-recorder.raw').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RAW_SHA
    assert raw[:8] == b'TRP2DUMP' and len(raw) == 16 + 88 * 24
    rows = {}
    for i in range(88):
        record = raw[16 + 24 * i:16 + 24 * (i+1)]
        ts, node, event, latch, seq, control, aux, crc = struct.unpack('<IHBBIIII', record)
        if node == 50:
            assert zlib.crc32(record[:20]) == crc
            rows[seq] = dict(time=ts-1791061740,event=event,latch=latch,
                             control=control,aux=aux)
    assert len(rows) == 72 and set(rows) == set(range(72))
    return rows


def add(basis, symbolic, stage, control):
    advanced=Basis()
    advanced.rows=dict(basis.rows)
    advanced.rank=basis.rank
    native=untemper(control)
    try:
        for bit,equation in enumerate(get(symbolic,stage)):
            advanced.insert(equation,(native>>bit)&1)
    except AssertionError:
        return None
    return advanced


def exact_candidates(basis,symbolic,control):
    # With two gaps 2..12 and original seq61=-417, seq63=-397:
    # seq62 is in [-409, -405]. This window is frozen without inspecting it.
    out=[]
    for stage in range(-409,-404):
        expanded=add(basis,symbolic,stage,control)
        if expanded is not None:out.append(stage)
    return out


def known_tempered(basis, symbolic, stage):
    mask=value=0
    for bit,equation in enumerate(temper(get(symbolic,stage))):
        predicted=basis.predict(equation)
        if predicted is not None:
            mask|=1<<bit
            value|=predicted<<bit
    return mask,value


def quotient(basis,symbolic):
    homogeneous=Basis()
    homogeneous.rows={p:(row,0) for p,(row,_) in basis.rows.items()}
    homogeneous.rank=basis.rank
    for stage in range(951,955):
        for equation in get(symbolic,stage):
            homogeneous.insert(equation,0)
    return homogeneous.rank-basis.rank


def seeded_positive(symbolic):
    # True stdlib MT generator, reconstruct synthetic source through identical
    # printer lanes, actual native stages and 15 heldout-style recorder anchors.
    rng=random.Random(20261103)
    generated=[rng.getrandbits(32) for _ in range(2141)]
    synthetic=Basis()
    for row,start in enumerate(STARTS):
        if row == 129:
            continue
        for stage in range(start,start+4):
            native=untemper(generated[stage+1100])
            for bit,equation in enumerate(get(symbolic,stage)):
                synthetic.insert(equation,(native>>bit)&1)
    assert synthetic.rank==15365
    for stage in ANCHORS.values():
        updated=add(synthetic,symbolic,stage,generated[stage+1100])
        assert updated is not None
        synthetic=updated
    planted=generated[-405+1100]
    assert exact_candidates(synthetic,symbolic,planted)==[-405]
    assert add(synthetic,symbolic,-405,planted) is not None


def main():
    recorder=read_recorder()
    basis,symbolic=source(ROOT/'resources')
    assert basis.rank==15365
    seeded_positive(symbolic)
    for seq,stage in sorted(ANCHORS.items()):
        next_basis=add(basis,symbolic,stage,recorder[seq]['control'])
        assert next_basis is not None,(seq,stage)
        basis=next_basis
    assert basis.rank==15375
    observed=recorder[62]['control']
    assert exact_candidates(basis,symbolic,observed)==[-405]
    selection=add(basis,symbolic,-405,observed)
    assert selection is not None and selection.rank==15407
    # Without the full-vector GF(2) insertion, the zero-bit-mask stage -409
    # appears as feasible as -405. Exact joint algebra eliminates -409.
    assert known_tempered(basis,symbolic,-409)[0]==0
    assert known_tempered(basis,symbolic,-405)[0]==0
    assert add(basis,symbolic,-409,observed) is None
    # A null calibration is essential: -405 has a 32/32 free quotient,
    # so completely unrelated random CONTROLs always fit it.
    unrelated=random.Random(20261103)
    null_unique=sum(exact_candidates(basis,symbolic,unrelated.getrandbits(32))==[-405]
                    for _ in range(1000))
    assert null_unique==742
    # Two consecutive independently printer-fixed outputs are rejection codes
    # for every listed standard CPython randbelow bound.
    rejection=[]
    for stage in (-408,-407):
        mask,value=known_tempered(selection,symbolic,stage)
        assert mask==0xffffffff
        codes={str(bound):value>>(32-bound.bit_length()) for bound in (4,40,400,6000)}
        assert all(code>=int(bound) for bound,code in codes.items())
        rejection.append({'stage':stage,'output':f'{value:08X}','codes':codes})
    # A model placing seq62 latch immediately before its CONTROL is falsified:
    # both already-determined upper-bit positions disagree with original latch2.
    mask,value=known_tempered(selection,symbolic,-406)
    assert ((mask>>29)&7).bit_count()==2
    assert (((value>>29)^recorder[62]['latch'])&((mask>>29)&7))!=0
    assert quotient(selection,symbolic)==128
    print(json.dumps({'original_printer_rank':15365,
                      'fifteen_control_anchor_rank':basis.rank,
                      'seq62_conditional_stage':-405,
                      'joint_rank_after_seq62':selection.rank,
                      'source_fixed_bits_at_both_candidate_stages':0,
                      'null_unrelated_unique_stage_trials':null_unique,
                      'two_universal_rejection_words':rejection,
                      'seq62_prior_latch_model':'CONTRADICTED',
                      'missing_selected_coupon_rank':128,
                      'true_seeded_MT_positive':'PASS','original_slot_status':'INCOMPLETE'},sort_keys=True))


if __name__=='__main__':main()
