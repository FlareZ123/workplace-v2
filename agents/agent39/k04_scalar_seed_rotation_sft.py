"""H-17 K04: reversible scalar MT19937 seeding with 624 register rotations.

Usage: python agents/agent39/k04_scalar_seed_rotation_sft.py [resources_dir]
Only intact original printer payloads enter the source model. The selected
row129, route mask, K04/K08 commitments, and original verifier are never read.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

U = 0xffffffff
MAG = 0x9908b0df
MUL = 1812433253
MUL_INVERSE = pow(MUL, -1, 1 << 32)
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]


def temper(x: int) -> int:
    x ^= x >> 11
    x ^= (x << 7) & 0x9d2c5680
    x ^= (x << 15) & 0xefc60000
    return (x ^ (x >> 18)) & U


def untemper(x: int) -> int:
    for shift, left, mask in ((18, False, U), (15, True, 0xefc60000),
                              (7, True, 0x9d2c5680), (11, False, U)):
        y = x
        for _ in range(6):
            y = x ^ (((y << shift) & mask) if left else (y >> shift))
        x = y & U
    return x


def symbolic_mt() -> list[list[int]]:
    words = [[1 << (i*32+b) for b in range(32)] for i in range(624)]
    for at in range(624, 1596):
        p, n, q = words[at-624], words[at-623], words[at-227]
        words.append([q[b] ^ (p[31] if b == 30 else n[b+1] if b < 30 else 0)
                      ^ (n[0] if (MAG >> b) & 1 else 0) for b in range(32)])
    return words


def reduce(row: int, basis: dict[int, int]) -> int:
    while row:
        pivot = row.bit_length()-1
        previous = basis.get(pivot)
        if previous is None:
            break
        row ^= previous
    return row


def source_basis(words: list[list[int]], root: Path) -> dict[int, int]:
    raw = (root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    blocks = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(blocks) == len(STARTS) == 133 and STARTS[129] == 951
    equations = {}
    for row, p in enumerate(STARTS):
        if row == 129:
            continue
        block = bytes.fromhex(blocks[row].decode())
        for lane in range(4):
            native = untemper(int.from_bytes(block[lane*4:lane*4+4], "little"))
            for bit, term in enumerate(words[624+p+lane]):
                remaining = reduce((term<<1) | ((native>>bit)&1), equations)
                assert remaining != 1, "intact printer source contradicted"
                if remaining > 1:
                    equations[remaining.bit_length()-1] = remaining
    assert len(equations) == 15365
    return equations


def fixed_word(at: int, words: list[list[int]], basis: dict[int, int]) -> int:
    value = 0
    for bit, expression in enumerate(words[at]):
        residual = reduce(expression<<1, basis)
        assert residual in (0, 1), (at, bit, "word not fully source-determined")
        value |= residual << bit
    return value


def initialized(seed: int) -> list[int]:
    state = [seed]
    for i in range(1, 624):
        state.append((MUL * (state[-1] ^ (state[-1] >> 30)) + i) & U)
    return state


def invert_step(value: int, i: int) -> int:
    y = ((value-i) * MUL_INVERSE) & U
    return y ^ (y >> 30)


def phase_search(observed: dict[int, int]) -> list[tuple[int, int]]:
    hits = []
    for phase in range(624):
        seed = observed[622]
        for i in range(phase, 0, -1):
            seed = invert_step(seed, i)
        state = initialized(seed)
        rotation = (phase-622) % 624
        if all(state[(i+rotation) % 624] == value for i, value in observed.items()):
            hits.append((phase, seed))
    return hits


def native_output(state: list[int], p: int) -> tuple[int, int, int, int]:
    state = state[:]
    for i in range(624, 624+p+4):
        pair = (state[i-624]&0x80000000) | (state[i-623]&0x7fffffff)
        state.append((state[i-227] ^ (pair >> 1) ^
                      (MAG if pair&1 else 0)) & U)
    return tuple(state[624+p:624+p+4])


def main(root: Path) -> None:
    words = symbolic_mt()
    basis = source_basis(words, root)
    original = {i: fixed_word(i, words, basis) for i in (2, 3, 4, 622)}
    assert original == {2:0xE32E1557, 3:0x3152E7CB,
                        4:0xBBDD46A0, 622:0xBBD5A4AB}
    print("PASS: 132 intact original packets fix four complete native initial words")
    assert temper(native_output(initialized(5489), 0)[0]) == 3499211612
    controls = 0
    for seed in (1, 5489, 0xDEADBEEF):
        state = initialized(seed)
        for rotation in (0, 17, 390):
            shifted = state[rotation:] + state[:rotation]
            observed = {i: shifted[i] for i in original}
            found = phase_search(observed)
            assert ((622+rotation)%624, seed) in found
            for phase, recovered_seed in found:
                recovered = initialized(recovered_seed)
                r = (phase-622)%624
                recovered = recovered[r:] + recovered[:r]
                assert native_output(recovered, 951) == native_output(shifted, 951)
            controls += 1
    assert controls == 9
    print("PASS: 9/9 seeded phase-and-complete-selected-coupon controls")
    found = phase_search(original)
    assert found == [], found
    print("ORIGINAL: 624/624 scalar-init register rotations contradict fixed source words")
    print("No independently authenticated K04 coupon bit or final K08 word recovered")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else
         Path(__file__).resolve().parents[2]/"resources")
