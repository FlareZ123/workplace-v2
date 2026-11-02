"""Whole-state GF(2) MT19937 source projection for H-17 p951 hypothesis.

Read only. Original selected printer row129, K04/K08 commitments and mask are
never loaded. The printer draw chronology is hypothetical. This is a reusable
library plus exact rank SFT; it does not recover any actual coupon bytes.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path

START, STOP = -1100, 1600
SP_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]


def untemper(value: int) -> int:
    for shift, left, mask in ((18,False,0xFFFFFFFF),
                              (15,True,0xEFC60000),
                              (7,True,0x9D2C5680),
                              (11,False,0xFFFFFFFF)):
        cur = value
        for _ in range(6):
            cur = value ^ (((cur << shift) & mask) if left else (cur >> shift))
        value = cur & 0xFFFFFFFF
    return value


def symbolic_words() -> list[list[int]]:
    """Return all symbolic native MT words using 19968 unconstrained base bits."""
    words = [[0]*32 for _ in range(STOP-START+1)]
    for i in range(624):
        words[i] = [1 << (i*32+b) for b in range(32)]
    for t in range(len(words)-624):
        x, successor, donor = words[t], words[t+1], words[t+397]
        words[t+624] = [donor[b]
                         ^ (successor[b+1] if b<30 else x[31] if b==30 else 0)
                         ^ (successor[0] if (0x9908B0DF>>b)&1 else 0)
                         for b in range(32)]
    return words


def tempered_bits(word: list[int]) -> list[int]:
    """Linear 32-bit MT temper; getrandbits(13) selects output bits [19..31]."""
    x=word[:]
    y=[x[k]^(x[k+11] if k+11<32 else 0) for k in range(32)]
    x=y
    y=[x[k]^(x[k-7] if k>=7 and (0x9D2C5680>>k)&1 else 0)
       for k in range(32)]
    x=y
    y=[x[k]^(x[k-15] if k>=15 and (0xEFC60000>>k)&1 else 0)
       for k in range(32)]
    x=y
    return [x[k]^(x[k+18] if k+18<32 else 0) for k in range(32)]


class Basis:
    def __init__(self) -> None:
        self.rows: dict[int,int]={}
        self.values: dict[int,int]={}

    def add(self, row: int, rhs: int) -> bool:
        while row:
            p=row.bit_length()-1
            if p in self.rows:
                row^=self.rows[p]
                rhs^=self.values[p]
            else:
                self.rows[p],self.values[p]=row,rhs
                return True
        if rhs:
            raise ValueError("MT source equations inconsistent")
        return False

    def reduce(self, row: int, rhs: int=0) -> tuple[int,int]:
        while row:
            p=row.bit_length()-1
            if p not in self.rows:
                break
            row^=self.rows[p]
            rhs^=self.values[p]
        return row,rhs

    def add_word(self, forms: list[int], word: int) -> None:
        for bit, form in enumerate(forms):
            self.add(form,(word>>bit)&1)

    def clone(self) -> "Basis":
        copy=Basis()
        copy.rows=self.rows.copy()
        copy.values=self.values.copy()
        return copy


def printer_observations(root: Path) -> list[tuple[int,int]]:
    data=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest()==SP_SHA
    payloads=[bytes.fromhex(hexpart.decode("ascii"))
              for hexpart in re.findall(rb"PAYLOAD=([A-F0-9]{32})",data)]
    assert len(payloads)==len(STARTS)==133
    observed=[]
    for row,(payload,first) in enumerate(zip(payloads,STARTS)):
        if row==129:
            continue
        for i in range(4):
            raw=int.from_bytes(payload[i*4:i*4+4],"little")
            observed.append((first+i,untemper(raw)))
    assert len(observed)==528
    return observed


def target_quotient(basis: Basis, words: list[list[int]]) -> int:
    independent: dict[int,int]={}
    for pos in range(951,955):
        for form in words[pos-START]:
            row,_=basis.reduce(form)
            while row:
                p=row.bit_length()-1
                if p in independent:
                    row^=independent[p]
                else:
                    independent[p]=row
                    break
    return len(independent)


def donor_bound(basis: Basis, words: list[list[int]],
                positions: list[int]) -> tuple[int,int]:
    b=basis.clone()
    # This is geometry only. No hypothetical donor values are asserted.
    b.values={pivot:0 for pivot in b.rows}
    for pos in positions:
        for form in words[pos-START]:
            b.add(form,0)
    return len(b.rows)-len(basis.rows),target_quotient(b,words)


def main() -> None:
    root=Path(__file__).resolve().parents[2]
    if not (root/"evidence").exists():
        root=root/"resources"
    words=symbolic_words()
    basis=Basis()
    for index,value in printer_observations(root):
        basis.add_word(words[index-START],value)
    initial=(len(basis.rows),target_quotient(basis,words))
    hypothetical=list(range(-919,-914))+list(range(-465,-460))+list(range(-296,-291))
    three=donor_bound(basis,words,hypothetical)
    plus_future=donor_bound(basis,words,hypothetical+[1349,1406])
    assert initial==(15365,128),initial
    assert three==(478,1),three
    assert plus_future==(480,0),plus_future
    print("PASS original printer GF2 rank",initial)
    print("PASS hypothetical 15 donor words",three)
    print("PASS hypothetical 15 donors plus 2 future",plus_future)
    print("Actual selected coupon bits recovered: zero of 128.")


if __name__=="__main__":
    main()
