#!/usr/bin/env python3
"""H-17 original K04 complete coupon construction from 4-fresh future native donors.

One runnable read-only source-pinned test:
    python agents/agent10/k04_fourfresh_future_source_donor_sft.py [resources-directory]

Both future donor stages are selected by GF(2) target-observability alone.
The unverified selected PS-0417 ACK2 copied payload is not decoded.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import re
import sys
from pathlib import Path

from k04_all42_wholewindow_sft import (
    ALT_STAGES, P951_STAGES, SPOOL_SHA, K04_SHA,
    build_basis, enumerate_windows, project, symbolic_words, temper, untemper,
)
from k04_all42_fourfresh_countermodel_sft import GAP_DELTAS, full_state, native_word

SOURCE_HASHES = {
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
    "evidence/telemetry/freeze-export.jsonl": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
    "evidence/maintenance/seal-receipts.jsonl": "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    "evidence/transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "evidence/recorder/trip-recorder.raw": "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
}
BLOCKS = {
    "K01_ink": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02_DIAG_raw": "E1A5E474BAD7E853A2E8C71D3317D507",
    "K02_accepted": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03_seals_raw": "D7DAD6BC9714519B7DAD0AD4BE8E87FD",
    "K03_accepted": "1384AF96E25D6ADA666209CB55E062FA",
    "K05_controls": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06_accepted": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07_checks_raw": "8947CEDCB9CC73BAB7E87BE63302C5C9",
    "K07_accepted": "93495F5E425AB8E592123DABAEB68545",
    "K04_route_mask": "8556C8CB6140A7F9A5123AC7571BEE1C",
    "K08_desk_nonce": "5F933DA6A1BD03C32DA5CBC25344F497",
}
ACCEPTED = {
    "K01": BLOCKS["K01_ink"], "K02": BLOCKS["K02_accepted"],
    "K03": BLOCKS["K03_accepted"], "K05": BLOCKS["K05_controls"],
    "K06": BLOCKS["K06_accepted"], "K07": BLOCKS["K07_accepted"],
}


def rank(equations: list[int]) -> int:
    basis = {}
    for form in equations:
        while form:
            pivot = form.bit_length() - 1
            if pivot in basis:
                form ^= basis[pivot]
            else:
                basis[pivot] = form
                break
    return len(basis)


def donor_mapping(basis, expressions, selected: int, donor: int):
    def projected(q: int):
        return [project(f, basis)
                for j in range(q, q + 4) for f in expressions[j]]
    local = {}
    for coordinate, (form, rhs) in enumerate(projected(donor)):
        binary = 1 << coordinate
        while form:
            pivot = form.bit_length() - 1
            if pivot not in local:
                local[pivot] = form, binary, rhs
                break
            previous, previous_binary, previous_rhs = local[pivot]
            form ^= previous
            binary ^= previous_binary
            rhs ^= previous_rhs
        else:
            return None
    target_reduction = []
    for form, rhs in projected(selected):
        binary = 0
        while form:
            pivot = form.bit_length() - 1
            if pivot not in local:
                return None
            previous, previous_binary, previous_rhs = local[pivot]
            form ^= previous
            binary ^= previous_binary
            rhs ^= previous_rhs
        target_reduction.append((binary, rhs))
    return target_reduction


def map_native(donor_bits: int, mapping) -> bytes:
    value = sum(
        (((selection & donor_bits).bit_count() & 1) ^ rhs) << bit
        for bit, (selection, rhs) in enumerate(mapping)
    )
    return b"".join(
        temper((value >> (32 * lane)) & 0xFFFFFFFF).to_bytes(4, "little")
        for lane in range(4)
    )


def donor_bits_from_block(buffer: bytes, permutation, endian, already_native: bool):
    vals = [int.from_bytes(buffer[4 * j:4 * j + 4], endian)
            for j in permutation]
    if not already_native:
        vals = [untemper(v) for v in vals]
    return sum(v << (32 * j) for j, v in enumerate(vals))


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / "resources"
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    for relative, expected_sha in SOURCE_HASHES.items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected_sha
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw, re.M,
    )
    assert len(rows) == 133 and rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    native = [
        None if i == 129 else tuple(
            untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4 * lane:4 * lane+4], "little"))
            for lane in range(4)
        )
        for i, row in enumerate(rows)
    ]
    acceptance = json.loads((root / "acceptance.json").read_text())
    route = json.loads((root / "evidence/recovery-routing.json").read_text())
    assert acceptance["slot_sha256"]["K04"] == K04_SHA
    for name, hx in ACCEPTED.items():
        assert hashlib.sha256(bytes.fromhex(hx)).hexdigest() == acceptance["slot_sha256"][name]
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert mask.hex().upper() == BLOCKS["K04_route_mask"]
    assert route["K08"]["desk_nonce"].upper() == BLOCKS["K08_desk_nonce"]

    gaps = [y - x for x, y in zip(ALT_STAGES, ALT_STAGES[1:])]
    for row, delta in GAP_DELTAS.items():
        gaps[row] += delta
    assert min(gaps) >= 4
    starts = [0]
    for gap in gaps:
        starts.append(starts[-1] + gap)
    assert starts[129] == 955
    expressions = symbolic_words(0, 2100)
    basis = build_basis(native, tuple(starts), expressions, 0)
    assert len(basis) == 15434
    target = [project(f, basis)[0]
              for q in range(955, 959) for f in expressions[q]]
    assert rank(target) == 128

    # Scan possible four-word donors by target GF(2) observability only.
    # Exclude any direct overlap with the missing coupon itself.
    donor_maps = {}
    for q in range(2097):
        if 952 <= q <= 958:
            continue
        mapping = donor_mapping(basis, expressions, 955, q)
        if mapping is not None:
            donor_maps[q] = mapping
    assert sorted(donor_maps) == [1409, 1863]

    # Synthetic positive: a planted complete MT state with deterministic
    # arbitrary free-state coordinates, never taken from the copied ACK2.
    seeded = random.Random(20261123).getrandbits(19968)
    for pivot in basis:
        seeded &= ~(1 << pivot)
    state = full_state(basis, seeded)
    original_target = b"".join(
        temper(native_word(state, expressions[955 + lane])).to_bytes(4, "little")
        for lane in range(4)
    )
    assert original_target != bytes(16)
    for q, mapping in donor_maps.items():
        donor_native = sum(
            native_word(state, expressions[q + lane]) << (32 * lane)
            for lane in range(4)
        )
        assert map_native(donor_native, mapping) == original_target

    seen = set()
    originals = []
    total = 0
    for label, hx in BLOCKS.items():
        buffer = bytes.fromhex(hx)
        for q, mapping in donor_maps.items():
            for order in itertools.permutations(range(4)):
                for endian in ("little", "big"):
                    for already_native in (False, True):
                        raw_coupon = map_native(
                            donor_bits_from_block(buffer, order, endian, already_native),
                            mapping
                        )
                        component = bytes(x ^ y for x, y in zip(raw_coupon, mask))
                        seen.add(component)
                        total += 1
                        if hashlib.sha256(component).hexdigest() == K04_SHA:
                            originals.append((label, q, order, endian, already_native, component.hex().upper()))
    assert total == len(seen) == 2112
    assert not originals, "Original K04 hit requires independent exact verification"

    # Distinct from the two previously source-complete stage-window corpora.
    alt_basis = build_basis(native, ALT_STAGES, expressions, 0)
    _, alt_candidates, _ = enumerate_windows(expressions, alt_basis, 0, 2)
    earlier_forms = symbolic_words(-1100, 2100)
    earlier_basis = build_basis(native, P951_STAGES, earlier_forms, -1100)
    _, earlier_candidates, _ = enumerate_windows(earlier_forms, earlier_basis, -1100, 1)
    old = {bytes(x ^ y for x, y in zip(c, mask))
           for c in set(alt_candidates) | set(earlier_candidates)}
    assert len(old) == 748 and len(seen & old) == 0
    print(json.dumps({
        "selected_copied_ACK2_loaded": False,
        "original_printer_source_rank": len(basis),
        "selected_rank_remaining_without_new_donor": 128,
        "four_word_future_donor_native_starts": sorted(donor_maps),
        "independent_source_objects_used": len(BLOCKS),
        "serialization_presentations_per_donor": 96,
        "complete_k04_candidate_components_checked": total,
        "distinct_from_previous_748_source_stage_coupons": len(seen),
        "full_synthetic_state_coupon_reconstruction_both_donors": True,
        "original_k04_acceptance_matches": originals
    }, indent=2))


if __name__ == "__main__":
    main()
