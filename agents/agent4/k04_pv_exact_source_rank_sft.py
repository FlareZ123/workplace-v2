"""Exact source-only 53-bit PV observation constraints on speculative p951 MT state.

Uses unchanged source files and Agent4's original GF(2) printer witness.
No selected coupon, mask, acceptance hashes, or final phrase are read.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources"
MODEL = ROOT / "agents" / "agent4" / "k04_mt_full_state_gf2.py"
HIST = SOURCE / "evidence" / "telemetry" / "freeze-export.jsonl"
HIST_PIN = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"


def load_model():
    spec = importlib.util.spec_from_file_location("source_model", MODEL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.START, module.STOP = -2000, 1040
    words = module.symbolic_words()
    basis = module.Basis()
    for stage, value in module.printer_observations(SOURCE):
        basis.add_word(words[stage - module.START], value)
    assert len(basis.rows) == 15365
    assert module.target_quotient(basis, words) == 128
    return module, words, basis


def affine_output(forms: list[int], basis):
    """Project 53 source words onto independent unknown GF(2) parameters."""
    local = {}
    variables = []
    expressions = []
    for form in forms:
        value = coefficients = 0
        while form:
            pivot = form.bit_length() - 1
            if pivot in basis.rows:
                form ^= basis.rows[pivot]
                value ^= basis.values[pivot]
            elif pivot in local:
                row, symbolic_mask = local[pivot]
                form ^= row
                coefficients ^= symbolic_mask
            else:
                local[pivot] = (form, 1 << len(variables))
                variables.append(form)
                coefficients ^= 1 << (len(variables) - 1)
                form = 0
        expressions.append((value, coefficients))
    base = sum(value << bit for bit, (value, _) in enumerate(expressions))
    columns = [
        sum(((coefficients >> k) & 1) << bit
            for bit, (_, coefficients) in enumerate(expressions))
        for k in range(len(variables))
    ]
    return base, columns, variables


def observed_interval(milli: int):
    """All exact 53-bit values rounding to the observed 0.001 reading."""
    scale, den = 1 << 53, 152000
    ceil = lambda numerator, denominator: -((-numerator) // denominator)
    low = ceil((2 * milli - 24001) * scale, den)
    high = ceil((2 * milli - 23999) * scale, den) - 1
    return max(0, low), min(scale - 1, high)


def source_candidates(module, words, basis, stage: int, milli: int):
    a = module.tempered_bits(words[stage - module.START])
    b = module.tempered_bits(words[stage + 1 - module.START])
    base, columns, variables = affine_output(b[6:] + a[5:], basis)
    low, high = observed_interval(milli)
    options = []
    for parameter in range(1 << len(variables)):
        actual = base
        for index, column in enumerate(columns):
            if (parameter >> index) & 1:
                actual ^= column
        if low <= actual <= high:
            options.append(parameter)
    return len(variables), options, variables


def main():
    raw = HIST.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == HIST_PIN
    values = {
        row["seq"]: round(row["value"] * 1000)
        for row in map(json.loads, raw.splitlines())
        if row["field"] == "PV"
    }
    assert len(values) == 112 and sorted(values) == list(range(100, 212))
    model, words, basis = load_model()
    outputs = {}
    for seq, stage in ((175, -1567), (176, -1560), (177, -1553)):
        rank, valid, variables = source_candidates(
            model, words, basis, stage, values[seq]
        )
        assert valid
        outputs[seq] = (rank, valid, variables)
        print(f"PV {seq}: local output rank {rank}; compatible assignments "
              f"{len(valid)}/{1 << rank}; assignments {valid}")
    assert outputs[175][:2] == (0, [0])
    assert outputs[176][:2] == (4, list(range(8)))
    assert outputs[177][:2] == (3, list(range(8)))

    # PV176 exactly fixes one source-independent affine parameter to zero.
    assert all((entry & 8) == 0 for entry in outputs[176][1])
    extended = basis.clone()
    extended.add(outputs[176][2][3], 0)
    assert len(extended.rows) == len(basis.rows) + 1
    assert model.target_quotient(extended, words) == 128
    print("SOURCE-CONDITIONAL ORIGINAL NEW EQUATIONS 1")
    print("Source rank 15365 -> 15366; selected K04 quotient 128 -> 128")
    print("Original selected coupon bytes authenticated: 0/16")


if __name__ == "__main__":
    main()
