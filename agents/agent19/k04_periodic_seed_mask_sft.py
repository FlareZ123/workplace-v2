"""Source-pinned H17 K04 conditional CPython binary-seed carrier test.

Run: python agents/agent19/k04_periodic_seed_mask_sft.py original-h17.zip
The first 132 intact printer rows, excluding selected ACK2, yield 86 exact or
two-choice seed words via Agent15's previously validated p951 inverse.
Test an original contiguous source byte window XORed or added modulo 2^32
with a periodic 1..64-word pad. Original K04 hash and suspect ACK2 are absent.
"""
from __future__ import annotations
import hashlib
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent15"))
from k04_p951_sparse_seed_donor_sft import recover_original_map, original_carriers

PERIODS = (1,2,3,4,5,6,7,8,12,16,24,32,48,64)
MASK = 0xffffffff

def domain_pads(b: bytes, end: int, j: int, choices: list[int],
                endian: str, mode: str) -> set[int]:
    k = end - 4*(j-15)
    raw = int.from_bytes(b[k:k+4], endian)
    return {(v ^ raw) if mode == "xor" else ((v-raw) & MASK)
            for v in choices}

def fits(b: bytes, end: int, domains: dict[int,list[int]],
         period: int, endian: str, mode: str) -> bool:
    pads: dict[int,set[int]] = {}
    for j, choices in domains.items():
        residue = j % period
        allowed = domain_pads(b,end,j,choices,endian,mode)
        if residue in pads:
            pads[residue].intersection_update(allowed)
            if not pads[residue]: return False
        else: pads[residue] = allowed
    return True

def controls(domains: dict[int,list[int]]) -> None:
    rng = random.Random(20261105)
    for period in (1,8,32,64):
        for mode in ("xor","add"):
            for endian in ("big","little"):
                source = bytearray(rng.randbytes(2600))
                end=2588
                pads=[rng.getrandbits(32) for _ in range(period)]
                for j, choices in domains.items():
                    key=choices[0]
                    pad=pads[j%period]
                    raw=(key ^ pad) if mode=="xor" else (key-pad)&MASK
                    k=end-4*(j-15)
                    source[k:k+4]=raw.to_bytes(4,endian)
                assert fits(source,end,domains,period,endian,mode)
    print("PLANTED: 16 source maps with differing periods/modes/endians PASS")

def main() -> None:
    assert len(sys.argv)==2
    archive=Path(sys.argv[1])
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==(
        "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7")
    domains={j:[int.from_bytes(v,"big") for v in opts]
             for j,opts in recover_original_map().items()}
    assert len(domains)==86 and sum(len(v)==1 for v in domains.values())==62
    controls(domains)
    sources=[(n,b) for n,b in original_carriers(archive) if len(b)>=2372]
    assert len(sources)==11
    tested=Counter()
    found=[]
    for name,b in sources:
        for period in PERIODS:
            groups=[sorted([j for j in domains if j%period==r])
                    for r in range(period)]
            lead=max(groups,key=len)
            assert len(lead)>=2
            j,k=lead[:2]
            for endian in ("big","little"):
                for mode in ("xor","add"):
                    for end in range(2372,len(b)+1):
                        tested[(period,mode)]+=1
                        a=domain_pads(b,end,j,domains[j],endian,mode)
                        c=domain_pads(b,end,k,domains[k],endian,mode)
                        if a.isdisjoint(c):continue
                        if fits(b,end,domains,period,endian,mode):
                            found.append((name,end,period,endian,mode))
    assert not found,found[:10]
    assert sum(tested.values())==5784128
    print("ORIGINAL: 11 sources, 86 constrained seed words,",
          sum(tested.values()),"complete window/mode tests; 0 compatible")
    print("PERIODS",PERIODS,"source-only K04 target unread")

if __name__=="__main__":main()
