#!/usr/bin/env python3
"""Source-bound K04 commitment scan for an original Windows SPL/SHD pair.

This composes the existing SPL/SHD pairer with the exact 16-byte K04
commitment-window scanner. It does not infer a job from a filename: the SHD
must contain the requested job ID, the SPL/SHD pair must share the pairer's
container/path/stem key, and the candidate must satisfy the pinned K04 SHA256
after the exact route-mask operation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = ROOT / "work"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(WORK_DIR) not in sys.path:
    sys.path.insert(0, str(WORK_DIR))

from agents.agent43 import h17_native_spool_pair_intake as pairer
from h17_k04_binary_window_intake import scan_bytes


class RawIntake(pairer.Intake):
    """Retain bounded SPL/SHD bytes in memory for the commitment scan."""

    def add(self, name, container, parent, data):
        before = len(self.members)
        super().add(name, container, parent, data)
        if len(self.members) > before:
            self.members[-1]["data"] = data


def scan_intake(intake, job_id: str, target_digest: bytes, mask: bytes):
    pairs, unpaired, ambiguous = pairer.pair_members(intake.members)
    matching = [
        pair for pair in pairs
        if job_id in pair["job_id_strings_in_shd"]
    ]
    pair_reports = []
    candidate_hits = []
    for pair in matching:
        spl = pair["spl"]
        hits = scan_bytes(
            spl["name"], spl["data"], target_digest, mask, stride=1
        )
        pair_reports.append({
            "container": pair["container"],
            "parent": pair["parent"],
            "normalized_stem": pair["normalized_stem"],
            "pairing_basis": pair["pairing_basis"],
            "job_id_strings_in_shd": pair["job_id_strings_in_shd"],
            "spl": {
                "name": spl["name"], "size": spl["size"],
                "sha256": spl["sha256"],
            },
            "shd": {
                "name": pair["shd"]["name"], "size": pair["shd"]["size"],
                "sha256": pair["shd"]["sha256"],
            },
            "candidate_hits": hits,
        })
        for hit in hits:
            candidate_hits.append({
                **hit,
                "container": pair["container"],
                "parent": pair["parent"],
                "normalized_stem": pair["normalized_stem"],
                "spl_sha256": spl["sha256"],
                "shd_sha256": pair["shd"]["sha256"],
                "job_id_strings_in_shd": pair["job_id_strings_in_shd"],
            })
    components = sorted({hit["component_hex"] for hit in candidate_hits})
    unique_pair = len(matching) == 1 and not any(
        item.get("key") == (
            matching[0]["container"], matching[0]["parent"],
            matching[0]["normalized_stem"]
        ) for item in ambiguous
    ) if matching else False
    recovered = unique_pair and len(components) == 1
    return {
        "job_id": job_id,
        "paired_member_count": len(pairs),
        "matching_job_pairs": len(matching),
        "ambiguous_pair_groups": len(ambiguous),
        "unpaired_member_count": len(unpaired),
        "pair_reports": pair_reports,
        "candidate_hits": candidate_hits,
        "distinct_component_hex": components,
        "component_hex": components[0] if recovered else None,
        "component_sha256": hashlib.sha256(bytes.fromhex(components[0])).hexdigest()
            if recovered else None,
        "recovered": recovered,
        "status": "K04 component recovered from job-ID-paired SPL"
            if recovered else "no unique commitment-matching component in a unique job-ID-paired SPL",
        "limitations": [
            "The SHD job-ID string plus exact container/path/stem pairing is a candidate job association, not a full undocumented SHD parse.",
            "Class, destination, attempt and ACK state are not inferred from an SPL filename; preserve independent queue/dispatch evidence.",
            "A matching SHA256 establishes the 16-byte component, while historical event attribution still depends on the paired source records.",
            "No source member is extracted to disk or modified.",
        ],
    }


def scan_source_path(source: Path, job_id: str, target_digest: bytes, mask: bytes):
    patterns = [
        ("job:" + job_id, job_id.encode("ascii")),
        ("job-utf16:" + job_id, job_id.encode("utf-16le")),
    ]
    intake = RawIntake(patterns)
    intake.walk_path(source)
    result = scan_intake(intake, job_id, target_digest, mask)
    result.update({
        "source": str(source),
        "members_scanned": len(intake.members),
        "total_spool_member_bytes_scanned": intake.spool_bytes,
        "total_archive_member_bytes_scanned": intake.archive_bytes,
        "errors": intake.errors,
    })
    return result


def self_test():
    mask = bytes.fromhex("102030405060708090A0B0C0D0E0F001")
    component = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    payload = bytes(a ^ b for a, b in zip(component, mask))
    target = hashlib.sha256(component).digest()
    job_id = "PS-261003-0417"
    import io
    import zipfile
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("spool/0417.SPL", b"prefix" + payload + b"suffix")
        archive.writestr("spool/0417.SHD", job_id.encode("ascii"))
        archive.writestr("decoy/0417.SPL", b"unrelated bytes")
        archive.writestr("decoy/0417.SHD", b"PS-261003-0999")
    intake = RawIntake([
        ("job:" + job_id, job_id.encode("ascii")),
        ("job-utf16:" + job_id, job_id.encode("utf-16le")),
    ])
    intake.walk_bytes("synthetic.zip", "synthetic.zip", buffer.getvalue())
    result = scan_intake(intake, job_id, target, mask)
    assert result["recovered"], result
    assert result["component_hex"] == component.hex().upper(), result
    assert len(result["candidate_hits"]) == 1, result
    return {
        "passed": True,
        "matching_pairs": result["matching_job_pairs"],
        "component_hex": result["component_hex"],
        "candidate_offset": result["candidate_hits"][0]["offset"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        help="authorized original spool directory/archive or a single SPL/SHD file")
    parser.add_argument("--job-id", default="PS-261003-0417")
    parser.add_argument("--evidence-root", type=Path, default=ROOT / "resources/evidence")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"synthetic_test": self_test()}, indent=2))
        return
    if not args.source:
        parser.error("--source is required unless --self-test is used")
    payloads, mask, _nonce = pairer.read_evidence(args.evidence_root)
    acceptance_path = args.evidence_root.parent / "acceptance.json"
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    result = scan_source_path(args.source, args.job_id, target, mask)
    result["evidence_pins_verified"] = True
    print(json.dumps(result, indent=2))
    if result["recovered"]:
        print("K04_COMPONENT_RECOVERED", result["component_hex"])


if __name__ == "__main__":
    main()
