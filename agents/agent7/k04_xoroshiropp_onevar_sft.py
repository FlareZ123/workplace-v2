#!/usr/bin/env python3
"""One-variable xoroshiro128++ flank inversion for H-17 K04.

Exploratory model: PS-261003-0417 RECOVER REQUESTED attempts 1 and 3
are outputs 0,1 and 4,5 of one xoroshiro128++ 1.0 stream. The selected
attempt-2 ACK bytes are withheld. The first observed ++ output determines
state word b algebraically from state word a, reducing the solve to one
symbolic 64-bit variable.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
import time
from pathlib import Path

from z3 import BitVec, BitVecVal, RotateLeft, RotateRight, SolverFor, sat, unknown

MASK64 = (1 << 64) - 1
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
FIRST = bytes.fromhex("CD3E4F216ADB2FB180DA2AA90B33F7A4")
THIRD = bytes.fromhex("44D53DFC29D7943A95D89371DA58EC64")
ROUTE_MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
TEST_STATE = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)


def rol(x: int, n: int) -> int:
    return ((x << n) | (x >> (64 - n))) & MASK64


def ror(x: int, n: int) -> int:
    return ((x >> n) | (x << (64 - n))) & MASK64


def native(a: int, b: int) -> tuple[int, int, int]:
    y = (rol((a + b) & MASK64, 17) + a) & MASK64
    t = a ^ b
    return y, (rol(a, 49) ^ t ^ ((t << 21) & MASK64)) & MASK64, rol(t, 28)


def outputs(a: int, b: int, count: int = 6) -> list[int]:
    out = []
    for _ in range(count):
        y, a, b = native(a, b)
        out.append(y)
    return out


def decode(payload: bytes, view: int) -> tuple[int, int]:
    words = list(struct.unpack(("<" if view % 2 == 0 else ">") + "QQ", payload))
    if view >= 2:
        words.reverse()
    return words[0], words[1]


def encode(words: tuple[int, int], view: int) -> bytes:
    seq = list(words)
    if view >= 2:
        seq.reverse()
    return struct.pack(("<" if view % 2 == 0 else ">") + "QQ", *seq)


def read_flanks(root: Path) -> tuple[bytes, bytes]:
    path = root / "resources/evidence/print/spool-reconstruction.log"
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SPOOL_SHA:
        raise ValueError("spool source SHA256 mismatch")
    found: dict[int, bytes] = {}
    for line in raw.decode("ascii").splitlines():
        if not line.startswith(("2026-10-03T18:01:00Z ", "2026-10-03T18:03:00Z ")):
            continue
        fields = dict(x.split("=", 1) for x in line.split() if "=" in x)
        if (fields.get("JOB"), fields.get("CLASS"), fields.get("STATE")) != (
            "PS-261003-0417", "RECOVER", "REQUESTED"
        ):
            raise ValueError("request source identity drift")
        attempt = int(fields["ATTEMPT"])
        if attempt in found:
            raise ValueError("duplicate exact request")
        found[attempt] = bytes.fromhex(fields["PAYLOAD"])
    if found != {1: FIRST, 3: THIRD}:
        raise ValueError("request payload source drift")
    return found[1], found[3]


def solve(flanks: tuple[int, int, int, int], timeout_ms: int):
    y0, y1, y4, y5 = flanks
    a0 = BitVec("a0", 64)

    # y0 = rotl(a0+b0,17)+a0, inverted exactly modulo 2^64.
    b0 = RotateRight(BitVecVal(y0, 64) - a0, 17) - a0

    a, b = a0, b0
    symbolic = []
    for _ in range(6):
        y = RotateLeft(a + b, 17) + a
        t = a ^ b
        a, b = RotateLeft(a, 49) ^ t ^ (t << 21), RotateLeft(t, 28)
        symbolic.append(y)

    solver = SolverFor("QF_BV")
    solver.set("timeout", timeout_ms)
    solver.add(symbolic[1] == BitVecVal(y1, 64))
    solver.add(symbolic[4] == BitVecVal(y4, 64))
    solver.add(symbolic[5] == BitVecVal(y5, 64))

    started = time.monotonic()
    answer = solver.check()
    elapsed = time.monotonic() - started
    print(
        f"solver={answer} elapsed_sec={elapsed:.3f} "
        f"reason={solver.reason_unknown() if answer == unknown else 'none'}",
        flush=True,
    )
    if answer != sat:
        return None

    model = solver.model()
    aa = model.eval(a0, model_completion=True).as_long()
    bb = (ror((y0 - aa) & MASK64, 17) - aa) & MASK64
    full = outputs(aa, bb)
    if tuple(full[i] for i in (0, 1, 4, 5)) != flanks:
        raise AssertionError("SAT model failed source flanks")

    solver.push()
    solver.add(a0 != BitVecVal(aa, 64))
    started2 = time.monotonic()
    alt = solver.check()
    elapsed2 = time.monotonic() - started2
    solver.pop()
    print(
        f"alternative_a0={alt} elapsed_sec={elapsed2:.3f} "
        f"reason={solver.reason_unknown() if alt == unknown else 'none'}",
        flush=True,
    )
    return aa, bb, full, alt


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--phase", required=True, choices=("positive", "original"))
    p.add_argument("--view", type=int, choices=range(4), default=0)
    p.add_argument("--timeout-ms", type=int, default=300000)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = p.parse_args()

    if args.timeout_ms <= 0:
        p.error("timeout must be positive")

    if args.phase == "positive":
        fixture = outputs(*TEST_STATE)
        flanks = tuple(fixture[i] for i in (0, 1, 4, 5))
        recovered = solve(flanks, args.timeout_ms)
        if recovered is None:
            print("PLANTED_UNCONSTRAINED_UNKNOWN", flush=True)
            return 2
        aa, bb, full, _ = recovered
        if (aa, bb) != TEST_STATE or full[2:4] != fixture[2:4]:
            raise AssertionError("unconstrained planted inversion did not recover exact state/middle")
        print(
            "PLANTED_UNCONSTRAINED_PASS",
            f"state={aa:016X}/{bb:016X}",
            f"middle={full[2]:016X}/{full[3]:016X}",
            flush=True,
        )
        return 0

    before, after = read_flanks(args.root)
    flanks = (*decode(before, args.view), *decode(after, args.view))
    recovered = solve(flanks, args.timeout_ms)
    if recovered is None:
        print("ORIGINAL_UNRESOLVED", flush=True)
        return 0

    aa, bb, full, alt = recovered
    coupon = encode((full[2], full[3]), args.view)
    component = bytes(x ^ y for x, y in zip(coupon, ROUTE_MASK))
    digest = hashlib.sha256(component).hexdigest()
    print(f"ORIGINAL_STATE={aa:016X}/{bb:016X}", flush=True)
    print(f"ORIGINAL_MIDDLE_COUPON={coupon.hex().upper()}", flush=True)
    print(f"ORIGINAL_K04_COMPONENT={component.hex().upper()}", flush=True)
    print(f"ORIGINAL_K04_SHA256={digest}", flush=True)
    print("K04_PASS" if digest == K04_SHA else "K04_NO_MATCH", flush=True)
    print(f"ALTERNATIVE_A0_STATUS={alt}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
