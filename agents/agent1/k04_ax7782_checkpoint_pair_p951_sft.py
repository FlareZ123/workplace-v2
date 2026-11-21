#!/usr/bin/env python3
"""Bounded AX-7782 checkpoint-pair donors for the conditional p951 K04 model.

Tests three source-motivated ways to turn the 16 retained 16-bit checkpoint
fields (8 chunks x 2 attempts) into the eight 32-bit native-word donors that
make the selected p951 coupon observable. This is an exploratory mapping test,
not a claim that AX checkpoints historically share the printer MT producer.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agents.agent49.k04_p951_symbolic_basis import (  # noqa: E402
    STARTS, Basis, get, packets, source, untemper,
)

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TRANSFER_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
TELEMETRY_SHA = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7"
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


def k02_values(root: Path, route: dict, acceptance: dict) -> tuple[list[int], bytes]:
    path = root / "resources/evidence/telemetry/freeze-export.jsonl"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TELEMETRY_SHA
    rule = route["K02"]
    parts = [part.strip() for part in rule["source"].split("/")]
    tag, field = parts[1], parts[2]
    start = datetime.fromisoformat(rule["start_utc"]).astimezone(timezone.utc)
    end = datetime.fromisoformat(rule["end_utc_exclusive"]).astimezone(timezone.utc)
    selected: dict[int, dict] = {}
    for line in raw.decode("utf-8").splitlines():
        record = json.loads(line)
        if (record.get("tag") != tag or record.get("field") != field
                or record.get("quality") != "GOOD" or record.get("state") != "HOLD"):
            continue
        timestamp = datetime.fromisoformat(record["ts"]).astimezone(timezone.utc)
        if not start <= timestamp < end:
            continue
        seq = int(record["seq"])
        if seq not in selected or int(record["revision"]) > int(selected[seq]["revision"]):
            selected[seq] = record
    assert sorted(selected) == list(range(8))
    values = [int(selected[seq]["value"]) for seq in range(8)]
    preimage = b"".join(value.to_bytes(2, "big") for value in values)
    component = hashlib.sha256(preimage).digest()[:16]
    assert hashlib.sha256(component).hexdigest() == acceptance["slot_sha256"]["K02"]
    return values, preimage


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


def words_from_attempt_vectors(rows: dict[int, dict[int, str]],
                               half_endian: str,
                               word_endian: str) -> dict[int, list[int]]:
    out = {}
    for attempt in (1, 2):
        raw = b"".join(halfword_bytes(rows[seq][attempt], half_endian)
                       for seq in range(8))
        assert len(raw) == 16
        out[attempt] = [
            int.from_bytes(raw[offset:offset + 4], word_endian)
            for offset in range(0, 16, 4)
        ]
    return out


def words_from_p212_complement(rows: dict[int, dict[int, str]],
                               half_endian: str,
                               word_endian: str) -> dict[str, list[int]]:
    # MAIL-13/Agent22 P212 selector: attempt 1 on even seq, attempt 2 on odd.
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
    # Independently replay every intact original packet under this synthetic
    # source-consistent state. The selected row remains withheld.
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
    k02_values_list, k02_preimage = k02_values(root, route, acceptance)
    k07_values_list = [int(rows[seq][2], 16) for seq in range(8)]

    # Verify that the official attempt-2 chain reproduces K07 exactly.
    k07_preimage = bytes.fromhex("".join(rows[seq][2] for seq in range(8)))
    k07_component = hashlib.sha256(k07_preimage).digest()[:16]
    assert hashlib.sha256(k07_component).hexdigest() == acceptance["slot_sha256"]["K07"]
    assert k07_preimage.hex().upper() == (
        "8947CEDCB9CC73BAB7E87BE63302C5C9"
    )

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

    # Model B: each complete attempt is one 16-byte vector / four words.
    for half_endian in ("big", "little"):
        for word_endian in ("big", "little"):
            vectors = words_from_attempt_vectors(rows, half_endian, word_endian)
            for gap_order, first, second in (
                ("attempt1_gap43", 1, 2),
                ("attempt2_gap43", 2, 1),
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
                        "model": "separate_attempt_vectors",
                        "half_endian": half_endian,
                        "word_endian": word_endian,
                        "gap_order": gap_order,
                        "interpretation": interpretation,
                        **recovered,
                    })

    # Model C: use the already source-derived P212 parity selector and its
    # complementary stream as the two four-word gap donors.
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

    # Model D: pair the two independently accepted K02/K07 source halfwords
    # at each sequence number to form one 32-bit donor word.
    for pair_order in ("k02k07", "k07k02"):
        for half_endian in ("big", "little"):
            for word_endian in ("big", "little"):
                words = []
                for seq in range(8):
                    pair = ([k02_values_list[seq], k07_values_list[seq]]
                            if pair_order == "k02k07"
                            else [k07_values_list[seq], k02_values_list[seq]])
                    raw = b"".join(value.to_bytes(2, half_endian) for value in pair)
                    words.append(int.from_bytes(raw, word_endian))
                for gap_order, stages in (
                    ("seq_to_gap43_then_gap96", DONOR_STAGES),
                    ("seq_to_gap96_then_gap43", GAP_B + GAP_A),
                ):
                    for interpretation in ("native", "tempered"):
                        recovered = recover(
                            base, state_forms, words, stages, interpretation,
                            mask, expected_k04_sha
                        )
                        results.append({
                            "model": "K02_K07_sequence_pairs",
                            "pair_order": pair_order,
                            "half_endian": half_endian,
                            "word_endian": word_endian,
                            "gap_order": gap_order,
                            "interpretation": interpretation,
                            **recovered,
                        })

    # Model E: each accepted 16-byte K02/K07 preimage is four 32-bit words;
    # place the two source vectors into the two four-word gaps.
    for half_endian in ("big", "little"):
        for word_endian in ("big", "little"):
            k02_raw = b"".join(value.to_bytes(2, half_endian) for value in k02_values_list)
            k07_raw = b"".join(value.to_bytes(2, half_endian) for value in k07_values_list)
            vectors = {
                "k02": [int.from_bytes(k02_raw[i:i + 4], word_endian) for i in range(0, 16, 4)],
                "k07": [int.from_bytes(k07_raw[i:i + 4], word_endian) for i in range(0, 16, 4)],
            }
            for gap_order, first, second in (
                ("k02_gap43", "k02", "k07"),
                ("k02_gap96", "k07", "k02"),
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
                        "model": "K02_K07_separate_vectors",
                        "half_endian": half_endian,
                        "word_endian": word_endian,
                        "gap_order": gap_order,
                        "interpretation": interpretation,
                        **recovered,
                    })

    assert len(results) == 112
    assert all(result["rank"] == 15621 for result in results)
    assert not any(result["K04_PASS"] for result in results)
    unique_coupons = {result["coupon_hex"] for result in results}
    unique_components = {result["component_hex"] for result in results}
    assert len(unique_coupons) == 80
    assert len(unique_components) == 80

    positive = synthetic_positive(base, state_forms, source_packets, selected_index)
    assert positive["status"] == "PASS"

    print(json.dumps({
        "status": "BOUNDED_NEGATIVE",
        "base_rank": base.rank,
        "target_stages": [951, 952, 953, 954],
        "donor_stages": DONOR_STAGES,
        "cases": len(results),
        "unique_complete_candidates": len(unique_components),
        "K02_preimage_hex": k02_preimage.hex().upper(),
        "original_k04_hits": 0,
        "synthetic_positive": positive,
        "results": results,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
