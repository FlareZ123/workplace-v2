"""K04 source-only exclusion: long CPython seed B emitted by any affine LCG32.

B = concatenation of sequential 32-bit outputs of x->a*x+b (mod 2**32);
a,b arbitrary. Both BE and LE serialization. Original p951 initialized-state
and CPython version2 bytes seed assumptions remain historically unproven.
Never reads selected ACK2 row129, route mask, K04 target, or verifier.
Run: python agents/agent15/k04_p951_nested_lcg_seed_sft.py
"""
from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path

import k04_p951_sha512_seed_fingerprint_sft as fp

ROOT=Path(__file__).resolve().parents[2]
M=1<<32


def solve_coefficients(x2: int,y2: int,x1: int,y1: int) -> list[tuple[int,int]]:
    # The same affine transition must explain both disjoint adjacent pairs.
    delta=(x1-x2)%M
    rhs=(y1-y2)%M
    gcd=math.gcd(delta,M)
    if rhs%gcd:
        return []
    modulus=M//gcd
    if modulus==1:
        raise AssertionError("unbounded 2^32 affine slopes; need more witnesses")
    a0=((rhs//gcd)*pow(delta//gcd,-1,modulus))%modulus
    return [(a0+k*modulus,(y1-(a0+k*modulus)*x1)%M)
            for k in range(gcd)]


def advance(x: int,a: int,b: int,steps: int) -> int:
    for _ in range(steps):
        x=(a*x+b)%M
    return x


def test_family(words: dict[int,list[int]]) -> tuple[int,int]:
    choices=0
    survivors=0
    for endian in ("big","little"):
        view=lambda w:int.from_bytes(w.to_bytes(4,"big"),endian)
        x1,y1=view(words[23][0]),view(words[22][0])
        y2=view(words[601][0])
        for word602 in words[602]:
            x2=view(word602)
            for a,b in solve_coefficients(x2,y2,x1,y1):
                choices+=1
                # For B, key[j] is at word offset n-1-j. Thus two
                # source pairs j602->601 and j23->22 are 579 apart.
                if advance(x2,a,b,602-23)==x1:
                    survivors+=1
    return choices,survivors


def positives() -> None:
    # Truly generated long binary inputs, in either word serialization,
    # prove that the same 579-step model recovers the family from both pairs.
    for endian in ("big","little"):
        for n,a,b in ((606,1664525,1013904223),
                      (623,1103515245,12345)):
            seq=[0x12345678]
            for _ in range(n-18):
                seq.append((a*seq[-1]+b)%M)
            assert len(seq)==n-17
            def key(j: int) -> int:
                raw=seq[n-1-j].to_bytes(4,endian)
                return int.from_bytes(raw,"big")
            source={j:[key(j)] for j in (22,23,601,602)}
            count,hits=test_family(source)
            assert hits>=1,(endian,n,count,hits)
            print(f"synthetic n{n} {endian} word-order: "
                  f"{hits}/{count} source-consistent true affine LCG",flush=True)


def main() -> None:
    positives()
    source=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest()==fp.SOURCE_SHA
    fields=re.findall(rb"PAYLOAD=([0-9A-F]{32})",source)
    assert len(fields)==133 and fp.STARTS[129]==951
    packets=[b"" if i==129 else bytes.fromhex(t.decode("ascii"))
             for i,t in enumerate(fields)]
    _,_,domains=fp.derive_seed_digest_words(packets,fp.expressions())
    evidence={j:domains[j] for j in (22,23,601,602)}
    assert evidence=={
       22:[0xFD6A4CF7],
       23:[0x06EDCDAD],
       601:[0x49342EC0],
       602:[0x64589C88,0xE4589C88],
    },evidence
    tested,hits=test_family(evidence)
    assert (tested,hits)==(6,0),(tested,hits)
    print("Original intact source: 6/6 possible unrestricted affine "
          "LCG32 models contradict 579-word distance; zero survivors")
    print("Original K04 selected bits authenticated: 0/128")


if __name__=="__main__":
    main()
