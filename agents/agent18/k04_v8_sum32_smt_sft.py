"""H-17 source-only exact current V8 Math.random sum32 packet emitter check.

Requires libz3 via ctypes; source facts:
https://github.com/v8/v8/blob/main/src/base/utils/random-number-generator.h
https://github.com/v8/v8/blob/main/src/numbers/math-random.cc

The tested architecture is hypothetical: four Math.floor(Math.random()*2**32)
outputs make each 16-byte printer payload, with 0..63 fixed extra RNG draws
between consecutive intact source packets. Selected 18:02 ACK2 is never parsed.
"""
from pathlib import Path
import ctypes
import ctypes.util
import hashlib
import re

SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
ORIGINAL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == ORIGINAL_SHA
packets = []
for line in SOURCE.read_text().splitlines():
    if not line.startswith(("2026-10-03T07:00:00+00:00 ", "2026-10-03T07:05:00+00:00 ")):
        continue
    data = dict(word.split("=", 1) for word in line.split()[1:])
    assert data["STATE"] == "ACK" and data["ATTEMPT"] == "1"
    packets.append(bytes.fromhex(data["PAYLOAD"]))
assert len(packets) == 2

lib = ctypes.CDLL(ctypes.util.find_library("z3"))
lib.Z3_mk_config.restype = ctypes.c_void_p
lib.Z3_mk_context.argtypes = [ctypes.c_void_p]
lib.Z3_mk_context.restype = ctypes.c_void_p
lib.Z3_set_param_value.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
lib.Z3_eval_smtlib2_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lib.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
lib.Z3_del_context.argtypes = [ctypes.c_void_p]
lib.Z3_del_config.argtypes = [ctypes.c_void_p]


def exact_model(values, gap, order, known_seed=None):
    """Z3 64-bit xorshift128+ equations for 8 observed top32 words."""
    assert len(values) == 2
    commands = [
        "(set-logic QF_BV)",
        "(declare-const s0init (_ BitVec 64))",
        "(declare-const s1init (_ BitVec 64))",
        "(define-fun z0 () (_ BitVec 64) s0init)",
        "(define-fun w0 () (_ BitVec 64) s1init)",
    ]
    last_step = 8 + gap
    for i in range(last_step):
        a, b = f"z{i}", f"w{i}"
        commands.extend((
            f"(define-fun z{i+1} () (_ BitVec 64) {b})",
            f"(define-fun t{i+1} () (_ BitVec 64) "
            f"(bvxor {a} (bvshl {a} #x0000000000000017)))",
            f"(define-fun q{i+1} () (_ BitVec 64) "
            f"(bvxor t{i+1} (bvlshr t{i+1} #x0000000000000011)))",
            f"(define-fun w{i+1} () (_ BitVec 64) "
            f"(bvxor (bvxor q{i+1} {b}) "
            f"(bvlshr {b} #x000000000000001a)))",
        ))
    for packet_num, payload in enumerate(values):
        for k in range(4):
            position = 4 * k
            observed = int.from_bytes(payload[position:position+4], order)
            idx = packet_num * (4 + gap) + k + 1
            commands.append(
                f"(assert (= ((_ extract 63 32) (bvadd z{idx} w{idx})) "
                f"(_ bv{observed} 32)))"
            )
    if known_seed is not None:
        commands.append(f"(assert (= s0init (_ bv{known_seed[0]} 64)))")
        commands.append(f"(assert (= s1init (_ bv{known_seed[1]} 64)))")
    commands.append("(check-sat)")
    config = lib.Z3_mk_config()
    lib.Z3_set_param_value(config, b"timeout", b"1800")
    context = lib.Z3_mk_context(config)
    try:
        answer = lib.Z3_eval_smtlib2_string(
            context, "\n".join(commands).encode()
        ).decode().splitlines()[0]
    finally:
        lib.Z3_del_context(context)
        lib.Z3_del_config(config)
    return answer


def seeded_fixture(gap):
    """Numerical V8 xorshift128+ control with independent source generation."""
    mask = (1 << 64) - 1
    seed = 0x1234567890ABCDEF, 0x9876543210012345
    a, b = seed
    words = []
    for _ in range(8 + gap):
        t = a ^ ((a << 23) & mask)
        t ^= t >> 17
        t ^= b ^ (b >> 26)
        a, b = b, t & mask
        words.append((a + b) & mask)
    observations = []
    for row in range(2):
        observations.append(
            b"".join((words[row * (4 + gap) + j] >> 32).to_bytes(4, "big")
                     for j in range(4))
        )
    return seed, observations


if __name__ == "__main__":
    for gap in (0, 3, 7):
        seed, sample = seeded_fixture(gap)
        assert exact_model(sample, gap, "big", seed) == "sat"
        damaged = [sample[0], bytes([sample[1][0] ^ 1]) + sample[1][1:]]
        assert exact_model(damaged, gap, "big", seed) == "unsat"
    print("Seeded positive and deliberate-bit-flip control: 3/3 each PASS")
    counts = {"unsat": 0, "sat": 0, "unknown": 0}
    for gap in range(64):
        for order in ("big", "little"):
            status = exact_model(packets, gap, order)
            counts[status] += 1
            assert status == "unsat", (gap, order, status)
        if gap % 8 == 7:
            print(f"Original source gaps 0..{gap}: {counts}")
    assert counts == {"unsat": 128, "sat": 0, "unknown": 0}
    print("PASS: all 128 original modern-V8 sum32 fixed-gap models UNSAT")
