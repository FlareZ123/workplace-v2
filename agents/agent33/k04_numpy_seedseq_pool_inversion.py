"""Exact source-only NumPy SeedSequence MT19937 4-pool initialization falsifier.

Original H17 printer row129 (K04), routing mask, acceptance hashes and verifier
are completely withheld. The intact row3/34 five-pair MT recurrence source
witness was previously reconstructed in v1 by Agent1; this script pins the
unmodified original printer SHA and checks the four directly present row3 words.

NumPy producer equations:
  numpy/random/bit_generator.pyx -> SeedSequence.generate_state
  numpy/random/_mt19937.pyx -> MT19937.__init__ (key0=0x80000000, pos=623)
Original witness:
  workplace-v1/results/h17-k04-python-initialization-inversion.md
"""
from __future__ import annotations

import hashlib
import re
import struct
import sys
from pathlib import Path

import numpy as np

U32 = 0xFFFFFFFF
A = 0x9908B0DF
INIT_B = 0x8B51F9DD
MULT_B = 0x58F38DED
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
# Untempered (X[t+j],X[t+j+227]) from intact original spool, selected row withheld.
PAIRS = (
    (0x482F6361, 0xA757A2AC),
    (0x6C881CF7, 0x56FC62AE),
    (0x0429B798, 0xFFAAF2D5),
    (0x4B9C858C, 0xAC0962C9),
    (0xD47006FA, 0xCC8EB204),
)


def untemper(value: int) -> int:
    x = value
    for shift, mask, left in ((18, U32, False),
                              (15, 0xEFC60000, True),
                              (7, 0x9D2C5680, True),
                              (11, U32, False)):
        y = x
        for _ in range(6):
            x = y ^ (((x << shift) & mask) if left else (x >> shift))
        x &= U32
    return x


def initial_quad(pairs: tuple[tuple[int, int], ...]) -> list[int]:
    halves = []
    for a, b in pairs:
        x = a ^ b
        parity = x >> 31
        y = (((x ^ (A if parity else 0)) << 1) | parity) & U32
        halves.append((y & 0x80000000, y & 0x7FFFFFFF))
    return [halves[j][1] | halves[j + 1][0] for j in range(4)]


def constants(index: int) -> tuple[int, int]:
    initial = (INIT_B * pow(MULT_B, index, 1 << 32)) & U32
    return initial, (initial * MULT_B) & U32


def recover_pool(pairs: tuple[tuple[int, int], ...], phase: int) -> tuple[int, ...]:
    pool = [0] * 4
    for j, initialized in enumerate(initial_quad(pairs)):
        i = phase + 228 + j
        before, multiplier = constants(i)
        unhashed = initialized ^ (initialized >> 16)
        pool[i % 4] = ((unhashed * pow(multiplier, -1, 1 << 32)) & U32) ^ before
    return tuple(pool)


def initial_key(pool: tuple[int, ...]) -> np.ndarray:
    key = np.empty(624, dtype=np.uint32)
    for i in range(624):
        before, multiplier = constants(i)
        v = ((pool[i % 4] ^ before) * multiplier) & U32
        key[i] = v ^ (v >> 16)
    key[0] = 0x80000000
    return key


def raw_output(key: np.ndarray, count: int) -> list[int]:
    rng = np.random.MT19937(0)
    rng.state = {"bit_generator": "MT19937", "state": {"key": key, "pos": 623}}
    return [int(v) for v in rng.random_raw(count)]


def control() -> None:
    for seed in (0, 1234, 20261020, (1 << 127) | 0xDEADBEEF):
        rng = np.random.MT19937(seed)
        true_key = rng.state["state"]["key"].copy()
        true_pool = tuple(int(v) for v in np.random.SeedSequence(seed).pool)
        outputs = [int(v) for v in rng.random_raw(625)]
        assert outputs[0] == _temper(int(true_key[623]))
        for phase in (0, 13, 99, 218, 390, 392):
            pairs = tuple((untemper(outputs[1 + phase + j]),
                           untemper(outputs[1 + phase + j + 227]))
                          for j in range(5))
            recovered = recover_pool(pairs, phase)
            assert recovered == true_pool, (seed, phase)
            key = initial_key(recovered)
            assert np.array_equal(key, true_key), (seed, phase)
            assert raw_output(key, 625) == outputs, (seed, phase)
    print("SYNTHETIC_NUMPY_SEEDSEQ_FULL_STATE_PASS", 24)


def _temper(value: int) -> int:
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    return (value ^ (value >> 18)) & U32


def main(spool: Path) -> None:
    data = spool.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SPOOL_SHA
    lines = [line for line in data.splitlines() if line.startswith(b"2026-")]
    assert len(lines) == 133
    # Only verify that the source's ordinary row3 is part of the predeclared
    # original 5-pair recurrence. Row129 is not used, even as a candidate.
    stored = re.search(rb"PAYLOAD=([0-9A-F]{32})", lines[3]).group(1)
    first = tuple(untemper(v) for v in struct.unpack("<4I", bytes.fromhex(stored.decode())))
    assert first == tuple(pair[0] for pair in PAIRS[1:])
    control()

    surviving = []
    for phase in range(393):
        pool = recover_pool(PAIRS, phase)
        actual = raw_output(initial_key(pool), 625)
        if all(untemper(actual[1 + phase + j]) == a and
               untemper(actual[1 + phase + 227 + j]) == b
               for j, (a, b) in enumerate(PAIRS)):
            surviving.append((phase, pool))
    print("SOURCE_SPOOL_SHA256", SPOOL_SHA)
    print("WITHHELD_SELECTED_ROW", 129)
    print("FIRSTCYCLE_PHASES_TESTED", 393)
    print("FULL_FIVE_PAIR_NUMPY_POOL_MODELS_SURVIVING", len(surviving))
    if surviving:
        raise AssertionError("Source-compatible NumPy pool recovered: check independent row0 heldout before asserting any K04 bytes.")
    print("RESULT", "NO_MATCH under NumPy default pool4 firstcycle model; actual K04 bits gained 0")


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    main(source)
