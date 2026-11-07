#!/usr/bin/env python3
"""Conditional p951 K04 donor test using both ST↔PTW offsets and PTW-417 revisions.

Run from the repository root:
    python agents/agent24/k04_ptw_crosswalk_revision_donors_sft.py

This is a finite hypothesis test, not proof of the historical MT producer or
of either ticket offset. It withholds printer row129 through Agent49's
source-only basis, constructs complete K04 candidates, and checks the original
slot commitment. No source, candidate, verifier, or acceptance file is changed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.agent49.k04_p951_symbolic_basis import (  # noqa: E402
    STARTS,
    Basis,
    get,
    source,
    temper,
    untemper,
)

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SEAL_SHA = "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
RETIREMENT_SHA = "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
SUPPLIER_SHA = "73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e"

NORTH_TICKETS = ("ST-094", "ST-106", "ST-099", "ST-112")
CROSSWALKS = {"+300": 300, "+304": 304}
GAP43 = (328, 329, 330, 331)
GAP96 = (724, 725, 726, 727)
WITNESS_ORDER = "BDAC"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_north_tickets(evidence: Path) -> None:
    """Assert the four posted FA-17/A3 North ticket rows used in this test."""
    retirement = evidence / "h17-supplemental-office-files/print-fleet-retirement-note.txt"
    supplier = evidence / "h17-supplemental-office-files/supplier-reconciliation-L29.csv"
    assert sha256(retirement) == RETIREMENT_SHA
    assert sha256(supplier) == SUPPLIER_SHA

    text = retirement.read_text(encoding="utf-8")
    for ticket in NORTH_TICKETS:
        assert re.search(rf"^L-29/N\\s+\\d+\\s+{ticket}\\s+", text, re.M), ticket

    with supplier.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(line for line in stream if not line.startswith("#")))
    for ticket in NORTH_TICKETS:
        matches = [
            row for row in rows
            if row["line_ref"] == ticket
            and row["source"] == "L29"
            and row["run"] == "R3"
            and row["posting"] == "POSTED"
            and row["account"] == "FA-17"
            and row["folio_or_jacket"] == "H17-POL-17/A3"
        ]
        assert len(matches) == 1, (ticket, matches)


def permit_group(evidence: Path, offset: int, order: str) -> list[str]:
    """Four singleton PTW serials implied by one offset, in ticket or bay order."""
    rows = [
        json.loads(line)
        for line in (evidence / "maintenance/seal-receipts.jsonl").read_text().splitlines()
    ]
    by_permit: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_permit[row["permit"]].append(row)

    selected = []
    for ticket in NORTH_TICKETS:
        permit = f"PTW-{int(ticket[-3:]) + offset:03d}"
        eligible = [
            row for row in by_permit[permit]
            if row["state"] == "CLOSED"
            and row["fitment"] == "AS_LEFT"
            and row["signed"] is True
        ]
        assert len(eligible) == 1, (permit, eligible)
        row = eligible[0]
        selected.append((row["bay"], row["serial"].split("-")[-1], permit))

    if order == "binder":
        return [serial for _, serial, _ in selected]
    if order == "walk":
        by_bay = {bay: serial for bay, serial, _ in selected}
        assert len(by_bay) == 4, selected
        assert set(by_bay) == set("ABCD"), selected
        return [by_bay[bay] for bay in WITNESS_ORDER]
    raise ValueError(order)


def ptw417_revision_groups(evidence: Path) -> dict[int, list[list[str]]]:
    """Use all four PTW-417 revision cohorts, preserving the B,D,A,C bay walk.

    Revision 1 has two original Bay-A serials, so both source alternatives are
    retained. Revisions 3 and 4 are OPEN/REMOVED records and are included as
    historical source values, not as accepted K03 values.
    """
    rows = [
        json.loads(line)
        for line in (evidence / "maintenance/seal-receipts.jsonl").read_text().splitlines()
    ]
    by_revision: dict[int, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["permit"] == "PTW-417":
            by_revision[row["revision"]][row["bay"]].append(row["serial"].split("-")[-1])

    groups: dict[int, list[list[str]]] = {}
    for revision in (1, 2, 3, 4):
        assert all(by_revision[revision].get(bay) for bay in WITNESS_ORDER)
        a_choices = by_revision[revision]["A"]
        assert len(a_choices) in (1, 2)
        groups[revision] = [
            [
                by_revision[revision]["B"][0],
                by_revision[revision]["D"][0],
                a_serial,
                by_revision[revision]["C"][0],
            ]
            for a_serial in a_choices
        ]
    assert [len(groups[r]) for r in (1, 2, 3, 4)] == [2, 1, 1, 1]
    return groups


def values(hex_words: list[str], endian: str, interpretation: str) -> list[int]:
    result = [int.from_bytes(bytes.fromhex(word), endian) for word in hex_words]
    if interpretation == "untemper":
        return [untemper(word) for word in result]
    assert interpretation == "native"
    return result


def recover(
    original_basis: Basis,
    state: list[list[int]],
    gap43_words: list[int],
    gap96_words: list[int],
    mask: bytes,
) -> tuple[bytes, bytes]:
    augmented = Basis()
    augmented.rows = original_basis.rows.copy()
    augmented.rank = original_basis.rank

    for stage, word in list(zip(GAP43, gap43_words)) + list(zip(GAP96, gap96_words)):
        for bit, expression in enumerate(get(state, stage)):
            augmented.insert(expression, (word >> bit) & 1)

    assert augmented.rank == 15621
    payload = bytearray()
    for stage in range(STARTS[129], STARTS[129] + 4):
        output_forms = temper(get(state, stage))
        word = 0
        for bit, expression in enumerate(output_forms):
            value = augmented.predict(expression)
            assert value is not None
            word |= value << bit
        payload.extend(word.to_bytes(4, "little"))

    component = bytes(left ^ right for left, right in zip(payload, mask))
    return bytes(payload), component


def source_consistent_positive_control(
    original_basis: Basis,
    state: list[list[int]],
    mask: bytes,
) -> None:
    """Complete the source affine basis with free variables zero, then replay."""
    assignment = 0
    for pivot in sorted(original_basis.rows):
        vector, rhs = original_basis.rows[pivot]
        bit = rhs ^ (((vector ^ (1 << pivot)) & assignment).bit_count() & 1)
        if bit:
            assignment |= 1 << pivot

    def native_word(stage: int) -> int:
        value = 0
        for bit, expression in enumerate(get(state, stage)):
            value |= ((expression & assignment).bit_count() & 1) << bit
        return value

    gap43 = [native_word(stage) for stage in GAP43]
    gap96 = [native_word(stage) for stage in GAP96]

    expected_payload = bytearray()
    for stage in range(STARTS[129], STARTS[129] + 4):
        word = 0
        for bit, expression in enumerate(temper(get(state, stage))):
            word |= ((expression & assignment).bit_count() & 1) << bit
        expected_payload.extend(word.to_bytes(4, "little"))

    recovered_payload, _ = recover(original_basis, state, gap43, gap96, mask)
    assert recovered_payload == bytes(expected_payload)


def main() -> None:
    evidence = ROOT / "resources/evidence"
    spool = evidence / "print/spool-reconstruction.log"
    seals = evidence / "maintenance/seal-receipts.jsonl"
    assert sha256(spool) == SPOOL_SHA
    assert sha256(seals) == SEAL_SHA
    selected_north_tickets(evidence)

    # Agent49's source loader withholds selected printer row129 before reading
    # its PAYLOAD; the model is the conditional p951 chronology.
    original_basis, state = source(ROOT)
    assert original_basis.rank == 15365
    assert STARTS[129] == 951

    route = json.loads((evidence / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text(encoding="utf-8"))
    mask = bytes.fromhex(route["K04"]["masked_component"])
    expected = acceptance["slot_sha256"]["K04"].lower()

    revision_groups = ptw417_revision_groups(evidence)
    candidates: dict[str, dict] = {}
    by_offset = {offset: 0 for offset in CROSSWALKS}
    hits = []

    for offset_name, offset in CROSSWALKS.items():
        for north_order in ("binder", "walk"):
            north_hex = permit_group(evidence, offset, north_order)
            for revision, revision_options in revision_groups.items():
                for a_choice, revision_hex in enumerate(revision_options):
                    for north_endian in ("big", "little"):
                        for revision_endian in ("big", "little"):
                            for north_interpretation in ("native", "untemper"):
                                for revision_interpretation in ("native", "untemper"):
                                    north_words = values(north_hex, north_endian, north_interpretation)
                                    revision_words = values(revision_hex, revision_endian, revision_interpretation)
                                    for north_at_gap43 in (True, False):
                                        gap43, gap96 = (
                                            (north_words, revision_words)
                                            if north_at_gap43
                                            else (revision_words, north_words)
                                        )
                                        payload, component = recover(
                                            original_basis, state, gap43, gap96, mask
                                        )
                                        digest = hashlib.sha256(component).hexdigest()
                                        key = component.hex().upper()
                                        assert key not in candidates
                                        record = {
                                            "offset": offset_name,
                                            "north_order": north_order,
                                            "ptw417_revision": revision,
                                            "revision1_A_choice": a_choice,
                                            "north_endian": north_endian,
                                            "revision_endian": revision_endian,
                                            "north_interpretation": north_interpretation,
                                            "revision_interpretation": revision_interpretation,
                                            "north_at_gap43": north_at_gap43,
                                            "payload": payload.hex().upper(),
                                            "component": key,
                                            "sha256": digest,
                                        }
                                        candidates[key] = record
                                        by_offset[offset_name] += 1
                                        if digest == expected:
                                            hits.append(record)

    assert len(candidates) == 640
    assert by_offset == {"+300": 320, "+304": 320}
    assert not hits

    source_consistent_positive_control(original_basis, state, mask)
    print(f"source_rank={original_basis.rank}")
    print(f"selected_stage={STARTS[129]}..{STARTS[129] + 3} (row129 payload withheld)")
    print(f"candidate_count={len(candidates)}")
    print(f"unique_components={len(candidates)}")
    print(f"candidate_count_by_offset={by_offset}")
    print(f"original_K04_commitment_hits={len(hits)}")
    print("source-consistent synthetic positive control=PASS")
    print("conclusion=0/640 candidates match; both ticket offsets remain unvalidated")


if __name__ == "__main__":
    main()
