#!/usr/bin/env python3
"""Read-only exact xoroshiro128+ summed-output K04 recovery candidate screen.

Two independently preserved PS-0417 REQUESTED flanks are full 16-byte source
anchors. The disputed copied ACK2 is withheld completely. Z3 reconstructs
every full 128-bit state solution of each two-64-bit-output anchor. Complete
future/previous native packets reach the unchanged original K04 SHA-256 gate.
Test both published (L,B,R) transition families: (55,14,36),(24,16,37).
Requires system libz3 shared library. No original file is modified.
"""
import argparse
import ctypes
import ctypes.util
import hashlib
import json
import re
import time
from pathlib import Path
from zipfile import ZipFile

M64 = (1 << 64) - 1
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
K04_TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"


def rol(x, k):
    return ((x << k) | (x >> (64 - k))) & M64


def ror(x, k):
    return ((x >> k) | (x << (64 - k))) & M64


def step(state, L, B, R):
    a, b = state
    result = (a + b) & M64
    v = a ^ b
    return result, (rol(a, L) ^ v ^ ((v << B) & M64), rol(v, R))


def backward(state, L, B, R):
    later_a, later_b = state
    v = ror(later_b, R)
    a = ror(later_a ^ v ^ ((v << B) & M64), L)
    before = (a, a ^ v)
    assert step(before, L, B, R)[1] == state
    return before


def equations(words, recurrence, limit_seconds):
    y0, y1 = words
    L, B, R = recurrence
    return f"""(set-logic QF_BV)
(set-option :timeout {limit_seconds*1000})
(declare-const a0 (_ BitVec 64))
(define-fun b0 () (_ BitVec 64) (bvsub #x{y0:016x} a0))
(define-fun v () (_ BitVec 64) (bvxor a0 b0))
(define-fun a1 () (_ BitVec 64) (bvxor (bvxor ((_ rotate_left {L}) a0) v) (bvshl v #x{B:016x})))
(define-fun b1 () (_ BitVec 64) ((_ rotate_left {R}) v))
(assert (= (bvadd a1 b1) #x{y1:016x}))
(check-sat)"""


def z3_api():
    libname = ctypes.util.find_library("z3")
    if not libname:
        raise RuntimeError("A system Z3 shared library is required")
    api = ctypes.CDLL(libname)
    api.Z3_mk_config.restype = ctypes.c_void_p
    api.Z3_mk_context.argtypes = (ctypes.c_void_p,)
    api.Z3_mk_context.restype = ctypes.c_void_p
    api.Z3_eval_smtlib2_string.argtypes = (ctypes.c_void_p, ctypes.c_char_p)
    api.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
    api.Z3_del_context.argtypes = (ctypes.c_void_p,)
    api.Z3_del_config.argtypes = (ctypes.c_void_p,)
    return api


def invert(words, recurrence, limit_seconds, cap=16):
    api = z3_api()
    config = api.Z3_mk_config()
    context = api.Z3_mk_context(config)
    begun = time.monotonic()
    states = []
    terminal = "unknown"
    try:
        for index in range(cap + 1):
            command = (equations(words, recurrence, limit_seconds)
                       if index == 0 else "(check-sat)")
            response = api.Z3_eval_smtlib2_string(context, command.encode()).decode().strip()
            if response != "sat":
                terminal = response
                break
            if index == cap:
                terminal = "CAP_REACHED"
                break
            answer = api.Z3_eval_smtlib2_string(context, b"(get-value (a0))").decode()
            a = int(re.search(r"#x([a-fA-F0-9]{16})", answer).group(1), 16)
            b = (words[0] - a) & M64
            state = a, b
            value, after = step(state, *recurrence)
            next_value, _ = step(after, *recurrence)
            assert [value, next_value] == words and state not in states
            states.append(state)
            api.Z3_eval_smtlib2_string(
                context, f"(assert (not (= a0 #x{a:016x})))".encode())
    finally:
        api.Z3_del_context(context)
        api.Z3_del_config(config)
    return states, terminal, round(time.monotonic() - begun, 3)


def generate(state, recurrence, count, reverse_time):
    for _ in range(count):
        if reverse_time:
            prior = backward(state, *recurrence)
            value, check = step(prior, *recurrence)
            assert check == state
            state = prior
        else:
            value, state = step(state, *recurrence)
        yield value


def decode(packet, endian, reverse_words):
    words = [int.from_bytes(packet[start:start+8], endian) for start in (0, 8)]
    return words[::-1] if reverse_words else words


def encode(words, endian, reverse_words):
    return b"".join(word.to_bytes(8, endian)
                    for word in (words[::-1] if reverse_words else words))


def source(path):
    if path.is_file():
        with ZipFile(path) as archive:
            def get(name):
                return archive.read(name)
            spool = get("evidence/print/spool-reconstruction.log")
            routing = get("evidence/recovery-routing.json")
            acceptance = get("acceptance.json")
    else:
        spool = (path / "evidence/print/spool-reconstruction.log").read_bytes()
        routing = (path / "evidence/recovery-routing.json").read_bytes()
        acceptance = (path / "acceptance.json").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(routing).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(acceptance).hexdigest() == ACCEPT_SHA
    routing = json.loads(routing)
    acceptance = json.loads(acceptance)
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"].lower()
    assert len(mask) == 16 and target == K04_TARGET
    records = []
    for line in spool.decode("ascii").splitlines():
        if "JOB=PS-261003-0417" in line and "CLASS=RECOVER" in line:
            words = line.split()
            fields = dict(word.split("=", 1) for word in words[1:])
            records.append(fields)
    assert [(r["ATTEMPT"], r["STATE"]) for r in records] == [
        ("1", "REQUESTED"), ("2", "ACK"), ("3", "REQUESTED")]
    # Never parse or admit the questionable ACK2 PAYLOAD as a source value.
    return [bytes.fromhex(records[0]["PAYLOAD"]),
            bytes.fromhex(records[2]["PAYLOAD"])], mask, target


def controls(limit_seconds):
    for recurrence in ((55, 14, 36), (24, 16, 37)):
        seed = (0x123456789ABCDEF0, 0xFEDCBA9876543210)
        for _ in range(1000):
            _, after = step(seed, *recurrence)
            assert backward(after, *recurrence) == seed
            seed = after
        seed = (0x123456789ABCDEF0, 0xFEDCBA9876543210)
        native = list(generate(seed, recurrence, 20, False))
        states, status, elapsed = invert(native[:2], recurrence, limit_seconds)
        assert seed in states and status == "unsat"
        assert list(generate(seed, recurrence, 20, False)) == native
        # Construct and verify complete synthetic 16-byte source targets.
        hypothetical = encode(native[10:12], "big", False)
        generated = list(generate(seed, recurrence, 12, False))
        assert encode(generated[10:12], "big", False) == hypothetical
        print(json.dumps({"synthetic": list(recurrence),
                          "planted_state_recovered": True,
                          "all_preimages": len(states), "terminal": status,
                          "inverse_roundtrips": 1000,
                          "full_packet_positive": "PASS",
                          "solver_seconds": elapsed}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resources", type=Path,
                        default=Path(__file__).resolve().parents[2] / "resources")
    parser.add_argument("--windows", type=int, default=65536)
    parser.add_argument("--limit-seconds", type=int, default=45)
    args = parser.parse_args()
    assert args.windows >= 4 and args.limit_seconds >= 1
    controls(args.limit_seconds)
    packets, mask, target = source(args.resources)
    totals = {"original_K04_matches": [], "source_pair_holdout": 0,
              "source_states": 0, "complete_K04_assignments": 0,
              "solver_nonexhaustive_views": 0}
    for recurrence in ((55, 14, 36), (24, 16, 37)):
        for anchor in (0, 1):
            backwards = anchor == 1
            for endian in ("little", "big"):
                for reverse_words in (False, True):
                    known = decode(packets[anchor], endian, reverse_words)
                    other = decode(packets[1 - anchor], endian, reverse_words)
                    states, status, elapsed = invert(
                        known, recurrence, args.limit_seconds)
                    row = {"recurrence": recurrence, "anchor_attempt": (1, 3)[anchor],
                           "endian": endian, "reverse_words": reverse_words,
                           "reverse_time": backwards, "source_states": len(states),
                           "terminal": status, "solver_seconds": elapsed,
                           "full_K04_checks": 0, "original_K04_matches": [],
                           "other_request_holdouts": []}
                    if status != "unsat":
                        totals["solver_nonexhaustive_views"] += 1
                    for state in states:
                        native = list(generate(state, recurrence, args.windows, backwards))
                        start = 0 if backwards else 2
                        for pos in range(start, args.windows - 1):
                            words = native[pos:pos+2]
                            if backwards:
                                words = words[::-1]
                            if words == other:
                                row["other_request_holdouts"].append(pos)
                            coupon = encode(words, endian, reverse_words)
                            candidate = bytes(a ^ b for a, b in zip(coupon, mask))
                            if hashlib.sha256(candidate).hexdigest() == target:
                                row["original_K04_matches"].append({
                                    "position": pos,
                                    "coupon": coupon.hex().upper(),
                                    "component": candidate.hex().upper()})
                            row["full_K04_checks"] += 1
                    totals["source_states"] += row["source_states"]
                    totals["complete_K04_assignments"] += row["full_K04_checks"]
                    totals["source_pair_holdout"] += len(row["other_request_holdouts"])
                    totals["original_K04_matches"] += row["original_K04_matches"]
                    print(json.dumps({"historical": row}, sort_keys=True), flush=True)
    print(json.dumps({"summary": totals}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
