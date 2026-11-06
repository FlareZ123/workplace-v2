"""Bitwuzla solver for Agent1's source-exact short-forward CPython k2496 model.

The model avoids the 624th first-pass wrap entirely: it constrains A7 from
source-fixed S6/S7, then follows the exact second-pass recurrence only as far
as the next original masked state observations. Selected spool row129 remains
withheld. SAT is only a candidate until all 132 intact packets and K04 SHA pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent1"))
import k04_cpython_initarray_wrap_sft as init  # noqa: E402
import k04_cpython_k2496_shortforward_source_sft as source  # noqa: E402
import k04_cpython_k2496_shortforward_smt as short  # noqa: E402

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
    """Parse the source-only QF_BV model and enable model extraction."""
    skip = ("(set-option", "(check-sat)", "(get-value")
    cleaned = "\n".join(
        line for line in formula.splitlines()
        if not line.lstrip().startswith(skip)
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


def write_result(seed_words: int, payload: dict) -> None:
    """Atomically persist a small per-job result for Actions artifact upload."""
    target = ROOT / f"bitwuzla-result-n{seed_words}.json"
    temporary = None
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=ROOT, prefix=target.name + ".",
        suffix=".tmp", delete=False
    ) as stream:
        temporary = stream.name
        json.dump(payload, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, target)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("seed_words", type=int, choices=(2, 3, 4))
    ap.add_argument("--timeout-seconds", type=int, default=900)
    args = ap.parse_args()
    n = args.seed_words
    stop = short.PRESETS[n]

    masks = source.original_source()
    short.seeded_controls(masks)
    assert masks[6] == (base.U, 0xE403BB7D)
    assert masks[7] == (base.U, 0x1F7B301F)
    observed_bits = 32 + sum(mask.bit_count() for mask, _ in masks[8:stop + 1])
    assert observed_bits == {2: 70, 3: 98, 4: 135}[n]
    print(
        "ORIGINAL_SOURCE_SHORT_FORWARD",
        "seed_words", n,
        "stop", stop,
        "source_constrained_bits", observed_bits,
        "key_bits", n * 32,
        "selected_row", "WITHHELD",
        "solver", "Bitwuzla 0.9.1 / CaDiCaL",
        flush=True,
    )

    planted = [
        (0x12345678 + j * 0x30158DA + 7 * 0x4F89D7) & init.U
        for j in range(n)
    ]
    _, _, planted_state = init.direct_initialized(planted)
    synthetic_masks = [
        (mask, planted_state[index] & mask)
        for index, (mask, _) in enumerate(masks)
    ]
    positive_formula = short.model_source(
        n, stop, synthetic_masks, planted_state[6], planted_state[7],
        frozen_keys=planted, timeout_ms=60000
    )
    positive, positive_keys, positive_elapsed, positive_timeout = solve(
        positive_formula, n, 120
    )
    assert (
        positive == "SAT"
        and positive_keys == planted
        and not positive_timeout
    ), (positive, positive_keys, positive_elapsed, positive_timeout)
    print(
        "SYNTHETIC_GENUINE_CPYTHON_SHORT_FORWARD_PASS",
        n,
        "elapsed_seconds", positive_elapsed,
        flush=True,
    )

    original_formula = short.model_source(
        n, stop, masks, masks[6][1], masks[7][1],
        timeout_ms=args.timeout_seconds * 1000
    )
    record = {
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "workflow_job": os.environ.get("GITHUB_JOB"),
        "seed_words": n,
        "stop": stop,
        "source_constrained_bits": observed_bits,
        "key_bits": n * 32,
        "selected_row_129_withheld": True,
        "solver": "Bitwuzla 0.9.1 / CaDiCaL",
        "source_model_sha256": hashlib.sha256(original_formula.encode()).hexdigest(),
        "synthetic_control": "PASS",
        "status": "RUNNING",
    }
    write_result(n, record)
    result, keys, elapsed, timed_out = solve(
        original_formula, n, args.timeout_seconds
    )
    record.update({
        "status": result,
        "elapsed_seconds": elapsed,
        "terminator_fired": timed_out,
    })
    print(
        "ORIGINAL_SOURCE_BITWUZLA_SHORT_FORWARD",
        "seed_words", n,
        "verdict", result,
        "elapsed_seconds", elapsed,
        "terminator_fired", timed_out,
        flush=True,
    )
    if result == "UNSAT":
        record["interpretation"] = "conditional CPython short-forward model excluded"
        write_result(n, record)
        print(
            "ORIGINAL_SOURCE_N", n,
            "UNSAT under the source-exact short-forward CPython model",
            flush=True,
        )
        return
    if result == "UNKNOWN":
        record["interpretation"] = "inconclusive; no exclusion"
        write_result(n, record)
        print("ORIGINAL_SOURCE_N", n, "UNKNOWN; no exclusion", flush=True)
        return

    assert keys is not None
    generated = base.seeded_packets(keys)
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == base.SHA
    import re
    packets = [
        bytes.fromhex(value.decode("ascii"))
        for value in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    ]
    assert len(packets) == 133
    intact_matches = sum(
        generated[index] == packets[index]
        for index in range(len(packets))
        if index != 129
    )
    coupon = generated[129]
    component = bytes(left ^ right for left, right in zip(coupon, base.MASK))
    digest = hashlib.sha256(component).hexdigest()
    target_match = digest == base.K04_SHA
    record.update({
        "seed_words_hex": [f"{value:08X}" for value in keys],
        "intact_packet_matches": intact_matches,
        "predicted_selected_coupon": coupon.hex().upper(),
        "derived_component": component.hex().upper(),
        "derived_sha256": digest,
        "K04_SHA_MATCH": target_match,
        "candidate_accepted": intact_matches == 132 and target_match,
    })
    if intact_matches == 132 and target_match:
        record["interpretation"] = "complete K04 candidate"
    elif intact_matches < 132:
        record["interpretation"] = "necessary projection only; no original-source model"
    else:
        record["interpretation"] = "full packet fit but K04 commitment mismatch"
    write_result(n, record)
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
