#!/usr/bin/env python3
"""Bounded historical K04 xoshiro128+ (four native 32-bit outputs per packet) test.

Hypothetical producer only. Invert both unselected PS-0417 REQUESTED attempts
independently; enumerate all returned source states and hash every reconstructed
whole 16-byte coupon in a fixed forward/backward 65536-output window.
UNKNOWN is not UNSAT, and a source fit does not authenticate physical media.

Source of xoshiro128+ transition: Blackman and Vigna, xoshiro128plus.c.
Depends on a system Z3 shared library, accessed through the official C API.
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import hashlib
import json
import random
import re
import time
from pathlib import Path
from zipfile import ZipFile

MASK32 = (1 << 32) - 1
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def rol(v: int, k: int) -> int:
    return ((v << k) | (v >> (32 - k))) & MASK32


def ror(v: int, k: int) -> int:
    return ((v >> k) | (v << (32 - k))) & MASK32


def forward(state: tuple[int, int, int, int]):
    a, b, c, d = state
    out = (a + d) & MASK32
    t = (b << 9) & MASK32
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= t
    d = rol(d, 11)
    return out, (a, b, c, d)


def backward(state: tuple[int, int, int, int]):
    A, B, C, D = state
    q = ror(D, 11)
    v = B ^ C
    b = (v ^ (v << 9) ^ (v << 18) ^ (v << 27)) & MASK32
    a = A ^ q
    c = B ^ b ^ a
    d = q ^ b
    return a, b, c, d


def stream(state: tuple[int, int, int, int], n: int, reverse: bool = False):
    emitted = []
    for _ in range(n):
        if reverse:
            older = backward(state)
            word, after = forward(older)
            assert after == state
            state = older
        else:
            word, state = forward(state)
        emitted.append(word)
    return emitted


def smt(words: list[int], limit_seconds: int) -> str:
    lines = ["(set-logic QF_BV)", f"(set-option :timeout {limit_seconds * 1000})"]
    for x in "abcd":
        lines.append(f"(declare-const {x}0 (_ BitVec 32))")
    for i, value in enumerate(words):
        a, b, c, d = (f"{x}{i}" for x in "abcd")
        lines.append(f"(assert (= (bvadd {a} {d}) #x{value:08x}))")
        if i == 3:
            break
        c1 = f"(bvxor {c} {a})"
        d1 = f"(bvxor {d} {b})"
        expr = (
            f"(bvxor {a} {d1})",
            f"(bvxor {b} {c1})",
            f"(bvxor {c1} (bvshl {b} #x00000009))",
            f"((_ rotate_left 11) {d1})",
        )
        for x, body in zip("abcd", expr):
            lines.append(f"(define-fun {x}{i+1} () (_ BitVec 32) {body})")
    lines.append("(check-sat)")
    return "\n".join(lines)


def z3_library():
    name = ctypes.util.find_library("z3")
    if name is None:
        raise RuntimeError("A system Z3 shared library is required")
    api = ctypes.CDLL(name)
    api.Z3_mk_config.restype = ctypes.c_void_p
    api.Z3_mk_context.argtypes = (ctypes.c_void_p,)
    api.Z3_mk_context.restype = ctypes.c_void_p
    api.Z3_eval_smtlib2_string.argtypes = (ctypes.c_void_p, ctypes.c_char_p)
    api.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
    api.Z3_del_context.argtypes = (ctypes.c_void_p,)
    api.Z3_del_config.argtypes = (ctypes.c_void_p,)
    return api


def states_for(words: list[int], limit_seconds: int, cap: int):
    api = z3_library()
    config = api.Z3_mk_config()
    context = api.Z3_mk_context(config)
    begun = time.monotonic()
    states = []
    status = "UNKNOWN"
    try:
        for index in range(cap + 1):
            query = smt(words, limit_seconds) if index == 0 else "(check-sat)"
            reply = api.Z3_eval_smtlib2_string(context, query.encode()).decode().strip()
            if reply != "sat":
                status = reply.upper()
                break
            if index == cap:
                status = "CAP_REACHED"
                break
            raw = api.Z3_eval_smtlib2_string(context, b"(get-value (a0 b0 c0 d0))").decode()
            values = dict((k, int(v, 16)) for k, v in
                          re.findall(r"\(([abcd]0) #x([0-9a-f]{8})\)", raw))
            assert len(values) == 4
            state = tuple(values[f"{x}0"] for x in "abcd")
            assert stream(state, 4) == words and state not in states
            states.append(state)
            pairs = " ".join(f"(= {x}0 #x{value:08x})"
                             for x, value in zip("abcd", state))
            api.Z3_eval_smtlib2_string(
                context, f"(assert (not (and {pairs})))".encode())
    finally:
        api.Z3_del_context(context)
        api.Z3_del_config(config)
    return states, status, round(time.monotonic() - begun, 3)


def fields(path: Path):
    if path.is_dir():
        def read(name: str):
            return (path / name).read_bytes()
        return read
    archive = ZipFile(path)
    def read(name: str):
        return archive.read(name.removeprefix("resources/"))
    return read


def original_inputs(path: Path):
    read = fields(path)
    prefix = "resources/" if path.is_dir() is False else ""
    spool = read(prefix + "evidence/print/spool-reconstruction.log")
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    routing = json.loads(read(prefix + "evidence/recovery-routing.json"))
    checks = json.loads(read(prefix + "acceptance.json"))
    rows = {}
    for line in spool.decode("ascii").splitlines():
        if line.startswith("2026-"):
            stamp, *values = line.split()
            rows[stamp] = dict(field.split("=", 1) for field in values)
    trio = [rows[f"2026-10-03T18:0{minute}:00Z"] for minute in (1, 2, 3)]
    assert all(x["JOB"] == "PS-261003-0417" and x["CLASS"] == "RECOVER"
               for x in trio)
    assert [(x["ATTEMPT"], x["STATE"]) for x in trio] == [
        ("1", "REQUESTED"), ("2", "ACK"), ("3", "REQUESTED")]
    return (
        [bytes.fromhex(x["PAYLOAD"]) for x in trio],
        bytes.fromhex(routing["K04"]["masked_component"]),
        checks["slot_sha256"]["K04"].lower(),
    )


def decode(packet: bytes, endian: str, reverse: bool):
    words = [int.from_bytes(packet[i:i+4], endian) for i in range(0, 16, 4)]
    return words[::-1] if reverse else words


def encode(words: list[int], endian: str, reverse: bool):
    return b"".join(v.to_bytes(4, endian)
                    for v in (words[::-1] if reverse else words))


def controls(limit_seconds: int):
    rng = random.Random(0x17A1C2026)
    for _ in range(10000):
        seed = tuple(rng.getrandbits(32) for _ in range(4))
        value, after = forward(seed)
        assert backward(after) == seed
        assert stream(after, 1, reverse=True) == [value]
    planted = (0x12345678, 0x9ABCDEF0, 0xFEDCBA98, 0x76543210)
    observed = stream(planted, 4)
    states, end, seconds = states_for(observed, limit_seconds, 8)
    assert planted in states and end == "UNSAT"
    print(json.dumps({"control": "PASS", "reverse_checks": 10000,
                      "planted_source_preimages": len(states),
                      "solver_seconds": seconds}), flush=True)


def evaluate(path: Path, limit_seconds: int, cap: int, windows: int):
    packets, mask, target = original_inputs(path)
    total, total_hits = 0, 0
    for anchor, reverse_time in [(0, False), (2, True)]:
        for endian in ("little", "big"):
            for reverse_words in (False, True):
                known = decode(packets[anchor], endian, reverse_words)
                states, end, seconds = states_for(known, limit_seconds, cap)
                held = decode(packets[2 if anchor == 0 else 0], endian,
                              reverse_words)
                row = {"anchor_attempt": anchor + 1,
                       "direction": "backward" if reverse_time else "forward",
                       "endian": endian, "reverse_words": reverse_words,
                       "source_states": len(states),
                       "enumeration_stop": end, "solver_seconds": seconds,
                       "whole_K04_candidates": 0, "K04_hits": [],
                       "other_request_holdouts": []}
                for state in states:
                    native = stream(state, windows + 3, reverse=reverse_time)
                    for pos in range(4, windows):
                        words = (native[pos-4:pos][::-1] if reverse_time
                                 else native[pos:pos+4])
                        if words == held:
                            row["other_request_holdouts"].append(pos)
                        coupon = encode(words, endian, reverse_words)
                        candidate = bytes(a ^ b for a, b in zip(coupon, mask))
                        if hashlib.sha256(candidate).hexdigest() == target:
                            row["K04_hits"].append({"coupon": coupon.hex().upper(),
                                "component": candidate.hex().upper(), "position": pos})
                        row["whole_K04_candidates"] += 1
                total += row["whole_K04_candidates"]
                total_hits += len(row["K04_hits"])
                print(json.dumps({"historical": row}, sort_keys=True), flush=True)
    print(json.dumps({"summary": {"complete_K04_assignments": total,
          "original_K04_hits": total_hits,
          "commitment": "PASS" if total_hits else "NO_HIT_IN_TESTED_DOMAIN",
          "historical_producer_authenticated": False}}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--resources", type=Path, default=Path("resources"))
    parser.add_argument("--limit-seconds", type=int, default=45)
    parser.add_argument("--max-states", type=int, default=8)
    parser.add_argument("--windows", type=int, default=65536)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    assert args.limit_seconds >= 1 and args.max_states >= 1 and args.windows >= 16
    controls(args.limit_seconds)
    if not args.controls_only:
        evaluate(args.resources, args.limit_seconds, args.max_states, args.windows)
