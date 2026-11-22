#!/usr/bin/env python3
"""Compact native-XOR inversion of a conditional xoroshiro128++ output triad.

The state transition is eliminated as symbolic GF(2) expressions. Only the
initial first word, arithmetic borrow chains, and carry-input words are
materialized. This is a solver-representation experiment, not evidence that
the printer historically used this generator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
from pathlib import Path
import sys

AGENTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTS / "agent36"))
from k04_dual_inverse_borrow_reference import BorrowCircuit

MASK = (1 << 64) - 1
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
FROZEN_STATES = (
    ("F007C59F9D9F4FB7", "C4CAE249D983EBD2"),
    ("2321A6781869EFE4", "ADE1F00D94B03946"),
    ("09BF52A28180679C", "C9EE30F095FC4904"),
    ("BBEB7C1CD5849259", "C3C0358F7BB3AFDF"),
    ("192CF5F4EBEAA437", "8172B263A2AD16A1"),
    ("E5AE140F20F001EF", "6DC3F607A400549A"),
    ("33BA4F681216A22B", "3D4FA00D07FC8AEB"),
    ("114BB35E07789458", "4282F657EB75517A"),
)

def rol(x, n):
    return ((x << n) | (x >> (64 - n))) & MASK

def ror(x, n):
    return ((x >> n) | (x << (64 - n))) & MASK

def stream(state, count=6):
    a, b = state
    out, states = [], []
    for _ in range(count):
        states.append((a, b))
        out.append((rol((a + b) & MASK, 17) + a) & MASK)
        t = a ^ b
        a, b = (rol(a, 49) ^ t ^ (t << 21)) & MASK, rol(t, 28)
    return out, states

def xor_expr(*exprs):
    terms, constant = set(), 0
    for expr in exprs:
        if expr is None:
            continue
        variables, bit = expr
        constant ^= int(bit)
        for variable in variables:
            if variable in terms:
                terms.remove(variable)
            else:
                terms.add(variable)
    return frozenset(terms), bool(constant)

def vexpr(variable):
    return frozenset((variable,)), False

def cexpr(bit):
    return frozenset(), bool(bit)

def add_xor_zero(circuit, expr):
    variables, constant = expr
    if not variables:
        if constant:
            raise ValueError("constant contradiction in symbolic parity")
        return
    circuit.xors.append((list(variables), constant))

def link(circuit, variable, expr):
    add_xor_zero(circuit, xor_expr(vexpr(variable), expr))

def rotate_expr(word, n):
    return [word[(i - n) % 64] for i in range(64)]

def shift_left_expr(word, n):
    return [cexpr(0) if i < n else word[i - n] for i in range(64)]

def xor_words(*words):
    return [xor_expr(*(word[i] for word in words)) for i in range(64)]

def materialize(circuit, expressions, value=None):
    result = []
    for i, expr in enumerate(expressions):
        bit = None if value is None else ((value >> i) & 1)
        variable = circuit.variable(bit)
        link(circuit, variable, expr)
        result.append(variable)
    return result

def subtract_constant(circuit, constant, a_bits):
    borrow = 0
    borrow_in, difference = [], []
    for i in range(64):
        ci = (constant >> i) & 1
        borrow_in.append(borrow)
        difference.append(xor_expr(cexpr(ci), vexpr(a_bits[i]),
                                   vexpr(borrow) if borrow else None))
        if i < 63:
            if borrow == 0:
                borrow = a_bits[i] if ci == 0 else 0
            else:
                borrow = (circuit.or_lits(a_bits[i], borrow) if ci == 0
                          else circuit.and_lits(a_bits[i], borrow))
    return difference, borrow_in

def subtract_word(circuit, x_bits, a_bits):
    borrow = 0
    borrow_in, difference = [], []
    for i in range(64):
        borrow_in.append(borrow)
        difference.append(xor_expr(vexpr(x_bits[i]), vexpr(a_bits[i]),
                                   vexpr(borrow) if borrow else None))
        if i < 63:
            borrow = (circuit.and_lits(-x_bits[i], a_bits[i]) if i == 0
                      else circuit.majority_lits(-x_bits[i], a_bits[i], borrow))
    return difference, borrow_in

def build_triad(words, seed=None):
    """Build exact constraints for three consecutive outputs, no state XOR gates."""
    assert len(words) == 3
    true_outputs, true_states = stream(seed, 3) if seed is not None else (None, None)
    circuit = BorrowCircuit()
    a0_value = None if seed is None else true_states[0][0]
    a0 = circuit.word(a0_value)

    def derive_t(y, a_bits, a_value):
        difference, _ = subtract_constant(circuit, y, a_bits)
        u_expr = rotate_expr(difference, -17)
        u_value = None if a_value is None else ror((y - a_value) & MASK, 17)
        u_bits = materialize(circuit, u_expr, u_value)
        _, second_borrow = subtract_word(circuit, u_bits, a_bits)
        t_expr = [xor_expr(vexpr(u_bits[i]),
                           vexpr(second_borrow[i]) if second_borrow[i] else None)
                  for i in range(64)]
        return u_bits, second_borrow, t_expr

    u0, borrow0, t0 = derive_t(words[0], a0, a0_value)
    a1_expr = xor_words(rotate_expr([vexpr(v) for v in a0], 49),
                        t0, shift_left_expr(t0, 21))
    a1_value = None if seed is None else true_states[1][0]
    a1 = materialize(circuit, a1_expr, a1_value)
    t1 = xor_words([vexpr(v) for v in a1], rotate_expr(t0, 28))
    a2_expr = xor_words(rotate_expr([vexpr(v) for v in a1], 49),
                        t1, shift_left_expr(t1, 21))
    a2_value = None if seed is None else true_states[2][0]
    a2 = materialize(circuit, a2_expr, a2_value)

    u1, borrow1, t1_expected = derive_t(words[1], a1, a1_value)
    for i in range(64):
        add_xor_zero(circuit, xor_expr(t1[i], t1_expected[i]))

    u2, borrow2, t2_expected = derive_t(words[2], a2, a2_value)
    t2 = xor_words([vexpr(v) for v in a2], rotate_expr(t1, 28))
    for i in range(64):
        add_xor_zero(circuit, xor_expr(t2[i], t2_expected[i]))

    return circuit, a0, u0, borrow0

def backward(state):
    a1, b1 = state
    t = ror(b1, 28)
    a0 = ror(a1 ^ t ^ ((t << 21) & MASK), 49)
    return a0, (a0 ^ t) & MASK

def solve_triad(words, limit_seconds):
    from pycryptosat import Solver
    circuit, a0, u0, borrow0 = build_triad(words)
    solver = Solver(threads=1, time_limit=float(limit_seconds))
    for variables, rhs in circuit.xors:
        solver.add_xor_clause(list(variables), rhs)
    for clause in circuit.clauses:
        solver.add_clause(clause)
    started = time.monotonic()
    status, model = solver.solve()
    result = {
        "status": "SAT" if status is True else "UNSAT" if status is False else "UNKNOWN",
        "seconds": round(time.monotonic() - started, 3),
        "variables": circuit.count,
        "cnf_clauses": len(circuit.clauses),
        "xor_clauses": len(circuit.xors),
    }
    if status is not True:
        return result
    a = sum(int(model[v]) << i for i, v in enumerate(a0))
    t = 0
    for i, variable in enumerate(u0):
        bit = int(model[variable])
        if borrow0[i]:
            bit ^= int(model[borrow0[i]])
        t |= bit << i
    state3 = (a, (a ^ t) & MASK)
    replay, _ = stream(state3, 3)
    assert replay == words
    initial = state3
    for _ in range(3):
        initial = backward(initial)
    full, _ = stream(initial, 6)
    assert full[3:6] == words
    result.update({
        "state3": [f"{x:016X}" for x in state3],
        "initial_state": [f"{x:016X}" for x in initial],
        "full_outputs": [f"{x:016X}" for x in full],
        "middle_words": [f"{x:016X}" for x in full[2:4]],
    })
    return result

def validate_circuit():
    import random
    rng = random.Random(0x12345678)
    for _ in range(100):
        seed = (rng.getrandbits(64), rng.getrandbits(64))
        outputs, states = stream(seed, 3)
        circuit, _, _, _ = build_triad(outputs, seed)
        circuit.validate_witness()
    return build_triad(stream((0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA), 3)[0])[0]

def parse_source(root):
    spool = (root / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SOURCE_SHA
    parsed = {}
    for line in spool.decode("ascii").splitlines():
        if line.startswith("2026-"):
            stamp, *fields = line.split()
            parsed[stamp] = dict(field.split("=", 1) for field in fields)
    trio = [parsed[f"2026-10-03T18:0{minute}:00Z"] for minute in (1, 2, 3)]
    assert all(row["JOB"] == "PS-261003-0417" and row["CLASS"] == "RECOVER" for row in trio)
    assert [(row["ATTEMPT"], row["STATE"]) for row in trio] == [
        ("1", "REQUESTED"), ("2", "ACK"), ("3", "REQUESTED")]
    return [bytes.fromhex(row["PAYLOAD"]) for row in trio]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-seconds", type=int, default=120)
    parser.add_argument("--source-limit-seconds", type=int, default=240)
    parser.add_argument("--minimum-calibration-hits", type=int, default=6)
    parser.add_argument("--calibration-only", action="store_true")
    args = parser.parse_args()
    assert 1 <= args.limit_seconds <= 300 and 1 <= args.source_limit_seconds <= 300
    sample = validate_circuit()
    print(json.dumps({"circuit_validation": "100 seeded witnesses PASS",
                      "variables": sample.count, "cnf_clauses": len(sample.clauses),
                      "xor_clauses": len(sample.xors)}), flush=True)

    started = time.monotonic()
    calibration = []
    for index, pair in enumerate(FROZEN_STATES):
        seed = tuple(int(value, 16) for value in pair)
        expected, states = stream(seed, 6)
        state3 = states[3]
        observed, _ = stream(state3, 3)
        result = solve_triad(observed, args.limit_seconds)
        exact_state = result.get("initial_state") == [f"{x:016X}" for x in seed]
        exact_full = result.get("full_outputs") == [f"{x:016X}" for x in expected]
        row = {
            "calibration_index": index, "frozen_state": pair,
            "status": result["status"], "seconds": result["seconds"],
            "variables": result["variables"], "cnf_clauses": result["cnf_clauses"],
            "xor_clauses": result["xor_clauses"],
            "exact_initial_state": exact_state if result["status"] == "SAT" else None,
            "exact_full_replay": exact_full if result["status"] == "SAT" else None,
        }
        calibration.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
    hits = sum(row["status"] == "SAT" and row["exact_initial_state"] and
               row["exact_full_replay"] for row in calibration)
    print(json.dumps({"calibration_summary": {
        "states_total": len(calibration), "exact_full_recoveries": hits,
        "sat": sum(row["status"] == "SAT" for row in calibration),
        "unknown": sum(row["status"] == "UNKNOWN" for row in calibration),
        "unsat": sum(row["status"] == "UNSAT" for row in calibration),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }}, sort_keys=True), flush=True)
    if args.calibration_only or hits < args.minimum_calibration_hits:
        print(json.dumps({"historical_source": "SKIPPED",
                          "reason": "compact inverse calibration below threshold",
                          "K04_status": "NOT_EVALUATED"}), flush=True)
        return

    root = Path(__file__).resolve().parents[2]
    first, selected, third = parse_source(root)
    route = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "resources/acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"].lower()
    for view in (0, 1):
        endian = "little" if view else "big"
        selected_words = [int.from_bytes(selected[i:i+8], endian) for i in (0, 8)]
        third_words = [int.from_bytes(third[i:i+8], endian) for i in (0, 8)]
        observed = [selected_words[1], *third_words]
        result = solve_triad(observed, args.source_limit_seconds)
        result.update({
            "historical_view": view, "fitted_output_positions": [3, 4, 5],
            "ACK2_head8_excluded": True, "blind_REQUESTED1_holdout": True,
            "source_sha256": SOURCE_SHA,
        })
        if result["status"] == "SAT":
            full = [int(value, 16) for value in result["full_outputs"]]
            coupon = b"".join(value.to_bytes(8, endian) for value in full[2:4])
            component = bytes(a ^ b for a, b in zip(coupon, mask))
            first_words = [int.from_bytes(first[i:i+8], endian) for i in (0, 8)]
            result["full_coupon"] = coupon.hex().upper()
            result["blind_REQUESTED1_match"] = full[:2] == first_words
            result["copied_tail8_match"] = coupon[8:] == selected[8:]
            result["K04_original_status"] = (
                "PASS" if hashlib.sha256(component).hexdigest() == target
                else "MISS_FULL_CANDIDATE")
            result["component"] = component.hex().upper()
        print(json.dumps(result, sort_keys=True), flush=True)

if __name__ == "__main__":
    validate_circuit()
    main()
