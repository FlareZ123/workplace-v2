"""K04/K08 original ZIP container-carrier completeness check.

Reads original supplied ZIP as bytes, independently of decompressed file bodies.
Checks K04 coupon, alternate mask and direct precomputed K04/K08 component,
plus four adjacent member-header CRC32 values in four serialization views.
All original commitments and verifier are unchanged. One planted positive.
Pass the unmodified H17 ZIP path as the single argument.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

PIN = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
SPOOL_PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
P = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")

def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def run(source: Path) -> None:
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    direct = {raw[i:i + 16]: ("raw", i) for i in range(len(raw) - 15)}
    assert len(raw) == 50526
    hex_assignments = 0
    for match in re.finditer(rb"[A-Fa-f0-9]{32,}", raw):
        for offset in range(len(match.group()) - 31):
            candidate = bytes.fromhex(match.group()[offset:offset + 32].decode("ascii"))
            direct.setdefault(candidate, ("hex", match.start() + offset))
            hex_assignments += 1

    with zipfile.ZipFile(source) as archive:
        names = [n for n in archive.infolist() if not n.is_dir()]
        assert len(names) == 46
        spool = archive.read("evidence/print/spool-reconstruction.log")
        assert hashlib.sha256(spool).hexdigest() == SPOOL_PIN
        assert b"2026-10-03T18:02:00Z JOB=PS-261003-0417" in spool
        assert P.hex().upper().encode() in spool
        mask = bytes.fromhex(json.loads(archive.read("evidence/recovery-routing.json"))["K04"]["masked_component"])
        acceptance = json.loads(archive.read("acceptance.json"))
        targets = {bytes.fromhex(acceptance["slot_sha256"][k]) for k in ("K04", "K08")}
        crc = {}
        for start in range(len(names) - 3):
            words = [n.CRC for n in names[start:start + 4]]
            for endian in ("little", "big"):
                for backward in (False, True):
                    serial = b"".join(v.to_bytes(4, endian) for v in (words[::-1] if backward else words))
                    crc.setdefault(serial, ("crc", start, endian, backward))

        original_member_carriers = {}
        for member in names:
            contents = archive.read(member)
            for offset in range(len(contents) - 15):
                original_member_carriers.setdefault(contents[offset:offset + 16], member.filename)
            for match in re.finditer(rb"[A-Fa-f0-9]{32,}", contents):
                for offset in range(len(match.group()) - 31):
                    val = bytes.fromhex(match.group()[offset:offset + 32].decode("ascii"))
                    original_member_carriers.setdefault(val, member.filename)

    hits = []
    for carrier, provenance in {**direct, **crc}.items():
        for stage, component in (
            ("physical_coupon", xor(carrier, mask)),
            ("alternative_mask", xor(P, carrier)),
            ("direct_component", carrier),
        ):
            if hashlib.sha256(component).digest() in targets:
                hits.append((stage, provenance, component.hex().upper()))
    planted = next(value for value in direct if value not in original_member_carriers
                   and direct[value][0] == "raw")
    planted_hash = hashlib.sha256(xor(planted, mask)).digest()
    control_hits = sum(hashlib.sha256(xor(value, mask)).digest() == planted_hash for value in direct)
    result = {
        "zip_bytes": len(raw), "raw_windows": len(raw) - 15,
        "hex_windows": hex_assignments, "distinct_zip_carriers": len(direct),
        "distinct_crc4_carriers": len(crc),
        "prior_member_carriers": len(original_member_carriers),
        "zip_member_overlap": len(set(direct) & set(original_member_carriers)),
        "zip_only_new_carriers": len(set(direct) - set(original_member_carriers)),
        "crc_prior_member_overlap": len(set(crc) & set(original_member_carriers)),
        "crc_zip_overlap": len(set(crc) & set(direct)),
        "original_commitment_hits": hits,
        "planted_positive_count": control_hits,
    }
    assert result == {
        "zip_bytes": 50526, "raw_windows": 50511,
        "hex_windows": 0, "distinct_zip_carriers": 44635,
        "distinct_crc4_carriers": 172,
        "prior_member_carriers": 67470, "zip_member_overlap": 40,
        "zip_only_new_carriers": 44595, "crc_prior_member_overlap": 0,
        "crc_zip_overlap": 0, "original_commitment_hits": [],
        "planted_positive_count": 1,
    }, result
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    assert len(sys.argv) == 2
    run(Path(sys.argv[1]))
