"""NumPy MT19937 second-cycle pool4 inversion, source-only K04 test.

Reads only intact original spool row3 and previously authenticated intact
row3/34 recurrence pairs. The selected ACK, original K04 mask and hashes
are never opened. Synthetic NumPy controls must pass before original solving.
"""
import argparse
import hashlib
import re
import struct

import numpy as np

U32 = 0xFFFFFFFF
A = 0x9908B0DF
INIT_B = 0x8B51F9DD
MULT_B = 0x58F38DED
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
PAIRS = ((0x482F6361, 0xA757A2AC), (0x6C881CF7, 0x56FC62AE),
         (0x0429B798, 0xFFAAF2D5), (0x4B9C858C, 0xAC0962C9),
         (0xD47006FA, 0xCC8EB204))


def untemper(x):
    for shift, mask, left in ((18, U32, False), (15, 0xEFC60000, True),
                              (7, 0x9D2C5680, True), (11, U32, False)):
        y = int(x)
        for _ in range(6):
            x = (y ^ ((int(x) << shift) & mask if left else int(x) >> shift)) & U32
    return int(x)


def halves(pairs):
    answer = []
    for a, b in pairs:
        x = a ^ b
        bit = x >> 31
        y = (((x ^ (A if bit else 0)) << 1) | bit) & U32
        answer.append((y & 0x80000000, y & 0x7FFFFFFF))
    return answer


def quad(pairs):
    h = halves(pairs)
    return [h[j][1] | h[j + 1][0] for j in range(4)]


def constants(i):
    before = (INIT_B * pow(MULT_B, i, 1 << 32)) & U32
    return before, (before * MULT_B) & U32


def state(pool, i):
    if i == 0:
        return 0x80000000
    before, factor = constants(i)
    v = ((pool[i % 4] ^ before) * factor) & U32
    return v ^ (v >> 16)


def twist(x, y):
    v = (x & 0x80000000) | (y & 0x7FFFFFFF)
    return (v >> 1) ^ (A if y & 1 else 0)


def first_twist(pool):
    t = [0] * 624
    for i in range(227):
        t[i] = state(pool, i + 397) ^ twist(state(pool, i), state(pool, i + 1))
    for i in range(227, 623):
        t[i] = t[i - 227] ^ twist(state(pool, i), state(pool, i + 1))
    t[623] = t[396] ^ twist(state(pool, 623), t[0])
    return t


def synthetic():
    for seed in (0, 1234, 20261020, (1 << 127) | 0xDEADBEEF):
        rng = np.random.MT19937(seed)
        key = rng.state["state"]["key"]
        pool = tuple(int(x) for x in np.random.SeedSequence(seed).pool)
        assert all(state(pool, i) == int(key[i]) for i in range(624))
        xs = [untemper(x) for x in rng.random_raw(1249)]
        t = first_twist(pool)
        assert t == xs[1:625]
        for phase in (0, 13, 99, 218, 390, 391):
            pairs = tuple((xs[625 + phase + j], xs[852 + phase + j])
                          for j in range(5))
            h = halves(pairs)
            assert quad(pairs) == t[phase + 228:phase + 232]
            assert h[0][0] == (t[phase + 227] & 0x80000000)
            assert h[4][1] == (t[phase + 232] & 0x7FFFFFFF)
    print("NUMPY_SECOND_CYCLE_24_SAMPLES_PASS", flush=True)


def solve_one(z, phase, pairs, timeout_ms):
    pp = [z.BitVec(f"P{i}", 32) for i in range(4)]
    bv = lambda x: z.BitVecVal(int(x), 32)
    ec, tc = {}, {}

    def init(i):
        if i == 0:
            return bv(0x80000000)
        if i not in ec:
            b, m = constants(i)
            v = (pp[i % 4] ^ bv(b)) * bv(m)
            ec[i] = v ^ z.LShR(v, 16)
        return ec[i]

    def twisted(x, y):
        v = (x & bv(0x80000000)) | (y & bv(0x7FFFFFFF))
        return z.LShR(v, 1) ^ ((y & bv(1)) * bv(A))

    def t(i):
        if i not in tc:
            if i < 227:
                expr = init(i + 397) ^ twisted(init(i), init(i + 1))
            elif i < 623:
                expr = t(i - 227) ^ twisted(init(i), init(i + 1))
            else:
                expr = t(396) ^ twisted(init(623), t(0))
            tc[i] = expr
        return tc[i]

    s = z.SolverFor("QF_BV")
    s.set(timeout=timeout_ms)
    h = halves(pairs)
    for i, word in enumerate(quad(pairs)):
        s.add(t(phase + 228 + i) == bv(word))
    s.add((t(phase + 227) & bv(0x80000000)) == bv(h[0][0]))
    s.add((t(phase + 232) & bv(0x7FFFFFFF)) == bv(h[4][1]))
    verdict = s.check()
    if verdict == z.sat:
        model = s.model()
        out = tuple(model.eval(v).as_long() for v in pp)
        witness = first_twist(out)
        assert witness[phase + 228:phase + 232] == quad(pairs)
        assert (witness[phase + 227] & 0x80000000) == h[0][0]
        assert (witness[phase + 232] & 0x7FFFFFFF) == h[4][1]
        return "sat", out
    return str(verdict), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase-start", type=int, default=0)
    ap.add_argument("--phase-stop", type=int, default=4)
    ap.add_argument("--timeout-ms", type=int, default=20000)
    args = ap.parse_args()
    assert 0 <= args.phase_start <= args.phase_stop <= 392
    from pathlib import Path
    spool = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    data = spool.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SPOOL_SHA
    lines = [x for x in data.splitlines() if x.startswith(b"2026-")]
    assert len(lines) == 133
    row3 = re.search(rb"PAYLOAD=([0-9A-F]{32})", lines[3]).group(1)
    raw = struct.unpack("<4I", bytes.fromhex(row3.decode()))
    assert tuple(untemper(x) for x in raw) == tuple(a for a, _ in PAIRS[1:])
    synthetic()
    import z3
    rng = np.random.MT19937(1234)
    xs = [untemper(x) for x in rng.random_raw(1249)]
    p = 13
    trial = tuple((xs[625 + p + j], xs[852 + p + j]) for j in range(5))
    verdict, pool = solve_one(z3, p, trial, args.timeout_ms)
    true_pool = tuple(int(x) for x in np.random.SeedSequence(1234).pool)
    print("SYNTHETIC_SMT", verdict, "TRUE_POOL", pool == true_pool, flush=True)
    if verdict != "sat":
        print("STOP: synthetic inversion did not converge; original not attempted", flush=True)
        return
    counts = {}
    for phase in range(args.phase_start, args.phase_stop):
        verdict, pool = solve_one(z3, phase, PAIRS, args.timeout_ms)
        counts[verdict] = counts.get(verdict, 0) + 1
        print("ORIGINAL_PHASE", phase, verdict, pool, flush=True)
    print("ORIGINAL_COUNTS", counts, flush=True)


if __name__ == "__main__":
    main()
