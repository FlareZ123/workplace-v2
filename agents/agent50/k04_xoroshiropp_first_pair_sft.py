"""Blind first-pair inversion for the H17 PS-0417 xoroshiro128++ hypothesis.

Only the 18:01 REQUESTED packet is used to recover the initial state.
The 18:02 ACK is withheld entirely from fitting; outputs 2/3 are the
predicted middle coupon. The 18:03 REQUESTED packet is a complete held-out
prediction. Requires pycryptosat for solving.
"""
import argparse
import hashlib
import json
import time

from k04_xoroshiropp_meet_sft import MeetCircuit
from k04_xoroshiropp_xorcnf_sft import (
    ROOT, SOURCE_SHA, SEED, bits_to_int, decode, encode, parse_source, stream,
)


def build_first_pair(circuit, observed, seed=None):
    assert len(observed) == 2 and all(x is not None for x in observed)
    a0 = circuit.word(None if seed is None else seed[0])
    b0 = circuit.get_state_from_output(a0, observed[0])
    initial = (a0, b0)
    state1 = circuit.step(*initial)
    circuit.constrain(circuit.output(*state1), observed[1])
    state2 = circuit.step(*state1)
    state3 = circuit.step(*state2)
    middle = [circuit.output(*state2), circuit.output(*state3)]
    return initial, middle


def self_test():
    outputs = stream(SEED)
    circuit = MeetCircuit()
    initial, middle = build_first_pair(circuit, outputs[:2], seed=SEED)
    circuit.validate_witness()
    recovered_state = tuple(bits_to_int(word, circuit.witness) for word in initial)
    recovered_middle = [bits_to_int(word, circuit.witness) for word in middle]
    assert recovered_state == SEED
    assert recovered_middle == outputs[2:4]
    print(json.dumps({
        "self_test": "PASS",
        "variables": circuit.count,
        "cnf_clauses": len(circuit.clauses),
        "xor_clauses": len(circuit.xors),
        "first_pair": [f"{x:016X}" for x in outputs[:2]],
        "middle": [f"{x:016X}" for x in recovered_middle],
    }), flush=True)


def solve_first_pair(first, holdout, ack2_payload, view, limit_seconds, check_candidate=True):
    from pycryptosat import Solver

    circuit = MeetCircuit()
    initial, middle = build_first_pair(circuit, first)
    solver = Solver(time_limit=float(limit_seconds), threads=1)
    circuit.emit_to(solver)
    start = time.monotonic()
    sat, assignment = solver.solve()
    result = {
        "status": "SAT" if sat is True else "UNSAT" if sat is False else "UNKNOWN",
        "solve_seconds": round(time.monotonic() - start, 3),
        "variables": circuit.count,
        "cnf_clauses": len(circuit.clauses),
        "xor_clauses": len(circuit.xors),
        "view": view,
        "source_sha256": SOURCE_SHA,
        "fit_scope": "18:01 REQUESTED outputs 0/1 only",
        "holdout_scope": "18:03 REQUESTED outputs 4/5 only",
        "withheld_from_fit": "18:02 ACK payload",
    }
    if sat is not True:
        result["coupon_status"] = "WITHHELD_SOLVE_" + result["status"]
        return result

    state = tuple(bits_to_int(word, assignment) for word in initial)
    replay = stream(state)
    assert replay[:2] == first
    result["initial_state"] = [f"{w:016X}" for w in state]
    result["predicted_middle_words"] = [f"{w:016X}" for w in replay[2:4]]
    result["predicted_later_words"] = [f"{w:016X}" for w in replay[4:6]]
    result["holdout_matches_full_18_03_packet"] = replay[4:6] == holdout

    # Exclude the complete 128-bit middle output. If another satisfying
    # assignment exists, the target packet is not uniquely determined.
    blocked = middle[0] + middle[1]
    solver.add_clause([-v if assignment[v] else v for v in blocked])
    alt_start = time.monotonic()
    alternative, _ = solver.solve()
    result["uniqueness_seconds"] = round(time.monotonic() - alt_start, 3)
    result["middle_unique"] = (
        True if alternative is False else
        False if alternative is True else None
    )

    if result["middle_unique"] is not True:
        result["coupon_status"] = (
            "WITHHELD_NONUNIQUE" if result["middle_unique"] is False
            else "WITHHELD_UNIQUENESS_UNKNOWN"
        )
        return result

    # Only now construct the complete 16-byte coupon from the unique middle.
    coupon = encode(replay[2:4], view)
    result["predicted_coupon_hex"] = coupon.hex().upper()
    result["predicted_middle_matches_withheld_ACK2"] = coupon == ack2_payload
    if not check_candidate:
        result["coupon_status"] = "SYNTHETIC_UNIQUE_MIDDLE_HOLDOUT_PASS" if result["holdout_matches_full_18_03_packet"] else "SYNTHETIC_HOLDOUT_FAIL"
        return result
    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    component = bytes(x ^ y for x, y in zip(coupon, mask))
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    hit = hashlib.sha256(component).hexdigest() == acceptance["slot_sha256"]["K04"]
    result.update({
        "predicted_component_hex": component.hex().upper() if hit else None,
        "K04_original_PASS": hit,
        "coupon_status": "UNIQUE_MIDDLE_HASH_PASS" if hit else "UNIQUE_MIDDLE_HASH_MISS",
    })
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--view", type=int, choices=range(4), default=0)
    parser.add_argument("--limit-seconds", type=float, default=180)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--control-only", action="store_true")
    args = parser.parse_args()

    self_test()
    if args.self_test:
        return

    if args.control_only:
        outputs = stream(SEED)
        result = solve_first_pair(outputs[:2], outputs[4:6], b"", 0, args.limit_seconds, check_candidate=False)
        assert result["status"] == "SAT"
        assert result["middle_unique"] is True
        assert result["holdout_matches_full_18_03_packet"] is True
        assert result["predicted_middle_words"] == [f"{x:016X}" for x in outputs[2:4]]
        print(json.dumps({"experiment": "synthetic_first_pair_positive", **result}, sort_keys=True), flush=True)
        return

    rows = parse_source()
    first = decode(rows[0], args.view)
    holdout = decode(rows[2], args.view)
    result = solve_first_pair(first, holdout, rows[1], args.view, args.limit_seconds)
    print(json.dumps({"experiment": "original_first_pair_only", **result}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
