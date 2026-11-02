"""K04 p951: complete seven-native donor expression including earlier index -237.

Original selected ACK2 withheld; genuine native MT seeded-state synthetics verify
a new mixed negative/future exact coupon reconstruction. Authentic native words
at the indicated donor positions are NOT present in the surviving archive.

Run: python agents/agent39/k04_p951_mixed_negative_future_coupon_sft.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import random
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location(
    "coupon", ROOT/"agents/agent39/k04_p951_seven_donor_affine_sft.py"
)
coupon=importlib.util.module_from_spec(spec)
spec.loader.exec_module(coupon)
ORIGIN=-1100
DONORS=(1178,1179,1180,1181,1347,1574,-237)
U=0xffffffff
K=len(DONORS)*32
MAG=0x9908b0df
LAST=1579


def symbols():
    out=[[1<<(32*i+b) for b in range(32)] for i in range(624)]
    for index in range(624,ORIGIN*-1+LAST+624):
        p,n,q=out[index-624],out[index-623],out[index-227]
        out.append([
            q[b]^(p[31] if b==30 else n[b+1] if b<30 else 0)
            ^(n[0] if (MAG>>b)&1 else 0)
            for b in range(32)
        ])
    return out


def reduce(row,basis):
    while row:
        pivot=row.bit_length()-1
        old=basis.get(pivot)
        if old is None:break
        row^=old
    return row


def source_basis(expressions,packets):
    basis={}
    for row,start in enumerate(coupon.prior.STARTS):
        if row==129:continue
        assert len(packets[row])==16
        for j in range(4):
            word=coupon.prior.untemper(int.from_bytes(
                packets[row][4*j:4*j+4],"little"
            ))
            for bit,expr in enumerate(expressions[1100+start+j]):
                row=(expr<<1)|((word>>bit)&1)
                residual=reduce(row,basis)
                assert residual!=1,"intact source conflict"
                if residual>1:basis[residual.bit_length()-1]=residual
    assert len(basis)==15365
    return basis


def affine_recovery(expressions,packets):
    source=source_basis(expressions,packets)
    basis={
        p+K:((row>>1)<<(K+1))|(row&1)
        for p,row in source.items()
    }
    native_independent=0
    for i,at in enumerate(DONORS):
        for bit,expr in enumerate(expressions[1100+at]):
            row=(expr<<(K+1))|(1<<(1+i*32+bit))
            residue=reduce(row,basis)
            assert residue!=1
            if residue>1:
                native_independent+=1
                basis[residue.bit_length()-1]=residue
    assert native_independent==K
    selected=[]
    for at in range(951,955):
        for expr in expressions[1100+at]:
            residue=reduce(expr<<(K+1),basis)
            assert residue.bit_length()<=K+1, "unresolved selected bit"
            selected.append((residue>>1,residue&1))
    assert len(selected)==128
    # The original printer alone fixes only bit0 and bit31 at -237.
    def source_bit(expr):
        r=reduce(expr<<1,source)
        return r if r<=1 else None
    fixed={
        bit:source_bit(expr)
        for bit,expr in enumerate(expressions[1100-237])
        if source_bit(expr) is not None
    }
    return selected,fixed


def evaluate(selected,native):
    assert len(native)==len(DONORS)
    bits=sum((word&U)<<(32*i) for i,word in enumerate(native))
    output=[0,0,0,0]
    for i,(mask,constant) in enumerate(selected):
        output[i//32] |= (((bits&mask).bit_count()&1)^constant)<<(i%32)
    return output


def synthetic(expressions):
    for seed in (3,17,42,731,20261102,126063,882713):
        rng=random.Random(seed)
        native=[rng.getrandbits(32) for _ in range(624)]
        for idx in range(624,len(expressions)):
            x=(native[idx-624]&0x80000000)|(native[idx-623]&0x7fffffff)
            native.append((native[idx-227]^coupon.prior.twist(x))&U)
        packets=[
            b"".join(coupon.temper(native[1100+at+j]).to_bytes(4,"little")
                     for j in range(4))
            for at in coupon.prior.STARTS
        ]
        packets[129]=b""
        transform,_=affine_recovery(expressions,packets)
        donor=[native[1100+at] for at in DONORS]
        selected=[native[1100+at] for at in range(951,955)]
        assert evaluate(transform,donor)==selected
    print("Seven native seeded-state source-spool full-coupon holdouts: PASS")


def main():
    expressions=symbols()
    synthetic(expressions)
    raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==coupon.SOURCE_SHA
    fields=re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)
    assert len(fields)==len(coupon.prior.STARTS)==133
    assert coupon.prior.STARTS[129]==951
    packets=[
        b"" if i==129 else bytes.fromhex(field.decode())
        for i,field in enumerate(fields)
    ]
    selected,fixed=affine_recovery(expressions,packets)
    assert fixed=={0:1,31:0},fixed
    print("Original printer native state[-237] fixed source bits:",fixed)
    print("Complete coupon affine reconstruction from 7 future/past indexed donors:",
          DONORS,len(selected),"selected bits")
    print("Actual native donors historically indexed:",0,
          "; authentic K04 original selected bits recovered:",0)


if __name__=="__main__":
    main()
