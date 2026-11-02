"""Conditional four-word source-only seq14 control reconstruction.
Run: python agents/agent46/k04_seq14_affine_quartet_sft.py resources
Selected printer row129, route masks, original K04/K08 commitments excluded.
"""
import hashlib,random,struct,sys,zlib
from pathlib import Path
from k04_seq14_conditional_stage_heldout_sft import (predict,
    candidate_control_positions,synthetic_controls,REC_SHA)
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'agent49'))
from k04_p951_symbolic_basis import Basis,source,get,temper,untemper
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'

def four_word_family(b,expressions):
    extra={};representation=[]
    for expr in expressions:
        v=expr;constant=coeff=0
        while v:
            pivot=v.bit_length()-1
            if pivot in b.rows:
                w,bit=b.rows[pivot];v^=w;constant^=bit
            elif pivot in extra:
                w,mask=extra[pivot];v^=w;coeff^=mask
            else:
                i=len(extra);extra[pivot]=(v,1<<i);coeff^=1<<i;v=0
        representation.append((constant,coeff))
    return [sum((known ^ ((mask&seed).bit_count()&1))<<j
                for j,(known,mask) in enumerate(representation))
            for seed in range(1<<len(extra))]

def seeded_affine_controls():
    for seed in range(20):
        rng=random.Random(seed+17000);secret=rng.getrandbits(32);b=Basis()
        while b.rank<30:
            equation=rng.getrandbits(32)
            b.insert(equation,(equation&secret).bit_count()&1)
        candidates=four_word_family(b,[1<<j for j in range(32)])
        assert len(candidates)==4 and secret in candidates
    print('PASS 20 synthetic four-word affine controls')

def main():
    synthetic_controls();seeded_affine_controls()
    b,s=source(ROOT)
    assert b.rank==15365
    raw=(ROOT/'evidence/recorder/trip-recorder.raw').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==REC_SHA
    row={}
    for i in range(88):
        p=16+24*i
        ts,node,event,latch,seq,ctrl,aux,crc=struct.unpack_from('<IHBBI4sII',raw,p)
        if node!=50:continue
        assert zlib.crc32(raw[p:p+20])==crc
        row[seq]=(ts,event,latch,untemper(int.from_bytes(ctrl,'little')),aux)
    native,outputs=predict(b,s,-772,-740)
    assert outputs[-768][0]>>(32-13)==1201 and row[13][4]==3201
    vals=(row[14][0]-1791061742,row[14][1]-1,row[14][2],row[14][4]-2000)
    candidates=candidate_control_positions(-767,vals,outputs)
    assert {i:native[i][1].bit_count() for i in candidates
            if native[i][1].bit_count()>=8}=={-759:16}
    # Freeze the position before any consultation of withheld seq14 control bytes.
    augmented=Basis();augmented.rows=b.rows.copy();augmented.rank=b.rank
    for pos,n,value in ((-766,9,vals[0]),(-765,6,vals[1]),
                        (-760,3,vals[2]),(-758,13,vals[3])):
        for bit,expression in enumerate(temper(get(s,pos))[-n:]):
            augmented.insert(expression,(value>>bit)&1)
    assert augmented.rank==15393
    family=four_word_family(augmented,get(s,-759))
    assert family==[0xAEC82C62,0x9CD94DDD,0x2EC82C62,0x1CD94DDD]
    assert row[14][3] in family
    assert all(row[seq][3] not in family for seq in row if seq!=14)
    print('PASS exactly four complete original seq14 native control candidates:',
          [f'{word:08X}' for word in family])
    print('Heldout original control belongs to this four-word family')
    print('This does not index or recover the selected K04 printer coupon')

if __name__=='__main__':main()
