#!/usr/bin/env python3
"""Source-only SFT for the K08 tea-bookmark mirror locator.

This reproducer does not read K08 acceptance data or test a target phrase.
It checks a closed locator loop across the preserved bookmark list, MAIL-09,
and MAIL-13.

Usage from repo root:
    python agents/agent22/k08_tea_bookmark_mirror_sft.py
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
BOOKMARKS = ROOT / "resources/evidence/h17-supplemental-office-files/retired-office-bookmarks.html"
MAIL09 = ROOT / "resources/evidence/mail/09.eml"
MAIL13 = ROOT / "resources/evidence/mail/13.eml"


def normalize_space(text: str) -> str:
    """Lowercase and collapse whitespace for exact source-phrase gates."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def main() -> None:
    html = BOOKMARKS.read_text(encoding="utf-8")
    mail09 = MAIL09.read_text(encoding="utf-8")
    mail13 = MAIL13.read_text(encoding="utf-8")

    links = re.findall(r'<A\s+HREF="([^"]+)">([^<]+)</A>', html, flags=re.IGNORECASE)
    assert len(links) == 15

    tea_rows = [
        index + 1
        for index, (href, label) in enumerate(links)
        if href.lower().endswith("/mug-stock.xls")
        and label.strip().lower() == "tea-room stock sheets"
    ]
    assert tea_rows == [3]
    tea_front = tea_rows[0]

    mail09_flat = normalize_space(mail09)
    assert "map in the back" in mail09_flat
    assert "tea receipt as a bookmark" in mail09_flat
    assert "left it in place" in mail09_flat

    tea_back = len(links) - tea_front + 1
    assert tea_back == 13

    assert "X-Records-Reference: MAIL-13" in mail13
    assert "Subject: Archive transfer receipt to keep with the folder" in mail13
    transfer_match = re.search(r"\bAX-(\d{4})\b", mail13)
    assert transfer_match is not None
    assert transfer_match.group(1) == "7782"

    digit_low_bits = [int(digit) & 1 for digit in transfer_match.group(1)]
    packed_lsb_first = sum(bit << index for index, bit in enumerate(digit_low_bits))
    assert digit_low_bits == [1, 1, 0, 0]
    assert packed_lsb_first == tea_front

    print("bookmark_count=15")
    print("tea_room_front_ordinal=3")
    print("tea_room_back_ordinal=13")
    print("mail13_transfer=AX-7782")
    print("ax7782_digit_low_bits=1,1,0,0")
    print("packed_lsb_first=3")
    print("round_trip=PASS")


if __name__ == "__main__":
    main()
