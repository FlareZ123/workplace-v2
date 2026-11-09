"""H-17 xoshiro512** 512-bit state inversion, original source and whole-packet holdout.

Single runnable test, standard Python 3. Code follows Blackman/Vigna xoshiro512**
reference: https://prng.di.unimi.it/xoshiro512starstar.c
The disputed PS-0417 ACK2 and acceptance commitment are withheld from fitting.
"""
from __future__ import annotations

import hashlib
import itertools
import random
import re
import sys
from pathlib import Path

MASK = (1 << 64) - 1
INV5 = pow(5, -1, 1 << 64)
INV9 = pow(9, -1, 1 << 64)
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
CLASSES = ("LABEL", "STORES", "RECOVER")
DESTS = ("store", "bench", "desk")


def rol(x: int, n: int) -> int:
    return ((x << n) | (x >> (64 - n))) & MASK


def native_output(state: list[int]) -> int:
    return (rol((state[1] * 5) & MASK, 7) * 9) & MASK


def output_inverse(value: int) -> int:
    return (rol((value * INV9) & MASK, 57) * INV5) & MASK


def native_step(s: list[int]) -> None:
    t = (s[1] << 11) & MASK
    s[2] ^= s[0]
    s[5] ^= s[1]
    s[1] ^= s[2]
    s[7] ^= s[3]
    s[3] ^= s[4]
    s[4] ^= s[5]
    s[0] ^= s[6]
    s[6] ^= s[7]
    s[6] ^= t
    s[7] = rol(s[7], 21)


def symbolic_step(s: list[list[int]]) -> None:
    t = [0] * 11 + s[1][:53]
    for i, j in ((2, 0), (5, 1), (1, 2), (7, 3), (3, 4), (4, 5), (0, 6), (6, 7)):
        s[i] = [a ^ b for a, b in zip(s[i], s[j])]
    s[6] = [a ^ b for a, b in zip(s[6], t)]
    s[7] = s[7][-21:] + s[7][:-21]


def recover(observations: list[int], positions: list[int]):
    """Exact GF(2) inverse of unknown native 512-bit state, first <=16 words."""
    s = [[1 << (64 * word + bit) for bit in range(64)] for word in range(8)]
    basis: dict[int, tuple[int, int]] = {}
    stage = 0
    for index, (value, at) in enumerate(zip(observations[:16], positions[:16])):
        for _ in range(at - stage):
            symbolic_step(s)
        stage = at
        known_word = output_inverse(value)
        for bit, equation in enumerate(s[1]):
            rhs = (known_word >> bit) & 1
            while equation:
                pivot = equation.bit_length() - 1
                prior = basis.get(pivot)
                if prior is None:
                    basis[pivot] = (equation, rhs)
                    break
                equation ^= prior[0]
                rhs ^= prior[1]
            else:
                if rhs:
                    return None, index, len(basis)
    state_bits = 0
    for pivot in sorted(basis):
        equation, rhs = basis[pivot]
        rhs ^= ((equation & state_bits).bit_count() & 1)
        if rhs:
            state_bits |= 1 << pivot
    state = [(state_bits >> (64 * i)) & MASK for i in range(8)]
    return state, None, len(basis)


def generate(state: list[int], positions: list[int]) -> list[int]:
    s = state.copy()
    stage = 0
    outputs = []
    for at in positions:
        for _ in range(at - stage):
            native_step(s)
        stage = at
        outputs.append(native_output(s))
    return outputs


def source(root: Path):
    data = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == SOURCE_SHA, "original source differs"
    pattern = re.compile(rb"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) "
                         rb"CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)")
    rows = []
    for line in data.splitlines():
        m = pattern.search(line)
        if m:
            rows.append((int(m[1]), int(m[2]), m[3].decode(), m[4].decode(),
                         bytes.fromhex(m[5].decode()), m[6].decode()))
    assert len(rows) == 133
    assert [r[0] for r in rows[:128]] == list(range(300, 428))
    return rows[:128]


def observed_words(rows, endian: str, swapped: bool):
    output = []
    for row in rows:
        halves = [row[4][:8], row[4][8:]]
        if swapped:
            halves.reverse()
        output.extend(int.from_bytes(part, endian) for part in halves)
    return output


def fixed_positions(n: int, stride: int):
    return [(i // 2) * stride + (i % 2) for i in range(n)]


def metadata_positions(rows, class_cost, dest_cost, n: int):
    stages = []
    stage = 0
    for row in rows[:(n + 1) // 2]:
        stages.extend((stage, stage + 1))
        stage += 2 + class_cost[row[3]] + dest_cost[row[5]]
    return stages[:n]


def planted_controls(rows):
    rng = random.Random(20261109)
    actual = [rng.getrandbits(64) for _ in range(8)]
    schedules = [
        fixed_positions(256, s) for s in (2, 3, 17, 64, 128)
    ]
    schedules.append(metadata_positions(
        rows, {"LABEL": 1, "STORES": 0, "RECOVER": 2},
        {"store": 1, "bench": 0, "desk": 1}, 256))
    for stages in schedules:
        values = generate(actual, stages)
        solved, inconsistent_at, rank = recover(values, stages)
        assert inconsistent_at is None and rank == 512 and solved == actual
        assert generate(solved, stages) == values, "240-word holdout mismatch"
        corrupted = values.copy()
        corrupted[15] ^= 1
        altered, fail, _ = recover(corrupted, stages)
        assert fail is not None or altered != actual
    print("synthetic: six exact 512-bit state inversions, 240 native holdouts each, "
          "one-bit negative controls PASS")


def main():
    root = (Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[2] / "resources")
    rows = source(root)
    planted_controls(rows)
    views = [(e, swap, observed_words(rows, e, swap))
             for e in ("little", "big") for swap in (False, True)]
    counts = {"fixed": 0, "class": 0, "dest": 0, "add01": 0}
    survivors = []
    for stride in range(2, 129):
        stages = fixed_positions(16, stride)
        counts["fixed"] += 1
        for endian, swapped, words in views:
            seed, bad, rank = recover(words, stages)
            if bad is None:
                full = generate(seed, fixed_positions(256, stride))
                survivors.append(("fixed", stride, endian, swapped, rank, full == words))
    seen = set()
    for mode in ("class", "dest", "add01"):
        choices = range(9) if mode != "add01" else range(2)
        repeat = 3 if mode != "add01" else 6
        for assignment in itertools.product(choices, repeat=repeat):
            if mode == "class":
                class_cost = dict(zip(CLASSES, assignment))
                dest_cost = dict.fromkeys(DESTS, 0)
            elif mode == "dest":
                class_cost = dict.fromkeys(CLASSES, 0)
                dest_cost = dict(zip(DESTS, assignment))
            else:
                class_cost = dict(zip(CLASSES, assignment[:3]))
                dest_cost = dict(zip(DESTS, assignment[3:]))
            stages = metadata_positions(rows, class_cost, dest_cost, 16)
            identifier = tuple(stages)
            if identifier in seen:
                continue
            seen.add(identifier)
            counts[mode] += 1
            for endian, swapped, words in views:
                seed, bad, rank = recover(words, stages)
                if bad is None:
                    full_positions = metadata_positions(
                        rows, class_cost, dest_cost, 256)
                    survivors.append((mode, assignment, endian, swapped, rank,
                                      generate(seed, full_positions) == words))
    assert counts == {"fixed": 127, "class": 729, "dest": 648, "add01": 12}
    assert not survivors, f"unexpected source-consistent model(s): {survivors!r}"
    print("original source: 128 ordinary ACK1 packets = 256 "
          "whole 64-bit outputs, four serializers")
    print("source-only stage hypotheses:", counts,
          "tested serializer assignments:", 4 * sum(counts.values()))
    print("all layouts contradict a 512-bit xoshiro512** model before output 16")
    print("no K04 coupon recovered, no original commitments changed")


if __name__ == "__main__":
    main()
