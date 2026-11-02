"""SFT: infer xoshiro128** hidden state from untouched four-word printer rows.
Probes historical *intact* stream prediction and same-job REQUESTED outer attempts.
Neither selected 18:02 ACK2 bytes, K04 mask, nor acceptance hash are read.
Run: python agents/agent3/k04_xoshiro128ss_source_sft.py resources
"""
import re
import sys
from pathlib import Path

U = (1 << 32) - 1
I5 = pow(5, -1, 1 << 32)
I9 = pow(9, -1, 1 << 32)

def rol(v, n):
    return ((v << n) | (v >> (32 - n))) & U

def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & U

def output(s):
    return rol((s[1] * 5) & U, 7) * 9 & U

def decode(v):
    return ror((v * I9) & U, 7) * I5 & U

def step(s):
    a, b, c, d = s
    t = (b << 9) & U
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= t
    d = rol(d, 11)
    return [a, b, c, d]

def table(count):
    st = [[1 << (k * 32 + bit) for bit in range(32)] for k in range(4)]
    out = []
    for _ in range(count):
        out.append(st[1][:])
        a, b, c, d = st
        t = [0] * 9 + b[:23]
        c = [c[i] ^ a[i] for i in range(32)]
        d = [d[i] ^ b[i] for i in range(32)]
        b = [b[i] ^ c[i] for i in range(32)]
        a = [a[i] ^ d[i] for i in range(32)]
        c = [c[i] ^ t[i] for i in range(32)]
        d = [d[(i - 11) % 32] for i in range(32)]
        st = [a, b, c, d]
    return out

def fit(symbols, observations):
    basis = {}
    for time, value in observations:
        decoded = decode(value)
        for bit in range(32):
            coeff = symbols[time][bit]
            rhs = (decoded >> bit) & 1
            while coeff:
                pivot = coeff.bit_length() - 1
                if pivot not in basis:
                    basis[pivot] = (coeff, rhs)
                    break
                coeff ^= basis[pivot][0]
                rhs ^= basis[pivot][1]
            else:
                if rhs:
                    return None, len(basis)
    state = 0
    for pivot in sorted(basis):
        coeff, rhs = basis[pivot]
        if rhs ^ ((coeff & state).bit_count() & 1):
            state |= 1 << pivot
    return state, len(basis)

def stream(state, n):
    out = []
    for _ in range(n):
        out.append(output(state))
        state = step(state)
    return out

def words(payload, endian, reverse):
    out = [int.from_bytes(payload[i:i+4], endian) for i in range(0, 16, 4)]
    return out[::-1] if reverse else out

def main(root):
    symbols = table(256)
    seed = [0x12345678, 0x9ABCDEF0, 0xFEDCBA98, 0x76543210]
    actual = stream(seed, 40)
    recovered, rank = fit(symbols, list(enumerate(actual[:6])))
    assert rank == 128
    assert stream([(recovered >> (32 * k)) & U for k in range(4)], 40) == actual
    print("PASS synthetic xoshiro128** exact-state inversion")

    intact = []
    requested = {}
    for line in (root / "evidence/print/spool-reconstruction.log").read_text().splitlines():
        m = re.search(r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([A-F0-9]{32})", line)
        if not m:
            continue
        job, attempt, state, category, payload = m.groups()
        job = int(job)
        if 300 <= job <= 427 and state == "ACK" and attempt == "1":
            intact.append(bytes.fromhex(payload))
        if job == 417 and state == "REQUESTED" and attempt in ("1", "3"):
            requested[attempt] = bytes.fromhex(payload)
    assert len(intact) == 128
    assert set(requested) == {"1", "3"}
    intact_tests = 0
    intact_survivors = []
    for endian in ("little", "big"):
        for reverse in (False, True):
            triple = [words(raw, endian, reverse) for raw in intact[:3]]
            for gap1 in range(17):
                for gap2 in range(17):
                    times = (list(range(4)) + [4 + gap1 + j for j in range(4)]
                        + [8 + gap1 + gap2 + j for j in range(4)])
                    values = sum(triple, [])
                    bits, rank = fit(symbols, list(zip(times[:8], values[:8])))
                    intact_tests += 1
                    if bits is None or rank < 128:
                        continue
                    predictions = stream([(bits >> (32 * i)) & U for i in range(4)], max(times) + 1)
                    if all(predictions[t] == v for t, v in zip(times, values)):
                        intact_survivors.append((endian, reverse, gap1, gap2))
    assert intact_tests == 1156
    print("intact three-row predictions:", intact_tests, "survivors", intact_survivors)

    retry_tests = 0
    retry_survivors = []
    for endian in ("little", "big"):
        for reverse in (False, True):
            observed = words(requested["1"], endian, reverse) + words(requested["3"], endian, reverse)
            for internal_skip in range(9):
                for external_skip in range(65):
                    start = 4 * (internal_skip + 1) + external_skip
                    times = ([i * (internal_skip + 1) for i in range(4)]
                        + [start + i * (internal_skip + 1) for i in range(4)])
                    bits, rank = fit(symbols, list(zip(times, observed)))
                    retry_tests += 1
                    if bits is not None and rank == 128:
                        retry_survivors.append((endian, reverse, internal_skip, external_skip))
    assert retry_tests == 2340
    print("same-job attempt1/attempt3 models:", retry_tests, "survivors", retry_survivors)
    assert not intact_survivors and not retry_survivors
    print("selected ACK2, XOR mask, and commitment: UNREAD")

if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
