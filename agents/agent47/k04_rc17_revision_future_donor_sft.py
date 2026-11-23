#!/usr/bin/env python3
"""Source-pinned RC-17 B/D revision blocks as K04 four-fresh future donors.

The selected PS-0417 ACK2 payload is withheld from the MT fit.  RC-17 B is
withdrawn and D is an unissued draft; this is an exploratory cross-stream
carrier test, not a claim that either revision was authorized for K06.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, "agents/agent10")
from k04_all42_wholewindow_sft import (
    ALT_STAGES, SPOOL_SHA, K04_SHA, build_basis, project, symbolic_words,
    temper, untemper,
)
from k04_all42_fourfresh_countermodel_sft import GAP_DELTAS, full_state, native_word
from k04_fourfresh_future_source_donor_sft import donor_mapping, map_native, donor_bits_from_block

ROOT = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("resources")
RC17_SHA = "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"
LABEL_SHA = "146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad"
DOCREG_SHA = "20d8dc63a28bab7084b6919207c50fb5bf957054f30b71c3ced0b3b5507e7f2c"
EXPECTED = {
    "B": "D82A73E9E1DB4379759E0027C130C9BB",
    "C": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "D-draft": "063380BE9402F11ADC789386ED607B30",
}
DONOR_STAGES = (1409, 1863)


def checked(path: Path, digest: str) -> bytes:
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest, path
    return data


def rc17_blocks(text: str, service_order: tuple[str, ...]) -> dict[str, bytes]:
    rows = re.findall(
        r"DOCUMENT RC-17 / REV (B|C|D-draft) / SECTION ([A-Z]+).*?"
        r"Footer control strip: ([0-9A-F]{8})",
        text, re.S,
    )
    records: dict[str, dict[str, str]] = {}
    for revision, section, value in rows:
        assert section not in records.setdefault(revision, {})
        records[revision][section] = value
    assert set(records) == {"B", "C", "D-draft"}
    assert all(set(records[rev]) == set(service_order) for rev in records)
    return {
        rev: b"".join(bytes.fromhex(records[rev][section]) for section in service_order)
        for rev in records
    }


def fixed_word_check(basis, expressions, stage: int, value: int) -> dict:
    projected = [project(form, basis) for form in expressions[stage]]
    fixed_mask = sum(1 << bit for bit, (form, _) in enumerate(projected) if form == 0)
    fixed_value = sum(rhs << bit for bit, (form, rhs) in enumerate(projected) if form == 0)
    mismatch = ((value ^ fixed_value) & fixed_mask).bit_count()
    return {
        "fixed_bits": fixed_mask.bit_count(),
        "mismatching_fixed_bits": mismatch,
        "fullword_match": fixed_mask == 0xffffffff and mismatch == 0,
        "compatible_with_all_fixed_bits": mismatch == 0,
    }


def main() -> None:
    spool = checked(ROOT / "evidence/print/spool-reconstruction.log", SPOOL_SHA)
    rc_text = checked(ROOT / "evidence/procedures/RC-17-scans.txt", RC17_SHA).decode("utf-8")
    labels = checked(ROOT / "evidence/archive-labels.ini", LABEL_SHA).decode("utf-8")
    docreg = checked(ROOT / "evidence/procedures/document-register.log", DOCREG_SHA).decode("utf-8")
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    assert acceptance["slot_sha256"]["K04"] == K04_SHA
    assert "RC-17 B        issued archive service sheets; withdrawn 2026-09-30" in docreg
    assert "RC-17 C        issued archive service sheets; approval receipt emailed" in docreg
    assert "RC-17 D-draft  review copy only; no issue authority" in docreg
    m = re.search(r"^service_order=([A-Z,]+)$", labels, re.M)
    assert m
    service_order = tuple(m.group(1).split(","))
    assert service_order == ("DRAIN", "ISOLATE", "PURGE", "VERIFY")
    blocks = rc17_blocks(rc_text, service_order)
    assert {k: v.hex().upper() for k, v in blocks.items()} == EXPECTED

    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) "
        rb"PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        spool, re.M,
    )
    assert len(rows) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    # The selected copied payload is not decoded or used in the source fit.
    native = [
        None if i == 129 else tuple(
            untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4*j:4*j+4], "little"))
            for j in range(4)
        )
        for i, row in enumerate(rows)
    ]
    gaps = [b - a for a, b in zip(ALT_STAGES, ALT_STAGES[1:])]
    for index, delta in GAP_DELTAS.items():
        gaps[index] += delta
    stages = [0]
    for gap in gaps:
        stages.append(stages[-1] + gap)
    assert stages[126:133] == [940, 947, 951, 955, 959, 963, 968]

    expressions = symbolic_words(0, 2100)
    basis = build_basis(native, tuple(stages), expressions, 0)
    assert len(basis) == 15434
    mappings = {q: donor_mapping(basis, expressions, 955, q) for q in DONOR_STAGES}
    assert all(mapping is not None for mapping in mappings.values())

    # End-to-end synthetic positive for both independently target-complete maps.
    seeded = random.Random(20261123).getrandbits(19968)
    for pivot in basis:
        seeded &= ~(1 << pivot)
    state = full_state(basis, seeded)
    target = b"".join(
        temper(native_word(state, expressions[955 + lane])).to_bytes(4, "little")
        for lane in range(4)
    )
    for q, mapping in mappings.items():
        donor = sum(
            native_word(state, expressions[q + lane]) << (32 * lane)
            for lane in range(4)
        )
        assert map_native(donor, mapping) == target


    # Independent stage bridge: the older p951 study found revision-B
    # VERIFY -> PURGE as an adjacent source-compatible pair. Test that same
    # source-defined reverse-service pair, plus C/D controls, against the
    # distinct all42/four-fresh chronology. Do not select a stage by target
    # information; scan the complete 0..2096 source range.
    def quotient_rank(forms, current_basis):
        residual = [project(form, current_basis)[0] for form in forms]
        pivots = {}
        for form in residual:
            while form:
                pivot = form.bit_length() - 1
                if pivot in pivots:
                    form ^= pivots[pivot]
                else:
                    pivots[pivot] = form
                    break
        return len(pivots)

    def add_equation(current_basis, form, rhs):
        while form:
            pivot = form.bit_length() - 1
            if pivot in current_basis:
                previous, previous_rhs = current_basis[pivot]
                form ^= previous
                rhs ^= previous_rhs
            else:
                current_basis[pivot] = (form, rhs)
                return True
        return rhs == 0

    target_forms = [
        form for q in range(955, 959) for form in expressions[q]
    ]
    assert quotient_rank(target_forms, basis) == 128
    projected_cache = [
        [project(form, basis) for form in expressions[q]]
        for q in range(2100)
    ]
    bridge_pairs = []
    bridge_blocks = []
    for revision, service_block in blocks.items():
        reverse_block = b"".join(
            service_block[4*lane:4*lane+4] for lane in (3, 2, 1, 0)
        )
        for endian in ("little", "big"):
            for stored_native in (False, True):
                observed = [
                    int.from_bytes(reverse_block[4*lane:4*lane+4], endian)
                    for lane in range(4)
                ]
                if not stored_native:
                    observed = [untemper(value) for value in observed]

                # The first two reverse-service words are VERIFY -> PURGE.
                for q in range(0, 2095):
                    checks = []
                    for lane in range(2):
                        projected = projected_cache[q+lane]
                        fixed_mask = sum(
                            1 << bit for bit, (form, _) in enumerate(projected)
                            if form == 0
                        )
                        fixed_value = sum(
                            rhs << bit for bit, (form, rhs) in enumerate(projected)
                            if form == 0
                        )
                        checks.append((
                            fixed_mask.bit_count(),
                            ((observed[lane] ^ fixed_value) & fixed_mask).bit_count()
                        ))
                    fixed_total = sum(x[0] for x in checks)
                    mismatch_total = sum(x[1] for x in checks)
                    if mismatch_total or fixed_total < 26 or min(x[0] for x in checks) < 8:
                        continue
                    augmented = basis.copy()
                    consistent = True
                    for lane in range(2):
                        for bit, form in enumerate(expressions[q+lane]):
                            if not add_equation(
                                augmented, form, (observed[lane] >> bit) & 1
                            ):
                                consistent = False
                                break
                        if not consistent:
                            break
                    if not consistent:
                        continue
                    target_rank = quotient_rank(target_forms, augmented)
                    bridge_pairs.append({
                        "revision": revision, "stage": q, "endian": endian,
                        "stored_as_native": stored_native,
                        "source_fixed_bits": fixed_total,
                        "added_rank": len(augmented) - len(basis),
                        "target_bits_fixed": 128 - target_rank,
                    })

                # Full four-word reverse-service block, same complete scan.
                for q in range(0, 2097):
                    checks = []
                    for lane in range(4):
                        projected = projected_cache[q+lane]
                        fixed_mask = sum(
                            1 << bit for bit, (form, _) in enumerate(projected)
                            if form == 0
                        )
                        fixed_value = sum(
                            rhs << bit for bit, (form, rhs) in enumerate(projected)
                            if form == 0
                        )
                        checks.append((
                            fixed_mask.bit_count(),
                            ((observed[lane] ^ fixed_value) & fixed_mask).bit_count()
                        ))
                    fixed_total = sum(x[0] for x in checks)
                    mismatch_total = sum(x[1] for x in checks)
                    if mismatch_total or fixed_total < 64 or min(x[0] for x in checks) < 8:
                        continue
                    augmented = basis.copy()
                    consistent = True
                    for lane in range(4):
                        for bit, form in enumerate(expressions[q+lane]):
                            if not add_equation(
                                augmented, form, (observed[lane] >> bit) & 1
                            ):
                                consistent = False
                                break
                        if not consistent:
                            break
                    if not consistent:
                        continue
                    target_rank = quotient_rank(target_forms, augmented)
                    bridge_blocks.append({
                        "revision": revision, "stage": q, "endian": endian,
                        "stored_as_native": stored_native,
                        "source_fixed_bits": fixed_total,
                        "added_rank": len(augmented) - len(basis),
                        "target_bits_fixed": 128 - target_rank,
                    })

    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert len(mask) == 16
    results = []
    source_fixed = []
    for revision, block in blocks.items():
        # The service-order block is tested without scanner-order or arbitrary
        # page permutations. Byte endianness and native/tempered views remain open.
        direct_component = bytes(a ^ b for a, b in zip(block, mask))
        results.append({
            "revision": revision,
            "mode": "direct_service_order_coupon",
            "component": direct_component.hex().upper(),
            "sha256_match": hashlib.sha256(direct_component).hexdigest() == K04_SHA,
        })
        for endian in ("little", "big"):
            for already_native in (False, True):
                words = [
                    int.from_bytes(block[4*lane:4*lane+4], endian)
                    for lane in range(4)
                ]
                native_words = words if already_native else [untemper(v) for v in words]
                for q in DONOR_STAGES:
                    checks = [
                        fixed_word_check(basis, expressions, q + lane, native_words[lane])
                        for lane in range(4)
                    ]
                    source_fixed.append({
                        "revision": revision,
                        "stage": q,
                        "endian": endian,
                        "stored_as_native": already_native,
                        "fixed_bits_total": sum(x["fixed_bits"] for x in checks),
                        "fixed_bit_mismatches": sum(x["mismatching_fixed_bits"] for x in checks),
                        "fullword_matches": sum(x["fullword_match"] for x in checks),
                        "compatible_words": sum(x["compatible_with_all_fixed_bits"] for x in checks),
                    })
                    donor_bits = donor_bits_from_block(
                        block, (0, 1, 2, 3), endian, already_native
                    )
                    coupon = map_native(donor_bits, mappings[q])
                    component = bytes(a ^ b for a, b in zip(coupon, mask))
                    results.append({
                        "revision": revision,
                        "stage": q,
                        "endian": endian,
                        "stored_as_native": already_native,
                        "coupon": coupon.hex().upper(),
                        "component": component.hex().upper(),
                        "sha256_match": hashlib.sha256(component).hexdigest() == K04_SHA,
                    })

    assert len(results) == 3 + 3 * 2 * 2 * 2
    matches = [x for x in results if x["sha256_match"]]
    print(json.dumps({
        "selected_ACK2_payload_used": False,
        "source_rank": len(basis),
        "selected_native_quotient_rank": 128,
        "donor_stages": list(DONOR_STAGES),
        "service_order": list(service_order),
        "revision_blocks": {k: v.hex().upper() for k, v in blocks.items()},
        "source_fixed_word_checks": source_fixed,
        "complete_candidates": len(results),
        "distinct_components": len({x["component"] for x in results}),
        "original_K04_commitment_matches": matches,
        "fourfresh_reverse_service_pair_bridge": {
            "compatible_pair_presentations": len(bridge_pairs),
            "target_informative_pairs": [
                x for x in bridge_pairs if x["target_bits_fixed"] > 0
            ],
            "best_pairs": sorted(
                bridge_pairs,
                key=lambda x: (x["target_bits_fixed"], x["source_fixed_bits"]),
                reverse=True
            )[:12],
            "compatible_full_blocks": len(bridge_blocks),
            "target_informative_full_blocks": [
                x for x in bridge_blocks if x["target_bits_fixed"] > 0
            ],
            "best_full_blocks": sorted(
                bridge_blocks,
                key=lambda x: (x["target_bits_fixed"], x["source_fixed_bits"]),
                reverse=True
            )[:12],
        },
        "synthetic_full_coupon_reconstruction": True,
        "interpretation": (
            "B is withdrawn and D-draft is unissued. Any candidate match would "
            "still require historical stage/issuer provenance; a miss excludes "
            "only these source-defined revision blocks under the stated model."
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
