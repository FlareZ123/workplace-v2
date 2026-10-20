"""Source-only falsifier of consecutive-output xoshiro256** for H-17 printer rows.

No K04 target, acceptance hash, XOR mask, route or selected payload is used.
Examines a bounded source-observed three-row predictor before any target test.
Synthetic state recovery is the positive control. Negative result is conditional
on direct xoshiro256** 64-bit output with 0..16 hidden draws per inter-row gap.
"""
from pathlib import Path
import hashlib
import re

U64 = (1 << 64) - 1
C5_INV = pow(5, -1, 1 << 64)
C9_INV = pow(9, -1, 1 << 64)
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def rotl(a, r):
    return ((a << r) | (a >> (64 - r))) & U64


def rotr(a, r):
    return ((a >> r) | (a << (64 - r))) & U64


def output(st):
    return (rotl((st[1] * 5) & U64, 7) * 9) & U64


def inv_output(y):
    return (rotr((y * C9_INV) & U64, 7) * C5_INV) & U64


def step(st):
    a, b, c, d = st
    t = (b << 17) & U64
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= t
    d = rotl(d, 45)
    return a, b, c, d


def apply_int_state(x, times):
    st = tuple((x >> (64 * k)) & U64 for k in range(4))
    observations = {}
    for t in range(max(times) + 1):
        if t in times:
            observations[t] = output(st)
        st = step(st)
    return observations


def step_symbolic(st):
    a, b, c, d = st
    t = [0] * 17 + b[:47]
    c = [c[i] ^ a[i] for i in range(64)]
    d = [d[i] ^ b[i] for i in range(64)]
    b = [b[i] ^ c[i] for i in range(64)]
    a = [a[i] ^ d[i] for i in range(64)]
    c = [c[i] ^ t[i] for i in range(64)]
    d = [d[(i - 45) % 64] for i in range(64)]
    return a, b, c, d


def symbolic_observations(max_t):
    st = [[1 << (64 * k + i) for i in range(64)] for k in range(4)]
    observations = []
    for _ in range(max_t + 1):
        observations.append(st[1][:])
        st = step_symbolic(st)
    return observations


def solve(equations):
    basis = {}
    for coeff, rhs in equations:
        while coeff:
            pivot = coeff.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (coeff, rhs)
                break
            prior, prior_rhs = basis[pivot]
            coeff ^= prior
            rhs ^= prior_rhs
        else:
            if rhs:
                return None, len(basis)
    x = 0
    for pivot in sorted(basis):
        coeff, rhs = basis[pivot]
        bit = rhs ^ ((coeff & x).bit_count() & 1)
        if bit:
            x |= 1 << pivot
    return x, len(basis)


def source_rows():
    source = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA256
    rows = []
    for line in raw.decode("ascii").splitlines():
        m = re.search(r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32})", line)
        if m and not (m.group(1) == "PS-261003-0417" and m.group(2) == "2"):
            rows.append((m.group(1), bytes.fromhex(m.group(5))))
    assert len(rows) == 132
    return rows


def constraints(symbolic, observed):
    equations = []
    for t, y in observed:
        source_state_word = inv_output(y)
        for bit in range(64):
            equations.append((symbolic[t][bit], (source_state_word >> bit) & 1))
    return equations


def test_synthetic():
    original_state = int("0123456789abcdefcba9876543210011beeff00dfacade42ff88eeddccbbaa55", 16)
    times = [0, 1, 5, 6, 9, 10]
    observed = apply_int_state(original_state, times)
    symbolic = symbolic_observations(max(times))
    recovered, rank = solve(constraints(symbolic, list(observed.items())))
    assert rank == 256 and recovered == original_state
    assert apply_int_state(recovered, times) == observed
    print(f"PASS synthetic exact xoshiro256** 256-bit state recovery, rank={rank}")


def main():
    test_synthetic()
    rows = source_rows()
    symbolic = symbolic_observations(40)
    first_four = rows[:4]
    checked = 0
    for endian in ("big", "little"):
        for reverse in (False, True):
            unpacked = []
            for name, payload in first_four:
                pair = [int.from_bytes(payload[i:i + 8], endian) for i in (0, 8)]
                if reverse:
                    pair.reverse()
                unpacked.append((name, pair))
            survivors = []
            for gap1 in range(17):
                for gap2 in range(17):
                    times = [0, 1, 2 + gap1, 3 + gap1, 4 + gap1 + gap2, 5 + gap1 + gap2]
                    observed = list(zip(times, unpacked[0][1] + unpacked[1][1] + unpacked[2][1]))
                    recovered, rank = solve(constraints(symbolic, observed))
                    checked += 1
                    if recovered is not None:
                        survivors.append((gap1, gap2, rank, recovered))
            print(f"endian={endian}, reverse_halves={reverse}, three-row exact state fits={len(survivors)}")
            for gap1, gap2, rank, recovered in survivors:
                if rank < 256:
                    continue
                for gap3 in range(17):
                    times = [6 + gap1 + gap2 + gap3, 7 + gap1 + gap2 + gap3]
                    prediction = apply_int_state(recovered, times)
                    if all(prediction[t] == value for t, value in zip(times, unpacked[3][1])):
                        print("FOUR-ROW PREDICTION MATCH", endian, reverse, gap1, gap2, gap3)
    assert checked == 1156
    print(f"Completed {checked} source-only gap/order tests. No target hash queried.")


if __name__ == "__main__":
    main()
