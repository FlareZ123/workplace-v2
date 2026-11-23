#!/usr/bin/env python3
"""Read-only K04 exact-commitment SPL scan with separate SHD source attribution.

Every bounded SPL member is scanned for the original 16-byte component
commitment after the specified route XOR. SHD literal job identifiers and
same-stem pairing provide context, but are never required for a hash hit.
Historical physical event attribution remains a separate evidentiary question.
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
from agents.agent43 import h17_native_spool_pair_intake as pairer


def _scan_spl_bytes(name: str, data: bytes, target_digest: bytes, mask: bytes):
    """Apply existing exact K04 native/rendered-media decoder to each SPL."""
    added = str(WORK_DIR) not in sys.path
    if added:
        sys.path.insert(0, str(WORK_DIR))
    try:
        from h17_k04_binary_window_intake import scan_member

        report = scan_member(
            name, data, 0, [0, pairer.MAX_TOTAL, 0, 10000],
            target_digest, mask, 1, pairer.MAX_MEMBER, 4
        )

        def hits_under(node):
            hits = list(node.get("hits", ()))
            for member in node.get("members", ()):
                hits.extend(hits_under(member))
            return hits

        return hits_under(report)
    finally:
        if added:
            sys.path.remove(str(WORK_DIR))



class RawIntake(pairer.Intake):
    """Retain bounded SPL/SHD bytes in memory for the commitment scan."""

    def add(self, name, container, parent, data):
        before = len(self.members)
        super().add(name, container, parent, data)
        if len(self.members) > before:
            self.members[-1]["data"] = data


def scan_intake(intake, job_id: str, target_digest: bytes, mask: bytes):
    """Find exact K04 matches first; record native job attribution separately."""
    pairs, unpaired, ambiguous = pairer.pair_members(intake.members)
    matching = [pair for pair in pairs if job_id in pair["job_id_strings_in_shd"]]
    paired_by_member = {id(pair["spl"]): pair for pair in pairs}
    pair_reports = []
    candidate_hits = []
    for spl in intake.members:
        if spl["ext"] != "SPL":
            continue
        pair = paired_by_member.get(id(spl))
        hits = _scan_spl_bytes(spl["name"], spl["data"], target_digest, mask)
        if not hits and pair not in matching:
            continue
        job_strings = pair["job_id_strings_in_shd"] if pair else []
        pair_reports.append({
            "container": spl["container"], "parent": spl["parent"],
            "normalized_stem": spl["normalized_stem"],
            "pairing_basis": pair["pairing_basis"] if pair else None,
            "job_id_strings_in_shd": job_strings,
            "job_id_literal_present": job_id in job_strings,
            "spl": {
                "name": spl["name"], "size": spl["size"],
                "sha256": spl["sha256"],
            },
            "shd": {
                "name": pair["shd"]["name"], "size": pair["shd"]["size"],
                "sha256": pair["shd"]["sha256"],
            } if pair else None,
            "candidate_hits": hits,
        })
        for hit in hits:
            candidate_hits.append({
                **hit,
                "container": spl["container"], "parent": spl["parent"],
                "normalized_stem": spl["normalized_stem"],
                "spl_sha256": spl["sha256"],
                "shd_sha256": pair["shd"]["sha256"] if pair else None,
                "job_id_strings_in_shd": job_strings,
                "job_id_literal_present": job_id in job_strings,
            })
    components = sorted({hit["component_hex"] for hit in candidate_hits})
    recovered = len(components) == 1
    attributed = recovered and any(hit["job_id_literal_present"] for hit in candidate_hits)
    return {
        "job_id": job_id,
        "paired_member_count": len(pairs),
        "matching_job_pairs": len(matching),
        "ambiguous_pair_groups": len(ambiguous),
        "unpaired_member_count": len(unpaired),
        "spl_members_scanned": sum(item["ext"] == "SPL" for item in intake.members),
        "pair_reports": pair_reports,
        "candidate_hits": candidate_hits,
        "distinct_component_hex": components,
        "component_hex": components[0] if recovered else None,
        "component_sha256": hashlib.sha256(bytes.fromhex(components[0])).hexdigest()
            if recovered else None,
        "recovered": recovered,
        "job_id_literal_at_matching_source": attributed,
        "historical_event_attribution_verified": False,
        "status": (
            "K04 exact commitment matched; accompanying SHD mentions logical job; confirm event separately"
            if attributed else
            "K04 exact commitment matched; original job association unverified"
            if recovered else
            "no unique commitment-matching component in scanned SPL members"
        ),
        "limitations": [
            "The full original K04 SHA256 is tested against every bounded SPL member, with or without SHD or a literal PS job ID.",
            "Same-stem pairing and a literal job-ID string do not prove route, RECOVER class, attempt 2, or ACK state.",
            "Corroborate historical event attribution with a contemporaneous queue/dispatch manifest.",
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
    """Test complete K04 value recovery with and without source job labels."""
    mask = bytes.fromhex("102030405060708090A0B0C0D0E0F001")
    component = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    payload = bytes(a ^ b for a, b in zip(component, mask))
    target = hashlib.sha256(component).digest()
    job_id = "PS-261003-0417"
    import io
    import zipfile

    def intake_zip(members):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, value in members:
                archive.writestr(name, value)
        intake = RawIntake([
            ("job:" + job_id, job_id.encode("ascii")),
            ("job-utf16:" + job_id, job_id.encode("utf-16le")),
        ])
        intake.walk_bytes("synthetic.zip", "synthetic.zip", stream.getvalue())
        return scan_intake(intake, job_id, target, mask)

    labelled = intake_zip([
        ("spool/0417.SPL", b"prefix" + payload + b"suffix"),
        ("spool/0417.SHD", job_id.encode("ascii")),
        ("decoy/0417.SPL", b"unrelated bytes"),
        ("decoy/0417.SHD", b"PS-261003-0999"),
    ])
    assert labelled["recovered"] and labelled["job_id_literal_at_matching_source"], labelled
    assert labelled["component_hex"] == component.hex().upper(), labelled
    assert len(labelled["candidate_hits"]) == 1, labelled

    # The genuine matching SPL may have only native numeric metadata in SHD.
    # An unrelated SHD that mentions the PS label must not preselect the decoy.
    unlabelled = intake_zip([
        ("spool/0007.SPL", b"before" + payload + b"after"),
        ("spool/0007.SHD", bytes.fromhex("070013000200A5F9")),
        ("decoy/0417.SPL", b"unrelated bytes"),
        ("decoy/0417.SHD", job_id.encode("ascii")),
    ])
    assert unlabelled["recovered"] and not unlabelled["job_id_literal_at_matching_source"], unlabelled
    assert unlabelled["matching_job_pairs"] == 1, unlabelled
    assert unlabelled["component_hex"] == component.hex().upper(), unlabelled

    # A spool file can survive even if its associated SHD was not retained.
    unpaired = intake_zip([("spool/0007.SPL", b"prefix" + payload + b"suffix")])
    assert unpaired["recovered"] and unpaired["matching_job_pairs"] == 0, unpaired
    assert unpaired["candidate_hits"][0]["shd_sha256"] is None, unpaired

    # A native XPS-spooled .SPL can begin with ZIP/OPC magic; the pairer must
    # retain its SPL identity and the decoder must join split page glyph runs.
    xps = io.BytesIO()
    ns = "http://schemas.microsoft.com/xps/2005/06"
    printed_hex = payload.hex().upper()
    with zipfile.ZipFile(xps, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
        package.writestr(
            "Documents/1/Pages/1.fpage",
            f'<FixedPage xmlns="{ns}"><Glyphs UnicodeString="{printed_hex[:16]}"/>'
            f'<Glyphs UnicodeString="{printed_hex[16:]}"/></FixedPage>',
        )
    xps_pair = intake_zip([
        ("spool/0042.SPL", xps.getvalue()),
        ("spool/0042.SHD", job_id.encode("utf-16le")),
    ])
    assert xps_pair["recovered"] and xps_pair["paired_member_count"] == 1, xps_pair
    assert any(
        "xps-page-1-joined" in hit["source"]
        and hit["component_hex"] == component.hex().upper()
        for hit in xps_pair["candidate_hits"]
    ), xps_pair

    return {
        "passed": True,
        "complete_commitment_cases": 4,
        "matching_pairs": labelled["matching_job_pairs"],
        "candidate_offset": labelled["candidate_hits"][0]["offset"],
        "literal_matched": labelled["job_id_literal_at_matching_source"],
        "unlabelled_pair_recovered": unlabelled["recovered"],
        "unpaired_spl_recovered": unpaired["recovered"],
        "native_xps_spool_recovered": xps_pair["recovered"],
        "component_hex": labelled["component_hex"],
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
