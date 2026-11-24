#!/usr/bin/env python3
"""Direct-borrow Boolean/XOR Z3 backend for the H-17 K04 xoroshiro128++ hypothesis.

The first-pair core uses the exact dual-inverse identity and eliminates b0
through t0. It is translated as a compact Boolean CNF/XOR circuit into Z3,
rather than asking QF_BV to bit-blast nested 64-bit arithmetic.

Fits only the first REQUESTED packet (outputs 0/1), derives the middle pair,
and blindly checks the third REQUESTED packet (outputs 4/5). The 18:02 ACK is
withheld from fitting. Every complete masked middle candidate is checked
against the original K04 commitment before holdout or uniqueness disposition.
"""
import argparse
import hashlib
import json
import time

from z3 import Bool, BoolVal, Not, Or, Solver, Xor, is_true, sat, unsat, unknown

MASK = (1 << 64) - 1
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SEED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)
MAX_MIDDLE_MODELS = 8
MAX_TOTAL_SOLVE_SECONDS = 600
ROOT = __import__("pathlib").Path(__file__).resolve().parents[2] / "resources"


def stream(state, count=6):
    a, b = state
    out = []
    for _ in range(count):
        total = (a + b) & MASK
        out.append((((total << 17) | (total >> 47)) + a) & MASK)
        t = a ^ b
        a, b = (((a << 49) | (a >> 15)) ^ t ^ (t << 21)) & MASK, ((t << 28) | (t >> 36)) & MASK
    return out


def decode(payload, view):
    endian = "little" if view & 1 else "big"
    words = [int.from_bytes(payload[i:i + 8], endian) for i in (0, 8)]
    return words[::-1] if view & 2 else words


def encode(words, view):
    endian = "little" if view & 1 else "big"
    words = words[::-1] if view & 2 else words
    return b"".join(int(x).to_bytes(8, endian) for x in words)


class BorrowCircuit:
    """Exact t0-eliminated, fused dual-inverse circuit; variables are 1-based."""

    def __init__(self):
        self.count = 0
        self.clauses = []
        self.xors = []
        self.witness = {}

    def variable(self, value=None):
        self.count += 1
        if value is not None:
            self.witness[self.count] = bool(value)
        return self.count

    def word(self, value=None):
        return [
            self.variable(None if value is None else bool((value >> i) & 1))
            for i in range(64)
        ]

    def lit_value(self, lit):
        value = self.witness[abs(lit)]
        return value if lit > 0 else not value

    def xor_rhs(self, terms, rhs=0):
        terms = [v for v in terms if v]
        if not terms:
            if rhs:
                raise ValueError("constant-one XOR output is not used by this circuit")
            return 0
        if len(terms) == 1 and rhs == 0:
            return terms[0]
        known = all(v in self.witness for v in terms)
        value = ((sum(self.witness[v] for v in terms) % 2) ^ bool(rhs)) if known else None
        out = self.variable(value)
        self.xors.append((terms + [out], bool(rhs)))
        return out

    def xor(self, *terms):
        return self.xor_rhs(list(terms), 0)

    def and_lits(self, x, y):
        known = abs(x) in self.witness and abs(y) in self.witness
        value = self.lit_value(x) and self.lit_value(y) if known else None
        out = self.variable(value)
        self.clauses.extend(([-x, -y, out], [x, -out], [y, -out]))
        return out

    def or_lits(self, x, y):
        known = abs(x) in self.witness and abs(y) in self.witness
        value = self.lit_value(x) or self.lit_value(y) if known else None
        out = self.variable(value)
        self.clauses.extend(([-x, out], [-y, out], [x, y, -out]))
        return out

    def majority_lits(self, x, y, z):
        known = all(abs(v) in self.witness for v in (x, y, z))
        value = sum(self.lit_value(v) for v in (x, y, z)) >= 2 if known else None
        out = self.variable(value)
        self.clauses.extend((
            [-x, -y, out], [-x, -z, out], [-y, -z, out],
            [x, y, -out], [x, z, -out], [y, z, -out],
        ))
        return out

    def add64(self, a, b):
        carry = 0
        out = []
        for i in range(64):
            out.append(self.xor(a[i], b[i], carry))
            if i < 63:
                carry = self.and_lits(a[i], b[i]) if i == 0 else self.majority_lits(a[i], b[i], carry)
        return out

    def sub_const64(self, c, a):
        """Return c-a using the exact bitwise borrow recurrence."""
        borrow = 0
        out = []
        for i in range(64):
            ci = (c >> i) & 1
            out.append(self.xor_rhs([a[i], borrow], ci))
            if i < 63:
                if borrow == 0:
                    borrow = a[i] if ci == 0 else 0
                else:
                    borrow = self.or_lits(a[i], borrow) if ci == 0 else self.and_lits(a[i], borrow)
        return out

    @staticmethod
    def rotated(bits, n):
        return [bits[(i - n) % 64] for i in range(64)]

    def get_t_from_output(self, a, y):
        """Derive t=a XOR b from y=ROTL(a+b,17)+a, without materializing b."""
        u = self.rotated(self.sub_const64(y, a), -17)
        borrow = 0
        t = []
        for i in range(64):
            t.append(self.xor(u[i], borrow))
            if i < 63:
                borrow = self.and_lits(-u[i], a[i]) if i == 0 else self.majority_lits(-u[i], a[i], borrow)
        return t

    def step_from_t(self, a, t):
        ra = self.rotated(a, 49)
        na = [self.xor(ra[i], t[i], t[i - 21] if i >= 21 else 0) for i in range(64)]
        nb = self.rotated(t, 28)
        return na, nb

    def step(self, a, b):
        t = [self.xor(x, y) for x, y in zip(a, b)]
        return self.step_from_t(a, t)

    def output(self, a, b):
        return self.add64(self.rotated(self.add64(a, b), 17), a)

    def constrain_sub64_equal(self, a, b, expected):
        """Constrain expected == a-b, fusing difference bits into equality."""
        borrow = 0
        for i in range(64):
            terms = [v for v in (a[i], b[i], borrow, expected[i]) if v]
            self.xors.append((terms, False))
            if i < 63:
                borrow = self.and_lits(-a[i], b[i]) if i == 0 else self.majority_lits(-a[i], b[i], borrow)

    def constrain_output(self, a, b, y):
        """Enforce y=ROTL(a+b,17)+a by inverting the observed output."""
        u = self.rotated(self.sub_const64(y, a), -17)
        self.constrain_sub64_equal(u, a, b)

    def build_first_pair(self, y0, y1, seed=None, include_middle=False):
        a0 = self.word(None if seed is None else seed[0])
        t0 = self.get_t_from_output(a0, y0)
        state1 = self.step_from_t(a0, t0)
        self.constrain_output(*state1, y1)
        middle = None
        if include_middle:
            state2 = self.step(*state1)
            state3 = self.step(*state2)
            middle = (self.output(*state2), self.output(*state3))
        return (a0, t0), middle

    def validate_witness(self):
        assert len(self.witness) == self.count
        for clause in self.clauses:
            assert any(self.lit_value(lit) for lit in clause), clause
        for terms, rhs in self.xors:
            assert (sum(self.witness[v] for v in terms) % 2) == int(rhs), (terms, rhs)


def bits_to_int_witness(bits, witness):
    return sum(int(witness[v]) << i for i, v in enumerate(bits))


def bits_to_int_model(bits, variables, model):
    return sum(
        (1 << i) for i, v in enumerate(bits)
        if is_true(model.eval(variables[v - 1], model_completion=True))
    )


def _xor_expr(terms):
    if not terms:
        return BoolVal(False)
    expr = terms[0]
    for term in terms[1:]:
        expr = Xor(expr, term)
    return expr


def make_solver(circuit, timeout_seconds):
    variables = [Bool(f"v{i}") for i in range(1, circuit.count + 1)]
    solver = Solver()
    solver.set(timeout=max(1, int(timeout_seconds * 1000)))
    solver.set(random_seed=0)
    for clause in circuit.clauses:
        literals = [
            variables[abs(lit) - 1] if lit > 0 else Not(variables[abs(lit) - 1])
            for lit in clause
        ]
        solver.add(Or(*literals))
    for terms, rhs in circuit.xors:
        solver.add(_xor_expr([variables[v - 1] for v in terms]) == BoolVal(rhs))
    return solver, variables


def block_middle_clause(middle_bits, middle_values, variables):
    literals = []
    for word_bits, word_value in zip(middle_bits, middle_values):
        for bit_index, variable_id in enumerate(word_bits):
            var = variables[variable_id - 1]
            bit_is_one = bool((word_value >> bit_index) & 1)
            literals.append(Not(var) if bit_is_one else var)
    return Or(*literals)


def self_test():
    outputs = stream(SEED)
    circuit = BorrowCircuit()
    state_bits, middle_bits = circuit.build_first_pair(outputs[0], outputs[1], seed=SEED, include_middle=True)
    circuit.validate_witness()
    a0, t0 = (bits_to_int_witness(bits, circuit.witness) for bits in state_bits)
    recovered = (a0, (a0 ^ t0) & MASK)
    assert recovered == SEED
    assert stream(recovered) == outputs
    assert [bits_to_int_witness(bits, circuit.witness) for bits in middle_bits] == outputs[2:4]
    print(json.dumps({
        "self_test": "PASS",
        "source_core_variables": 566,
        "source_core_cnf": 1119,
        "source_core_xors": 317,
        "synthetic_core_variables": 567,
        "synthetic_core_cnf": 1122,
        "synthetic_core_xors": 317,
        "full_middle_variables": circuit.count,
        "full_middle_cnf": len(circuit.clauses),
        "full_middle_xors": len(circuit.xors),
    }, sort_keys=True), flush=True)


def _remaining(deadline, per_check):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return 0.0
    return min(float(per_check), remaining)


def solve_first_pair(first, holdout, ack2_payload, view, timeout_seconds, check_candidate=True,
                     expected_middle=None, max_middle_models=MAX_MIDDLE_MODELS):
    started = time.monotonic()
    deadline = started + MAX_TOTAL_SOLVE_SECONDS
    core = BorrowCircuit()
    state_bits, _ = core.build_first_pair(first[0], first[1], include_middle=False)
    first_timeout = _remaining(deadline, timeout_seconds)
    result = {
        "experiment": "z3_boolean_xor_direct_borrow_first_pair_only",
        "view": view,
        "fit_scope": "18:01 REQUESTED outputs 0/1 only",
        "holdout_scope": "18:03 REQUESTED outputs 4/5; first unconditioned model only",
        "withheld_from_fit": "18:02 ACK payload",
        "source_sha256": SOURCE_SHA,
        "timeout_seconds": timeout_seconds,
        "middle_model_cap": max_middle_models,
        "total_solver_budget_seconds": MAX_TOTAL_SOLVE_SECONDS,
        "holdout_selection_policy": "first unconditioned model only; never used to select candidates",
        "commitment_selection_policy": "hash every complete masked middle candidate before any holdout or uniqueness disposition",
        "component_commitment_status": "NOT_EVALUATED",
        "component_candidate_models_hashed": 0,
        "core_variables": core.count,
        "core_cnf_clauses": len(core.clauses),
        "core_xor_clauses": len(core.xors),
    }
    if first_timeout <= 0:
        result.update({
            "status": "UNKNOWN",
            "reason_unknown": "overall solver time budget exhausted before first solve",
            "coupon_status": "WITHHELD_SOLVE_UNKNOWN",
            "K04_original_PASS": None,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        })
        return result

    solver, variables = make_solver(core, first_timeout)
    check = solver.check()
    if check != sat:
        result["status"] = str(check).upper()
        if check == unknown:
            result["reason_unknown"] = solver.reason_unknown()
        result.update({
            "coupon_status": "WITHHELD_SOLVE_" + str(check).upper(),
            "K04_original_PASS": None,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        })
        return result

    first_model = solver.model()
    a0, t0 = (bits_to_int_model(bits, variables, first_model) for bits in state_bits)
    first_state = (a0, (a0 ^ t0) & MASK)
    first_replay = stream(first_state)
    assert first_replay[:2] == list(first)
    first_middle = tuple(first_replay[2:4])
    first_holdout = tuple(first_replay[4:6])

    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text()) if check_candidate else None
    mask = bytes.fromhex(routing["K04"]["masked_component"]) if check_candidate else None
    acceptance = json.loads((ROOT / "acceptance.json").read_text()) if check_candidate else None
    target_sha = acceptance["slot_sha256"]["K04"] if check_candidate else None

    def inspect_middle(middle, index):
        coupon = encode(middle, view)
        record = {
            "model_index": index,
            "middle_words": [f"{x:016X}" for x in middle],
            "predicted_coupon_hex": coupon.hex().upper(),
        }
        hit = False
        if check_candidate:
            component = bytes(x ^ y for x, y in zip(coupon, mask))
            hit = hashlib.sha256(component).hexdigest() == target_sha
            record.update({
                "predicted_component_hex": component.hex().upper(),
                "K04_original_PASS": hit,
            })
        if expected_middle is not None:
            record["middle_matches_planted_control"] = middle == tuple(expected_middle)
        return record, hit

    # Hash the first complete middle candidate before looking at the blind
    # 18:03 holdout or asking whether another middle is possible.
    first_record, first_hit = inspect_middle(first_middle, 0)
    candidate_records = [first_record]
    commitment_hit = first_hit
    planted_middle_seen = bool(first_record.get("middle_matches_planted_control", False))
    planted_middle_model_index = 0 if planted_middle_seen else None
    enumeration_status = "NOT_NEEDED"

    # Enumerate distinct middle outputs in a separate full circuit. The first
    # middle is blocked; every alternative is hashed immediately on discovery.
    uniqueness_status = None
    if max_middle_models <= 1:
        enumeration_status = "MODEL_CAP_REACHED"
        uniqueness_status = "UNKNOWN"
    else:
        full = BorrowCircuit()
        full_state_bits, middle_bits = full.build_first_pair(first[0], first[1], include_middle=True)
        full_timeout = _remaining(deadline, timeout_seconds)
        if full_timeout <= 0:
            enumeration_status = "TOTAL_BUDGET_EXHAUSTED"
            uniqueness_status = "UNKNOWN"
        else:
            full_solver, full_variables = make_solver(full, full_timeout)
            full_solver.add(block_middle_clause(middle_bits, first_middle, full_variables))
            while len(candidate_records) < max_middle_models:
                remaining = _remaining(deadline, timeout_seconds)
                if remaining <= 0:
                    enumeration_status = "TOTAL_BUDGET_EXHAUSTED"
                    uniqueness_status = "UNKNOWN"
                    break
                full_solver.set(timeout=max(1, int(remaining * 1000)))
                alternative = full_solver.check()
                if alternative == unsat:
                    enumeration_status = "EXHAUSTED"
                    uniqueness_status = "UNSAT"
                    break
                if alternative == unknown:
                    enumeration_status = "UNKNOWN"
                    uniqueness_status = "UNKNOWN"
                    result["enumeration_reason_unknown"] = full_solver.reason_unknown()
                    break
                alt_model = full_solver.model()
                alt_a0, alt_t0 = (
                    bits_to_int_model(bits, full_variables, alt_model)
                    for bits in full_state_bits
                )
                alt_state = (alt_a0, (alt_a0 ^ alt_t0) & MASK)
                alt_replay = stream(alt_state)
                assert alt_replay[:2] == list(first)
                middle = tuple(alt_replay[2:4])
                model_middle = tuple(
                    bits_to_int_model(bits, full_variables, alt_model)
                    for bits in middle_bits
                )
                assert middle == model_middle
                index = len(candidate_records)
                record, hit = inspect_middle(middle, index)
                candidate_records.append(record)
                if hit:
                    commitment_hit = True
                    result["commitment_hit_model_index"] = index
                    result["commitment_hit_candidate"] = record
                if expected_middle is not None and middle == tuple(expected_middle):
                    planted_middle_seen = True
                    planted_middle_model_index = index
                    enumeration_status = "PLANTED_MIDDLE_FOUND"
                    uniqueness_status = "SAT"
                    break
                if hit:
                    enumeration_status = "COMMITMENT_HIT"
                    uniqueness_status = "SAT"
                    break
                full_solver.add(block_middle_clause(middle_bits, middle, full_variables))
            else:
                enumeration_status = "CAP_REACHED"
                uniqueness_status = "SAT"

    # The holdout is a diagnostic for the first unconditioned model only. It
    # never selects, filters, or reorders the candidate list.
    result["status"] = "SAT"
    result["initial_state"] = [f"{x:016X}" for x in first_state]
    result["predicted_middle_words"] = [f"{x:016X}" for x in first_middle]
    result["predicted_later_words"] = [f"{x:016X}" for x in first_holdout]
    result["holdout_matches_full_18_03_packet"] = first_holdout == tuple(holdout)
    result["holdout_model_index"] = 0
    result["holdout_is_blind"] = True
    result["predicted_coupon_hex"] = first_record["predicted_coupon_hex"]
    result["predicted_middle_matches_withheld_ACK2"] = encode(first_middle, view) == ack2_payload
    result["uniqueness_status"] = uniqueness_status or "UNKNOWN"
    result["middle_unique"] = uniqueness_status == "UNSAT"
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    result["candidate_models"] = candidate_records
    result["candidate_models_examined"] = len(candidate_records)
    result["enumeration_status"] = enumeration_status
    result["planted_middle_seen"] = planted_middle_seen
    result["planted_middle_model_index"] = planted_middle_model_index

    if check_candidate:
        result["K04_original_PASS"] = commitment_hit
        result["component_commitment_status"] = "PASS" if commitment_hit else "MISS_WITHIN_EVALUATED_MODELS"
        result["component_candidate_models_hashed"] = len(candidate_records)
        if commitment_hit:
            result["coupon_status"] = "K04_COMMITMENT_HIT"
        elif enumeration_status in ("CAP_REACHED", "MODEL_CAP_REACHED"):
            result["coupon_status"] = "NO_COMMITMENT_HIT_WITHIN_MODEL_CAP"
        elif enumeration_status in ("TOTAL_BUDGET_EXHAUSTED", "UNKNOWN"):
            result["coupon_status"] = "NO_COMMITMENT_HIT_WITHIN_BUDGET"
        elif result["middle_unique"]:
            result["coupon_status"] = "NO_COMMITMENT_HIT_UNIQUE_MIDDLE"
        else:
            result["coupon_status"] = "NO_COMMITMENT_HIT"
    else:
        result["middle_matches_seed"] = planted_middle_seen
        result["coupon_status"] = (
            "SYNTHETIC_PLANTED_MIDDLE_RECOVERED"
            if planted_middle_seen else "SYNTHETIC_PLANTED_MIDDLE_NOT_FOUND"
        )
    return result


def parse_source():
    path = ROOT / "evidence/print/spool-reconstruction.log"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = {}
    for line in raw.decode("ascii").splitlines():
        if line.startswith("2026-"):
            stamp, *fields = line.split()
            rows[stamp] = dict(x.split("=", 1) for x in fields)
    assert len(rows) == 133
    trio = [rows[f"2026-10-03T18:0{minute}:00Z"] for minute in (1, 2, 3)]
    assert all(x["JOB"] == "PS-261003-0417" and x["CLASS"] == "RECOVER" for x in trio)
    assert [(x["ATTEMPT"], x["STATE"]) for x in trio] == [
        ("1", "REQUESTED"), ("2", "ACK"), ("3", "REQUESTED")
    ]
    return [bytes.fromhex(x["PAYLOAD"]) for x in trio]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--view", type=int, choices=range(4), default=0)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--max-middle-models", type=int, default=MAX_MIDDLE_MODELS)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--synthetic-only", action="store_true",
                      help="run only the unseeded first-pair positive control")
    mode.add_argument("--source-only", action="store_true",
                      help="run source solve; caller must gate on positive-control success")
    args = parser.parse_args()

    self_test()
    if not args.source_only:
        outputs = stream(SEED)
        synthetic = solve_first_pair(
            outputs[:2], outputs[4:6], b"", 0, args.timeout_seconds, False,
            expected_middle=outputs[2:4], max_middle_models=args.max_middle_models
        )
        synthetic["experiment"] = "synthetic_positive_control"
        control_pass = (
            synthetic.get("status") == "SAT"
            and synthetic.get("planted_middle_seen") is True
        )
        synthetic["control_pass"] = control_pass
        synthetic["control_gate_policy"] = (
            "unseeded SAT plus planted middle recovered within explicit model cap; "
            "first-model holdout and uniqueness are separate diagnostics"
        )
        print(json.dumps(synthetic, sort_keys=True), flush=True)

        if args.synthetic_only:
            if not control_pass:
                raise SystemExit(2)
            return
        if not control_pass:
            print(json.dumps({
                "experiment": "original_first_pair_only",
                "status": "NOT_RUN",
                "coupon_status": "WITHHELD_CONTROL_FAILED",
                "reason": "unseeded planted middle was not recovered within the explicit model cap",
            }, sort_keys=True), flush=True)
            raise SystemExit(2)

    if args.synthetic_only:
        return

    first, ack2_payload, holdout = parse_source()
    original = solve_first_pair(
        decode(first, args.view), decode(holdout, args.view), ack2_payload,
        args.view, args.timeout_seconds, True,
        max_middle_models=args.max_middle_models
    )
    original["experiment"] = "original_first_pair_only"
    original["control_gate"] = (
        "positive-control workflow dependency passed" if args.source_only
        else "unseeded planted control passed in this process"
    )
    print(json.dumps(original, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
