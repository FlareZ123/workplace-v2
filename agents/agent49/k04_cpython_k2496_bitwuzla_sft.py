"""Bitwuzla engine for the conditional CPython MT19937 k=2496 source inverse.

This is an independent solver backend for Agent37's frozen source model.
The selected printer row 129 is withheld from every constraint. A SAT result
is only a projection model until all 132 intact packets are reproduced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent37"))
import k04_cpython_k2496_shortseed_sft as base  # noqa: E402

from bitwuzla import Option, Options, Parser, TermManager  # noqa: E402


class Deadline:
    """Bitwuzla termination callback using a monotonic runtime clock."""

    def __init__(self, seconds: int) -> None:
        self.deadline = time.monotonic() + seconds
        self.expired = False

    def __call__(self) -> bool:
        self.expired = time.monotonic() >= self.deadline
        return self.expired


def make_solver(formula: str):
    """Parse the frozen QF_BV formula and enable model extraction."""
    cleaned = "\n".join(
        line for line in formula.splitlines()
        if not line.lstrip().startswith("(set-option")
    )
    manager = TermManager()
    options = Options()
    options.set(Option.PRODUCE_MODELS, True)
    options.set(Option.SAT_SOLVER, "cadical")
    parser = Parser(manager, options)
    parser.parse(cleaned, True, False)
    return manager, parser, parser.bitwuzla()


def verdict_name(result) -> str:
    value = str(result).strip().lower()
    if value in {"sat", "result.sat"}:
        return "SAT"
    if value in {"unsat", "result.unsat"}:
        return "UNSAT"
    if value in {"unknown", "result.unknown"}:
        return "UNKNOWN"
    raise RuntimeError(f"Unexpected Bitwuzla result: {result!r}")


def solve(formula: str, key_words: int, timeout_seconds: int):
    manager, parser, solver = make_solver(formula)
    deadline = Deadline(timeout_seconds)
    solver.configure_terminator(deadline)
    started = time.monotonic()
    result = verdict_name(solver.check_sat())
    elapsed = round(time.monotonic() - started, 3)
    keys = None
    if result == "SAT":
        keys = []
        for index in range(key_words):
            term = parser.parse_term(f"k{index}")
            value = str(solver.get_value(term).value(16)).lower()
            value = value.removeprefix("0x").removeprefix("#x")
            keys.append(int(value, 16))
    return result, keys, elapsed, deadline.expired


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("seed_words", type=int, choices=(2, 3, 4))
    ap.add_argument("--timeout-seconds", type=int, default=1500)
    args = ap.parse_args()
    n = args.seed_words

    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == base.SHA
    packets = [
        bytes.fromhex(value.decode("ascii"))
        for value in base.re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    ]
    assert len(packets) == len(base.mt.STARTS) == 133
    assert base.mt.STARTS[129] == 951
    masks = base.source_states(base.OFFSET, packets)
    fixed_bits = sum(mask.bit_count() for mask, _ in masks)
    assert fixed_bits == 711
    print(
        "ORIGINAL_SOURCE",
        "seed_words", n,
        "known_init_bits", fixed_bits,
        "selected_row", "WITHHELD",
        "solver", "Bitwuzla 0.9.1 / CaDiCaL",
        flush=True,
    )

    planted = [(0x12345678 + j * 0x11111111) & base.U for j in range(n)]
    synthetic_packets = base.seeded_packets(planted)
    synthetic_masks = base.source_states(base.OFFSET, synthetic_packets)
    positive_formula = base.smt(synthetic_masks, n, planted, timeout_ms=60000)
    positive, positive_keys, positive_elapsed, positive_timeout = solve(
        positive_formula, n, 120
    )
    assert positive == "SAT" and positive_keys == planted and not positive_timeout, (
        "synthetic genuine CPython seed control failed",
        positive, positive_keys, positive_elapsed, positive_timeout,
    )
    print(
        "SYNTHETIC_GENUINE_PYTHON_SEED_SOURCE_PASS",
        n,
        "elapsed_seconds", positive_elapsed,
        flush=True,
    )

    original_formula = base.smt(masks, n, timeout_ms=args.timeout_seconds * 1000)
    result, keys, elapsed, timed_out = solve(
        original_formula, n, args.timeout_seconds
    )
    print(
        "ORIGINAL_SOURCE_BITWUZLA",
        "seed_words", n,
        "verdict", result,
        "elapsed_seconds", elapsed,
        "terminator_fired", timed_out,
        "selected_row_WITHHELD",
        flush=True,
    )
    if result == "UNSAT":
        print("ORIGINAL_SOURCE_N", n, "UNSAT under frozen CPython/k2496 model", flush=True)
        return
    if result == "UNKNOWN":
        print("ORIGINAL_SOURCE_N", n, "UNKNOWN; no exclusion", flush=True)
        return

    assert keys is not None
    generated = base.seeded_packets(keys)
    intact_matches = sum(
        generated[index] == packets[index]
        for index in range(len(packets))
        if index != 129
    )
    coupon = generated[129]
    component = bytes(left ^ right for left, right in zip(coupon, base.MASK))
    digest = hashlib.sha256(component).hexdigest()
    target_match = digest == base.K04_SHA
    print(
        "SOURCE_PROJECTION_SAT",
        "seed_words", n,
        "seed_words_hex", [f"{value:08X}" for value in keys],
        "intact_packet_matches", f"{intact_matches}/132",
        "predicted_selected_coupon", coupon.hex().upper(),
        "derived_component", component.hex().upper(),
        "derived_sha256", digest,
        "K04_SHA_MATCH", target_match,
        flush=True,
    )
    if intact_matches == 132 and target_match:
        print("COMPLETE_K04_CANDIDATE", component.hex().upper(), flush=True)
    elif intact_matches < 132:
        print("NECESSARY_PROJECTION_ONLY; no original-source model", flush=True)
    else:
        print("FULL_132_PACKET_FIT_BUT_K04_COMMITMENT_MISMATCH", flush=True)


if __name__ == "__main__":
    main()
