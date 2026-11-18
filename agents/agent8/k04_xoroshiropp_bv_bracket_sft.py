#!/usr/bin/env python3
"""Recover a *hypothetical* missing middle xoroshiro128++ coupon from two intact request flanks.

One job supplies four independent 64-bit output observations at native output
positions 0,1,4,5. Positions 2,3 are withheld and constitute the predicted
entire 16-byte coupon. This source-UNATTESTED model is exploratory.

A bounded planted model supplies the low 16 state bits as a solver-liveness
control. No such prefix is assumed for the original source.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
import time
from pathlib import Path

from z3 import BitVec, BitVecVal, RotateLeft, SolverFor, sat, unknown

MASK64 = (1 << 64) - 1
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ATTEMPT1 = "CD3E4F216ADB2FB180DA2AA90B33F7A4"
ATTEMPT3 = "44D53DFC29D7943A95D89371DA58EC64"
ROUTE_MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
TEST_STATE = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)


def rotate(x: int, n: int) -> int:
    return ((x << n) | (x >> (64 - n))) & MASK64


def next_native(a: int, b: int) -> tuple[int, int, int]:
    y = (rotate((a + b) & MASK64, 17) + a) & MASK64
    t = a ^ b
    return y, rotate(a, 49) ^ t ^ ((t << 21) & MASK64), rotate(t, 28)


def next_symbolic(a, b):
    y = RotateLeft(a + b, 17) + a
    t = a ^ b
    return y, RotateLeft(a, 49) ^ t ^ (t << 21), RotateLeft(t, 28)


def six_outputs(a: int, b: int) -> list[int]:
    result = []
    for _ in range(6):
        out, a, b = next_native(a, b)
        result.append(out)
    return result


def view_words(payload: bytes, index: int) -> tuple[int, int]:
    if len(payload) != 16 or index not in range(4):
        raise ValueError("invalid whole coupon or serializer")
    words = list(struct.unpack(("<" if index % 2 == 0 else ">") + "QQ", payload))
    if index >= 2:
        words.reverse()
    return words[0], words[1]


def to_bytes(words: tuple[int, int], index: int) -> bytes:
    ordered = list(words)
    if index >= 2:
        ordered.reverse()
    return struct.pack(("<" if index % 2 == 0 else ">") + "QQ", *ordered)


def read_flanks(root: Path) -> tuple[bytes, bytes]:
    path = root / "resources" / "evidence" / "print" / "spool-reconstruction.log"
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPOOL_SHA:
        raise ValueError("source spool SHA256 mismatch")
    found = {}
    for line in data.decode("utf-8").splitlines():
        if "JOB=PS-261003-0417" not in line:
            continue
        # Only requests are parsed. The selected ACK2 payload is *not* read.
        if "ATTEMPT=1 " not in line and "ATTEMPT=3 " not in line:
            continue
        fields = dict(word.split("=", 1) for word in line.split() if "=" in word)
        if fields.get("STATE") != "REQUESTED" or fields.get("CLASS") != "RECOVER":
            raise ValueError("same-job original request metadata changed")
        attempt = int(fields["ATTEMPT"])
        if attempt in found:
            raise ValueError("ambiguous request witness")
        found[attempt] = bytes.fromhex(fields["PAYLOAD"])
    if found != {1: bytes.fromhex(ATTEMPT1), 3: bytes.fromhex(ATTEMPT3)}:
        raise ValueError("original request witnesses changed")
    return found[1], found[3]


def solve(flanks: tuple[int, int, int, int], timeout_ms: int, prefix16: int | None):
    a, b = BitVec("first_state_a", 64), BitVec("first_state_b", 64)
    solver = SolverFor("QF_BV")
    solver.set("timeout", timeout_ms)
    if prefix16 is not None:
        solver.add((a & BitVecVal(0xFFFF, 64)) == BitVecVal(prefix16, 64))
    state_a, state_b = a, b
    symbolic = []
    for _ in range(6):
        out, state_a, state_b = next_symbolic(state_a, state_b)
        symbolic.append(out)
    for position, expected in zip((0, 1, 4, 5), flanks):
        solver.add(symbolic[position] == BitVecVal(expected, 64))
    start = time.monotonic()
    answer = solver.check()
    elapsed = time.monotonic() - start
    print(f"solver={answer} elapsed_sec={elapsed:.3f} reason={solver.reason_unknown() if answer == unknown else 'none'}", flush=True)
    if answer != sat:
        return None
    model = solver.model()
    recovered = (model.eval(a, model_completion=True).as_long(),
                 model.eval(b, model_completion=True).as_long())
    actual = six_outputs(*recovered)
    if tuple(actual[i] for i in (0, 1, 4, 5)) != flanks:
        raise AssertionError("SAT model did not reproduce complete original flank outputs")
    print(f"state={recovered[0]:016X}/{recovered[1]:016X}", flush=True)
    return actual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=("positive", "original"))
    parser.add_argument("--view", type=int, default=0, choices=range(4))
    parser.add_argument("--timeout-ms", type=int, default=90000)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    if args.timeout_ms <= 0:
        parser.error("timeout must be positive")
    if args.phase == "positive":
        fixture = six_outputs(*TEST_STATE)
        expected = tuple(fixture[i] for i in (0, 1, 4, 5))
        prediction = solve(expected, args.timeout_ms, TEST_STATE[0] & 0xFFFF)
        if prediction is None:
            print("PLANTED_LIVENESS_UNKNOWN: no conclusion about original source", flush=True)
            return 2
        if prediction[2:4] != fixture[2:4]:
            raise AssertionError("SAT source fits but does not recover planted held-out coupon")
        print("PLANTED_WHOLE_MIDDLE_COUPON_PASS", to_bytes(tuple(prediction[2:4]), args.view).hex().upper(), flush=True)
        return 0
    first, third = read_flanks(args.root)
    w0,w1 = view_words(first, args.view)
    w4,w5 = view_words(third, args.view)
    prediction = solve((w0,w1,w4,w5), args.timeout_ms, None)
    if prediction is None:
        print("ORIGINAL_UNRESOLVED: model neither confirmed nor excluded", flush=True)
        return 0
    coupon = to_bytes(tuple(prediction[2:4]), args.view)
    component = bytes(x ^ y for x,y in zip(coupon, ROUTE_MASK))
    digest = hashlib.sha256(component).hexdigest()
    print(f"ORIGINAL_PREDICTED_COUPON={coupon.hex().upper()}", flush=True)
    print(f"ORIGINAL_K04_COMPONENT={component.hex().upper()} COMMITMENT={digest}", flush=True)
    print("K04_PASS" if digest == K04_SHA else "K04_NO_MATCH", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
