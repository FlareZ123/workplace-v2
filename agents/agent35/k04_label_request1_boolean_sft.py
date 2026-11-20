#!/usr/bin/env python3
"""Source-causal two-input Boolean construction for K04 (PS-0417).

Changed assumption: the physical ESC-N coupon payload could be a deterministic
four-lane Boolean combination of the two same-job records that precede the
selected attempt-2 ACK: the earlier LABEL/ACK and RECOVER/REQUESTED1 rows.

The selected ACK2 payload is withheld from candidate construction. It is used
only for an observational per-lane fit diagnostic. Candidate checks cover
all 16 two-input Boolean truth tables independently in each of four 32-bit
lanes, both common byte orders, and both direct / XOR-mask component stages.
No original evidence or acceptance file is modified.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from pathlib import Path
from zipfile import ZipFile

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK32 = (1 << 32) - 1


def read_source(path: str, root: Path, archive: ZipFile | None) -> bytes:
    if archive is not None:
        return archive.read(path)
    return (root / "resources" / path).read_bytes()


def truth32(a: int, b: int, code: int) -> int:
    buckets = (
        (~a & ~b) & MASK32,
        (~a & b) & MASK32,
        (a & ~b) & MASK32,
        (a & b) & MASK32,
    )
    return sum(value for index, value in enumerate(buckets) if code & (1 << index))


def construct(a: bytes, b: bytes, ops: tuple[int, ...], endian: str) -> bytes:
    output = bytearray()
    for lane, code in enumerate(ops):
        left = int.from_bytes(a[4 * lane : 4 * lane + 4], endian)
        right = int.from_bytes(b[4 * lane : 4 * lane + 4], endian)
        output.extend(truth32(left, right, code).to_bytes(4, endian))
    return bytes(output)


def per_lane_observed_fit(a: bytes, b: bytes, observed: bytes, endian: str) -> list[list[int]]:
    fits = []
    for lane in range(4):
        left = int.from_bytes(a[4 * lane : 4 * lane + 4], endian)
        right = int.from_bytes(b[4 * lane : 4 * lane + 4], endian)
        target = int.from_bytes(observed[4 * lane : 4 * lane + 4], endian)
        fits.append([code for code in range(16) if truth32(left, right, code) == target])
    return fits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", type=Path, help="optional original archive ZIP")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    archive = ZipFile(args.zip) if args.zip else None
    try:
        spool = read_source("evidence/print/spool-reconstruction.log", args.root, archive)
        route = json.loads(read_source("evidence/recovery-routing.json", args.root, archive))
        acceptance = json.loads(read_source("acceptance.json", args.root, archive))
    finally:
        if archive is not None:
            archive.close()

    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA256
    lines = [line for line in spool.decode("ascii").splitlines() if "JOB=PS-261003-0417 " in line]
    assert len(lines) == 4, len(lines)
    assert "ATTEMPT=1 STATE=ACK CLASS=LABEL" in lines[0]
    assert "ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER" in lines[1]
    assert "ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[2]
    assert "ATTEMPT=3 STATE=REQUESTED CLASS=RECOVER" in lines[3]
    assert lines[0].startswith("2026-10-03T16:45:00")
    assert lines[1].startswith("2026-10-03T18:01:00")
    assert lines[2].startswith("2026-10-03T18:02:00")

    payloads = [bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1)) for line in lines]
    earlier_label, recover_request1, selected_ack2 = payloads[:3]
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])

    # Validate the complete truth-table implementation on all four binary inputs.
    truth_table_tests = 0
    for code in range(16):
        for left, right in itertools.product((0, MASK32), repeat=2):
            expected = MASK32 if (code >> (2 * bool(left) + bool(right))) & 1 else 0
            assert truth32(left, right, code) == expected
            truth_table_tests += 1

    results = {}
    total_candidates = 0
    for endian, planted_ops in (("little", (1, 6, 9, 14)), ("big", (2, 5, 10, 13))):
        observed_fit = per_lane_observed_fit(earlier_label, recover_request1, selected_ack2, endian)
        planted_coupon = construct(earlier_label, recover_request1, planted_ops, endian)
        planted_component = bytes(x ^ y for x, y in zip(planted_coupon, mask))
        planted_digest = hashlib.sha256(planted_component).digest()
        original_hits = []
        planted_hits = []
        candidates = 0

        for ops in itertools.product(range(16), repeat=4):
            coupon = construct(earlier_label, recover_request1, ops, endian)
            for stage, component in (
                ("coupon_xor_mask", bytes(x ^ y for x, y in zip(coupon, mask))),
                ("direct_component", coupon),
            ):
                digest = hashlib.sha256(component).digest()
                candidates += 1
                if digest == target:
                    original_hits.append({"ops": ops, "stage": stage, "component": component.hex().upper()})
                if digest == planted_digest:
                    planted_hits.append({"ops": ops, "stage": stage, "component": component.hex().upper()})

        assert candidates == 131072
        assert planted_hits == [{"ops": planted_ops, "stage": "coupon_xor_mask", "component": planted_component.hex().upper()}]
        total_candidates += candidates
        results[endian] = {
            "observed_ack2_per_lane_truth_table_fits": observed_fit,
            "candidates": candidates,
            "original_k04_hits": original_hits,
            "planted_ops": planted_ops,
            "planted_positive_hits": planted_hits,
        }

    assert total_candidates == 262144
    print(json.dumps({
        "changed_assumption": "ACK2 coupon may be a four-lane Boolean transform of the two causally prior same-job records LABEL/ACK1 and RECOVER/REQUESTED1",
        "spool_sha256": SPOOL_SHA256,
        "selected_ack2_used_for_candidate_generation": False,
        "source_pair": {
            "earlier_label_ack": earlier_label.hex().upper(),
            "recover_requested1": recover_request1.hex().upper(),
            "selected_ack2_observed_only": selected_ack2.hex().upper(),
        },
        "truth_table_binary_tests": truth_table_tests,
        "total_complete_candidates": total_candidates,
        "results_by_endian": results,
    }, indent=2))


if __name__ == "__main__":
    main()
