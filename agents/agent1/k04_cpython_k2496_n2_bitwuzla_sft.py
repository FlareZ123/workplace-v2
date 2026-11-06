"""Independent Bitwuzla original K04 CPython k2496 n2 seed check.

Historical candidate requires 132/132 original intact packet source prediction
before checking the selected coupon against the unmodified K04 commitment.
Selected printer row129 is never entered into the source fit.
"""
from __future__ import annotations

import hashlib
import random
import re
import sys
import time
from pathlib import Path

import bitwuzla
from bitwuzla import TermManager, Options, Option, Parser, Result

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent1"))
from k04_cpython_initarray_wrap_sft import direct_initialized, U
from k04_cpython_k2496_shortforward_source_sft import (
    original_source, synthetic_controls, mt, OFFSET,
)
from k04_cpython_k2496_shortforward_smt import model_source

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET4 = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MAX_RUNTIME = 15 * 60


class Deadline:
    def __init__(self, seconds):
        self.deadline = time.monotonic() + seconds

    def __call__(self):
        return time.monotonic() >= self.deadline


def parse_solver(text, seconds):
    tm = TermManager()
    opts = Options()
    opts.set(Option.PRODUCE_MODELS, True)
    parser = Parser(tm, opts)
    # Stop at check-sat; run solver directly to retain model and timeout control.
    parser.parse(text.split("(check-sat)", 1)[0],
                 parse_only=True, parse_file=False)
    parser.configure_terminator(Deadline(seconds))
    return parser


def get_keys(parser):
    solver = parser.bitwuzla()
    return [
        int(solver.get_value(parser.parse_term(f"k{index}")).value(16), 16)
        for index in (0, 1)
    ]


def original_packets():
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    payloads = [bytes.fromhex(s.decode()) for s in
                re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(payloads) == 133 and mt.STARTS[129] == 951
    return payloads


def fully_validate(keys, packets):
    seed = keys[0] | (keys[1] << 32)
    prng = random.Random(seed)
    words = [prng.getrandbits(32) for _ in
             range(OFFSET + max(mt.STARTS) + 4)]
    predicted = [
        b"".join(words[OFFSET + start + j].to_bytes(4, "little")
                 for j in range(4))
        for start in mt.STARTS
    ]
    matched = sum(predicted[index] == packets[index]
                  for index in range(133) if index != 129)
    return matched, predicted[129]


def main():
    synthetic_controls()
    masks = original_source()
    assert masks[6] == (U, 0xE403BB7D)
    assert masks[7] == (U, 0x1F7B301F)
    keys = [0x12345678, 0x1535AF52]
    a, b1, state = direct_initialized(keys)
    planted = [(m, state[i] & m) for i, (m, _) in enumerate(masks)]
    positive = model_source(
        2, 17, planted, state[6], state[7], frozen_keys=keys,
        timeout_ms=12000,
    )
    pos_parser = parse_solver(positive, seconds=12)
    pos_result = pos_parser.bitwuzla().check_sat()
    assert pos_result == Result.SAT, ("genuine seed n2 must SAT", pos_result)
    assert get_keys(pos_parser) == keys, "genuine n2 seed recovery"
    print("BITWUZLA_INDEPENDENT_GENUINE_CPYTHON_N2_SAT_POSITIVE PASS",
          flush=True)

    source = model_source(2, 17, masks, masks[6][1], masks[7][1],
                          timeout_ms=900000)
    print("ORIGINAL_SOURCE_N2_SMT_SHA256",
          hashlib.sha256(source.encode()).hexdigest(), flush=True)
    parser = parse_solver(source, seconds=MAX_RUNTIME)
    solver = parser.bitwuzla()
    packets = original_packets()
    for iteration in range(16):
        result = solver.check_sat()
        print("ORIGINAL_SOURCE_N2_BITWUZLA_RESULT", result,
              "iteration", iteration, flush=True)
        if result == Result.UNSAT:
            print("ORIGINAL_K2496_N2_CONDITIONAL_SOURCE_UNSAT", flush=True)
            return
        if result == Result.UNKNOWN:
            print("ORIGINAL_K2496_N2_UNDECIDED", flush=True)
            return
        if result != Result.SAT:
            raise AssertionError(("unexpected Bitwuzla result", result))
        found = get_keys(parser)
        matched, coupon = fully_validate(found, packets)
        print("CANDIDATE_KEY", [f"{x:08X}" for x in found],
              "WHOLE_ORIGINAL_INTACT_MATCHES", f"{matched}/132", flush=True)
        if matched == 132:
            component = bytes(x ^ y for x, y in zip(coupon, MASK))
            valid = hashlib.sha256(component).hexdigest() == TARGET4
            print("FULL_SOURCE_MATCH_K04_COMMITMENT", valid, flush=True)
            if valid:
                print("RECOVERED_K04_COMPONENT", component.hex().upper(),
                      flush=True)
            return
        exclusion = "(assert (or " + " ".join(
            f"(distinct k{i} #x{found[i]:08X})" for i in (0, 1)
        ) + "))"
        parser.parse(exclusion, parse_only=True, parse_file=False)
    print("ORIGINAL_K2496_N2_REMAINING_SAT_MODELS_UNRESOLVED", flush=True)


if __name__ == "__main__":
    main()
