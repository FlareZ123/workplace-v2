#!/usr/bin/env python3
"""K04 same-job erasure source gate for xoroshiro128+ 2016 and 2018.

Full 128-bit unanchored solver. Original input is restricted to the intact
PS-261003-0417 RECOVER REQUESTED attempt 1 and attempt 3 (two 64-bit output
words each). Original ACK attempt 2 is never read, and its supposed original
coupon words are the two missing consecutive generator outputs.

Original checks only locally, never GitHub Actions/public CI. No original
payload, state, candidate, K04 target, or HMAC value is printed. The two
source-free planted full-state controls must pass before original inspection.

Requirements: Python 3 stdlib, GNU libz3.so.4 shared library.
Usage from repository: python agents/agent3/k04_xorplus_samejob_gap_sft.py
Optional private hit: --private-hit-output=/local/private/file.txt
"""
from pathlib import Path
from hashlib import sha256
import ctypes
import json
import os
import random
import re
import sys
import time

if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
    raise SystemExit("Do not run historical source in public CI")

ROOT = Path(__file__).resolve().parents[2] / "resources"
PINS = {
    "evidence/print/spool-reconstruction.log":
        "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/recovery-routing.json":
        "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json":
        "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
MASK64 = (1 << 64) - 1
PARAMS = ((55, 14, 36), (24, 16, 37))
TIMEOUT_MS = 90_000

try:
    Z = ctypes.CDLL("libz3.so.4")
except OSError as e:
    raise SystemExit("GNU libz3.so.4 shared library required") from e
Z.Z3_mk_config.restype = ctypes.c_void_p
Z.Z3_set_param_value.argtypes = (ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p)
Z.Z3_mk_context.argtypes = (ctypes.c_void_p,)
Z.Z3_mk_context.restype = ctypes.c_void_p
Z.Z3_eval_smtlib2_string.argtypes = (ctypes.c_void_p, ctypes.c_char_p)
Z.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
Z.Z3_del_context.argtypes = (ctypes.c_void_p,)


def rotl(x, k):
    return ((x << k) | (x >> (64 - k))) & MASK64


def generate(a, b, params, n=6):
    l, shift, r = params
    out = []
    for _ in range(n):
        out.append((a + b) & MASK64)
        x = a ^ b
        a = rotl(a, l) ^ x ^ ((x << shift) & MASK64)
        b = rotl(x, r)
    return out


def smt(observed, params, model=False):
    l, shift, r = params
    lines = [
        f"(set-option :timeout {TIMEOUT_MS})",
        "(set-option :produce-models true)",
        "(set-logic QF_BV)",
        "(declare-fun a0 () (_ BitVec 64))",
        "(declare-fun b0 () (_ BitVec 64))",
    ]
    for i in range(5):
        lines.extend((
            f"(define-fun t{i} () (_ BitVec 64) (bvxor a{i} b{i}))",
            f"(define-fun a{i+1} () (_ BitVec 64) "
            f"(bvxor (bvxor ((_ rotate_left {l}) a{i}) t{i}) "
            f"(bvshl t{i} (_ bv{shift} 64))))",
            f"(define-fun b{i+1} () (_ BitVec 64) ((_ rotate_left {r}) t{i}))",
        ))
    for i in (0, 1, 4, 5):
        lines.append(
            f"(assert (= (bvadd a{i} b{i}) #x{observed[i]:016x}))"
        )
    lines.append("(check-sat)")
    if model:
        lines.append("(get-value (a0 b0))")
    return ("\n".join(lines) + "\n").encode()


def z3_eval(text):
    cfg = Z.Z3_mk_config()
    Z.Z3_set_param_value(cfg, b"timeout", str(TIMEOUT_MS).encode())
    ctx = Z.Z3_mk_context(cfg)
    try:
        return Z.Z3_eval_smtlib2_string(ctx, text).decode().strip()
    finally:
        Z.Z3_del_context(ctx)


def recovered_state(obs, params):
    status = z3_eval(smt(obs, params))
    if status != "sat":
        if status not in ("unsat", "unknown"):
            raise RuntimeError("Unexpected Z3 solver status")
        return status, None
    # Never issue get-value after UNSAT or UNKNOWN: Z3 correctly has no model.
    answer = z3_eval(smt(obs, params, model=True))
    vals = re.findall(r"#x([0-9a-fA-F]{16})", answer)
    if not answer.startswith("sat") or len(vals) != 2:
        raise RuntimeError("SAT result without complete initial state model")
    state = tuple(int(s, 16) for s in vals)
    replay = generate(*state, params)
    if any(replay[i] != obs[i] for i in (0, 1, 4, 5)):
        raise RuntimeError("Original full output replay mismatch")
    return status, state


def check_synthetic():
    for params in PARAMS:
        rng = random.Random(20261128)
        original = (rng.getrandbits(64), rng.getrandbits(64))
        obs = generate(*original, params)
        status, recovered = recovered_state(obs, params)
        if status != "sat" or recovered != original:
            raise AssertionError("Full 128-bit planted state control failed")


def read_original():
    for rel, need in PINS.items():
        path = ROOT / rel
        if sha256(path.read_bytes()).hexdigest() != need:
            raise RuntimeError("Untouched source SHA mismatch: " + rel)
    records = {}
    for line in (ROOT / "evidence/print/spool-reconstruction.log").read_text().splitlines():
        if "JOB=PS-261003-0417 " not in line:
            continue
        if "STATE=REQUESTED " not in line or "CLASS=RECOVER " not in line:
            continue
        stage = ("before" if "ATTEMPT=1 " in line else
                 "after" if "ATTEMPT=3 " in line else None)
        if stage is None:
            continue
        match = re.search(r"PAYLOAD=([0-9A-Fa-f]{32})(?:\s|$)", line)
        if not match or stage in records:
            raise RuntimeError("Unexpected original 0417 source selector")
        records[stage] = bytes.fromhex(match[1])
    if set(records) != {"before", "after"}:
        raise RuntimeError("Original source flanks missing")
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    accept = json.loads((ROOT / "acceptance.json").read_text())
    return (records["before"], records["after"],
            bytes.fromhex(route["K04"]["masked_component"]),
            bytes.fromhex(accept["slot_sha256"]["K04"]))


def decode(packet, endian, swap):
    words = [int.from_bytes(packet[i:i + 8], endian) for i in (0, 8)]
    return words[::-1] if swap else words


def encode(words, endian, swap):
    words = words[::-1] if swap else words
    return b"".join(x.to_bytes(8, endian) for x in words)


def main():
    check_synthetic()
    before, after, mask, target = read_original()
    if len(mask) != 16 or len(target) != 32:
        raise RuntimeError("Malformed original slot gate")
    models = sat = unsat = unknown = hits = 0
    for params in PARAMS:
        for endian in ("big", "little"):
            for swap in (False, True):
                y0, y1 = decode(before, endian, swap)
                y4, y5 = decode(after, endian, swap)
                obs = [y0, y1, 0, 0, y4, y5]
                status, state = recovered_state(obs, params)
                models += 1
                if status == "sat":
                    sat += 1
                    history = generate(*state, params)
                    packet = encode(history[2:4], endian, swap)
                    candidate = bytes(x ^ y for x, y in zip(packet, mask))
                    if sha256(candidate).digest() == target:
                        hits += 1
                        prefix = "--private-hit-output="
                        chosen = [a[len(prefix):] for a in sys.argv[1:]
                                  if a.startswith(prefix)]
                        if not chosen:
                            raise RuntimeError(
                                "Accepted K04 source hit; specify a private local output path"
                            )
                        Path(chosen[0]).write_text(candidate.hex().upper() + "\n")
                elif status == "unsat":
                    unsat += 1
                else:
                    unknown += 1
    assert models == 8
    print(
        f"models={models} complete_original_flank_fits={sat} "
        f"original_unsat={unsat} unresolved_unknown={unknown} "
        f"original_k04_hits={hits} "
        f"planted_full_128bit_states=2/2_PASS selected_ack_input=NONE"
    )


if __name__ == "__main__":
    main()
