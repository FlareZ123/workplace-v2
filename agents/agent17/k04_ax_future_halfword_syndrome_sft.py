"""Find original late AX 16-halfword bursts compatible with conditional p951 MT.

Original spool and transfer audit source-pinned; selected RECOVER/ACK2, route
mask and authentic K04 commitment are never consulted. All claims conditional
on the hypothetical common MT stream/stage.
"""
from __future__ import annotations
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
from k04_p951_symbolic_basis import source, temper, ORIGIN, MAG

PIN = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"

def score(equations, observations):
    return sum(((mask & observations).bit_count() & 1) != bit for mask, bit in equations)

def main():
    raw = (ROOT / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    records = [json.loads(line) for line in raw.splitlines()]
    streams = {}
    for name in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
        rows = sorted((r for r in records if r["kind"] == "CHUNK" and r["transfer"] == name),
                      key=lambda r: (r["seq"], r["attempt"]))
        assert len(rows) == 16
        assert [(r["seq"], r["attempt"]) for r in rows] == [
            (seq, attempt) for seq in range(8) for attempt in (1, 2)]
        streams[name] = [bytes.fromhex(r["checkpoint"]) for r in rows]
    basis, state = source(ROOT)
    assert basis.rank == 15365
    for i in range(len(state), 5320 - ORIGIN + 1):
        j = i - 624
        state.append([state[j + 397][k]
                      ^ (state[j][31] if k == 30 else (state[j + 1][k + 1] if k < 30 else 0))
                      ^ (state[j + 1][0] if MAG >> k & 1 else 0)
                      for k in range(32)])

    def constraints(start, upper):
        quotient = {}
        checks = []
        for i in range(16):
            bits = temper(state[start + i - ORIGIN])
            for bit in range(16, 32) if upper else range(16):
                value = bits[bit]
                coeff = 1 << (16 * i + (bit - 16 if upper else bit))
                rhs = 0
                while value:
                    pivot = value.bit_length() - 1
                    base = basis.rows.get(pivot)
                    if base is not None:
                        vector, known = base
                        value ^= vector
                        rhs ^= known
                        continue
                    conditional = quotient.get(pivot)
                    if conditional is not None:
                        vector, coef, known = conditional
                        value ^= vector
                        coeff ^= coef
                        rhs ^= known
                        continue
                    quotient[pivot] = (value, coeff, rhs)
                    break
                else:
                    checks.append((coeff, rhs))
        return checks

    views = {(name, endian): sum(int.from_bytes(cp, endian) << (16 * i)
                                for i, cp in enumerate(rows))
             for name, rows in streams.items() for endian in ("little", "big")}
    # Original-source positive: AX-7778 preincident drill at stage -157.
    positive = constraints(-157, True)
    assert len(positive) == 126
    assert score(positive, views["AX-7778", "little"]) == 0
    assert score(positive, views["AX-7778", "big"]) == 60
    assert score(constraints(-157, False), views["AX-7778", "little"]) == 58
    print("PASS original AX-7778 upper16/little 126/126 independent parity checks")

    # Seeded source-consistent synthetic MT state, plus deliberate one-bit fault.
    rng = random.Random(20261103)
    synthetic = rng.getrandbits(19968)
    pivot_mask = sum(1 << pivot for pivot in basis.rows)
    synthetic &= ~pivot_mask
    for pivot, (vector, known) in sorted(basis.rows.items()):
        synthetic |= (known ^ ((vector & synthetic).bit_count() & 1)) << pivot
    assert all(((vector & synthetic).bit_count() & 1) == known
               for vector, known in basis.rows.values())
    fabricated = sum(
        (sum(((vector & synthetic).bit_count() & 1) << bit
             for bit, vector in enumerate(temper(state[1347 + i - ORIGIN]))) >> 16)
        << (16 * i) for i in range(16))
    checks = constraints(1347, True)
    assert len(checks) == 94 and score(checks, fabricated) == 0
    changed_bit = next(mask for mask, wanted in checks if mask)
    assert score(checks, fabricated ^ (changed_bit & -changed_bit)) > 0
    print("PASS synthetic source-consistent future burst and one-bit negative")

    totals = {16: 0, 24: 0, 32: 0, 64: 0, 128: 0}
    minimum = {threshold: 257 for threshold in totals}
    informative = zero = 0
    for start in range(1040, 5301):
        for upper in (True, False):
            checks = constraints(start, upper)
            if len(checks) < 16:
                continue
            informative += 1
            for name in ("AX-7781", "AX-7782", "AX-7783"):
                for endian in ("little", "big"):
                    errors = score(checks, views[name, endian])
                    for threshold in totals:
                        if len(checks) >= threshold:
                            totals[threshold] += 1
                            minimum[threshold] = min(minimum[threshold], errors)
                    zero += errors == 0
    assert informative == 6112
    assert totals == {16: 36672, 24: 34248, 32: 27084, 64: 12984, 128: 1692}
    assert minimum == {16: 3, 24: 4, 32: 9, 64: 20, 128: 53}
    assert zero == 0
    print(json.dumps({"result": "NO_COMPATIBLE_LATE_TRANSFER_STAGE",
                      "future_starts": 4261, "informative_stage_views": informative,
                      "assignment_counts": totals, "minimum_violations": minimum,
                      "zero_syndrome": zero}, sort_keys=True))
    print("Original selected coupon and K04 target commitment UNREAD")

if __name__ == "__main__":
    main()
