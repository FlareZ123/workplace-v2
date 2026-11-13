"""H-17 source-only TinyMT64 constant-gap, low-bit GF(2) producer probe.

Official TinyMT64 reference: MersenneTwister-Lab/TinyMT tinymt/tinymt64.h.
The disputed K04 ACK2 payload is excluded from fitting and controls.
No original source, official verifier, route or commitment is mutated.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MAT1, MAT2, TMAT = 0xFA051F40, 0xFFD0FFF4, 0x58D02FFEFFBFFFBC
MASK64 = (1 << 64) - 1


def step(state: tuple[int, int]) -> tuple[int, int]:
    old0, old1 = state
    x = (old0 & 0x7FFFFFFFFFFFFFFF) ^ old1
    x ^= (x << 12) & MASK64
    x ^= x >> 32
    x ^= (x << 32) & MASK64
    x ^= (x << 11) & MASK64
    return ((old1 ^ (MAT1 if x & 1 else 0)) & MASK64,
            (x ^ ((MAT2 << 32) if x & 1 else 0)) & MASK64)


def temper(state: tuple[int, int]) -> int:
    y = ((state[0] + state[1]) & MASK64) ^ (state[0] >> 8)
    return y ^ (TMAT if y & 1 else 0)


def output_lsb(state: tuple[int, int]) -> int:
    # TMAT has bit 0 clear, and bit 0 of modular addition is XOR.
    return (state[0] ^ state[1] ^ (state[0] >> 8)) & 1


def official_seed_one() -> tuple[int, int]:
    state = ((1 ^ (MAT1 << 32)) & MASK64, MAT2 ^ TMAT)
    for i in range(1, 8):
        prev = state[(i - 1) & 1]
        new = (state[i & 1] ^ (i + 6364136223846793005 * (prev ^ (prev >> 62)))) & MASK64
        state = (new, state[1]) if not i & 1 else (state[0], new)
    if (state[0] & 0x7FFFFFFFFFFFFFFF) == 0 and state[1] == 0:
        state = (ord("T"), ord("M"))
    return state


def sample_seed_one() -> list[int]:
    st = official_seed_one()
    vals = []
    for _ in range(30):
        st = step(st)
        vals.append(temper(st))
    return vals


def masks_for_output_bit(max_t: int) -> list[int]:
    masks = [0] * max_t
    for i in range(128):
        bit = 1 << i
        state = (bit, 0) if i < 64 else (0, bit >> 64)
        for t in range(max_t):
            state = step(state)
            if output_lsb(state):
                masks[t] |= bit
    return masks


def gf2_fit(equations: list[tuple[int, int]]) -> tuple[bool, int, int, int]:
    pivots: dict[int, tuple[int, int]] = {}
    for index, (mask, val) in enumerate(equations):
        while mask:
            pivot = mask.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = mask, val
                break
            other, rhs = pivots[pivot]
            mask ^= other
            val ^= rhs
        else:
            if val:
                return False, len(pivots), index + 1, 0
    sol = 0
    for pivot in sorted(pivots):
        mask, rhs = pivots[pivot]
        if rhs ^ ((mask & sol).bit_count() & 1):
            sol |= 1 << pivot
    return True, len(pivots), len(equations), sol


def observations(packets: list[bytes], order: int, endian: str) -> list[int]:
    vals = []
    for packet in packets:
        halves = [packet[0:8], packet[8:16]]
        if order:
            halves.reverse()
        vals.extend(int.from_bytes(h, endian) & 1 for h in halves)
    return vals


def rows_for(masks: list[int], observed: list[int], gap: int) -> list[tuple[int, int]]:
    return [(masks[(j // 2) * (gap + 2) + (j & 1)], bit)
            for j, bit in enumerate(observed)]


def gen_packets(state: tuple[int, int], gap: int, count: int, order: int, endian: str) -> list[bytes]:
    packets = []
    for _ in range(count):
        words = []
        for _ in range(2):
            state = step(state)
            words.append(temper(state).to_bytes(8, endian))
        if order:
            words.reverse()
        packets.append(b"".join(words))
        for _ in range(gap):
            state = step(state)
    return packets


def run() -> None:
    assert sha256(SPOOL.read_bytes()).hexdigest() == SHA
    values = [bytes.fromhex(x) for x in re.findall(r"PAYLOAD=([0-9A-F]{32})", SPOOL.read_text())]
    assert len(values) == 133
    expected_seed_1 = [
        15503804787016557143, 17280942441431881838, 2177846447079362065,
        10087979609567186558, 8925138365609588954, 13030236470185662861,
    ]
    assert sample_seed_one()[:6] == expected_seed_1
    probe_state = (0x0123456789ABCDEF, 0xFEDCBA9876543210)
    for _ in range(19):
        assert output_lsb(probe_state) == (temper(probe_state) & 1)
        probe_state = step(probe_state)
    max_t = 128 * (8 + 2)
    masks = masks_for_output_bit(max_t)
    # Planted full-input producer models with 48 blind entire packets each.
    positives = []
    for gap, order, endian in [(0, 0, "little"), (3, 1, "big"), (8, 0, "big")]:
        original_state = (0x0123456789ABCDEF, 0xFEDCBA9876543210)
        packets = gen_packets(original_state, gap, 128, order, endian)
        rows = rows_for(masks, observations(packets, order, endian), gap)
        fit, rank, count, state_bits = gf2_fit(rows[:160])
        assert fit and rank == 127, (gap, rank, count)
        state = (state_bits & MASK64, state_bits >> 64)
        assert gen_packets(state, gap, 128, order, endian) == packets
        assert all(((m & state_bits).bit_count() & 1) == bit for m, bit in rows)
        positives.append(dict(gap=gap, order=order, endian=endian,
                              rank=rank, whole_heldout_packets=48))
    results = []
    for gap in range(9):
        for order in (0, 1):
            for endian in ("little", "big"):
                obs = observations(values[:128], order, endian)
                rows = rows_for(masks, obs, gap)
                fit, rank, count, state_bits = gf2_fit(rows[:160])
                late_hit = None
                if fit:
                    st = (state_bits & MASK64, state_bits >> 64)
                    predicted = gen_packets(st, gap, 128, order, endian)
                    late_hit = sum(predicted[i] == values[i] for i in range(80, 128))
                results.append(dict(gap=gap, order=order, endian=endian,
                                    first80_consistent=fit, rank=rank,
                                    equations_examined=count, blind_full_matches=late_hit))
    print(json.dumps(dict(official_seed_one_control=True, positive_controls=positives,
                          tested_models=len(results),
                          consistent_training=sum(x["first80_consistent"] for x in results),
                          model_results=results), indent=2))
    assert len(results) == 36


if __name__ == "__main__":
    run()
