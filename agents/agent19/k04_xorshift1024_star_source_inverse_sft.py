"""SFT: source-only exact GF(2) inverse of xorshift1024* and xorshift1024*phi.

USAGE: python agents/agent19/k04_xorshift1024_star_source_inverse_sft.py resources
Reference for state transition:
https://vigna.di.unimi.it/ftp/papers/xorshift.pdf
Reference phi multiplier:
https://svn.apache.org/repos/infra/websites/production/commons/content/proper/commons-rng/
Run with read-only official resources; no K04 target or selected ACK2 is read.
"""
from __future__ import annotations

import hashlib
import random
import re
import sys
from pathlib import Path

MASK = (1 << 64) - 1
MULTIPLIERS = (
    ("Vigna M8", 1181783497276652981),
    ("Vigna phi", 0x9e3779b97f4a7c13),
)
SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def source_words(root: Path) -> list[list[int]]:
    src = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(src).hexdigest() == SOURCE_SHA256
    matches = re.findall(
        rb"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) "
        rb"CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)", src
    )
    assert len(matches) == 133
    rows = [(int(m[0]), bytes.fromhex(m[4].decode())) for m in matches[:128]]
    assert [n for n, payload in rows] == list(range(300, 428))
    views = []
    for endian in ("big", "little"):
        for swapped in (False, True):
            words = []
            for _, payload in rows:
                halves = [payload[:8], payload[8:]]
                if swapped:
                    halves.reverse()
                words.extend(int.from_bytes(h, endian) for h in halves)
            views.append(words)
    return views


def generator_step(state: list[int], p: int, multiplier: int):
    old = state[p]
    p = (p + 1) & 15
    cur = state[p]
    cur ^= (cur << 31) & MASK
    state[p] = cur ^ old ^ (cur >> 11) ^ (old >> 30)
    return state[p] * multiplier & MASK, p


def symbolic_step(state: list[list[int]], p: int):
    old = state[p]
    p = (p + 1) & 15
    cur = state[p]
    shifted = [v ^ (cur[i - 31] if i >= 31 else 0) for i, v in enumerate(cur)]
    new = [
        shifted[i] ^ old[i]
        ^ (shifted[i + 11] if i + 11 < 64 else 0)
        ^ (old[i + 30] if i + 30 < 64 else 0)
        for i in range(64)
    ]
    state[p] = new
    return new, p


def emit(seed: list[int], positions: list[int], multiplier: int) -> list[int]:
    state = seed.copy()
    p, index = 0, 0
    values = []
    for target in positions:
        while index <= target:
            value, p = generator_step(state, p, multiplier)
            index += 1
        values.append(value)
    return values


def recover(
    observed: list[int], positions: list[int], multiplier: int, n: int = 48
):
    """Invert full native state; return state, contradiction index, equation rank."""
    state = [[1 << (64 * word + bit) for bit in range(64)]
             for word in range(16)]
    p, index, basis = 0, 0, {}
    inverse = pow(multiplier, -1, 1 << 64)
    for obs_index, (value, at) in enumerate(zip(observed[:n], positions[:n])):
        while index <= at:
            symbolic, p = symbolic_step(state, p)
            index += 1
        pre = (value * inverse) & MASK
        for bit, equation in enumerate(symbolic):
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
                    return None, obs_index, len(basis)
    bits = 0
    for pivot in sorted(basis):
        equation, rhs = basis[pivot]
        rhs ^= (equation & bits).bit_count() & 1
        if rhs:
            bits |= 1 << pivot
    return [(bits >> (64 * w)) & MASK for w in range(16)], None, len(basis)


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
    views = source_words(root)
    rng = random.Random(20261109)
    planted = [rng.getrandbits(64) for _ in range(16)]
    for name, multiplier in MULTIPLIERS:
        positives = 0
        contradictions = 0
        for stride in range(2, 129):
            positions = [(i // 2) * stride + (i % 2) for i in range(256)]
            if stride in (2, 5, 24):
                synthetic = emit(planted, positions, multiplier)
                recovered, bad, rank = recover(synthetic, positions, multiplier)
                assert bad is None and rank == 1024 and recovered == planted
                assert emit(recovered, positions, multiplier) == synthetic
                negative = synthetic.copy()
                negative[44] ^= 1
                altered, fail, _ = recover(negative, positions, multiplier)
                assert fail is not None or altered != planted
                positives += 1
            for view in views:
                recovered, bad, rank = recover(view, positions, multiplier)
                if bad is None:
                    assert emit(recovered, positions, multiplier) != view
                    raise AssertionError(
                        f"unexpected training survivor {name} {stride} {rank}"
                    )
                contradictions += 1
        assert positives == 3 and contradictions == 508
        print(
            f"{name}: planted full-state + 240 heldout words = {positives} PASS; "
            f"original whole-source layouts = {contradictions} contradicted; "
            "original survivors = 0"
        )
    print("No original K04 commitment candidate constructed; official data unchanged")


if __name__ == "__main__":
    main()
