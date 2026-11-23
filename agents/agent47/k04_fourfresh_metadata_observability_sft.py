#!/usr/bin/env python3
"""Four-fresh H-17 MT source: generous metadata-bit oracles versus K04 rank.

Read-only standalone SFT with the existing Agent10 native MT source machinery.
Usage from repository root:
    python agents/agent47/k04_fourfresh_metadata_observability_sft.py

The copied target ACK2 payload and both commitment files are never loaded.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent10"))
from k04_all42_wholewindow_sft import ALT_STAGES, SPOOL_SHA, build_basis, project, symbolic_words, untemper
from k04_all42_fourfresh_countermodel_sft import GAP_DELTAS, full_state, native_word, packet, quotient_rank


def temper_forms(native: list[int]) -> list[int]:
    first = [v ^ (native[i + 11] if i + 11 < 32 else 0) for i, v in enumerate(native)]
    second = [v ^ (first[i - 7] if i >= 7 and (0x9D2C5680 >> i) & 1 else 0)
              for i, v in enumerate(first)]
    third = [v ^ (second[i - 15] if i >= 15 and (0xEFC60000 >> i) & 1 else 0)
             for i, v in enumerate(second)]
    return [v ^ (third[i + 18] if i + 18 < 32 else 0)
            for i, v in enumerate(third)]


def add_observation(basis: dict[int, tuple[int, int]], form: int, rhs: int) -> None:
    while form:
        pivot = form.bit_length() - 1
        if pivot not in basis:
            basis[pivot] = (form, rhs)
            return
        old, old_rhs = basis[pivot]
        form ^= old
        rhs ^= old_rhs
    assert rhs == 0


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
    source = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SPOOL_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        source, re.M
    )
    assert len(rows) == len(ALT_STAGES) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )

    gaps = [b - a + GAP_DELTAS.get(i, 0)
            for i, (a, b) in enumerate(zip(ALT_STAGES, ALT_STAGES[1:]))]
    assert len(gaps) == 132 and min(gaps) >= 4 and max(gaps) <= 16
    stages = [0]
    for gap in gaps:
        stages.append(stages[-1] + gap)
    assert stages[128:131] == [951, 955, 959]

    native = [
        None if i == 129 else tuple(
            untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4*j:4*j+4], "little"))
            for j in range(4)
        )
        for i, row in enumerate(rows)
    ]
    expressions = symbolic_words(0, max(stages) + 4)
    basis = build_basis(native, tuple(stages), expressions, 0)
    assert len(basis) == 15434

    projections: dict[str, list[int]] = {
        "native_high2": [], "native_low2": [],
        "tempered_high2": [], "tempered_low2": []
    }
    for i, gap in enumerate(gaps):
        for q in range(stages[i] + 4, stages[i + 1]):
            value = expressions[q]
            tempered = temper_forms(value)
            for name, forms in (
                ("native_high2", value[30:32]),
                ("native_low2", value[:2]),
                ("tempered_high2", tempered[30:32]),
                ("tempered_low2", tempered[:2]),
            ):
                projections[name].extend(project(form, basis)[0] for form in forms)

    selected = [
        project(form, basis)[0]
        for q in range(stages[129], stages[129] + 4)
        for form in expressions[q]
    ]
    assert quotient_rank(selected) == 128

    combinations = (
        ("native_high2",),
        ("native_low2",),
        ("tempered_high2",),
        ("tempered_low2",),
        ("native_high2", "native_low2"),
        ("tempered_high2", "tempered_low2"),
    )
    expected = ((369,124),(379,124),(508,128),(493,128),(653,116),(982,128))
    source_state = full_state(basis)
    output = {}
    for names, (leak_rank_expected, remaining_expected) in zip(combinations, expected):
        leaked = [f for name in names for f in projections[name]]
        rank = quotient_rank(leaked)
        remaining = quotient_rank(leaked + selected) - rank
        assert (rank, remaining) == (leak_rank_expected, remaining_expected)
        output["+".join(names)] = {"hypothetical_leak_rank": rank,
                                   "remaining_selected_bits": remaining}
        if names in (("tempered_high2",), ("native_high2", "native_low2")):
            extended = dict(basis)
            for form in leaked:
                if form:
                    add_observation(extended, form,
                                    ((form & source_state).bit_count() & 1))
            second_residual = [project(form, extended)[0]
                               for q in range(stages[129], stages[129] + 4)
                               for form in expressions[q]]
            assert quotient_rank(second_residual) == remaining
            pivot = next(f.bit_length()-1 for f in second_residual if f)
            witness = full_state(extended, 1 << pivot)
            assert source_state != witness
            for i, original in enumerate(native):
                if original is None:
                    continue
                for j, stored in enumerate(original):
                    assert native_word(witness, expressions[stages[i] + j]) == stored
            assert all(((form & source_state).bit_count() & 1) ==
                       ((form & witness).bit_count() & 1) for form in leaked)
            first_packet = packet(source_state, expressions, stages[129])
            second_packet = packet(witness, expressions, stages[129])
            assert first_packet != second_packet
            output["+".join(names)]["two_full_states_source_and_leak_equivalent"] = True
            output["+".join(names)]["synthetic_selected_packets"] = [
                first_packet.hex().upper(), second_packet.hex().upper()
            ]

    print(json.dumps({
        "source_sha256": SPOOL_SHA,
        "original_intact_words_reproduced": 528,
        "source_rank": len(basis),
        "selected_stage": stages[129],
        "unobserved_gap_words": sum(g - 4 for g in gaps),
        "selected_payload_loaded": False,
        "historical_K04_recovered": False,
        "oracle_results": output
    }, indent=2))


if __name__ == "__main__":
    main()
