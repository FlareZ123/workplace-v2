"""Focused original n2 CPython-k2496 short-forward SAT experiment.

Requires z3-solver package, Python standard library, original full repo.
Reads original selected packet only into a parsed list, explicitly excludes it
from fitting and from validating source; checks original K04 digest only after
all other 132 intact source packets match an independently inferred seed.
"""
from __future__ import annotations

import hashlib
import random
import re
import sys
from pathlib import Path

import z3

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent1"))

from k04_cpython_initarray_wrap_sft import control as wrap_control, direct_initialized, U
from k04_cpython_k2496_shortforward_source_sft import original_source, mt, OFFSET
from k04_cpython_k2496_shortforward_smt import model_source

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET4 = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
TIMEOUT_MS = 14 * 60 * 1000


def get_solver(smt: str):
    declarations = smt.split("(check-sat)", 1)[0]
    solver = z3.SolverFor("QF_BV")
    solver.set(timeout=TIMEOUT_MS)
    solver.from_string(declarations)
    return solver


def genuine_model_positive(masks):
    keys = [0x12345678, 0x1535AF52]
    a, b1, state = direct_initialized(keys)
    seeded_masks = [(m, state[i] & m) for i, (m, _) in enumerate(masks)]
    proof = model_source(2, 17, seeded_masks, state[6], state[7],
                         frozen_keys=keys, timeout_ms=3000)
    solver = get_solver(proof)
    solver.set(timeout=3000)
    status = solver.check()
    assert status == z3.sat, ("seeded source exact positive", status)
    assert solver.model().eval(z3.BitVec("k0", 32)).as_long() == keys[0]
    assert solver.model().eval(z3.BitVec("k1", 32)).as_long() == keys[1]
    print("GENUINE_SEEDED_N2_SMT_POSITIVE=PASS", flush=True)


def source_packets():
    spool = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    packets = [bytes.fromhex(v.decode()) for v in
               re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(packets) == len(mt.STARTS) == 133 and mt.STARTS[129] == 951
    return packets


def validate_seed(keys, packets):
    integer_seed = keys[0] | (keys[1] << 32)
    rng = random.Random(integer_seed)
    words = [rng.getrandbits(32)
             for _ in range(OFFSET + max(mt.STARTS) + 4)]
    predicted = [
        b"".join(words[OFFSET + stage + lane].to_bytes(4, "little")
                 for lane in range(4))
        for stage in mt.STARTS
    ]
    correct = sum(predicted[i] == packets[i]
                  for i in range(133) if i != 129)
    return correct, predicted[129]


def main():
    wrap_control()
    masks = original_source()
    genuine_model_positive(masks)
    packets = source_packets()
    source = model_source(2, 17, masks, masks[6][1], masks[7][1],
                          timeout_ms=TIMEOUT_MS)
    print("ORIGINAL_N2_17ROUND_SOURCE_SMT_SHA256=" +
          hashlib.sha256(source.encode()).hexdigest(), flush=True)
    solver = get_solver(source)
    seen = 0
    while seen < 32:
        result = solver.check()
        print("ORIGINAL_N2_STATUS", str(result), "candidate_iteration", seen,
              flush=True)
        if result == z3.unsat:
            print("ORIGINAL_N2_SOURCE_MODEL_EXCLUDED", flush=True)
            return
        if result == z3.unknown:
            print("ORIGINAL_N2_UNDECIDED", solver.reason_unknown(), flush=True)
            return
        m = solver.model()
        keys = [m.eval(z3.BitVec(f"k{i}", 32)).as_long() for i in range(2)]
        matched, packet = validate_seed(keys, packets)
        print(f"ORIGINAL_N2_POSSIBLE_SOURCE_KEY={keys[0]:08X}:{keys[1]:08X}"
              f"_MATCHED_INTACT_PACKETS={matched}/132", flush=True)
        if matched == 132:
            component = bytes(a ^ b for a, b in zip(packet, MASK))
            status = hashlib.sha256(component).hexdigest() == TARGET4
            print("ORIGINAL_N2_FULL_SOURCE_MODEL_PASS", flush=True)
            print("ORIGINAL_K04_ACCEPTANCE_PASS" if status else
                  "ORIGINAL_K04_ACCEPTANCE_FAIL", flush=True)
            if status:
                print("RECOVERED_ORIGINAL_K04_COMPONENT=" +
                      component.hex().upper(), flush=True)
            return
        solver.add(z3.Or(*[
            z3.BitVec(f"k{i}", 32) != keys[i] for i in range(2)
        ]))
        seen += 1
    print("ORIGINAL_N2_REMAINING_SOURCE_SEED_MODELS_UNRESOLVED", flush=True)


if __name__ == "__main__":
    main()
