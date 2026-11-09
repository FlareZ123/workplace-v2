"""H-17 conditional MT19937 prehistory / later-stage complete coupon scan.

Run from the workplace-v2 repository root:
    python agents/agent10/k04_mt_prehistory_stage_extension_sft.py

Original source and checker are read-only. The selected ESC-N ACK2 payload is
excluded by the imported source selector. This model is exploratory, with no
historically authenticated selected physical coupon generation stage.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
sys.path.insert(0, str(ROOT / "agents" / "agent44"))

from k04_p951_symbolic_basis import source, ORIGIN, STARTS, MAG
from k04_p951_hidden_stage_coupon_sft import (
    source_rows,
    state_expressions,
    source_basis,
    source_fixed_words,
    coupons_for_stage,
    temper,
)

LIMIT = 8000
MASK32 = 0xFFFFFFFF


def component(coupon: bytes, mask: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(coupon, mask))


def extend_native_expressions(expressions: list[list[int]], latest: int) -> None:
    # Identical native MT19937 bit recurrence to Agent49's source generator.
    for i in range(len(expressions), latest - ORIGIN + 1):
        t = i - 624
        expressions.append([
            expressions[t + 397][bit]
            ^ (expressions[t][31] if bit == 30 else
               expressions[t + 1][bit + 1] if bit < 30 else 0)
            ^ (expressions[t + 1][0] if (MAG >> bit) & 1 else 0)
            for bit in range(32)
        ])


def project(expression: int, rows: dict[int, tuple[int, int]]) -> tuple[int, int]:
    # Fully eliminate every known pivot, continuing past unknown high pivots.
    free = constant = 0
    while expression:
        pivot = expression.bit_length() - 1
        known = rows.get(pivot)
        if known is None:
            free ^= 1 << pivot
            expression ^= 1 << pivot
        else:
            mask, rhs = known
            expression ^= mask
            constant ^= rhs
    return free, constant


def stage_coupons(expressions: list[list[int]],
                  rows: dict[int, tuple[int, int]], stage: int) -> list[bytes]:
    native = [
        [project(expression, rows) for expression in expressions[q - ORIGIN]]
        for q in range(stage, stage + 4)
    ]
    free = {variable for word in native for variable, _ in word if variable}
    if len(free) > 1:
        return []
    result = []
    for branch in range(2 if free else 1):
        values = [
            sum((rhs ^ (branch if variable else 0)) << bit
                for bit, (variable, rhs) in enumerate(word))
            for word in native
        ]
        result.append(b"".join(temper(value).to_bytes(4, "little")
                               for value in values))
    return result


def main() -> None:
    source_path = ROOT / "resources" / "evidence" / "print" / "spool-reconstruction.log"
    raw = source_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    )
    route = json.loads((ROOT / "resources" / "evidence" / "recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources" / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]

    # Reproduce the 399 historical four-consecutive-output coupon candidates
    # from Agent44's zero-prehistory model without using the selected payload.
    _, intact_rows, selected_index, _ = source_rows(raw, ROOT)
    assert selected_index == 129
    original_vectors = state_expressions(STARTS[-1] + 3)
    original_basis = source_basis(original_vectors, intact_rows)
    assert len(original_basis) == 15365
    original_fixed = source_fixed_words(original_vectors, original_basis)
    old_windows = {
        stage: list(coupons_for_stage(original_fixed, stage) or ())
        for stage in range(STARTS[-1] + 1)
    }
    old_windows = {stage: coupons for stage, coupons in old_windows.items() if coupons}
    previous = {
        component(coupon, mask)
        for coupons in old_windows.values()
        for coupon in coupons
    }
    assert len(previous) == 399

    # Agent49's independent symbolic implementation starts 1100 draws before
    # printer stage zero. Extend that phase far beyond Agent44's last stage.
    basis, vectors = source(ROOT)
    assert basis.rank == 15365
    extend_native_expressions(vectors, LIMIT + 3)
    accepted_windows = {}
    full = one_free = 0
    extended = []
    for stage in range(LIMIT + 1):
        coupons = stage_coupons(vectors, basis.rows, stage)
        if not coupons:
            continue
        accepted_windows[stage] = coupons
        full += (len(coupons) == 1)
        one_free += (len(coupons) == 2)
        extended.extend(component(coupon, mask) for coupon in coupons)

    assert (full, one_free, len(extended)) == (268, 97, 462)
    assert len(set(extended)) == 462
    assert previous.issubset(set(extended))
    new_candidates = set(extended) - previous
    assert len(new_candidates) == 63
    extra_historical = sorted(set(accepted_windows) & set(range(964)) - set(old_windows))
    assert extra_historical == [620, 621, 622, 623, 847]
    later = sorted(stage for stage in accepted_windows if stage >= 964)
    assert len(later) == 34 and later[-1] == 1948

    # A documented previously inferred unprinted four-word coupon is fixed.
    assert accepted_windows[697] == [bytes.fromhex(
        "C9304FE833674EFD67B213839E4BA01D"
    )]
    # Synthetic positive exercises the newly admitted prehistory stage847.
    planted = hashlib.sha256(accepted_windows[847][1]).digest()
    assert sum(hashlib.sha256(c).digest() == planted
               for coupons in accepted_windows.values() for c in coupons) == 1
    assert len(accepted_windows[847]) == 2

    hits = [value.hex().upper() for value in extended
            if hashlib.sha256(value).hexdigest() == target]
    print(json.dumps({
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_rank": basis.rank,
        "previous_complete_candidates": len(previous),
        "extended_complete_candidates": len(extended),
        "additional_unique_candidates": len(new_candidates),
        "full_windows": full,
        "one_free_dimension_windows": one_free,
        "new_previously_scanned_stages": extra_historical,
        "later_stages_964_to_8000": later,
        "planted_stage847_positive": True,
        "original_k04_matches": hits,
    }, indent=2))
    assert hits == [], "A genuine original K04 hit requires immediate review"


if __name__ == "__main__":
    main()
