"""K04 p951: derive six SHA512 digest words of a hypothetical CPython bytes seed.

Source-only, selected printer row129 withheld; no acceptance digest or XOR.
Run: python agents/agent15/k04_p951_sha512_seed_fingerprint_sft.py
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
U = 0xFFFFFFFF
MAGIC = 0x9908B0DF
ANCHORS = (3,4,5,9,10,11)
EXPECTED = (0x04ADA358,0x70935318,0x61C74260,
            0x900C8064,0x3C3DF54F,0xB8BC5EA5)
BASE = [19650218]
for i in range(1,624):
    BASE.append((1812433253*(BASE[-1] ^ (BASE[-1] >> 30))+i)&U)


def mix(x: int, multiplier: int) -> int:
    return (x ^ (x >> 30))*multiplier & U


def key_term(j: int, a: int, b: int, c: int) -> int:
    i = j+1
    prior = ((b+i-1)&U) ^ mix(a,1566083941)
    later = ((c+i)&U) ^ mix(b,1566083941)
    return (later - (BASE[i] ^ mix(prior,1664525)))&U


def untemper(x: int) -> int:
    for shift,left,mask in ((18,False,U),(15,True,0xEFC60000),
                             (7,True,0x9D2C5680),(11,False,U)):
        y=x
        for _ in range(6):
            y=x ^ (((y<<shift)&mask) if left else y>>shift)
        x=y&U
    return x


def expressions() -> list[list[int]]:
    s=[[1<<(32*i+bit) for bit in range(32)] for i in range(624)]
    for i in range(624,1601):
        p,n,q=s[i-624],s[i-623],s[i-227]
        s.append([
            q[bit] ^
            (p[31] if bit==30 else n[bit+1] if bit<30 else 0) ^
            (n[0] if (MAGIC>>bit)&1 else 0)
            for bit in range(32)
        ])
    return s


def reduce(equation: int, basis: dict[int,int]) -> int:
    while equation:
        pivot=equation.bit_length()-1
        row=basis.get(pivot)
        if row is None:
            break
        equation ^= row
    return equation


def derive_seed_digest_words(packets: list[bytes],
                             expr: list[list[int]]) -> dict[int,int]:
    assert len(packets)==len(STARTS)==133 and STARTS[129]==951
    basis: dict[int,int]={}
    for row,start in enumerate(STARTS):
        if row==129:
            continue  # the disputed ACK2 is never interpreted here
        assert len(packets[row])==16
        for lane in range(4):
            token=untemper(int.from_bytes(
                packets[row][4*lane:4*lane+4],"little"
            ))
            for bit,equation in enumerate(expr[624+start+lane]):
                reduced=reduce((equation<<1)|((token>>bit)&1),basis)
                assert reduced != 1, "native original-source contradiction"
                if reduced > 1:
                    basis[reduced.bit_length()-1]=reduced
    assert len(basis)==15365
    for bit,equation in enumerate(expr[0]):
        reduced=reduce((equation<<1)|((0x80000000>>bit)&1),basis)
        assert reduced!=1
        if reduced>1:
            basis[reduced.bit_length()-1]=reduced
    assert len(basis)==15397
    result={}
    for j in ANCHORS:
        words=[]
        for i in (j-1,j,j+1):
            v=m=0
            for bit,equation in enumerate(expr[i]):
                reduced=reduce(equation<<1,basis)
                if reduced<=1:
                    v|=reduced<<bit
                    m|=1<<bit
            assert m==U,(j,i,hex(m))
            words.append(v)
        result[j]=(key_term(j,*words)-j)&U
    return result


def seeded_spool_control(n: int, expr: list[list[int]]) -> None:
    source=bytes((i*37+5)%256 for i in range(4*n-64))
    nonce=hashlib.sha512(source).digest()
    complete=int.from_bytes(source+nonce,"big")
    assert (complete.bit_length()+31)//32==n
    generator=random.Random(source)
    draws=[generator.getrandbits(32) for _ in range(967)]
    packet=[
        b"".join(draws[start+lane].to_bytes(4,"little") for lane in range(4))
        for start in STARTS
    ]
    packet[129]=b""
    observed=derive_seed_digest_words(packet,expr)
    expected={j:((complete>>(32*j))&U) for j in ANCHORS}
    assert observed==expected,(n,observed,expected)
    print(f"Actual seeded binary Python full-source positive n={n}: PASS",flush=True)


def main() -> None:
    expr=expressions()
    for n in (606,623):
        seeded_spool_control(n,expr)
    raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    tokens=re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)
    assert len(tokens)==133
    # Source's selected payload bytes are never decoded.
    packets=[b"" if i==129 else bytes.fromhex(token.decode("ascii"))
             for i,token in enumerate(tokens)]
    observed=derive_seed_digest_words(packets,expr)
    assert tuple(observed[j] for j in ANCHORS)==EXPECTED,observed
    print(json.dumps({
        "source_derived_SHA512_digest_32bit_big_endian_chunks": {
            str(j):f"{observed[j]:08X}" for j in ANCHORS
        },
        "conditional_seed_key_lengths": "606..623",
        "model": "p951 first-cycle first-output CPython seed(bytes, version=2)",
        "binary_seed_matches": "not asserted",
        "selected_K04_bits_authenticated": 0,
    },indent=2))


if __name__=="__main__":
    main()
