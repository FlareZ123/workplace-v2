#!/usr/bin/env python3
"""K04 xoroshiro128++ direct-borrow native-XOR first-pair inversion SFT.

The unseeded synthetic positive must recover a hidden state before any source
view is admitted by the control-gated CI workflow. The physical ACK2 is never
used to constrain the state. This is a speculative producer hypothesis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent36"))
from k04_dual_inverse_borrow_reference import BorrowCircuit, SEED, stream
from k04_xoroshiropp_xorcnf_sft import ROOT, SOURCE_SHA, decode, encode, parse_source

MASK64 = (1 << 64) - 1


def solve_pair(first: list[int], view: int, limit_seconds: int) -> dict:
    from pycryptosat import Solver

    circuit = BorrowCircuit()
    (a0_bits, t0_bits), unused_middle = circuit.build_first_pair(
        first[0], first[1], seed=None, include_middle=False
    )
    assert unused_middle is None
    expected = (567, 1122, 317) if view == -1 else (566, 1119, 317)
    counts = (circuit.count, len(circuit.clauses), len(circuit.xors))
    assert counts == expected, (counts, expected)

    solver = Solver(threads=1, time_limit=float(limit_seconds))
    for terms, rhs in circuit.xors:
        solver.add_xor_clause(terms, rhs)
    for clause in circuit.clauses:
        solver.add_clause(clause)
    start = time.monotonic()
    sat, model = solver.solve()
    elapsed = round(time.monotonic() - start, 3)
    result = dict(
        encoding="t0_direct_borrow_xor_native", view=view, counts=list(counts),
        planted_seed_withheld=True, fit_scope="outputs0,1",
        first_status="SAT" if sat is True else "UNSAT" if sat is False else "UNKNOWN",
        first_solve_seconds=elapsed, source_sha256=SOURCE_SHA,
        component_commitment_status="NOT_EVALUATED",
    )
    if sat is not True:
        return result

    a0 = sum(int(model[var]) << i for i, var in enumerate(a0_bits))
    t0 = sum(int(model[var]) << i for i, var in enumerate(t0_bits))
    reconstructed = (a0, (a0 ^ t0) & MASK64)
    emitted = stream(reconstructed, 6)
    assert emitted[:2] == first
    result.update(
        initial_state=[f"{w:016X}" for w in reconstructed],
        middle_words=[f"{w:016X}" for w in emitted[2:4]],
        later_words=[f"{w:016X}" for w in emitted[4:6]],
    )
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    select = ap.add_mutually_exclusive_group(required=True)
    select.add_argument("--synthetic", action="store_true")
    select.add_argument("--source-view", type=int, choices=range(4))
    ap.add_argument("--limit-seconds", type=int, default=180)
    args = ap.parse_args()
    assert 1 <= args.limit_seconds <= 300

    outputs = stream(SEED, 6)
    checked = BorrowCircuit()
    checked.build_first_pair(outputs[0], outputs[1], seed=SEED, include_middle=False)
    checked.validate_witness()
    assert (checked.count, len(checked.clauses), len(checked.xors)) == (567, 1122, 317)

    if args.synthetic:
        result = solve_pair(outputs[:2], -1, args.limit_seconds)
        result["experiment"] = "unseeded_planted_middle_positive"
        if result["first_status"] == "SAT":
            result["planted_complete_middle_recovered"] = (
                result["middle_words"] == [f"{x:016X}" for x in outputs[2:4]]
            )
            result["blind_later_pair_matches"] = (
                result["later_words"] == [f"{x:016X}" for x in outputs[4:6]]
            )
        print(json.dumps(result, sort_keys=True), flush=True)
        assert result["first_status"] == "SAT", "unseeded planted inversion did not converge"
        assert result["planted_complete_middle_recovered"], "planted coupon not reconstructed"
        assert result["blind_later_pair_matches"], "planted holdout failed"
        return

    view = args.source_view
    assert view is not None
    rows = parse_source()  # requires exact original 18:01/18:02/18:03 records
    first, third = decode(rows[0], view), decode(rows[2], view)
    result = solve_pair(first, view, args.limit_seconds)
    result["experiment"] = "original_first_pair_source"
    result["selected_ACK2_withheld_from_fit"] = True
    if result["first_status"] == "SAT":
        coupon = encode([int(w, 16) for w in result["middle_words"]], view)
        route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
        acceptance = json.loads((ROOT / "acceptance.json").read_text())
        mask = bytes.fromhex(route["K04"]["masked_component"])
        component = bytes(x ^ y for x, y in zip(coupon, mask))
        hit = hashlib.sha256(component).hexdigest().lower() == acceptance["slot_sha256"]["K04"].lower()
        result["candidate_complete_coupon"] = coupon.hex().upper()
        result["candidate_complete_component"] = component.hex().upper()
        result["component_commitment_status"] = "PASS" if hit else "MISS_ONE_MODEL"
        result["holdout_match"] = [int(w, 16) for w in result["later_words"]] == third
        result["ACK2_buffer_match"] = coupon == rows[1]
        result["middle_uniqueness"] = "NOT_EVALUATED"
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
