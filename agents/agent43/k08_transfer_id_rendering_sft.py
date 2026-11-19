#!/usr/bin/env python3
"""Reproduce K08 LOW BIT values for source-exact transfer-ID renderings.

Read-only and stdlib-only. Reads the four transfer IDs from the retained
transfer audit and the source-selected ID from MAIL-13. It reports the full
hyphenated ID, compact ID, prefix, and numeric suffix under forward/reversed
numeric digits and LSB/MSB character-bit weighting. It does not choose a
rendering or assert a K08 recovery.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "resources/evidence/transfers/transfer-audit.jsonl"
MAIL13 = ROOT / "resources/evidence/mail/13.eml"
EXPECTED_AUDIT_SHA256 = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
EXPECTED_MAIL13_SHA256 = "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pack_lowbits(value: str, lsb_first: bool) -> tuple[str, int]:
    bits = [ord(char) & 1 for char in value]
    if lsb_first:
        packed = sum(bit << index for index, bit in enumerate(bits))
    else:
        packed = sum(bit << (len(bits) - 1 - index) for index, bit in enumerate(bits))
    return "".join(map(str, bits)), packed


def variants(identifier: str) -> dict[str, dict[str, dict[str, int | str]]]:
    prefix, suffix = identifier.split("-", 1)
    forms = {
        "full_hyphenated": (prefix + "-" + suffix, prefix + "-" + suffix[::-1]),
        "compact": (prefix + suffix, prefix + suffix[::-1]),
        "prefix": (prefix, prefix),
        "numeric_suffix": (suffix, suffix[::-1]),
    }
    out = {}
    for form, (forward, reverse) in forms.items():
        out[form] = {}
        for direction, value in (("forward", forward), ("reverse_digits", reverse)):
            if form == "prefix" and direction == "reverse_digits":
                continue
            lsb_bits, lsb_value = pack_lowbits(value, True)
            msb_bits, msb_value = pack_lowbits(value, False)
            out[form][direction] = {
                "rendered": value,
                "ascii_lsb_stream": lsb_bits,
                "lsb_first_value": lsb_value,
                "msb_first_value": msb_value,
            }
    return out


def main() -> None:
    if sha256(AUDIT) != EXPECTED_AUDIT_SHA256:
        raise SystemExit("transfer-audit.jsonl hash mismatch")
    if sha256(MAIL13) != EXPECTED_MAIL13_SHA256:
        raise SystemExit("MAIL-13 hash mismatch")

    identifiers = set()
    for line in AUDIT.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        identifier = record.get("transfer")
        if isinstance(identifier, str) and re.fullmatch(r"AX-\d{4}", identifier):
            identifiers.add(identifier)
    selected_match = re.search(
        r"The final custodian handoff is (AX-\d{4})",
        MAIL13.read_text(encoding="utf-8"),
    )
    if not selected_match:
        raise SystemExit("MAIL-13 source-selected transfer ID not found")
    selected = selected_match.group(1)
    if selected not in identifiers:
        raise SystemExit("MAIL-13 selected ID is absent from transfer audit")

    print(json.dumps({
        "audit_sha256": EXPECTED_AUDIT_SHA256,
        "mail13_sha256": EXPECTED_MAIL13_SHA256,
        "source_selected_id": selected,
        "transfer_ids": {identifier: variants(identifier) for identifier in sorted(identifiers)},
        "method": "ASCII character LSB stream; first character weighted as bit 0 or as the most significant bit; reverse only numeric digits for direction control",
        "interpretation": "rendering sensitivity only; source supplies full hyphenated IDs and does not select a normalization",
    }, indent=2))


if __name__ == "__main__":
    main()
