"""Exact source-only GF(2) K04 observability gates for early native MT words.

Run from workplace-v2 checkout: python agents/agent15/k04_early_native_observability_sft.py
The selected original printer ACK2, K04 mask, acceptance and verifier are not
used as reconstruction constraints. All oracle records are hypothetical.
"""
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, get, source

printer, states = source(ROOT / "resources")
assert printer.rank == 15365
selected = [v for stage in range(951, 955) for v in get(states, stage)]


def residual_rank(basis):
    residual = {}
    for expression in selected:
        v = expression
        while v:
            pivot = v.bit_length() - 1
            if pivot in basis.rows:
                v ^= basis.rows[pivot][0]
            elif pivot in residual:
                v ^= residual[pivot]
            else:
                residual[pivot] = v
                break
    return len(residual)


def hypothetical_window(start, end):
    """Add *symbolic* 32-bit oracle directions without asserting unseen values."""
    basis = Basis()
    basis.rows = printer.rows.copy()
    basis.rank = printer.rank
    for stage in range(start, end + 1):
        assert not 951 <= stage <= 954
        for expression in get(states, stage):
            v = expression
            while v:
                pivot = v.bit_length() - 1
                if pivot not in basis.rows:
                    basis.rows[pivot] = (v, 0)  # RHS deliberately unknown
                    basis.rank += 1
                    break
                v ^= basis.rows[pivot][0]
    return {"window": [start, end], "new_rank": basis.rank - printer.rank,
            "remaining_k04_bits": residual_rank(basis)}


assert residual_rank(printer) == 128
windows = [
    (-1100, -880),
    (-861, -857),
    (-1100, -857),
    (-810, -700),
    (-810, -600),
    (-810, -500),
    (-810, -400),
    (-810, -339),
    (-900, -500),
    (-692, -400),
]
results = [hypothetical_window(a, b) for a, b in windows]
expected = [128, 128, 2, 128, 128, 127, 0, 0, 0, 1]
assert [x["remaining_k04_bits"] for x in results] == expected, results
assert all(item["new_rank"] <= 19968 - printer.rank for item in results)
print(json.dumps({"model": "conditional-p951-mt19937",
                  "printer_source_rank": printer.rank,
                  "selected_k04_original_unknown_bits": 128,
                  "hypothetical_full_word_oracles": results,
                  "authenticated_new_k04_bits": 0}, indent=2))
