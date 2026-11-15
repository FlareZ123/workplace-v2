#!/usr/bin/env python3
"""Bounded p951 test of TRP2 record-aligned 16-byte donor windows.

Run from the repository root:
    python agents/agent6/k04_p951_trp2_record_window_donor_sft.py

The p951 MT19937 model is conditional, not source-attested. This test asks
whether CRC-valid original recorder records carry its two missing four-word
blocks in a fixed, record-aligned 16-byte field window.
"""
from __future__ import annotations

import hashlib
import json
import random
import struct
import sys
import time
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
sys.path.insert(0, str(ROOT / "agents" / "agent50"))

import k04_p951_symbolic_basis as mt  # noqa: E402
from k04_p951_crossstream_donor_sft import build_candidate_blocks  # noqa: E402


class SmallBasis:
    def __init__(self):
        self.rows = {}

    def insert(self, value: int, rhs: int) -> bool:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = (value, rhs)
                return True
            row, bit = self.rows[pivot]
            value ^= row
            rhs ^= bit
        return rhs == 0

    def predict(self, value: int):
        rhs = 0
        while value:
            pivot = value.bit_length() - 1
            if pivot not in self.rows:
                return None
            row, bit = self.rows[pivot]
            value ^= row
            rhs ^= bit
        return rhs


def temper_int(x: int) -> int:
    y = x
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & 0xFFFFFFFF


def reduce_form(value: int, rhs: int, source_basis):
    remainder = 0
    while value:
        pivot = value.bit_length() - 1
        if pivot in source_basis.rows:
            row, bit = source_basis.rows[pivot]
            value ^= row
            rhs ^= bit
        else:
            remainder |= 1 << pivot
            value ^= 1 << pivot
    return remainder, rhs


def donor_forms(block: bytes, start: int, endian: str, transform: str, sym, source_basis):
    forms = []
    for lane in range(4):
        word = int.from_bytes(block[lane * 4 : lane * 4 + 4], endian)
        native = mt.untemper(word) if transform == "untemper" else word
        for bit, equation in enumerate(mt.get(sym, start + lane)):
            remainder, offset = reduce_form(equation, 0, source_basis)
            forms.append((remainder, ((native >> bit) & 1) ^ offset))
    return forms


def reconstruct(forms_a, forms_b, target_forms, mask: bytes):
    basis = SmallBasis()
    for vector, rhs in forms_a + forms_b:
        if not basis.insert(vector, rhs):
            return None
    raw_bits = []
    for vector, offset in target_forms:
        predicted = basis.predict(vector)
        if predicted is None:
            return None
        raw_bits.append(offset ^ predicted)
    output_words = []
    for lane in range(4):
        native = sum(raw_bits[lane * 32 + bit] << bit for bit in range(32))
        output_words.append(temper_int(native))
    payload = b"".join(word.to_bytes(4, "little") for word in output_words)
    component = bytes(a ^ b for a, b in zip(payload, mask))
    return payload, component, hashlib.sha256(component).hexdigest()


def synthetic_positive(source_basis, sym, target_forms, mask):
    """Plant a source-consistent state and reveal exact native gap blocks."""
    free = set(range(19968)) - set(source_basis.rows)
    assignment = 0
    rng = random.Random(1706)
    for bit in free:
        if rng.getrandbits(1):
            assignment |= 1 << bit
    for pivot in sorted(source_basis.rows):
        row, rhs = source_basis.rows[pivot]
        parity = (row & assignment).bit_count() & 1
        if parity ^ rhs:
            assignment |= 1 << pivot

    def native_block(stage: int) -> bytes:
        output = bytearray()
        for lane in range(4):
            word = 0
            for bit, equation in enumerate(mt.get(sym, stage + lane)):
                word |= ((equation & assignment).bit_count() & 1) << bit
            output.extend(word.to_bytes(4, "little"))
        return bytes(output)

    donor_a = native_block(328)
    donor_b = native_block(724)
    forms_a = donor_forms(donor_a, 328, "little", "raw", sym, source_basis)
    forms_b = donor_forms(donor_b, 724, "little", "raw", sym, source_basis)
    recovered = reconstruct(forms_a, forms_b, target_forms, mask)

    actual_payload = bytearray()
    for stage in range(951, 955):
        native = 0
        for bit, equation in enumerate(mt.get(sym, stage)):
            native |= ((equation & assignment).bit_count() & 1) << bit
        actual_payload.extend(temper_int(native).to_bytes(4, "little"))
    actual_payload = bytes(actual_payload)
    actual_component = bytes(a ^ b for a, b in zip(actual_payload, mask))
    assert recovered is not None
    assert recovered[0] == actual_payload
    assert recovered[1] == actual_component
    return hashlib.sha256(actual_component).hexdigest()


def main():
    started = time.time()
    source_basis, sym = mt.source(ROOT)
    assert source_basis.rank == 15365

    rows, selected_index = mt.packets(ROOT)
    assert len(rows) == 133 and selected_index == 129
    assert mt.STARTS[selected_index] == 951

    blocks, _, _, route, acceptance = build_candidate_blocks()
    prior_blocks = set(blocks.values())
    prior_blocks.update(payload for payload in rows if payload)
    assert len(blocks) == 40

    route_path = ROOT / "resources" / "evidence" / "recovery-routing.json"
    acceptance_path = ROOT / "resources" / "acceptance.json"
    assert hashlib.sha256(route_path.read_bytes()).hexdigest() == (
        "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
    )
    assert hashlib.sha256(acceptance_path.read_bytes()).hexdigest() == (
        "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
    )
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target_hash = acceptance["slot_sha256"]["K04"].lower()

    target_forms = []
    for stage in range(951, 955):
        for equation in mt.get(sym, stage):
            target_forms.append(reduce_form(equation, 0, source_basis))
    assert len(target_forms) == 128

    recorder_path = ROOT / "resources" / "evidence" / "recorder" / "trip-recorder.raw"
    raw = recorder_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
    )
    assert raw[:8] == b"TRP2DUMP"
    _, record_size, count = struct.unpack_from("<HHI", raw, 8)
    assert record_size == 24 and len(raw) == 16 + count * record_size

    records = []
    for index in range(count):
        record = raw[16 + index * record_size : 16 + (index + 1) * record_size]
        ts, node, event, latch, seq, control, aux, stored_crc = struct.unpack(
            "<IHBBI4sII", record
        )
        calculated_crc = zlib.crc32(record[:20]) & 0xFFFFFFFF
        if calculated_crc == stored_crc and node in (49, 50):
            records.append((index, node, event, latch, seq, record))
    assert len(records) == 84

    results = []
    total_assignments = 0
    total_complete = 0
    total_hits = []
    for offset in (0, 4, 8):
        windows = {}
        for index, node, event, latch, seq, record in records:
            block = record[offset : offset + 16]
            label = (
                f"record={index};node={node};event={event};latch={latch};"
                f"seq={seq};offset={offset}"
            )
            windows.setdefault(block, []).append(label)

        assert len(windows) == 84
        overlaps = sum(block in prior_blocks for block in windows)
        novel = {block: labels for block, labels in windows.items() if block not in prior_blocks}
        assert overlaps == 0 and len(novel) == 84

        variants = []
        for block, labels in novel.items():
            for endian in ("little", "big"):
                for transform in ("untemper", "raw"):
                    name = f"{labels[0]}|{endian}|{transform}"
                    variants.append((name, block, endian, transform))
        assert len(variants) == 336

        forms_328 = {}
        forms_724 = {}
        compatible = []
        for name, block, endian, transform in variants:
            a = donor_forms(block, 328, endian, transform, sym, source_basis)
            b = donor_forms(block, 724, endian, transform, sym, source_basis)
            if any(vector == 0 and rhs for vector, rhs in a):
                continue
            if any(vector == 0 and rhs for vector, rhs in b):
                continue
            forms_328[name] = a
            forms_724[name] = b
            compatible.append(name)
        assert len(compatible) == 336

        complete = 0
        hits = []
        for left in compatible:
            for right in compatible:
                candidate = reconstruct(
                    forms_328[left], forms_724[right], target_forms, mask
                )
                if candidate is None:
                    continue
                complete += 1
                if candidate[2] == target_hash:
                    hits.append(
                        {
                            "offset": offset,
                            "donor_a": left,
                            "donor_b": right,
                            "payload": candidate[0].hex(),
                            "component": candidate[1].hex(),
                        }
                    )
        assignments = len(compatible) ** 2
        assert assignments == 112896 and complete == assignments and not hits
        total_assignments += assignments
        total_complete += complete
        total_hits.extend(hits)
        results.append(
            {
                "record_offset": offset,
                "unique_windows": len(windows),
                "overlap_with_prior_donor_blocks_or_intact_printer_payloads": overlaps,
                "novel_windows": len(novel),
                "variants": len(variants),
                "source_compatible_variants": len(compatible),
                "ordered_donor_pairs": assignments,
                "complete_pairs": complete,
                "K04_commitment_hits": len(hits),
            }
        )

    planted_hash = synthetic_positive(source_basis, sym, target_forms, mask)
    assert total_assignments == 338688
    assert total_complete == 338688
    assert not total_hits

    print(
        json.dumps(
            {
                "source_model": "conditional MT19937 p951, selected row129 withheld",
                "source_rank": source_basis.rank,
                "target_native_stages": [951, 952, 953, 954],
                "gap_donor_stages": {"A": [328, 329, 330, 331], "B": [724, 725, 726, 727]},
                "recorder_records_total": count,
                "CRC_valid_node49_or_node50_records": len(records),
                "prior_block_values": len(prior_blocks),
                "per_offset": results,
                "total_ordered_same_offset_pairs": total_assignments,
                "total_complete_pairs": total_complete,
                "original_K04_commitment_hits": len(total_hits),
                "cross_offset_pairs_tested": False,
                "synthetic_positive_control": "PASS",
                "synthetic_component_sha256": planted_hash,
                "elapsed_seconds": round(time.time() - started, 3),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
