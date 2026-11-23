#!/usr/bin/env python3
"""Compare two source-compatible MT printer chronologies with independent RC-17 footers.

Portable source-pinned single-file test; original selected ACK2 copy is withheld.
Run: python agents/agent21/k04_rc17_crossmodel_source_selector_sft.py [resources-or-original-zip]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent10"))
from k04_all42_wholewindow_sft import ALT_STAGES, SPOOL_SHA, build_basis, project, symbolic_words, untemper
from k04_all42_fourfresh_countermodel_sft import GAP_DELTAS
sys.path.insert(0, str(ROOT / "agents/agent49"))
from k04_p951_symbolic_basis import STARTS as P951_STAGES

RC17_SHA = "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"
ORIGIN = -1100
LAST = 2095


def read_evidence(root: Path, name: str) -> bytes:
    if root.is_file() and root.suffix.lower() == ".zip":
        with zipfile.ZipFile(root) as archive:
            return archive.read("evidence/" + name)
    if (root / "evidence").is_dir():
        return (root / "evidence" / name).read_bytes()
    return (root / "resources/evidence" / name).read_bytes()


def source_syndrome(forms: list[int], basis: dict[int, tuple[int, int]]) -> list[tuple[int, int]]:
    """All independent parity equations on the 32 native candidate word bits."""
    local: dict[int, tuple[int, int, int]] = {}
    constraints: list[tuple[int, int]] = []
    for bit, form in enumerate(forms):
        free, parity = project(form, basis)
        mask = 1 << bit
        while free:
            pivot = free.bit_length() - 1
            known = local.get(pivot)
            if known is None:
                local[pivot] = (free, mask, parity)
                break
            expression, wordmask, rhs = known
            free ^= expression
            mask ^= wordmask
            parity ^= rhs
        else:
            constraints.append((mask, parity))
    assert len(constraints) + len(local) == 32
    return constraints


def agrees(constraints: list[tuple[int, int]], value: int) -> bool:
    return all(((value & mask).bit_count() & 1) == parity
               for mask, parity in constraints)


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else ROOT / "resources"
    spool = read_evidence(root, "print/spool-reconstruction.log")
    rc17 = read_evidence(root, "procedures/RC-17-scans.txt")
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(rc17).hexdigest() == RC17_SHA

    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        spool, re.M,
    )
    assert len(rows) == len(P951_STAGES) == len(ALT_STAGES) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    native = [
        None if index == 129 else tuple(
            untemper(int.from_bytes(
                bytes.fromhex(row[5].decode())[4 * lane:4 * lane + 4], "little"
            )) for lane in range(4)
        )
        for index, row in enumerate(rows)
    ]
    assert native[129] is None

    footers = []
    for sheet in rc17.split(b"\x0c"):
        header = re.search(rb"DOCUMENT RC-17 / REV ([^ /]+) / SECTION ([A-Z]+)", sheet)
        checksum = re.search(rb"Footer control strip: ([0-9A-F]{8})", sheet)
        if header and checksum:
            footers.append((header[1].decode(), header[2].decode(), bytes.fromhex(checksum[1].decode())))
    assert len(footers) == 12
    assert {(revision, section) for revision, section, _ in footers
            if revision == "B"} == {("B", "DRAIN"), ("B", "ISOLATE"), ("B", "PURGE"), ("B", "VERIFY")}
    assert {section: value.hex().upper() for revision, section, value in footers if revision == "B"} == {
        "DRAIN": "D82A73E9", "ISOLATE": "E1DB4379",
        "PURGE": "759E0027", "VERIFY": "C130C9BB"
    }

    gaps = [b - a + GAP_DELTAS.get(index, 0)
            for index, (a, b) in enumerate(zip(ALT_STAGES, ALT_STAGES[1:]))]
    assert 4 <= min(gaps) <= max(gaps) <= 16
    all_fresh = [0]
    for gap in gaps:
        all_fresh.append(all_fresh[-1] + gap)
    assert all_fresh[129] == 955 and all_fresh[-1] == 968

    symbols = symbolic_words(ORIGIN, LAST + 2)
    models = (("p951", tuple(P951_STAGES), 15365),
              ("all42_fourfresh", tuple(all_fresh), 15434))
    outcomes = []
    for name, stages, rank in models:
        basis = build_basis(native, stages, symbols, ORIGIN)
        assert len(basis) == rank

        informative = {}
        for stage in range(ORIGIN, LAST + 1):
            constraints = source_syndrome(symbols[stage - ORIGIN], basis)
            if len(constraints) >= 14:
                informative[stage] = constraints

        # Both models must positively reproduce the exact source observations.
        control_stage = stages[43] + 2
        assert agrees(informative[control_stage], native[43][2])
        controls = [("B", "VERIFY", -186, bytes.fromhex("C130C9BB"), 32),
                    ("B", "PURGE", -185, bytes.fromhex("759E0027"), 31)]
        if name == "p951":
            for _, _, stage, value, expected in controls:
                constraints = informative[stage]
                assert len(constraints) == expected
                native_word = untemper(int.from_bytes(value, "little"))
                assert agrees(constraints, native_word)
            assert not agrees(informative[-186],
                              untemper(int.from_bytes(bytes.fromhex("C130C9BA"), "little")))

        matches = []
        for revision, section, buffer in footers:
            for endian in ("little", "big"):
                word = int.from_bytes(buffer, endian)
                for presentation in ("native", "tempered"):
                    native_word = word if presentation == "native" else untemper(word)
                    for stage, constraints in informative.items():
                        if agrees(constraints, native_word):
                            matches.append({
                                "revision": revision, "section": section,
                                "stage": stage, "endian": endian,
                                "presentation": presentation,
                                "source_parity_checks": len(constraints)
                            })
        if name == "p951":
            assert matches == [
                {"revision": "B", "section": "PURGE", "stage": -185,
                 "endian": "little", "presentation": "tempered", "source_parity_checks": 31},
                {"revision": "B", "section": "VERIFY", "stage": -186,
                 "endian": "little", "presentation": "tempered", "source_parity_checks": 32}
            ]
            assert len(informative) == 1656
        else:
            assert not matches
            assert len(informative) == 1723

        outcomes.append({
            "model": name, "printer_source_equations": 528 * 32,
            "printer_source_rank": rank, "informative_stages": len(informative),
            "footer_views_per_stage": len(footers) * 4,
            "all_original_footer_matches": matches
        })

    print(json.dumps({
        "original_spool_sha256": SPOOL_SHA,
        "original_rc17_sha256": RC17_SHA,
        "selected_ack2_payload_loaded": False,
        "nonselected_printer_packets": 132,
        "footer_strips": 12,
        "original_model_checks": outcomes,
        "historical_shared_issuer_authenticated": False,
        "actual_k04_recovered": False,
        "note": "Cross-source discriminator only; both models remain target-underdetermined"
    }, indent=2))


if __name__ == "__main__":
    main()
