"""Original H-17 K04, CPython integer seed after 0..623 *actual* prior outputs.

The 624 initial-register origins are separately reanchored. A cyclic register
rotation is not substituted for an output offset. The selected spool row129,
slot commitments, canonical candidate and route mask are never consulted.
Run: python agents/agent28/k04_cpython_real_output_offset_sft.py
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import hashlib
import random
import re

from k04_cpython_initarray_ringphase_source_sft import (
    mt, term_domains, consistent,
)

ROOT = Path(__file__).resolve().parents[2] / "resources"
ORIGINAL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U = 0xFFFFFFFF
MAG = 0x9908B0DF


class Basis:
    def __init__(self) -> None:
        self.rows: dict[int, tuple[int, int]] = {}

    def add(self, expression: int, value: int) -> None:
        while expression:
            pivot = expression.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = expression, value
                return
            prior, bit = self.rows[pivot]
            expression ^= prior
            value ^= bit
        assert value == 0, "retained source contradicts this MT schedule"

    def known(self, expression: int) -> int | None:
        value = 0
        while expression:
            pivot = expression.bit_length() - 1
            if pivot not in self.rows:
                return None
            prior, bit = self.rows[pivot]
            expression ^= prior
            value ^= bit
        return value


def words(offset: int) -> list[list[int]]:
    """Symbolic native initial register and all post-twist outputs to stage971."""
    stop = 624 + offset + 974
    state = [[1 << (32 * i + j) for j in range(32)] for i in range(624)]
    for i in range(624, stop):
        old = i - 624
        w0, w1, w2 = state[old], state[old + 1], state[old + 397]
        state.append([
            w2[j] ^ (w0[31] if j == 30 else w1[j + 1] if j < 30 else 0)
            ^ (w1[0] if (MAG >> j) & 1 else 0)
            for j in range(32)
        ])
    return state


def source_states(offset: int, packets: list[bytes]) -> list[tuple[int, int]]:
    assert len(packets) == len(mt.STARTS) == 133
    expressions = words(offset)
    basis = Basis()
    for row, (packet, p) in enumerate(zip(packets, mt.STARTS)):
        if row == 129:
            continue
        for lane in range(4):
            observed = int.from_bytes(packet[4 * lane: 4 * lane + 4], "little")
            native = mt.untemper(observed)
            for bit, term in enumerate(expressions[624 + offset + p + lane]):
                basis.add(term, (native >> bit) & 1)
    assert len(basis.rows) == 15365
    result = []
    for register_word in expressions[:624]:
        mask = value = 0
        for bit, expression in enumerate(register_word):
            known = basis.known(expression)
            if known is not None:
                mask |= 1 << bit
                value |= known << bit
        result.append((mask, value))
    return result


def synthetic_positive_controls() -> None:
    passed = 0
    for n in (1, 2, 4, 8, 16, 64, 128, 365, 623):
        seed = sum(((0x12345678 + i * 0x30158DA) & U) << (32 * i)
                   for i in range(n))
        for offset in (0, 1, 2, 3, 17, 73, 301, 623):
            generator = random.Random(seed)
            original_register = generator.getstate()[1][:624]
            emitted = [generator.getrandbits(32) for _ in range(offset + 975)]
            packets = [
                b"".join(emitted[offset + p + j].to_bytes(4, "little")
                         for j in range(4))
                for p in mt.STARTS
            ]
            states = source_states(offset, packets)
            assert all(value == (actual & mask)
                       for (mask, value), actual in
                       zip(states, original_register)), (n, offset)
            assert (states[0][1] ^ 0x80000000) & states[0][0] == 0
            assert consistent(term_domains(states, 0), n), (n, offset)
            passed += 1
    assert passed == 72
    print("SYNTHETIC: 72/72 genuine CPython seeded whole-stream/source tests PASS")


def original() -> None:
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ORIGINAL_SHA
    packets = [bytes.fromhex(v.decode()) for v in
               re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(packets) == len(mt.STARTS) == 133
    domains = {}
    zero_word_mask_hist = Counter()
    triple_domains_hist = Counter()
    for offset in range(624):
        states = source_states(offset, packets)
        mask, value = states[0]
        zero_word_mask_hist[mask.bit_count()] += 1
        if (value ^ 0x80000000) & mask:
            continue
        rows = term_domains(states, 0)
        domains[offset] = rows
        triple_domains_hist[len(rows)] += 1

    # Every n=1..623 and every actual output offset 0..623 inclusive.
    count = {n: sum(consistent(rows, n) for rows in domains.values())
             for n in range(1, 624)}
    assert len(domains) == 508
    assert zero_word_mask_hist == {0: 398, 1: 226}
    assert min(triple_domains_hist) == 28 and max(triple_domains_hist) == 98
    assert sum(v == 0 for v in count.values()) == 250
    assert all(count[n] == 0 for n in range(1, 89))
    assert count[89] == 11
    assert count[128] == count[256] == 0
    assert count[623] == 508
    assert sum(count.values()) == 74414
    assert [k for k, rows in domains.items() if consistent(rows, 89)] == [
        612, 613, 614, 615, 616, 617, 618, 619, 621, 622, 623
    ]
    print("ORIGINAL intact printer sources: rank 15365, copied row129 withheld")
    print("S0=80000000: 116/624 offsets excluded; 508 source-possible")
    print("Original seed lengths n1..623 × 624 actual output offsets: 388752 tests")
    print("Fully rejected lengths: 250; contiguous prefix n1..88")
    print("First conditionally possible n=89 at 11 offsets; n128, n256 excluded")
    print("Necessary compatible phase × n pairs:", sum(count.values()))
    print("No seed recovered and no authentic K04 coupon bit inferred")


if __name__ == "__main__":
    synthetic_positive_controls()
    original()
