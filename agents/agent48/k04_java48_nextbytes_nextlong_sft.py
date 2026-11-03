"""SFT: conditional Java Random 48-bit printer producer on original intact records.

Model grounded in Oracle's java.util.Random next(int), nextBytes and nextLong
specifications. A missing coupon is not modeled unless intact source rows fit.
No original K04 selected ACK, route mask, commitments or K08 are inspected.

Run from the repository with Python, NumPy installed.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE = ROOT / "evidence" / "print" / "spool-reconstruction.log"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
A = np.uint64(0x5DEECE66D)
B = np.uint64(0xB)
MASK = np.uint64((1 << 48) - 1)
LOW = np.arange(65536, dtype=np.uint64)
MAX_GAP = 5


def advance(state: np.ndarray | np.uint64, steps: int) -> np.ndarray | np.uint64:
    with np.errstate(over="ignore"):
        for _ in range(steps):
            state = (state * A + B) & MASK
    return state


def witness(words: tuple[int, ...]) -> tuple[int, tuple[int, ...]] | None:
    """Reconstruct a 48-bit post-first-output state and three output spacings."""
    first, second, third, fourth = words
    states0 = (np.uint64(first) << np.uint64(16)) | LOW
    states1 = states0
    for gap1 in range(1, MAX_GAP + 1):
        states1 = advance(states1, 1)
        matches = states1[(states1 >> np.uint64(16)) == np.uint64(second)]
        for state1 in matches.tolist():
            state2 = np.uint64(state1)
            for gap2 in range(1, MAX_GAP + 1):
                state2 = advance(state2, 1)
                if int(state2 >> np.uint64(16)) != third:
                    continue
                state3 = np.uint64(state2)
                for gap3 in range(1, MAX_GAP + 1):
                    state3 = advance(state3, 1)
                    if int(state3 >> np.uint64(16)) == fourth:
                        original = int(states0[np.nonzero(states1 == state1)[0][0]])
                        return original, (gap1, gap2, gap3)
    return None


def nextlong_words(data: bytes, byteorder: str, reverse_longs: bool) -> tuple[int, ...]:
    """Undo Java signed-nextInt carry from two serialized nextLong outputs."""
    longs = [int.from_bytes(data[i:i + 8], byteorder) for i in (0, 8)]
    if reverse_longs:
        longs.reverse()
    words = []
    for value in longs:
        low = value & 0xFFFFFFFF
        high = (value >> 32) & 0xFFFFFFFF
        words.extend(((high + (low >> 31)) & 0xFFFFFFFF, low))
    return tuple(words)


def main() -> None:
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA256
    packets = []
    for line in raw.decode().splitlines():
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        if match:
            packets.append(bytes.fromhex(match.group(1)))
    assert len(packets) == 133
    intact = packets[:129] + packets[130:]
    assert len(intact) == 132

    # True seeded LCG controls, including three distinct hidden-call counts.
    seed0 = np.uint64(0xBBAA1133F2)
    gaps = (2, 4, 1)
    states = [advance(seed0, 1)]
    for n in gaps:
        states.append(advance(states[-1], n))
    planted = tuple(int(x >> np.uint64(16)) for x in states)
    assert witness(planted) == (int(states[0]), gaps)
    print("Synthetic seeded-gaps Java nextInt control: PASS")

    def signed32(value: int) -> int:
        return value if value < (1 << 31) else value - (1 << 32)

    seed1 = np.uint64(0xCACB00BA5E)
    states = [advance(seed1, 1)]
    for _ in range(3):
        states.append(advance(states[-1], 1))
    words = tuple(int(x >> np.uint64(16)) for x in states)
    longs = [((signed32(words[i]) << 32) + signed32(words[i + 1])) & ((1 << 64) - 1)
             for i in (0, 2)]
    planted_longs = b"".join(x.to_bytes(8, "big") for x in longs)
    assert nextlong_words(planted_longs, "big", False) == words
    assert witness(words) == (int(states[0]), (1, 1, 1))
    print("Synthetic signed Java nextLong control: PASS")

    def views(payload: bytes):
        for order in ("little", "big"):
            for reverse in (False, True):
                w = tuple(int.from_bytes(payload[i:i + 4], order) for i in range(0, 16, 4))
                yield f"nextBytes-{order}-reverse{int(reverse)}", w[::-1] if reverse else w
                yield f"nextLong-{order}-reverse{int(reverse)}", nextlong_words(payload, order, reverse)

    tests = 0
    hits = []
    for row, payload in enumerate(intact):
        for label, words in views(payload):
            state = witness(words)
            tests += 1
            if state is not None:
                hits.append((row, label, state))
    assert tests == 1056
    print("Original intact printer packets:", len(intact))
    print("Four-word serialization tests:", tests)
    print("Allowed gap between nextInt outputs: 1..5 LCG steps (0..4 hidden calls)")
    print("Complete original-source hits:", len(hits), hits)
    print("Selected original ACK2, route mask, K04 and K08 commitments untouched")


if __name__ == "__main__":
    main()
