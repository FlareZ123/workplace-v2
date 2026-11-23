#!/usr/bin/env python3
"""Read-only original H17 K04 future four-word recorder donor test.

Source-specific extension of Agent10's original all42 fourfresh inverse.
Usage: python agents/agent22/k04_fourfresh_recorder_future_donor_sft.py [resources]

A matching hash would identify a candidate, not authenticate common
printer/recorder PRNG provenance. Selected ACK2 payload is withheld.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import re
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent10"))
from k04_all42_wholewindow_sft import (
    ALT_STAGES, K04_SHA, SPOOL_SHA, build_basis, symbolic_words, temper, untemper,
)
from k04_all42_fourfresh_countermodel_sft import GAP_DELTAS, full_state, native_word
from k04_fourfresh_future_source_donor_sft import (
    BLOCKS, donor_bits_from_block, donor_mapping, map_native,
)

RECORDER_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
SOURCE_ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
SOURCE_ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"


def recorder_cohorts(raw: bytes) -> dict[str, list[bytes]]:
    assert raw[:8] == b"TRP2DUMP"
    version, width, count = struct.unpack_from("<HHI", raw, 8)
    assert (version, width, count, len(raw)) == (2, 24, 88, 16 + 24 * 88)
    records = []
    for row in range(count):
        record = raw[16 + 24 * row:16 + 24 * (row + 1)]
        utc, node, event, latch, seq = struct.unpack_from("<IHBBI", record)
        crc = struct.unpack_from("<I", record, 20)[0] == zlib.crc32(record[:20])
        records.append((utc, node, event, latch, seq, record[12:16], crc))
    good = [r for r in records if r[6]]
    assert len(good) == 84 and sum(not r[6] for r in records) == 4

    def windows(sequence):
        return [b"".join(x[5] for x in sequence[i:i + 4])
                for i in range(len(sequence) - 3)]

    cohorts = {
        "crc_valid_file_order": windows(good),
        "crc_valid_utc_order": windows(sorted(good, key=lambda x: (x[0], x[1], x[4]))),
        "node50_sequence_order": windows(sorted(
            (r for r in good if r[1] == 50), key=lambda x: x[4])),
        "node50_utc_order": windows(sorted(
            (r for r in good if r[1] == 50), key=lambda x: (x[0], x[4]))),
    }
    for start in (200, 300, 990):
        selected = sorted(
            (r for r in good if r[1:3] == (49, 82) and start <= r[4] < start + 4),
            key=lambda x: x[4],
        )
        assert len(selected) == 4
        cohorts[f"node49_event82_seq{start}"] = [b"".join(r[5] for r in selected)]
    assert [len(v) for v in cohorts.values()] == [81, 81, 69, 69, 1, 1, 1]
    assert len({x for group in cohorts.values() for x in group}) == 236
    return cohorts


def main() -> None:
    root = (Path(sys.argv[1]) if len(sys.argv) == 2
            else Path(__file__).resolve().parents[2] / "resources")
    source = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SPOOL_SHA
    recorder = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(recorder).hexdigest() == RECORDER_SHA
    route_bytes = (root / "evidence/recovery-routing.json").read_bytes()
    acceptance_bytes = (root / "acceptance.json").read_bytes()
    assert hashlib.sha256(route_bytes).hexdigest() == SOURCE_ROUTE_SHA
    assert hashlib.sha256(acceptance_bytes).hexdigest() == SOURCE_ACCEPTANCE_SHA
    route, acceptance = json.loads(route_bytes), json.loads(acceptance_bytes)
    assert acceptance["slot_sha256"]["K04"] == K04_SHA
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert mask.hex().upper() == BLOCKS["K04_route_mask"]

    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        source, re.M,
    )
    assert len(rows) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417",
        b"2", b"ACK", b"RECOVER",
    )
    # Row129 payload is not hex-decoded or admitted as an MT source.
    native = [None if i == 129 else tuple(
        untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4 * lane:4 * lane + 4], "little"))
        for lane in range(4)
    ) for i, row in enumerate(rows)]

    gaps = [b - a for a, b in zip(ALT_STAGES, ALT_STAGES[1:])]
    for i, delta in GAP_DELTAS.items():
        gaps[i] += delta
    assert 4 <= min(gaps) and max(gaps) <= 16
    stages = [0]
    for gap in gaps:
        stages.append(stages[-1] + gap)
    assert stages[129] == 955
    symbols = symbolic_words(0, 2100)
    basis = build_basis(native, tuple(stages), symbols, 0)
    assert len(basis) == 15434
    mappings = {q: donor_mapping(basis, symbols, 955, q) for q in (1409, 1863)}
    assert all(m is not None and len(m) == 128 for m in mappings.values())

    # Positive end-to-end full-state coupon, not derived from selected ACK2.
    planted = random.Random(20261123).getrandbits(19968)
    for pivot in basis:
        planted &= ~(1 << pivot)
    state = full_state(basis, planted)
    planted_coupon = b"".join(
        temper(native_word(state, symbols[955 + p])).to_bytes(4, "little")
        for p in range(4)
    )
    assert planted_coupon != bytes(16)
    for q, mapping in mappings.items():
        donor = sum(native_word(state, symbols[q + p]) << (32 * p) for p in range(4))
        assert map_native(donor, mapping) == planted_coupon

    cohorts = recorder_cohorts(recorder)
    seen = set()
    coupons_by_future_stage = {1409: set(), 1863: set()}
    matches = []
    tested = 0
    permutations = tuple(itertools.permutations(range(4)))
    for group, blocks in cohorts.items():
        for row_idx, block in enumerate(blocks):
            for q, mapping in mappings.items():
                for perm in permutations:
                    for endian in ("little", "big"):
                        for already_native in (False, True):
                            raw_coupon = map_native(
                                donor_bits_from_block(block, perm, endian, already_native), mapping)
                            component = bytes(x ^ y for x, y in zip(raw_coupon, mask))
                            seen.add(component)
                            coupons_by_future_stage[q].add(raw_coupon)
                            tested += 1
                            if hashlib.sha256(component).hexdigest() == K04_SHA:
                                matches.append((group, row_idx, q, perm, endian,
                                                already_native, component.hex().upper()))
    assert tested == 58176 and len(seen) == 45312
    assert [len(coupons_by_future_stage[q]) for q in (1409, 1863)] == [22656, 22656]
    # A genuine paired recorder donor at both future sites must predict the
    # identical selected 16-byte coupon. Search joins by complete coupon.
    paired = coupons_by_future_stage[1409] & coupons_by_future_stage[1863]
    assert not paired, "Two independent recorder future sites predict one coupon"

    # Distinct same-emitter control: the exact 132 original intact printer
    # buffers, as if a native printer buffer were replayed at a later stage.
    # This does not assert a genuine historical replay or shared state.
    original_printer = [
        bytes.fromhex(record[5].decode())
        for i, record in enumerate(rows) if i != 129
    ]
    assert len(original_printer) == len(set(original_printer)) == 132
    printer_seen = set()
    printer_sites = {q: set() for q in mappings}
    printer_hits = []
    printer_tested = 0
    for block in original_printer:
        for q, mapping in mappings.items():
            for perm in permutations:
                for endian in ("little", "big"):
                    for already_native in (False, True):
                        raw_coupon = map_native(
                            donor_bits_from_block(block, perm, endian, already_native), mapping)
                        component = bytes(x ^ y for x, y in zip(raw_coupon, mask))
                        printer_seen.add(component)
                        printer_sites[q].add(raw_coupon)
                        printer_tested += 1
                        if hashlib.sha256(component).hexdigest() == K04_SHA:
                            printer_hits.append((block.hex().upper(), q, perm, endian,
                                                 already_native, component.hex().upper()))
    assert printer_tested == len(printer_seen) == 25344
    assert [len(printer_sites[q]) for q in (1409, 1863)] == [12672, 12672]
    assert not printer_hits
    assert len(printer_seen & seen) == 0
    assert not (printer_sites[1409] & printer_sites[1863])
    assert not ((printer_sites[1409] | coupons_by_future_stage[1409])
                & (printer_sites[1863] | coupons_by_future_stage[1863]))

    # Exact prior Agent10 source block corpus. The existing K05 source
    # quartet is deliberately present in both studies, hence 192 overlap.
    earlier = set()
    for hx in BLOCKS.values():
        block = bytes.fromhex(hx)
        for mapping in mappings.values():
            for perm in permutations:
                for endian in ("little", "big"):
                    for already_native in (False, True):
                        raw_coupon = map_native(
                            donor_bits_from_block(block, perm, endian, already_native), mapping)
                        earlier.add(bytes(x ^ y for x, y in zip(raw_coupon, mask)))
    assert (len(earlier), len(earlier & seen), len(seen - earlier)) == (2112, 192, 45120)
    assert len(earlier & printer_seen) == 0
    assert len((seen | printer_seen) - earlier) == 70464

    assert not matches, "Original K04 hit requires independent source adjudication"
    print(json.dumps({
        "selected_ACK2_payload_decoded": False,
        "recorder_records": 88, "recorder_good_crc": 84,
        "cohort_windows": {k: len(v) for k, v in cohorts.items()},
        "distinct_original_recorder_quartets": 236,
        "target_native_rank_before_donor": 128,
        "target_reaching_future_native_stages": sorted(mappings),
        "synthetic_full_coupon_both_donors": planted_coupon.hex().upper(),
        "whole_original_k04_checks": tested,
        "unique_original_k04_components": len(seen),
        "independent_complete_coupon_predictions_per_future_site": 22656,
        "source_only_same_coupon_dual_recorder_site_matches": len(paired),
        "intact_printer_replay_4fresh_future_checks": printer_tested,
        "intact_printer_replay_unique_components": len(printer_seen),
        "printer_recorder_complete_component_overlap": len(printer_seen & seen),
        "intact_printer_replay_original_k04_matches": printer_hits,
        "all_recorder_printer_cross_site_complete_coupon_joins":
            len((printer_sites[1409] | coupons_by_future_stage[1409])
                & (printer_sites[1863] | coupons_by_future_stage[1863])),
        "all_new_complete_components_relative_to_previous_2112":
            len((seen | printer_seen) - earlier),
        "overlap_with_agent10_previous_components": len(earlier & seen),
        "new_complete_components_relative_to_previous_2112": len(seen - earlier),
        "original_k04_acceptance_matches": matches,
        "shared_printer_recorder_state_authenticated": False,
    }, indent=2))


if __name__ == "__main__":
    main()
