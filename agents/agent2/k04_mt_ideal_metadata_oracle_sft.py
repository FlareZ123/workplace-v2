"""Rank-first H-17 K04: ideal metadata-oracle ceiling under hypothetical p951 MT.
Run from any cwd: python agents/agent2/k04_mt_ideal_metadata_oracle_sft.py
No selected ACK or acceptance commitment ever enters a reconstruction.
"""
from pathlib import Path
import hashlib
import re
import sys

AGENTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTS))
from agent49 import k04_p951_symbolic_basis as mt

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROOT = Path(__file__).resolve().parents[2] / "resources"
U = 0xFFFFFFFF

class LinearBasis:
    def __init__(self, rows=None):
        self.rows = {} if rows is None else rows.copy()
        self.rank = len(self.rows)

    def insert(self, vector):
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = vector
                self.rank += 1
                return True
            vector ^= self.rows[pivot]
        return False

def selected_free(base, selected):
    augmented = LinearBasis(base.rows)
    for equation in selected:
        augmented.insert(equation)
    return augmented.rank - base.rank

def synthetic_control(state):
    # Independent full-word native MT forward recurrence, including selected stage951.
    concrete = [((i * 0x9E3779B9) ^ (i << 16)) & U for i in range(624)]
    for index in range(624, len(state)):
        old = index - 624
        combined = (concrete[old] & 0x80000000) | (concrete[old + 1] & 0x7FFFFFFF)
        concrete.append((concrete[old + 397] ^ (combined >> 1) ^
                         (mt.MAG if combined & 1 else 0)) & U)
    initial = sum(word << (32 * i) for i, word in enumerate(concrete[:624]))
    for index in (0, 623, 624, 951, 1040):
        inferred = sum(
            ((vector & initial).bit_count() & 1) << bit
            for bit, vector in enumerate(mt.get(state, index))
        )
        assert inferred == concrete[index - mt.ORIGIN], (index, inferred)
    print("PASS: genuine synthetic native MT states including withheld stage951")

def main():
    source = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA
    assert len(re.findall(rb"PAYLOAD=([0-9A-F]{32})", source)) == len(mt.STARTS) == 133
    assert b"2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in source
    state = mt.words()
    synthetic_control(state)
    source_rank = LinearBasis()
    for row, start in enumerate(mt.STARTS):
        if row == 129:
            continue
        for lane in range(4):
            for equation in mt.get(state, start + lane):
                source_rank.insert(equation)
    assert source_rank.rank == 15365
    selected = [
        equation
        for lane in range(4)
        for equation in mt.get(state, mt.STARTS[129] + lane)
    ]
    assert len(selected) == 128 and selected_free(source_rank, selected) == 128
    print("original-source rank", source_rank.rank, "selected quotient", 128)

    # All hidden 32-bit output stages between packet payloads, including those
    # where NO original metadata draw was observed. Stronger than any proposed
    # ordinary 2-bit CLASS/DEST sampler; row129 and its stages stay excluded.
    hidden = [
        start + offset
        for row, start in enumerate(mt.STARTS[:129])
        for offset in range(4, mt.STARTS[row + 1] - start)
    ]
    assert len(hidden) == 435 and all(x not in range(951, 955) for x in hidden)
    layers = [[] for _ in range(32)]
    for stage in hidden:
        for bit, equation in enumerate(mt.temper(mt.get(state, stage))):
            layers[31 - bit].append(equation)

    working = LinearBasis(source_rank.rows)
    expected = {
        1: (15623, 128), 2: (15873, 128), 3: (16106, 128),
        4: (16339, 128), 6: (16805, 128), 8: (17271, 128),
        12: (18203, 128), 16: (19090, 127), 20: (19302, 95),
        24: (19514, 63), 28: (19726, 31), 32: (19937, 0),
    }
    for depth, equations in enumerate(layers, 1):
        for equation in equations:
            working.insert(equation)
        if depth in expected:
            actual = (working.rank, selected_free(working, selected))
            assert actual == expected[depth], (depth, actual)
            print(
                "ideal known topbits", depth, "of 435 hidden words",
                "rank", actual[0], "selected free", actual[1]
            )
    print("PASS: all hypothetical oracle geometry checks; no original target guessed")

if __name__ == "__main__":
    main()
