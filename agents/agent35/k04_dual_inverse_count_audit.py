#!/usr/bin/env python3
"""Independent arithmetic and gate-count audit for xoroshiro128++ first-pair inversion.

This is not a solver and does not search for a state. It reads the three PS-0417
RECOVER rows, checks inverse-output arithmetic on deterministic random witnesses,
and reports the borrow-chain circuit counts implied by the fused dual-inverse design.
"""
from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

MASK = (1 << 64) - 1
SEED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)


def rol(x: int, n: int) -> int:
    n %= 64
    return ((x << n) | (x >> (64 - n))) & MASK if n else x & MASK


def ror(x: int, n: int) -> int:
    return rol(x, -n)


def output(a: int, b: int) -> int:
    return (rol((a + b) & MASK, 17) + a) & MASK


def step(a: int, b: int) -> tuple[int, int]:
    t = a ^ b
    return (rol(a, 49) ^ t ^ (t << 21)) & MASK, rol(t, 28)


def decode(payload: bytes, view: int) -> tuple[int, int]:
    endian = "little" if view & 1 else "big"
    words = [int.from_bytes(payload[i:i + 8], endian) for i in (0, 8)]
    if view & 2:
        words.reverse()
    return words[0], words[1]


def first_zero_bit(c: int) -> int | None:
    """First zero among bits 0..62; final borrow-out is unused."""
    for i in range(63):
        if ((c >> i) & 1) == 0:
            return i
    return None


def sub_const_counts(c: int) -> dict:
    k = first_zero_bit(c)
    if k is None:
        return {"first_zero_bit": None, "output_vars": 64, "borrow_vars": 0,
                "cnf_clauses": 0, "xor_clauses": 64}
    return {"first_zero_bit": k, "output_vars": 63, "borrow_vars": 62 - k,
            "cnf_clauses": 3 * (62 - k), "xor_clauses": 63}


def fused_core_counts(y0: int, y1: int) -> dict:
    c0, c1 = sub_const_counts(y0), sub_const_counts(y1)
    variables = (64 + c0["output_vars"] + c0["borrow_vars"] + 127 + 128
                 + c1["output_vars"] + c1["borrow_vars"] + 63)
    cnf = c0["cnf_clauses"] + 375 + c1["cnf_clauses"] + 375
    xor = c0["xor_clauses"] + 64 + 128 + c1["xor_clauses"] + 64
    return {
        "y0": f"{y0:016X}",
        "y1": f"{y1:016X}",
        "sub_const_y0": c0,
        "sub_const_y1": c1,
        "fused_core": {"variables": variables, "cnf_clauses": cnf, "xor_clauses": xor},
        "full_middle_uniqueness": {
            "variables": variables + 764, "cnf_clauses": cnf + 1500,
            "xor_clauses": xor + 512, "blocking_clause_counted": False,
        },
        "nonfused_core": {
            "variables": variables + 64, "cnf_clauses": cnf, "xor_clauses": xor + 64,
        },
        "nonfused_full_middle_uniqueness": {
            "variables": variables + 828, "cnf_clauses": cnf + 1500,
            "xor_clauses": xor + 576, "blocking_clause_counted": False,
        },
    }


def parse_rows(path: Path) -> dict[int, bytes]:
    rows: dict[int, bytes] = {}
    pattern = re.compile(
        r"PS-261003-0417.*?ATTEMPT=(\d+).*?STATE=(REQUESTED|ACK).*?"
        r"CLASS=RECOVER.*?PAYLOAD=([0-9A-Fa-f]{32})"
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        m = pattern.search(line)
        if m:
            rows[int(m.group(1))] = bytes.fromhex(m.group(3))
    missing = sorted({1, 2, 3} - set(rows))
    if missing:
        raise ValueError(f"missing PS-0417 RECOVER attempts: {missing}")
    return rows


def sub_const(c: int, a: int) -> int:
    borrow = 0
    out = 0
    for i in range(64):
        ci, ai = (c >> i) & 1, (a >> i) & 1
        out |= (ci ^ ai ^ borrow) << i
        if i < 63:
            if borrow == 0:
                borrow = ai if ci == 0 else 0
            else:
                borrow = (ai | borrow) if ci == 0 else (ai & borrow)
    return out


def sub_var(a: int, b: int) -> int:
    borrow = 0
    out = 0
    for i in range(64):
        ai, bi = (a >> i) & 1, (b >> i) & 1
        out |= (ai ^ bi ^ borrow) << i
        if i < 63:
            if i == 0:
                borrow = (1 - ai) & bi
            else:
                borrow = ((1 - ai) & bi) | ((1 - ai) & borrow) | (bi & borrow)
    return out


def arithmetic_checks(n: int) -> None:
    rng = random.Random(0x35D0A11)
    for _ in range(n):
        c, a, b = rng.getrandbits(64), rng.getrandbits(64), rng.getrandbits(64)
        assert sub_const(c, a) == (c - a) & MASK
        assert sub_var(a, b) == (a - b) & MASK
        y = output(a, b)
        assert (ror((y - a) & MASK, 17) - a) & MASK == b
        a1, b1 = step(a, b)
        y1 = output(a1, b1)
        u = ror((y1 - a1) & MASK, 17)
        assert sub_var(u, a1) == b1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spool", type=Path,
                        default=Path("resources/evidence/print/spool-reconstruction.log"))
    parser.add_argument("--random-checks", type=int, default=100000)
    args = parser.parse_args()

    rows = parse_rows(args.spool)
    arithmetic_checks(args.random_checks)
    first, ack, third = rows[1], rows[2], rows[3]
    result = {
        "arithmetic_checks": args.random_checks,
        "selected_attempt_payloads": {
            "attempt1_requested": first.hex().upper(),
            "attempt2_ack": ack.hex().upper(),
            "attempt3_requested": third.hex().upper(),
        },
        "views": [fused_core_counts(*decode(first, view)) | {"view": view}
                  for view in range(4)],
    }
    a, b = SEED
    seed_outputs = []
    for _ in range(2):
        seed_outputs.append(output(a, b))
        a, b = step(a, b)
    result["synthetic_seed_outputs"] = [f"{x:016X}" for x in seed_outputs]
    result["synthetic_seed_counts"] = fused_core_counts(*seed_outputs)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
