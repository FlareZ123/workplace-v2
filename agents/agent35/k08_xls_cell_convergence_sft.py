#!/usr/bin/env python3
"""Target-blind K08 workbook-coordinate convergence test.

Uses surviving source records only. It never reads acceptance.json or the K08
commitment. Official component reducers remain distinct from K08-side alternate
retry strata.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import zlib
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


def pack(bits):
    return sum(bit << i for i, bit in enumerate(bits))


def lowpack16(raw):
    bits = [b & 1 for b in raw]
    return bytes(pack(bits[o:o + 8]) for o in (0, 8))


def excel_col(n):
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None
        self.text = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.href = dict(attrs).get("href")
            self.text = []

    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.href is not None:
            self.links.append((self.href, "".join(self.text).strip()))
            self.href = None
            self.text = []


def parse_notes(text):
    p = re.compile(
        r"^N(\d{2}) / ([^\n]+?) \[censored\]\n(.*?)(?=\n\nN\d{2} /|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    return {
        int(m.group(1)): " ".join(m.group(3).split())
        for m in p.finditer(text)
    }


def body_words(content):
    body = content.split(":", 1)[1] if ":" in content else content
    return re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", body)


def k05_strata(root):
    route = json.loads((root / "evidence/recovery-routing.json").read_text())["K05"]
    raw = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
    magic, version, record_size, record_count = struct.unpack_from("<8sHHI", raw, 0)
    assert (magic, version, record_size, record_count) == (b"TRP2DUMP", 2, 24, 88)

    start = datetime.fromisoformat(route["start_utc"])
    end = datetime.fromisoformat(route["end_utc_exclusive"])
    by_latch = {i: [] for i in range(4)}

    for i in range(record_count):
        row = raw[16 + i * record_size:16 + (i + 1) * record_size]
        if zlib.crc32(row[:20]) & 0xFFFFFFFF != struct.unpack_from("<I", row, 20)[0]:
            continue
        ts, node, event, latch, seq = struct.unpack_from("<IHBBI", row, 0)
        when = datetime.fromtimestamp(ts, timezone.utc)
        if (
            node == route["node"]
            and event == route["event"]
            and start <= when < end
            and latch in by_latch
        ):
            by_latch[latch].append((seq, row[12:16]))

    expected = {
        0: [(200, bytes.fromhex("42BFD053")), (300, bytes.fromhex("FF8B7820"))],
        1: [(201, bytes.fromhex("8052760C")), (301, bytes.fromhex("0A56E858"))],
        2: [(202, bytes.fromhex("6FC2B743")), (302, bytes.fromhex("6DCDA00E"))],
        3: [(203, bytes.fromhex("BFB00270")), (303, bytes.fromhex("F01E4572"))],
    }
    assert {k: sorted(v) for k, v in by_latch.items()} == expected

    official = b"".join(sorted(by_latch[l])[-1][1] for l in range(4))
    low_if_even = b"".join(
        sorted(by_latch[l])[0 if l % 2 == 0 else -1][1]
        for l in range(4)
    )
    return by_latch, official, low_if_even


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "resources",
    )
    root = ap.parse_args().root

    parser = LinkParser()
    parser.feed(
        (root / "evidence/h17-supplemental-office-files/retired-office-bookmarks.html")
        .read_text()
    )
    assert len(parser.links) == 15
    mug = [
        (i + 1, href, label)
        for i, (href, label) in enumerate(parser.links)
        if href.lower().endswith("/mug-stock.xls")
    ]
    assert mug == [
        (3, "file:///R:/Stores/consumables/mug-stock.xls", "Tea-room stock sheets")
    ]

    groups = {}
    for path in ("03.eml", "06.eml"):
        text = (root / "evidence/mail" / path).read_text()
        for group, value in re.findall(
            r"WN-14 / group ([A-D]) / ([0-9A-F]{8})", text
        ):
            groups[group] = bytes.fromhex(value)
    k01 = b"".join(groups[g] for g in "ABCD")
    assert k01.hex().upper() == "049AAB2E1CDE7A82CD7C60234303C91A"
    cells = [
        f"{excel_col(k01[i + 1])}{k01[i]}"
        for i in range(0, len(k01), 2)
    ]
    assert cells == [
        "EX4", "AT171", "HN28", "DZ122",
        "DT205", "AI96", "C67", "Z201",
    ]

    notes = parse_notes(
        (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_text()
    )
    selected = [2, 6, 11, 13, 17, 18, 20, 23]
    heads = "".join(body_words(notes[n])[0][0].upper() for n in selected)
    assert heads == "ATEALBIT"
    m_byte = pack([ord(c) & 1 for c in heads])
    assert m_byte == ord("M")

    receipts = [
        json.loads(line)
        for line in (root / "evidence/maintenance/seal-receipts.jsonl")
        .read_text()
        .splitlines()
        if line
    ]
    best = {}
    for row in receipts:
        if (
            row.get("permit") == "PTW-417"
            and row.get("state") == "CLOSED"
            and row.get("fitment") == "AS_LEFT"
            and row.get("signed") is True
        ):
            if row["bay"] not in best or row["revision"] > best[row["bay"]]["revision"]:
                best[row["bay"]] = row
    serials = [
        best[bay]["serial"].split("-", 1)[1]
        for bay in ["B", "D", "A", "C"]
    ]
    ten = pack([int(serial, 16) & 1 for serial in serials])
    assert ten == 10
    independent_cell = f"{chr(m_byte)}{ten}"
    assert independent_cell == "M10"

    by_latch, official, alternate = k05_strata(root)
    assert official.hex().upper() == "FF8B78200A56E8586DCDA00EF01E4572"
    assert alternate.hex().upper() == "42BFD0530A56E8586FC2B743F01E4572"

    official_low = lowpack16(official)
    alternate_low = lowpack16(alternate)
    assert official_low == bytes([3, ord("C")])
    assert alternate_low == bytes([10, ord("M")])

    official_cell = f"{chr(official_low[1])}{official_low[0]}"
    alternate_cell = f"{chr(alternate_low[1])}{alternate_low[0]}"
    assert official_cell == "C3"
    assert alternate_cell == "M10"
    assert alternate_cell == independent_cell

    # Exhaustive retry-choice specificity control: each latch has low/high row.
    outputs = {}
    for mask in range(16):
        raw = b"".join(
            sorted(by_latch[l])[(mask >> l) & 1][1]
            for l in range(4)
        )
        outputs.setdefault(lowpack16(raw), []).append(mask)
    assert len(outputs) == 8
    assert outputs[bytes([10, ord("M")])] == [8, 10]
    assert 10 in outputs[bytes([10, ord("M")])]  # L,H,L,H = LOW IF EVEN

    chain = [3, 9, 13, 4, 10]
    initials = ""
    for n in chain:
        mail = (root / f"evidence/mail/{n:02d}.eml").read_text()
        subject = re.search(r"(?m)^Subject:\s*(.*)$", mail)
        assert subject
        initials += subject.group(1)[0].upper()
    assert initials == "WRAPT"

    audit = [
        json.loads(line)
        for line in (root / "evidence/transfers/transfer-audit.jsonl")
        .read_text()
        .splitlines()
        if line
    ]
    ax = {
        (r["seq"], r["attempt"]): bytes.fromhex(r["checkpoint"])
        for r in audit
        if r.get("kind") == "CHUNK" and r.get("transfer") == "AX-7782"
    }
    mixed = b"".join(ax[(seq, 1 if seq % 2 == 0 else 2)] for seq in range(8))
    committed = b"".join(ax[(seq, 2)] for seq in range(8))
    assert lowpack16(mixed) == bytes([ord("P"), 212])
    assert lowpack16(committed).hex().upper() == "53D5"

    print("BOOKMARK", mug[0][0], mug[0][2], mug[0][1])
    print("K01_CELLS", ",".join(cells))
    print("ATEALBIT_LOW", f"{m_byte:02X}", chr(m_byte))
    print("SEAL_SELECTOR", ten)
    print("INDEPENDENT_CELL", independent_cell)
    print("K05_OFFICIAL_LOW", official_low.hex().upper(), official_cell)
    print("K05_ALT_LOW", alternate_low.hex().upper(), alternate_cell)
    print("K05_ALT_MATCHES_INDEPENDENT", alternate_cell == independent_cell)
    print("K05_RETRY_LOWBIT_OUTPUTS", len(outputs))
    print("MAIL_SUBJECT_INITIALS_FROM_C3", initials)
    print("AX_CONDITIONAL_LOW", lowpack16(mixed).hex().upper(), "P212")
    print("AX_COMMITTED_LOW", lowpack16(committed).hex().upper())
    print("PASS target-blind workbook-coordinate convergence")


if __name__ == "__main__":
    main()
