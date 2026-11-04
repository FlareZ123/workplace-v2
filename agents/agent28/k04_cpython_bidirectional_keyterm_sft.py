"""Original H-17 K04: exact CPython key-term state propagation, first-cycle offsets.

Checks all seed-array n1..200 and n217 across 624 original-source startup epochs.
Source selected ACK row129, mask, commitments and candidate are never consulted.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import hashlib
import random
import re

from k04_cpython_real_output_offset_sft import source_states, mt, ROOT
from k04_cpython_initarray_ringphase_source_sft import term_domains, consistent

U = 0xFFFFFFFF
G = [19650218]
for i in range(1, 624):
    G.append((1812433253 * (G[-1] ^ (G[-1] >> 30)) + i) & U)
INV1 = pow(1566083941, -1, 1 << 32)
INV2 = pow(1664525, -1, 1 << 32)


def f(c: int, value: int) -> int:
    return c * (value ^ (value >> 30)) & U


def inv_f(inv: int, value: int) -> int:
    x = (inv * value) & U
    return x ^ (x >> 30)


def key_term(a: int, b: int, c: int, i: int) -> int:
    p = (((b + i - 1) & U) ^ f(1566083941, a))
    q = (((c + i) & U) ^ f(1566083941, b))
    return (q - (G[i] ^ f(1664525, p))) & U


def candidates(mask: int, value: int) -> tuple[int, ...]:
    if mask == U:
        return (value,)
    if mask.bit_count() == 31:
        return (value, value | ((~mask) & U))
    return ()


def key_domains(state: list[tuple[int, int]], n: int):
    domains: dict[int, set[int]] = {}
    for i in range(4, 624):
        a, b, c = [candidates(*state[i - j]) for j in (2, 1, 0)]
        if not a or not b or not c:
            continue
        position = (i - 1) % n
        vals = {(key_term(x, y, z, i) - position) & U
                for x in a for y in b for z in c}
        if position in domains:
            domains[position].intersection_update(vals)
            if not domains[position]:
                return None
        else:
            domains[position] = vals
    return domains


def forward(a: int, b: int, i: int, key: int, n: int) -> int:
    p = (((b + i - 1) & U) ^ f(1566083941, a))
    q = (G[i] ^ f(1664525, p)) + key + (i - 1) % n
    return ((q & U) ^ f(1566083941, b)) - i & U


def backward(b: int, c: int, i: int, key: int, n: int) -> int:
    q = (((c + i) & U) ^ f(1566083941, b))
    p = inv_f(INV2, G[i] ^ ((q - key - (i - 1) % n) & U))
    return inv_f(INV1, (((b + i - 1) & U) ^ p))


def propagate(original: list[tuple[int, int]], n: int):
    state = list(original)
    for _ in range(100):
        before = sum(mask == U for mask, _ in state)
        domains = key_domains(state, n)
        if domains is None:
            return False, "incompatible_seed_word"
        for i in range(4, 624):
            a, b, c = state[i - 2:i + 1]
            residue = (i - 1) % n
            domain = domains.get(residue)
            if domain is None or len(domain) != 1:
                continue
            key = next(iter(domain))
            if a[0] == U and b[0] == U and c[0] != U:
                val = forward(a[1], b[1], i, key, n)
                if (val & c[0]) != c[1]:
                    return False, "forward_word_conflict"
                state[i] = (U, val)
            if b[0] == U and c[0] == U and a[0] != U:
                val = backward(b[1], c[1], i, key, n)
                if (val & a[0]) != a[1]:
                    return False, "backward_word_conflict"
                state[i - 2] = (U, val)
        if sum(mask == U for mask, _ in state) == before:
            return True, state
    raise AssertionError("Unexpected nonconverging generator propagation")


def genuine_seed_tests() -> None:
    count = 0
    for n in (1, 2, 4, 16, 89, 113, 166, 200, 217, 249, 365, 623):
        integer = sum(((0x12345678 + j * 0x30158DA) & U) << (32 * j)
                      for j in range(n))
        for offset in (0, 17, 301, 612, 623):
            generator = random.Random(integer)
            register = generator.getstate()[1][:624]
            outputs = [generator.getrandbits(32) for _ in range(offset + 975)]
            packets = [
                b"".join(outputs[offset + p + j].to_bytes(4, "little")
                         for j in range(4)) for p in mt.STARTS
            ]
            states = source_states(offset, packets)
            accepted, result = propagate(states, n)
            assert accepted, (n, offset, result)
            for i, (mask, value) in enumerate(result):
                assert value == (register[i] & mask), (n, offset, i)
            count += 1
    assert count == 60
    print("SYNTHETIC: 60/60 genuine CPython seed/offset histories PASS")


def original_source() -> None:
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    )
    packets = [bytes.fromhex(v.decode()) for v in
               re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(packets) == 133

    baseline = Counter()
    survived = Counter()
    n217_surviving_epochs = []
    for k in range(624):
        states = source_states(k, packets)
        mask, value = states[0]
        if (value ^ 0x80000000) & mask:
            continue
        source_terms = term_domains(states, 0)
        for n in (*range(1, 201), 217):
            if not consistent(source_terms, n):
                continue
            baseline[n] += 1
            accepted, result = propagate(states, n)
            if accepted:
                survived[n] += 1
                if n == 217:
                    n217_surviving_epochs.append(k)

    assert sum(baseline[n] for n in range(1, 201)) == 585
    assert all(survived[n] == 0 for n in range(1, 201))
    assert baseline[217] == 51 and survived[217] == 5
    assert n217_surviving_epochs == [593, 595, 608, 617, 619]
    print("ORIGINAL: 585 prior-necessary n1..200 models -> 0 survivors")
    print("ORIGINAL: n217 51 prior-necessary -> 5 surviving output offsets",
          n217_surviving_epochs)
    print("No originally authenticated selected coupon value or bit")


if __name__ == "__main__":
    genuine_seed_tests()
    original_source()
