"""Source-pinned xoroshiro128++ low-prefix SAT partition pilot.

Tests one complete 16-bit state-prefix partition per invocation. The selected
PS-0417 attempt-2 ACK payload is excluded from inversion and is never read.
A prefix-specific UNSAT does not reject any other prefix or serializer view.
The plant fixture verifies both genuine unknown-state recovery and rejection
of a deliberately incorrect state prefix.

Uses the system Z3 shared library via ctypes and Python's standard library.
"""
import argparse
import ctypes
import ctypes.util
import hashlib
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = (1 << 64) - 1
SEED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)


def rotate_left(number, count):
    return ((number << count) | (number >> (64 - count))) & MASK


def stream(seed):
    a, b = seed
    words = []
    for _ in range(6):
        words.append((rotate_left((a + b) & MASK, 17) + a) & MASK)
        t = a ^ b
        a, b = (rotate_left(a, 49) ^ t ^ (t << 21)) & MASK, rotate_left(t, 28)
    return words


def decode(packet, view):
    endian = "little" if view & 1 else "big"
    words = [int.from_bytes(packet[i:i + 8], endian) for i in (0, 8)]
    return list(reversed(words)) if view & 2 else words


def encode(words, view):
    endian = "little" if view & 1 else "big"
    words = list(reversed(words)) if view & 2 else words
    return b"".join(w.to_bytes(8, endian) for w in words)


def original_bracket():
    source = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA
    rows = {}
    for line in source.decode("ascii").splitlines():
        if line.startswith("2026-"):
            timestamp, *fields = line.split()
            rows[timestamp] = dict(field.split("=", 1) for field in fields)
    assert len(rows) == 133
    trio = [rows[f"2026-10-03T18:0{i}:00Z"] for i in (1, 2, 3)]
    assert all(record["JOB"] == "PS-261003-0417" for record in trio)
    assert [(r["ATTEMPT"], r["STATE"], r["CLASS"]) for r in trio] == [
        ("1", "REQUESTED", "RECOVER"),
        ("2", "ACK", "RECOVER"),
        ("3", "REQUESTED", "RECOVER"),
    ]
    # The middle ACK payload is intentionally not decoded or hashed here.
    return bytes.fromhex(trio[0]["PAYLOAD"]), bytes.fromhex(trio[2]["PAYLOAD"])


def smt_program(values, prefix, prefix_bits):
    assert 0 <= prefix < 1 << prefix_bits <= 1 << 20
    lines = [
        "(set-logic QF_BV)",
        "(declare-fun a0 () (_ BitVec 64))",
        f"(define-fun b0 () (_ BitVec 64) "
        f"(bvsub ((_ rotate_right 17) (bvsub #x{values[0]:016x} a0)) a0))",
    ]
    for i in range(6):
        if i < 5:
            lines.extend((
                f"(declare-fun a{i + 1} () (_ BitVec 64))",
                f"(declare-fun b{i + 1} () (_ BitVec 64))",
                f"(assert (= a{i + 1} (bvxor (bvxor ((_ rotate_left 49) a{i}) "
                f"(bvxor a{i} b{i})) "
                f"(bvshl (bvxor a{i} b{i}) #x0000000000000015))))",
                f"(assert (= b{i + 1} ((_ rotate_left 28) (bvxor a{i} b{i}))))",
            ))
        if values[i] is not None:
            lines.append(
                f"(assert (= (bvadd ((_ rotate_left 17) (bvadd a{i} b{i})) a{i}) "
                f"#x{values[i]:016x}))"
            )
    lines.append(f"(assert (= ((_ extract {prefix_bits - 1} 0) a0) (_ bv{prefix} {prefix_bits})))")
    lines.append("(check-sat-using (then simplify solve-eqs propagate-values bit-blast sat))")
    return "\n".join(lines)


def solve_partition(values, prefix, prefix_bits, timeout_ms):
    library = ctypes.util.find_library("z3")
    assert library is not None, "A system Z3 shared library is required"
    api = ctypes.CDLL(library)
    pointer = ctypes.c_void_p
    api.Z3_mk_config.restype = pointer
    api.Z3_mk_context.argtypes = [pointer]
    api.Z3_mk_context.restype = pointer
    api.Z3_del_config.argtypes = [pointer]
    api.Z3_del_context.argtypes = [pointer]
    api.Z3_eval_smtlib2_string.argtypes = [pointer, ctypes.c_char_p]
    api.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
    config = api.Z3_mk_config()
    context = api.Z3_mk_context(config)
    api.Z3_del_config(config)
    start = time.monotonic()
    try:
        program = f"(set-option :timeout {timeout_ms})\n" + smt_program(values, prefix, prefix_bits)
        answer = api.Z3_eval_smtlib2_string(context, program.encode("ascii")).decode("ascii")
        result = answer.strip().splitlines()[0]
        elapsed = round(time.monotonic() - start, 3)
        if result != "sat":
            assert result in ("unsat", "unknown"), answer
            return {"status": result.upper(), "elapsed_seconds": elapsed}
        model = api.Z3_eval_smtlib2_string(context, b"(get-value (a0 b0))").decode("ascii")
        values_hex = re.findall(r"#x([0-9a-fA-F]{16})", model)
        assert len(values_hex) == 2, model
        state = tuple(int(value, 16) for value in values_hex)
        predicted = stream(state)
        assert all(expected is None or expected == actual
                   for expected, actual in zip(values, predicted)), (model, predicted)
        return {"status": "SAT", "elapsed_seconds": elapsed,
                "state": [f"{word:016X}" for word in state],
                "middle_words": [f"{word:016X}" for word in predicted[2:4]]}
    finally:
        api.Z3_del_context(context)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--view", type=int, choices=range(4), default=0)
    parser.add_argument("--prefix-bits", type=int, choices=range(12, 21), default=16)
    parser.add_argument("--prefix", type=lambda value: int(value, 0), default=0xBEEF)
    parser.add_argument("--timeout-ms", type=int, default=20000)
    parser.add_argument("--control-only", action="store_true")
    args = parser.parse_args()
    assert 0 <= args.prefix < 1 << args.prefix_bits
    assert args.timeout_ms > 0
    assert all(encode(decode(bytes(range(16)), v), v) == bytes(range(16)) for v in range(4))
    first, last = original_bracket()
    assert first.hex().upper() == "CD3E4F216ADB2FB180DA2AA90B33F7A4"
    assert last.hex().upper() == "44D53DFC29D7943A95D89371DA58EC64"
    synthetic = stream(SEED)
    actual_prefix = SEED[0] & ((1 << args.prefix_bits) - 1)
    control = solve_partition(synthetic, actual_prefix, args.prefix_bits, args.timeout_ms)
    assert control["status"] == "SAT", control
    assert control["middle_words"] == [f"{word:016X}" for word in synthetic[2:4]], control
    negative = solve_partition(synthetic, actual_prefix ^ 1, args.prefix_bits, args.timeout_ms)
    assert negative["status"] == "UNSAT", negative
    print(json.dumps({"control": "PASS", "positive": control, "negative": negative}, sort_keys=True), flush=True)
    if args.control_only:
        return
    source = [*decode(first, args.view), None, None, *decode(last, args.view)]
    original = solve_partition(source, args.prefix, args.prefix_bits, args.timeout_ms)
    summary = {"view": args.view, "prefix_bits": args.prefix_bits,
               "prefix": args.prefix, "original": original, "full_domain_tested": False}
    if original["status"] == "SAT":
        coupon = encode([int(word, 16) for word in original["middle_words"]], args.view)
        routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
        mask = bytes.fromhex(routing["K04"]["masked_component"])
        component = bytes(x ^ y for x, y in zip(coupon, mask))
        acceptance = json.loads((ROOT / "acceptance.json").read_text())
        accepted = hashlib.sha256(component).hexdigest() == acceptance["slot_sha256"]["K04"]
        summary.update({"K04_original_PASS": accepted,
                        "component_if_pass": component.hex().upper() if accepted else None})
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
