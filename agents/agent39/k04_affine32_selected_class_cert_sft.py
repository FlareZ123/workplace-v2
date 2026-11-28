#!/usr/bin/env python3
"""Exact selected-CLASS source-only GF(2)-affine issuer contradiction certificates.

A real affine next-word map F(x)=M*x XOR c must send a zero XOR of augmented
(1||x) inputs to a zero XOR of 32-bit output words. Two original intact
RECOVER-class witness subsets violate this necessary condition. No selected
ACK2, mask, SHA or guess is needed.
"""
import argparse,hashlib,random,re
from pathlib import Path

PIN="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
CERTS=(
    ("SERIAL_RECOVER",(6,7,9,10,11,14,15,17,19,20,21,28,29,31,32,33),19),
    ("LANE1_RECOVER",(3,4,8,12,15,16,21,26,27,32),15),
)

def aff(x,coeff,pad):
    y=pad
    for j in range(32):
        if (x>>j)&1:y^=coeff[j]
    return y

def main(root):
    raw=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN
    rows=[dict(re.findall(r"([A-Z]+)=([^ ]+)",line)) for line in raw.decode().splitlines()[1:129]]
    assert len(rows)==128
    recovery=[r for r in rows if r["CLASS"]=="RECOVER"]
    assert len(recovery)==35
    packets=[[int.from_bytes(bytes.fromhex(r["PAYLOAD"])[i:i+4],"big") for i in (0,4,8,12)]
             for r in recovery]
    streams={"SERIAL_RECOVER":[x for packet in packets for x in packet],
             "LANE1_RECOVER":[packet[1] for packet in packets]}
    for label,indices,want_bits in CERTS:
        stream=streams[label]
        assert max(indices)<len(stream)-1
        inputs=outputs=0
        for i in indices:
            inputs^=(1<<32)|stream[i]
            outputs^=stream[i+1]
        assert inputs==0
        assert outputs!=0 and outputs.bit_count()==want_bits
        rng=random.Random(20261128+len(indices))
        for k in range(8):
            coeff=[rng.getrandbits(32) for j in range(32)]
            pad=rng.getrandbits(32)
            positive=0
            for i in indices:
                positive^=aff(stream[i],coeff,pad)
            assert positive==0
        print(label,"terms",len(indices),"input_dependency","ZERO",
              "original_output_XOR_nonzero_bits",want_bits,"8/8 synthetic controls PASS")
    print("FINAL two exact original-source selected-class contradictions; no K04 bits inferred")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]/"resources")
    arg=p.parse_args()
    main(arg.root)
