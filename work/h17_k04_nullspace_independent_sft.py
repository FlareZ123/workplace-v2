"""Read-only independent SFT of the conditional H17 K04 MT19937 nullspace.

Input is an unpacked H17 ZIP resources tree (default: repository resources/).
The 133-row position array is a published source-payload-consistent *model*.
This test does not authenticate the physical producer, reveal coupon bytes, or
read K04 ciphertext, XOR mask, verifier or acceptance digest.
"""
import argparse
import hashlib
import random
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "resources"
EXPECTED_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
STARTS = [0,7,15,22,30,38,44,51,67,76,84,92,99,112,120,126,132,138,144,151,158,165,171,179,186,192,198,205,211,218,224,230,237,243,250,260,268,278,285,298,305,311,318,328,339,346,352,358,364,370,376,382,388,394,401,407,416,423,429,436,442,456,463,474,481,489,495,507,515,522,530,536,543,549,563,569,576,584,590,597,604,610,617,624,632,638,644,650,659,665,671,679,689,697,705,714,721,733,740,747,753,759,766,772,783,789,796,807,813,820,826,833,839,846,853,861,870,876,882,888,896,906,916,922,928,934,940,946,951,955,959,963,967]


def forward(seed_state):
    state = seed_state.copy()
    for t in range(347):
        mixed = (state[t] & 0x80000000) | (state[t + 1] & 0x7FFFFFFF)
        state.append(state[t + 397] ^ (mixed >> 1) ^ (0x9908B0DF if mixed & 1 else 0))
    assert len(state) == 971
    return state


def temper(v):
    v ^= v >> 11
    v ^= (v << 7) & 0x9D2C5680
    v ^= (v << 15) & 0xEFC60000
    return v ^ (v >> 18)


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            i = value.bit_length() - 1
            if i not in pivots:
                pivots[i] = value
                break
            value ^= pivots[i]
    return len(pivots)


def basis():
    changes = [(j, 1 << bit) for j in range(332, 336) for bit in range(31)]
    changes.extend((j, 0x80000000) for j in range(332, 335))
    changes.append((104, 0x80000000))
    assert len(changes) == 128
    return changes


def check(root):
    source = (root / "evidence" / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == EXPECTED_SHA256, "spool original SHA256 changed"
    rows = [x for x in source.decode("ascii").splitlines() if " PAYLOAD=" in x]
    assert len(rows) == len(STARTS) == 133
    assert "JOB=PS-261003-0417" in rows[129]
    assert "ATTEMPT=2" in rows[129]
    assert STARTS[129] == 955 and STARTS[130] == 959
    intact = [start + j for r, start in enumerate(STARTS) if r != 129 for j in range(4)]
    assert len(intact) == 528 and max(intact) == 970
    assert not set(intact).intersection(range(955, 959))
    print("PASS original source SHA256 and 133 published model rows")

    for seed in (20261020, 99171125):
        rng = random.Random(seed)
        initial = [rng.getrandbits(32) for _ in range(624)]
        original = forward(initial)
        vectors = []
        for index, bitmask in basis():
            modified = initial.copy()
            modified[index] ^= bitmask
            after = forward(modified)
            assert all(original[i] == after[i] for i in intact), (seed, index, bitmask)
            vector = 0
            for j in range(4):
                vector |= (temper(original[955 + j]) ^ temper(after[955 + j])) << (32*j)
            assert vector
            vectors.append(vector)
        assert rank(vectors) == 128
        forbidden = initial.copy()
        forbidden[335] ^= 0x80000000
        assert forward(forbidden)[959] != original[959]
        print(f"PASS synthetic seed={seed}: 128 independent target bits, 528 intact words unchanged")

    count = 0
    for p in range(945, 956):
        for d in range(11, 66):
            for delta in range(627, d + 617):
                count += 1
                r43 = p - delta
                r44 = r43 + d
                r12 = r43 - 229
                r13 = r44 - 227
                r96 = r43 + 393
                r97 = r44 + 394
                u, q, m = p - 851, p - 623, p - 227
                assert r12 + 3 < u < r13
                assert r43 + 3 < q and q + 3 < r44
                assert r96 + 3 < m and m + 3 < r97
                assert u < 397 and q + 3 < 397
                assert d + 94 + 1 <= 160 < 227
    assert count == 16940
    print("PASS 16,940 conditional three-gap geometry bounds")
    print("REPLICATION COMPLETE. Historical K04 bits recovered: 0")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    check(parser.parse_args().root)
