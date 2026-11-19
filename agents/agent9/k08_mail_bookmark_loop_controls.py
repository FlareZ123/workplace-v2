#!/usr/bin/env python3
"""Reproduce the K05 -> MAIL03/C -> MAIL09 -> bookmark-3 -> MAIL13 -> AX-7782 loop.

Run from the workplace-v2 repository root:
    python agents/agent9/k08_mail_bookmark_loop_controls.py
This is a locator/control analysis, not proof that the physical receipt and browser
bookmark are the same object, and not a K08 phrase recovery.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources/evidence"
EXPECTED = {
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
    "recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "mail/01.eml": "df0729237a3d6d5e90bcaffa95b396d54e511007ec4b0c7e5e8490280aa1d698",
    "mail/02.eml": "a4ac849e45362b93eea9950e61132213494ab3a7cc3967e353850dc221de3a11",
    "mail/03.eml": "3cf886c12e094cb0362999c5a4d93f913c848a64471f833fbddbfdc2d57ff889",
    "mail/04.eml": "c9e83a610f9240c3abd4b4d435588bd9056de34edf6fa3e6d7aca88d8a21f439",
    "mail/05.eml": "29d6d60c6addc16b6f3fd1803b582481a22ce0e757e0a1601a3dc7e116730272",
    "mail/06.eml": "6049994562a82e46afd3f0231e136a1e6911cc3040d848e32eaa5771a6f8c2f3",
    "mail/07.eml": "ee0830aba2e08cc862179aeca034e075f76a08914e5ee6d604ad17f4b806ac22",
    "mail/08.eml": "2da71346103454b6743698103f4d80d79bc0b6013046646e4611c08e8d5f0937",
    "mail/09.eml": "1bda8bbf1e7b661a04fd58c36c38f2b66d2e2410265c311cc09c8e2bf810f08c",
    "mail/10.eml": "ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48",
    "mail/11.eml": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "mail/12.eml": "4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd",
    "mail/13.eml": "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
    "mail/14.eml": "9c86de086a1727ca09b4df6f12cf5c634eaa22a3949424171cc50b4ef9983be5",
    "mail/15.eml": "249ec45e7c21b66faf0d3310cc742ffdc70e88396a10272932ce821649b7c9e2",
    "h17-supplemental-office-files/retired-office-bookmarks.html": "b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096",
    "transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def low_pack(raw: bytes) -> bytes:
    bits = [byte & 1 for byte in raw]
    return bytes(sum(bits[i + j] << j for j in range(min(8, len(bits) - i)))
                 for i in range(0, len(bits), 8))


def low_value(text: str, first_bit_lsb: bool = True) -> int:
    bits = [ord(ch) & 1 for ch in text]
    if first_bit_lsb:
        return sum(bit << i for i, bit in enumerate(bits))
    return sum(bit << (len(bits) - 1 - i) for i, bit in enumerate(bits))


def main() -> None:
    for relative, expected in EXPECTED.items():
        path = ROOT / "resources" / relative if relative == "acceptance.json" else EVIDENCE / relative
        actual = sha256(path.read_bytes())
        if actual != expected:
            raise AssertionError(f"source hash mismatch for {relative}: {actual}")

    candidate = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text(encoding="utf-8"))
    k01 = bytes.fromhex(candidate["K01"])
    k05 = bytes.fromhex(candidate["K05"])
    for slot, raw in (("K01", k01), ("K05", k05)):
        if sha256(raw).upper() != acceptance["slot_sha256"][slot].upper():
            raise AssertionError(f"accepted {slot} commitment mismatch")

    # K05 accepted component: two packed bytes are 03 43, i.e. 03C.
    k05_low = low_pack(k05)
    if k05_low != bytes.fromhex("0343") or chr(k05_low[1]) != "C":
        raise AssertionError("K05 -> 03C locator changed")

    # K01 is four source-ordered four-byte words A/B/C/D.
    group_outputs = {}
    for index, letter in enumerate("ABCD"):
        group = k01[index * 4:(index + 1) * 4]
        group_outputs[letter] = {"source_hex": group.hex().upper(),
                                 "lowpack_hex": low_pack(group).hex().upper(),
                                 "numeric_selector": low_pack(group)[0]}
    if {k: v["numeric_selector"] for k, v in group_outputs.items()} != {"A": 4, "B": 0, "C": 9, "D": 7}:
        raise AssertionError("K01 group selector map changed")

    mail03 = (EVIDENCE / "mail/03.eml").read_text(encoding="utf-8")
    mail09 = (EVIDENCE / "mail/09.eml").read_text(encoding="utf-8")
    mail13 = (EVIDENCE / "mail/13.eml").read_text(encoding="utf-8")
    if "group A" not in mail03 or "group C" not in mail03:
        raise AssertionError("MAIL-03 no longer establishes groups A/C")
    mail09_flat = " ".join(mail09.lower().split())
    if "tea receipt" not in mail09_flat or "map in the back" not in mail09_flat:
        raise AssertionError("MAIL-09 bookmark description changed")
    if "AX-7782" not in mail13 or "transfer receipt" not in mail13.lower():
        raise AssertionError("MAIL-13 transfer receipt reference changed")

    # Enumerate every bookmark, preserving the 15-item list and reverse ordinal.
    bookmark_path = EVIDENCE / "h17-supplemental-office-files/retired-office-bookmarks.html"
    html = bookmark_path.read_text(encoding="utf-8")
    anchors = re.findall(r'<A HREF="([^"]+)">([^<]+)</A>', html)
    if len(anchors) != 15:
        raise AssertionError(f"expected 15 browser bookmarks, got {len(anchors)}")
    bookmark_rows = []
    for index, (url, title) in enumerate(anchors, 1):
        mail_id = 16 - index
        mail_path = EVIDENCE / f"mail/{mail_id:02d}.eml"
        text = mail_path.read_text(encoding="utf-8")
        subject_match = re.search(r"^Subject: (.*)$", text, re.MULTILINE)
        subject = subject_match.group(1) if subject_match else ""
        has_transfer_receipt = "transfer receipt" in text.lower() and "AX-7782" in text
        bookmark_rows.append({"bookmark_index": index, "title": title, "url": url,
                              "reverse_mail_id": mail_id, "mail_subject": subject,
                              "has_AX7782_transfer_receipt": has_transfer_receipt})

    receipt_hits = [row for row in bookmark_rows if row["has_AX7782_transfer_receipt"]]
    if len(receipt_hits) != 1 or receipt_hits[0]["bookmark_index"] != 3 or receipt_hits[0]["reverse_mail_id"] != 13:
        raise AssertionError("reverse-ordinal transfer receipt hit changed")
    if receipt_hits[0]["title"] != "Tea-room stock sheets":
        raise AssertionError("bookmark 3 is no longer Tea-room stock sheets")

    # All four retained transfer IDs are controls for the final return selector.
    transfer_rows = [json.loads(line) for line in (EVIDENCE / "transfers/transfer-audit.jsonl").read_text().splitlines() if line.strip()]
    transfer_ids = sorted({row["transfer"] for row in transfer_rows if "transfer" in row})
    transfer_selectors = {transfer: low_value(transfer.split("-")[-1]) for transfer in transfer_ids}
    if transfer_selectors != {"AX-7778": 7, "AX-7781": 11, "AX-7782": 3, "AX-7783": 11}:
        raise AssertionError("numeric-suffix LSB selector controls changed")
    suffix_return_hits = [transfer for transfer, selector in transfer_selectors.items() if selector == 3]
    if suffix_return_hits != ["AX-7782"]:
        raise AssertionError("AX-7782 is no longer the unique numeric-suffix selector returning bookmark 3")
    transfer_renderings = {}
    for transfer in transfer_ids:
        prefix, suffix = transfer.split("-", 1)
        forms = {
            "full_hyphenated": transfer,
            "full_hyphenated_reversed_digits": prefix + "-" + suffix[::-1],
            "compact": prefix + suffix,
            "compact_reversed_digits": prefix + suffix[::-1],
            "prefix": prefix,
            "numeric_suffix": suffix,
            "reversed_numeric_suffix": suffix[::-1],
        }
        transfer_renderings[transfer] = {
            form: {"LSB_first": low_value(value, True), "MSB_first": low_value(value, False)}
            for form, value in forms.items()
        }
    if transfer_renderings["AX-7782"]["compact"]["LSB_first"] != 13:
        raise AssertionError("compact AX7782 no longer returns to MAIL13")
    compact_mail13_hits = [t for t, v in transfer_renderings.items()
                           if v["compact"]["LSB_first"] == 13]
    if compact_mail13_hits != ["AX-7782"]:
        raise AssertionError("compact-ID MAIL13 self-return is no longer unique")

    result = {
        "K05_lowpack": k05_low.hex().upper(),
        "K05_locator": "03C",
        "K01_group_lowbit_controls": group_outputs,
        "K01_group_C_mail_locator": group_outputs["C"]["numeric_selector"],
        "bookmark_count": len(bookmark_rows),
        "reverse_ordinal_transfer_receipt_hits": len(receipt_hits),
        "reverse_ordinal_hit": receipt_hits[0],
        "all_bookmark_reverse_controls": bookmark_rows,
        "transfer_id_numeric_suffix_lsb_controls": transfer_selectors,
        "unique_numeric_suffix_transfer_returning_bookmark_3": suffix_return_hits,
        "transfer_id_rendering_controls": transfer_renderings,
        "unique_compact_transfer_id_returning_MAIL13": compact_mail13_hits,
        "simple_uniform_control_rate": "1/15 bookmark-position hit x 1/4 numeric-suffix transfer-ID return = 1/60 (conditional toy null; not calibrated; rendering-dependent)",
        "semantic_limit": "MAIL-09's physical tea-receipt bookmark is not established as the same object as browser bookmark 3; reverse ordinal is inferred, not source-authenticated",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
