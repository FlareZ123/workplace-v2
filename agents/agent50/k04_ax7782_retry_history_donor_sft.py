#!/usr/bin/env python3
"""Source-pinned K04 screen using all AX-7782 chunk retry checkpoints.

The selected ACK2 payload is withheld before decoding. This tests a
hypothetical p951 MT19937 donor construction; it does not authenticate a
common transfer/printer producer or the AX-7782 object chronology.

Run from the repository root:
    python agents/agent50/k04_ax7782_retry_history_donor_sft.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TRANSFER_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
K04_MASK = "8556C8CB6140A7F9A5123AC7571BEE1C"
K04_COMMITMENT = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

spec = importlib.util.spec_from_file_location(
    "agent39_p951_coupon", ROOT / "agents/agent39/k04_p951_seven_donor_affine_sft.py"
)
prior = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(prior)


def selected_withheld_packets() -> list[bytes]:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    lines = [line for line in raw.decode("ascii").splitlines() if line.startswith("2026-")]
    assert len(lines) == 133 and prior.prior.STARTS[129] == 951
    selected = lines[129]
    assert all(token in selected for token in (
        "JOB=PS-261003-0417", "ATTEMPT=2", "STATE=ACK", "CLASS=RECOVER"
    ))
    packets = []
    for index, line in enumerate(lines):
        if index == 129:
            # Do not decode or load the disputed copied ACK2 payload.
            packets.append(b"")
            continue
        match = re.search(r"(?:^|\s)PAYLOAD=([0-9A-F]{32})(?=\s|$)", line)
        assert match is not None, index
        packets.append(bytes.fromhex(match.group(1)))
    return packets


def ax7782_retry_halfwords() -> dict[tuple[int, int], bytes]:
    path = ROOT / "resources/evidence/transfers/transfer-audit.jsonl"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TRANSFER_SHA
    rows = [json.loads(line) for line in raw.decode("ascii").splitlines()]
    selected = [
        row for row in rows
        if row.get("kind") == "CHUNK" and row.get("transfer") == "AX-7782"
    ]
    assert len(selected) == 16
    checkpoints = {
        (row["seq"], row["attempt"]): bytes.fromhex(row["checkpoint"])
        for row in selected
    }
    assert set(checkpoints) == {
        (seq, attempt) for seq in range(8) for attempt in (1, 2)
    }
    assert all(len(value) == 2 for value in checkpoints.values())
    return checkpoints


def ax_word_views(checkpoints):
    arrangements = {
        "seq_major": [
            checkpoints[(seq, attempt)]
            for seq in range(8) for attempt in (1, 2)
        ],
        "attempt_major": [
            checkpoints[(seq, attempt)]
            for attempt in (1, 2) for seq in range(8)
        ],
    }
    views = []
    for arrangement, halfwords in arrangements.items():
        for pair_reverse in (False, True):
            ordered = (
                halfwords if not pair_reverse else
                [value for i in range(0, 16, 2)
                 for value in (halfwords[i + 1], halfwords[i])]
            )
            raw_words = [
                ordered[i] + ordered[i + 1] for i in range(0, 16, 2)
            ]
            for endian in ("big", "little"):
                values = [int.from_bytes(word, endian) for word in raw_words]
                for reverse in (False, True):
                    ordered_values = values[::-1] if reverse else values
                    for is_tempered in (False, True):
                        native = (
                            [prior.prior.untemper(value) for value in ordered_values]
                            if is_tempered else ordered_values
                        )
                        views.append((
                            arrangement, pair_reverse, endian, reverse,
                            is_tempered, native
                        ))
    assert len(views) == 32
    return views


def source_block_views(block: bytes):
    assert len(block) == 16
    result = []
    for endian in ("big", "little"):
        values = [
            int.from_bytes(block[i:i + 4], endian)
            for i in range(0, 16, 4)
        ]
        for reverse in (False, True):
            ordered = values[::-1] if reverse else values
            for is_tempered in (False, True):
                native = (
                    [prior.prior.untemper(value) for value in ordered]
                    if is_tempered else ordered
                )
                result.append((endian, reverse, is_tempered, native))
    assert len(result) == 8
    return result


def main() -> None:
    acceptance_path = ROOT / "resources/acceptance.json"
    route_path = ROOT / "resources/evidence/recovery-routing.json"
    assert hashlib.sha256(acceptance_path.read_bytes()).hexdigest() == ACCEPTANCE_SHA
    assert hashlib.sha256(route_path.read_bytes()).hexdigest() == ROUTE_SHA
    acceptance = json.loads(acceptance_path.read_text())
    route = json.loads(route_path.read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    commitment = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    assert mask.hex().upper() == K04_MASK
    assert commitment.hex() == K04_COMMITMENT

    expressions = prior.express()
    # Re-run the established seven seeded full-stream controls for the
    # source-constrained 224-to-128 inverse before using it on originals.
    prior.positive_controls(expressions)
    packets = selected_withheld_packets()
    coupon_map = prior.make_coupon_map(expressions, packets)

    # Reuse the six source-derived groups. K07raw is omitted as a separate
    # donor because its attempt-2 halfwords are already embedded in AX-7782.
    groups = prior.preserved_groups()
    groups = {name: block for name, block in groups.items() if name != "K07raw"}
    assert set(groups) == {"WN14", "K02raw", "PTW417", "K05raw", "K06raw"}
    other_views = {
        name: source_block_views(block) for name, block in groups.items()
    }
    ax_views = ax_word_views(ax7782_retry_halfwords())

    def component(donors, output_endian):
        native = prior.select_native(coupon_map, donors)
        payload = b"".join(
            prior.temper(value).to_bytes(4, output_endian) for value in native
        )
        return bytes(a ^ b for a, b in zip(payload, mask))

    # First: all eight AX-derived words alone, omitting one to supply seven.
    ax_only = set()
    ax_only_hits = []
    for ax_meta in ax_views:
        for omitted in range(8):
            donors = [
                value for index, value in enumerate(ax_meta[5])
                if index != omitted
            ]
            for output_endian in ("little", "big"):
                candidate = component(donors, output_endian)
                ax_only.add(candidate)
                if hashlib.sha256(candidate).digest() == commitment:
                    ax_only_hits.append((ax_meta[:5], omitted, output_endian))

    # Second: AX supplies either the three consecutive donors or the four
    # separated donors; a non-overlapping source block supplies the remainder.
    cross_source = set()
    cross_source_hits = []
    for ax_meta in ax_views:
        ax_values = ax_meta[5]

        for window_start in range(6):
            ax_three = ax_values[window_start:window_start + 3]
            for source_name, views in other_views.items():
                for source_meta in views:
                    source_four = source_meta[3]
                    for output_endian in ("little", "big"):
                        candidate = component(ax_three + source_four, output_endian)
                        cross_source.add(candidate)
                        if hashlib.sha256(candidate).digest() == commitment:
                            cross_source_hits.append((
                                "AX-three", ax_meta[:5], window_start,
                                source_name, source_meta[:3], output_endian
                            ))

        for window_start in range(5):
            ax_four = ax_values[window_start:window_start + 4]
            for source_name, views in other_views.items():
                for source_meta in views:
                    source_values = source_meta[3]
                    for pick in ("first", "last"):
                        source_three = (
                            source_values[:3] if pick == "first"
                            else source_values[1:]
                        )
                        for output_endian in ("little", "big"):
                            candidate = component(
                                source_three + ax_four, output_endian
                            )
                            cross_source.add(candidate)
                            if hashlib.sha256(candidate).digest() == commitment:
                                cross_source_hits.append((
                                    "AX-four", ax_meta[:5], window_start,
                                    source_name, source_meta[:3], pick,
                                    output_endian
                                ))

    combined = ax_only | cross_source
    assert len(ax_only) == 484
    assert len(cross_source) == 38720
    assert len(combined) == 39204
    assert not ax_only_hits and not cross_source_hits

    print(json.dumps({
        "selected_ACK2_payload_decoded": False,
        "AX7782_attempt_rows": 16,
        "AX_word_views": len(ax_views),
        "nonoverlapping_source_blocks": sorted(groups),
        "AX_only_candidate_presentations": 512,
        "AX_only_distinct_components": len(ax_only),
        "cross_source_candidate_presentations": 40960,
        "cross_source_distinct_components": len(cross_source),
        "total_candidate_presentations": 41472,
        "total_distinct_components": len(combined),
        "original_K04_commitment_matches": 0,
        "seven_seeded_full_stream_controls": "7/7 PASS",
        "historical_AX_printer_producer_link_authenticated": False
    }, indent=2))


if __name__ == "__main__":
    main()
