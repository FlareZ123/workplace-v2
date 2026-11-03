"""K04 selected-middle retry inverse SFT, read-only and source-pinned.

Models 18:01 REQUESTED1 as four xorshift128+ 32-bit summed outputs,
withholds four 18:02 ACK2 outputs, and constrains 18:03 REQUESTED3
as the next four outputs. Tests both high/low 32-bit halves and four
packet serialization views, 8 conditional producer families total.

Requires an installed Z3 shared library (libz3.so / libz3.dll).
"""
import ctypes
import ctypes.util
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK64 = (1 << 64) - 1


def xorshift_step(a, b):
    x = (a ^ ((a << 23) & MASK64)) & MASK64
    c = (x ^ b ^ (x >> 17) ^ (b >> 26)) & MASK64
    return (b, c), ((b + c) & MASK64)


def inverse_middle(before, after, upper, extra_draws=0, timeout_ms=15000):
    """Return all SMT model states and missing middle words, or fail on UNKNOWN."""
    assert len(before) == len(after) == 4 and 0 <= extra_draws <= 8
    last_start = 8 + extra_draws
    stream_size = last_start + 4
    name = ctypes.util.find_library("z3") or "libz3.so.4"
    lib = ctypes.CDLL(name)
    lib.Z3_mk_config.restype = ctypes.c_void_p
    lib.Z3_mk_context.argtypes = [ctypes.c_void_p]
    lib.Z3_mk_context.restype = ctypes.c_void_p
    lib.Z3_del_config.argtypes = [ctypes.c_void_p]
    lib.Z3_del_context.argtypes = [ctypes.c_void_p]
    lib.Z3_eval_smtlib2_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype = ctypes.c_char_p

    config = lib.Z3_mk_config()
    context = lib.Z3_mk_context(config)
    lib.Z3_del_config(config)

    def eval_smt(commands):
        return lib.Z3_eval_smtlib2_string(context, commands.encode()).decode().strip()

    try:
        lines = [f"(set-option :timeout {timeout_ms})", "(set-logic QF_BV)"]
        for i in range(stream_size + 1):
            lines += [f"(declare-const a{i} (_ BitVec 64))",
                      f"(declare-const b{i} (_ BitVec 64))"]
        for i in range(stream_size):
            lines.append(f"(assert (= a{i+1} b{i}))")
            x = f"(bvxor a{i} (bvshl a{i} #x0000000000000017))"
            y = (f"(bvxor (bvxor (bvxor {x} b{i}) "
                 f"(bvlshr {x} #x0000000000000011)) "
                 f"(bvlshr b{i} #x000000000000001a))")
            lines.append(f"(assert (= b{i+1} {y}))")
            observed = before[i] if i < 4 else (after[i - last_start] if i >= last_start else None)
            if observed is not None:
                top, bottom = (63, 32) if upper else (31, 0)
                expr = f"((_ extract {top} {bottom}) (bvadd b{i} b{i+1}))"
                lines.append(f"(assert (= {expr} #x{observed:08x}))")
        eval_smt("\n".join(lines))
        models = []
        for _ in range(16):
            # Explicit QF_BV bit-blast SAT tactic is far faster than the
            # default solver on the lower32 historical/synthetic branches.
            status = eval_smt("(check-sat-using (then simplify bit-blast sat))")
            if status == "unsat":
                return models
            if status != "sat":
                raise RuntimeError("Inconclusive exact inversion: " + status)
            returned = eval_smt("(get-value (a0 b0))")
            values = re.findall(r"#x([0-9a-fA-F]{16})", returned)
            assert len(values) == 2, returned
            seed = tuple(int(x, 16) for x in values)
            state = seed
            stream = []
            for _ in range(stream_size):
                state, word64 = xorshift_step(*state)
                stream.append(word64 >> 32 if upper else word64 & 0xFFFFFFFF)
            assert stream[:4] == before and stream[last_start:] == after
            models.append((seed, stream[4:last_start]))
            a, b = seed
            eval_smt(f"(assert (not (and (= a0 #x{a:016x}) (= b0 #x{b:016x}))))")
        raise RuntimeError("More than 16 models; enumeration incomplete")
    finally:
        lib.Z3_del_context(context)


def read_source():
    data = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == SOURCE_SHA
    rows = []
    selected_ack_count = 0
    for line in data.decode("ascii").splitlines():
        if "PAYLOAD=" not in line:
            continue
        if "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER " in line:
            selected_ack_count += 1
            continue
        fields = dict(re.findall(r"([A-Z]+)=([^ ]+)", line))
        fields["timestamp"] = line.split()[0]
        rows.append(fields)

    def select(when, attempt, state):
        selected = [x for x in rows if x["JOB"] == "PS-261003-0417"
                    and x["timestamp"].startswith(when)
                    and x["ATTEMPT"] == str(attempt)
                    and x["STATE"] == state and x["CLASS"] == "RECOVER"]
        assert len(selected) == 1
        return bytes.fromhex(selected[0]["PAYLOAD"])

    first = select("2026-10-03T18:01:", 1, "REQUESTED")
    # Presence-only; the selected 18:02 payload was excluded before parsing.
    assert selected_ack_count == 1
    last = select("2026-10-03T18:03:", 3, "REQUESTED")
    assert first.hex().upper() == "CD3E4F216ADB2FB180DA2AA90B33F7A4"
    assert last.hex().upper() == "44D53DFC29D7943A95D89371DA58EC64"
    return first, last


def main():
    seed = (0x123456789ABCDEF0, 0xFEDCBA9876543210)
    state = seed
    stream = []
    for _ in range(17):
        state, out = xorshift_step(*state)
        stream.append(out)
    first, last = read_source()
    count = 0
    for upper in (True, False):
        example = [x >> 32 if upper else x & 0xFFFFFFFF for x in stream]
        planted = inverse_middle(example[:4], example[8:12], upper)
        assert planted == [(seed, example[4:8])]
        extra_positive = inverse_middle(example[:4], example[13:17], upper, extra_draws=5)
        assert extra_positive == [(seed, example[4:13])]
        assert extra_positive[0][1][2:6] == example[6:10]
        print(f"SYNTHETIC upper32={upper} zero and five extra-draw missing coupons PASS")
        for endian in ("little", "big"):
            for reverse in (False, True):
                before = [int.from_bytes(first[i:i + 4], endian) for i in range(0, 16, 4)]
                after = [int.from_bytes(last[i:i + 4], endian) for i in range(0, 16, 4)]
                if reverse:
                    before.reverse()
                    after.reverse()
                for extra_draws in range(9):
                    models = inverse_middle(before, after, upper, extra_draws=extra_draws)
                    assert models == [], (upper, endian, reverse, extra_draws, models)
                    count += 1
                print(f"ORIGINAL upper32={upper} endian={endian} reverse={reverse}, extra 0..8: 9 UNSAT")
    assert count == 72
    print("72 historical source models UNSAT; K04 selected ACK withheld and unchanged")


if __name__ == "__main__":
    main()
