"""Original-source K04 target quotient: node49 interleaved controls and AX donors.

Conditional p951 native MT geometry. Original selected printer row129 omitted
before decoding its bytes; no route mask, K04 hash, candidate or verifier.
Run: python agents/agent19/k04_node49_ax_future_donor_synergy_sft.py
"""
import hashlib
import importlib.util
import itertools
import json
import struct
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location(
    "agent49", ROOT/"agents/agent49/k04_p951_symbolic_basis.py"
)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.LAST=1600
resources=ROOT/"resources"
original_basis,states=m.source(resources)
assert original_basis.rank==15365
raw=(resources/"evidence/recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(raw).hexdigest()==(
    "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
)
expected={200+l:-324+3*l for l in range(4)}
expected.update({900+l:-323+3*l for l in range(4)})
expected.update({990+l:-322+3*l for l in range(4)})
records={}
for index in range(struct.unpack_from("<I",raw,12)[0]):
    line=raw[16+index*24:16+(index+1)*24]
    stamp,node,event,latch,seq,control,aux,crc=struct.unpack(
        "<I H B B I 4s I I",line
    )
    if node==49 and seq in expected:
        assert expected[seq]==(-324 if seq<300 else -323 if seq<990 else -322)+3*latch
        assert seq not in records
        records[seq]=(control,(zlib.crc32(line[:20])&0xffffffff)==crc)
assert len(records)==12
assert sum(valid for _,valid in records.values())==8
transfer=(resources/"evidence/transfers/transfer-audit.jsonl").read_bytes()
assert hashlib.sha256(transfer).hexdigest()==(
    "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
)
chunks=sorted(
    (json.loads(line) for line in transfer.splitlines()
     if json.loads(line).get("kind")=="CHUNK"
     and json.loads(line).get("transfer")=="AX-7778"),
    key=lambda x:(x["seq"],x["attempt"])
)
assert len(chunks)==16


def extend(include_recorder=False,valid_only=False,include_ax=False):
    b=m.Basis()
    b.rows=original_basis.rows.copy()
    b.rank=original_basis.rank
    if include_ax:
        for ix,chunk in enumerate(chunks):
            word=int(chunk["checkpoint"],16)
            upper16=(word>>8)|((word&255)<<8)
            for bit,expr in enumerate(m.temper(m.get(states,-157+ix))[16:]):
                b.insert(expr,(upper16>>bit)&1)
    if include_recorder:
        for seq,index in expected.items():
            coupon,crc_valid=records[seq]
            if valid_only and not crc_valid:continue
            word=m.untemper(int.from_bytes(coupon,"little"))
            for bit,expr in enumerate(m.get(states,index)):
                b.insert(expr,(word>>bit)&1)
    return b


def reduce(expr,basis):
    while expr:
        pivot=expr.bit_length()-1
        if pivot not in basis:break
        expr ^= basis[pivot]
    return expr


def rank_gain(base,donors):
    # Use homogeneous equations for observability; source RHS does not
    # matter to target *rank* once consistency was independently checked.
    matrix={p:expr for p,(expr,val) in base.rows.items()}
    before=len(matrix)
    for index in donors:
        for expr in m.get(states,index):
            residual=reduce(expr,matrix)
            if residual:
                matrix[residual.bit_length()-1]=residual
    rank=len(matrix)-before
    without=len(matrix)
    for index in range(951,955):
        for expr in m.get(states,index):
            residual=reduce(expr,matrix)
            if residual:
                matrix[residual.bit_length()-1]=residual
    return len(matrix)-without,rank


donors=(1179,1180,1181,1347,1348,1574,1575)
expected_short=(1,32,32,31,2,31,2)
for name,with_ax,with_recorder,valid_only,rank in (
    ("printer",False,False,False,15365),
    ("recorder-valid8",False,True,True,15432),
    ("recorder-all12",False,True,False,15493),
    ("ax",True,False,False,15495),
    ("ax+recorder-valid8",True,True,True,15561),
    ("ax+recorder-all12",True,True,False,15622)
):
    basis=extend(with_recorder,valid_only,with_ax)
    assert basis.rank==rank,(name,basis.rank,rank)
    assert rank_gain(basis,())[0]==128
    assert rank_gain(basis,donors)[0]==0
    short=[rank_gain(basis,donors[:i]+donors[i+1:])[0] for i in range(7)]
    assert tuple(short)==expected_short,(name,short)
    print(name,"source_rank",rank,"target_unknown_0donor",128,
          "target_unknown_7donor",0,
          "six_donor_residuals",short)
print("PASS: +257 independent source equations do not shorten the"
      " frozen seven-future-word portfolio; historical K04 remains unknown")
