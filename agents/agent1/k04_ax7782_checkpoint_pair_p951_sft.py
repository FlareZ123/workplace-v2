#!/usr/bin/env python3
"""Bounded AX-7782 halfword interleave donors for the conditional p951 K04 model.

Tests two source-motivated arrangements of the two 16-bit attempts per chunk:
pair attempts within each chunk, and use the already-derived P212 selector
plus its complement. It deliberately excludes separate per-attempt 16-byte
vectors and K02/K07 donor pairings because those are covered by prior SFTs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agents.agent49.k04_p951_symbolic_basis import (  # noqa: E402
    STARTS, Basis, get, packets, source, untemper,
)

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TRANSFER_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
DONOR_STAGES = [328, 329, 330, 331, 724, 725, 726, 727]
GAP_A = [328, 329, 330, 331]
GAP_B = [724, 725, 726, 727]


def temper_int(value: int) -> int:
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    value ^= value >> 18
    return value & 0xFFFFFFFF


def clone_basis(base: Basis) -> Basis:
    out = Basis()
    out.rows = base.rows.copy()
    out.rank = base.rank
    return out


def evaluate(forms: list[int], assignment: int) -> int:
    return sum((((form & assignment).bit_count() & 1) << bit)
               for bit, form in enumerate(forms))


def zero_free_assignment(base: Basis) -> int:
    """Solve the echelon system with every nonpivot variable set to zero."""
    assignment = 0
    for pivot in sorted(base.rows):
        form, rhs = base.rows[pivot]
        remainder = form ^ (1 << pivot)
        value = rhs ^ ((remainder & assignment).bit_count() & 1)
        if value:
            assignment |= 1 << pivot
    assert all(((form & assignment).bit_count() & 1) == rhs
               for form, rhs in base.rows.values())
    return assignment


def recover(base: Basis, state_forms: list[list[int]], words: list[int],
            stages: list[int], interpretation: str, mask: bytes,
            expected_k04_sha: str) -> dict:
    assert len(words) == len(stages) == 8
    basis = clone_basis(base)
    for stage, observed in zip(stages, words):
        native = observed if interpretation == "native" else untemper(observed)
        for bit, form in enumerate(get(state_forms, stage)):
            basis.insert(form, (native >> bit) & 1)

    target_native = []
    for stage in range(951, 955):
        value = 0
        for bit, form in enumerate(get(state_forms, stage)):
            predicted = basis.predict(form)
            if predicted is None:
                raise AssertionError("eight donors did not determine the target")
            value |= predicted << bit
        target_native.append(value)

    coupon = b"".join(temper_int(value).to_bytes(4, "little")
                      for value in target_native)
    component = bytes(a ^ b for a, b in zip(coupon, mask))
    digest = hashlib.sha256(component).hexdigest()
    return {
        "rank": basis.rank,
        "coupon_hex": coupon.hex().upper(),
        "component_hex": component.hex().upper(),
        "component_sha256": digest,
        "K04_PASS": digest == expected_k04_sha,
    }


def checkpoint_rows(root: Path) -> dict[int, dict[int, str]]:
    path = root / "resources/evidence/transfers/transfer-audit.jsonl"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TRANSFER_SHA
    rows: dict[int, dict[int, str]] = {}
    for line in raw.decode("utf-8").splitlines():
        record = json.loads(line)
        if record.get("transfer") == "AX-7782" and record.get("kind") == "CHUNK":
            seq = int(record["seq"])
            attempt = int(record["attempt"])
            assert attempt in (1, 2)
            rows.setdefault(seq, {})[attempt] = record["checkpoint"]
    assert sorted(rows) == list(range(8))
    assert all(set(rows[seq]) == {1, 2} for seq in range(8))
    return rows


def halfword_bytes(hex_value: str, endian: str) -> bytes:
    return int(hex_value, 16).to_bytes(2, endian)


def words_from_seq_attempt_pairs(rows: dict[int, dict[int, str]],
                                 pair_order: str, half_endian: str,
                                 word_endian: str) -> list[int]:
    words = []
    for seq in range(8):
        pair = ([1, 2] if pair_order == "a1a2" else [2, 1])
        raw = b"".join(halfword_bytes(rows[seq][attempt], half_endian)
                       for attempt in pair)
        words.append(int.from_bytes(raw, word_endian))
    return words


def words_from_p212_pairs(rows: dict[int, dict[int, str]],
                           selected_first: bool, half_endian: str,
                           word_endian: str) -> list[int]:
    words = []
    for seq in range(8):
        selected = rows[seq][1 if seq % 2 == 0 else 2]
        complement = rows[seq][2 if seq % 2 == 0 else 1]
        pair = ([selected, complement] if selected_first
                else [complement, selected])
        raw = b"".join(halfword_bytes(value, half_endian) for value in pair)
        words.append(int.from_bytes(raw, word_endian))
    return words


def words_from_p212_complement(rows: dict[int, dict[int, str]],
                               half_endian: str,
                               word_endian: str) -> dict[str, list[int]]:
    # P212 selector: attempt 1 on even seq, attempt 2 on odd.
    p212 = [rows[seq][1 if seq % 2 == 0 else 2] for seq in range(8)]
    complement = [rows[seq][2 if seq % 2 == 0 else 1] for seq in range(8)]
    out = {}
    for label, values in (("p212", p212), ("complement", complement)):
        raw = b"".join(halfword_bytes(value, half_endian) for value in values)
        out[label] = [
            int.from_bytes(raw[offset:offset + 4], word_endian)
            for offset in range(0, 16, 4)
        ]
    return out


def synthetic_positive(base: Basis, state_forms: list[list[int]],
                       source_packets: list[bytes], selected_index: int) -> dict:
    assignment = zero_free_assignment(base)
    for row, (payload, start) in enumerate(zip(source_packets, STARTS)):
        if row == selected_index:
            assert payload == b""
            continue
        predicted = b"".join(
            temper_int(evaluate(get(state_forms, start + lane), assignment))
            .to_bytes(4, "little")
            for lane in range(4)
        )
        assert predicted == payload, ("synthetic source replay", row)

    donors = [evaluate(get(state_forms, stage), assignment)
              for stage in DONOR_STAGES]
    augmented = clone_basis(base)
    for stage, value in zip(DONOR_STAGES, donors):
        for bit, form in enumerate(get(state_forms, stage)):
            augmented.insert(form, (value >> bit) & 1)

    recovered = []
    expected = []
    for stage in range(951, 955):
        value = 0
        for bit, form in enumerate(get(state_forms, stage)):
            predicted = augmented.predict(form)
            assert predicted is not None
            value |= predicted << bit
        recovered.append(value)
        expected.append(evaluate(get(state_forms, stage), assignment))
    assert recovered == expected
    return {
        "status": "PASS",
        "intact_packets_replayed": 132,
        "base_rank": base.rank,
        "augmented_rank": augmented.rank,
        "synthetic_coupon_hex": b"".join(
            temper_int(value).to_bytes(4, "little") for value in recovered
        ).hex().upper(),
    }


def main() -> None:
    root = ROOT
    spool = root / "resources/evidence/print/spool-reconstruction.log"
    route_path = root / "resources/evidence/recovery-routing.json"
    acceptance_path = root / "resources/acceptance.json"
    assert hashlib.sha256(spool.read_bytes()).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(route_path.read_bytes()).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(acceptance_path.read_bytes()).hexdigest() == ACCEPTANCE_SHA

    route = json.loads(route_path.read_text())
    acceptance = json.loads(acceptance_path.read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    expected_k04_sha = acceptance["slot_sha256"]["K04"]
    rows = checkpoint_rows(root)

    # Official attempt-2 chain positive source-parsing control for K07.
    k07_preimage = bytes.fromhex("".join(rows[seq][2] for seq in range(8)))
    k07_component = hashlib.sha256(k07_preimage).digest()[:16]
    assert hashlib.sha256(k07_component).hexdigest() == acceptance["slot_sha256"]["K07"]
    assert k07_preimage.hex().upper() == "8947CEDCB9CC73BAB7E87BE63302C5C9"

    base, state_forms = source(root)
    source_packets, selected_index = packets(root)
    assert selected_index == 129 and STARTS[selected_index] == 951
    assert base.rank == 15365

    results = []
    # Model A: pair the two attempts within each chunk, producing 8 words.
    for pair_order in ("a1a2", "a2a1"):
        for half_endian in ("big", "little"):
            for word_endian in ("big", "little"):
                words = words_from_seq_attempt_pairs(
                    rows, pair_order, half_endian, word_endian
                )
                for gap_order, stages in (
                    ("seq0-3_to_gap43", DONOR_STAGES),
                    ("seq0-3_to_gap96", GAP_B + GAP_A),
                ):
                    for interpretation in ("native", "tempered"):
                        recovered = recover(
                            base, state_forms, words, stages, interpretation,
                            mask, expected_k04_sha
                        )
                        results.append({
                            "model": "within_chunk_attempt_pair",
                            "pair_order": pair_order,
                            "half_endian": half_endian,
                            "word_endian": word_endian,
                            "gap_order": gap_order,
                            "interpretation": interpretation,
                            **recovered,
                        })

    # Model B: P212 parity selector plus its complement as two gap vectors.
    for half_endian in ("big", "little"):
        for word_endian in ("big", "little"):
            vectors = words_from_p212_complement(rows, half_endian, word_endian)
            for gap_order, first, second in (
                ("p212_gap43", "p212", "complement"),
                ("p212_gap96", "complement", "p212"),
            ):
                stages_words = list(zip(GAP_A, vectors[first])) + list(zip(GAP_B, vectors[second]))
                stages = [item[0] for item in stages_words]
                words = [item[1] for item in stages_words]
                for interpretation in ("native", "tempered"):
                    recovered = recover(
                        base, state_forms, words, stages, interpretation,
                        mask, expected_k04_sha
                    )
                    results.append({
                        "model": "p212_and_complement_vectors",
                        "half_endian": half_endian,
                        "word_endian": word_endian,
                        "gap_order": gap_order,
                        "interpretation": interpretation,
                        **recovered,
                    })

    # Model C: interleave the P212-selected halfword and its complement
    # within each chunk, preserving the selector's alternating attempt order.
    for selected_first in (True, False):
        for half_endian in ("big", "little"):
            for word_endian in ("big", "little"):
                words = words_from_p212_pairs(
                    rows, selected_first, half_endian, word_endian
                )
                for gap_order, stages in (
                    ("seq0-3_to_gap43", DONOR_STAGES),
                    ("seq0-3_to_gap96", GAP_B + GAP_A),
                ):
                    for interpretation in ("native", "tempered"):
                        recovered = recover(
                            base, state_forms, words, stages, interpretation,
                            mask, expected_k04_sha
                        )
                        results.append({
                            "model": "p212_within_chunk_pair",
                            "selected_first": selected_first,
                            "half_endian": half_endian,
                            "word_endian": word_endian,
                            "gap_order": gap_order,
                            "interpretation": interpretation,
                            **recovered,
                        })

    assert len(results) == 80
    assert all(result["rank"] == 15621 for result in results)
    assert not any(result["K04_PASS"] for result in results)
    unique_coupons = {result["coupon_hex"] for result in results}
    unique_components = {result["component_hex"] for result in results}
    assert len(unique_coupons) == 48
    assert len(unique_components) == 48

    positive = synthetic_positive(base, state_forms, source_packets, selected_index)
    assert positive["status"] == "PASS"

    print(json.dumps({
        "status": "BOUNDED_NEGATIVE",
        "base_rank": base.rank,
        "target_stages": [951, 952, 953, 954],
        "donor_stages": DONOR_STAGES,
        "cases": len(results),
        "unique_complete_candidates": len(unique_components),
        "original_k04_hits": 0,
        "synthetic_positive": positive,
        "results": results,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
