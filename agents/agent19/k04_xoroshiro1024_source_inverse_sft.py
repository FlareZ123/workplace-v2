"""K04 original-source test: full inverse of xoroshiro1024* and xoroshiro1024**.

Read-only, standard-library SFT. Run from the repository root:
python agents/agent19/k04_xoroshiro1024_source_inverse_sft.py

Algorithm: Blackman/Vigna, Scrambled Linear Pseudorandom Number Generators,
Fig.2, https://vigna.di.unimi.it/ftp/papers/ScrambledLinear.pdf .
Official physical K04 copied ACK2 and target commitment are excluded entirely.
"""
from __future__ import annotations

import hashlib
import random
import re
import sys
from pathlib import Path

MASK = (1 << 64) - 1
SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
PHI = 0x9e3779b97f4a7c13
INV5, INV9, INVPHI = (pow(m, -1, 1 << 64) for m in (5, 9, PHI))


def rol(x: int, n: int) -> int:
    return ((x << n) | (x >> (64 - n))) & MASK


def native_inverse(value: int, kind: str) -> int:
    if kind == "starstar":
        return (rol((value * INV9) & MASK, 57) * INV5) & MASK
    return (value * INVPHI) & MASK


def native_next(state: list[int], pointer: int, kind: str):
    q = pointer
    pointer = (pointer + 1) & 15
    s0, s15 = state[pointer], state[q]
    value = ((rol((s0 * 5) & MASK, 7) * 9) & MASK
             if kind == "starstar" else (s0 * PHI) & MASK)
    s15 ^= s0
    state[q] = rol(s0, 25) ^ s15 ^ ((s15 << 27) & MASK)
    state[pointer] = rol(s15, 36)
    return value, pointer


def symbolic_next(state: list[list[int]], pointer: int):
    q = pointer
    pointer = (pointer + 1) & 15
    s0, s15 = state[pointer], state[q]
    changed = [a ^ b for a, b in zip(s15, s0)]
    state[q] = [s0[(i - 25) % 64] ^ changed[i]
                ^ (changed[i - 27] if i >= 27 else 0)
                for i in range(64)]
    state[pointer] = changed[-36:] + changed[:-36]
    return s0, pointer


def emit(seed: list[int], positions: list[int], kind: str) -> list[int]:
    state = seed.copy()
    pointer = next_index = 0
    outputs = []
    for target in positions:
        while next_index <= target:
            value, pointer = native_next(state, pointer, kind)
            next_index += 1
        outputs.append(value)
    return outputs


def invert(observed: list[int], positions: list[int], kind: str):
    state = [[1 << (64 * word + bit) for bit in range(64)]
             for word in range(16)]
    next_index = pointer = 0
    basis = {}
    for obs_idx, (value, stage) in enumerate(zip(observed[:48], positions[:48])):
        while next_index <= stage:
            output, pointer = symbolic_next(state, pointer)
            next_index += 1
        pre = native_inverse(value, kind)
        for bit, equation in enumerate(output):
            rhs = (pre >> bit) & 1
            while equation:
                pivot = equation.bit_length() - 1
                previous = basis.get(pivot)
                if previous is None:
                    basis[pivot] = equation, rhs
                    break
                equation ^= previous[0]
                rhs ^= previous[1]
            else:
                if rhs:
                    return None, obs_idx, len(basis)
    bits = 0
    for pivot in sorted(basis):
        equation, rhs = basis[pivot]
        rhs ^= (equation & bits).bit_count() & 1
        if rhs:
            bits |= 1 << pivot
    return [(bits >> (64 * w)) & MASK for w in range(16)], None, len(basis)


def original_views(root: Path) -> list[list[int]]:
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256
    rows = re.findall(
        rb"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) "
        rb"CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)", raw
    )
    assert len(rows) == 133
    assert [int(r[0]) for r in rows[:128]] == list(range(300, 428))
    payloads = [bytes.fromhex(r[4].decode()) for r in rows[:128]]
    return [
        [int.from_bytes(half, endian)
         for packet in payloads
         for half in ((packet[8:], packet[:8]) if swap
                      else (packet[:8], packet[8:]))]
        for endian in ("big", "little")
        for swap in (False, True)
    ]


def main() -> None:
    root = (Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[2] / "resources")
    views = original_views(root)
    planted = [random.Random(1947 + i).getrandbits(64) for i in range(16)]
    for kind in ("starstar", "star"):
        positives = contradictions = 0
        for stride in range(2, 129):
            positions = [(i // 2) * stride + i % 2 for i in range(256)]
            if stride in (2, 5, 24):
                synthetic = emit(planted, positions, kind)
                state, bad, rank = invert(synthetic, positions, kind)
                assert bad is None and rank == 1024 and state == planted
                assert emit(state, positions, kind) == synthetic
                tampered = synthetic.copy()
                tampered[44] ^= 1
                wrong, error, _ = invert(tampered, positions, kind)
                assert error is not None or wrong != planted
                positives += 1
            for view in views:
                state, bad, rank = invert(view, positions, kind)
                assert bad is not None, (
                    f"unexpected source-consistent {kind} stride {stride}, "
                    f"state rank {rank}"
                )
                contradictions += 1
        assert positives == 3 and contradictions == 508
        print(f"xoroshiro1024{kind}: 3 planted whole-state inversions/240 "
              f"withheld native64 words PASS; {contradictions} original native "
              "producer layouts contradicted; K04 source PASS 0")
    print("Six accepted REC8 slots unchanged; no K04 or K08 recovered")


if __name__ == "__main__":
    main()
