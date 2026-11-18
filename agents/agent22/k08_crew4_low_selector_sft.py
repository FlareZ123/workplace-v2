#!/usr/bin/env python3
"""Reproduce the source-local CREW4 -> LOW -> ATEALBIT selector chain."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path("resources/evidence/crew/noticeboard-and-desk-notes.txt")
EXPECTED_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
SEAL_SOURCE = Path("resources/evidence/maintenance/seal-receipts.jsonl")
SEAL_SHA256 = "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
MAIL03_SOURCE = Path("resources/evidence/mail/03.eml")
MAIL03_SHA256 = "3cf886c12e094cb0362999c5a4d93f913c848a64471f833fbddbfdc2d57ff889"
MAIL09_SOURCE = Path("resources/evidence/mail/09.eml")
MAIL09_SHA256 = "1bda8bbf1e7b661a04fd58c36c38f2b66d2e2410265c311cc09c8e2bf810f08c"
MAIL10_SOURCE = Path("resources/evidence/mail/10.eml")
MAIL10_SHA256 = "ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48"
RECORDER_SOURCE = Path("resources/evidence/recorder/trip-recorder.raw")
RECORDER_SHA256 = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
ROUTE_SOURCE = Path("resources/evidence/recovery-routing.json")
ACCEPTED_K05 = bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572")


def parse_notes(text: str) -> list[tuple[int, str, str]]:
    pattern = re.compile(
        r"^N(\d{2}) / ([^\n]+?) \[censored\]\n(.*?)(?=\n\nN\d{2} /|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    notes: list[tuple[int, str, str]] = []
    for match in pattern.finditer(text):
        number = int(match.group(1))
        author = match.group(2).strip()
        content = " ".join(match.group(3).split())
        notes.append((number, author, content))
    assert [number for number, _, _ in notes] == list(range(1, 25))
    return notes


def body_words(content: str) -> list[str]:
    body = content.split(":", 1)[1] if ":" in content else content
    return re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", body)


def heading(content: str) -> str | None:
    return content.split(":", 1)[0].strip() if ":" in content else None


def decode_a0_lsb(bits: list[int]) -> tuple[str, int]:
    letters: list[str] = []
    full = len(bits) // 5
    for group_index in range(full):
        group = bits[group_index * 5 : group_index * 5 + 5]
        value = sum(bit << offset for offset, bit in enumerate(group))
        assert 0 <= value < 26
        letters.append(chr(ord("A") + value))
    remainder = bits[full * 5 :]
    tail = sum(bit << offset for offset, bit in enumerate(remainder))
    return "".join(letters), tail


def main() -> None:
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    notes = parse_notes(raw.decode("utf-8"))

    authors = [author for _, author, _ in notes]
    first_appearance: list[str] = []
    for author in authors:
        if author not in first_appearance:
            first_appearance.append(author)
    assert first_appearance == ["Jason", "Emily", "Zoey", "David", "Gabriel", "Simon"]

    emily_bits = [1 if author == "Emily" else 0 for author in authors]
    word, crew_number = decode_a0_lsb(emily_bits)
    assert (word, crew_number) == ("CREW", 4)
    selected_author = first_appearance[crew_number - 1]
    assert selected_author == "David"

    emily_note_numbers = [number for number, author, _ in notes if author == "Emily"]
    assert emily_note_numbers == [2, 6, 10, 13, 17, 18, 20, 23]
    emily_heads = "".join(
        body_words(notes[number - 1][2])[0][0].upper()
        for number in emily_note_numbers
    )
    assert emily_heads == "ATTALBIT"

    count_decodes: dict[str, str] = {}
    for author in first_appearance:
        counts = [
            len(body_words(content))
            for _, note_author, content in notes
            if note_author == author
        ]
        count_decodes[author] = "".join(
            chr(ord("A") + count) if 0 <= count < 26 else "?"
            for count in counts
        )
    assert count_decodes == {
        "Jason": "LNJ",
        "Emily": "NLZWIF?V",
        "Zoey": "MNLK",
        "David": "LOW",
        "Gabriel": "OOL",
        "Simon": "MLN",
    }

    david_notes = [(number, content) for number, author, content in notes if author == selected_author]
    assert [number for number, _ in david_notes] == [4, 11, 19]
    david_body_counts = [len(body_words(content)) for _, content in david_notes]
    assert david_body_counts == [11, 14, 22]
    low = count_decodes[selected_author]
    assert low == "LOW"

    lowered: list[tuple[int, int, str, str, str]] = []
    for position, original in enumerate(emily_note_numbers):
        candidate = emily_note_numbers.copy()
        candidate[position] += 1
        if candidate != sorted(candidate) or len(set(candidate)) != len(candidate):
            continue
        initials = "".join(
            body_words(notes[number - 1][2])[0][0].upper()
            for number in candidate
        )
        count_letters = "".join(
            chr(ord("A") + count) if 0 <= count < 26 else "?"
            for count in (
                len(body_words(notes[number - 1][2]))
                for number in candidate
            )
        )
        low_bit_instruction = initials[0] + count_letters[1:4] + initials[5:8]
        lowered.append(
            (original, candidate[position], initials, count_letters, low_bit_instruction)
        )

    exact = [item for item in lowered if item[2] == "ATEALBIT"]
    assert exact == [(10, 11, "ATEALBIT", "NLOWIF?V", "ALOWBIT")]
    assert [item for item in lowered if item[4] == "ALOWBIT"] == exact
    assert [item for item in lowered if "TEA" in item[2]] == exact

    selected_notes = emily_note_numbers.copy()
    selected_notes[2] = 11
    selected_heads = "".join(
        body_words(notes[number - 1][2])[0][0].upper()
        for number in selected_notes
    )
    assert selected_heads == "ATEALBIT"

    low_bits = [ord(letter) & 1 for letter in selected_heads]
    low_byte = sum(bit << index for index, bit in enumerate(low_bits))
    assert low_bits == [1, 0, 1, 1, 0, 0, 1, 0]
    assert low_byte == 0x4D
    assert chr(low_byte) == "M"

    assert "LOWIF" == exact[0][3][1:6]
    assert body_words(notes[10][2])[0].upper() == "EVEN"

    conditional_bits = [
        (ord(letter) & 1) if number % 2 == 0 else ((ord(letter) >> 7) & 1)
        for number, letter in zip(selected_notes, selected_heads)
    ]
    conditional_byte = sum(bit << index for index, bit in enumerate(conditional_bits))
    assert conditional_bits == [1, 0, 0, 0, 0, 0, 1, 0]
    assert conditional_byte == ord("A")

    selector_note = conditional_byte - ord("A") + 1
    assert selector_note == 1

    photograph_notes = [
        number
        for number, _, content in notes
        if heading(content) is not None and "photograph" in heading(content).lower()
    ]
    assert photograph_notes == [1, 3, 4, 8, 14]
    tea_photographs = [
        number
        for number in photograph_notes
        if "tea" in [word.lower() for word in body_words(notes[number - 1][2])]
    ]
    assert tea_photographs == [1]
    note1_words = [word.lower() for word in body_words(notes[0][2])]
    assert "sea" in note1_words and "tea" in note1_words
    assert "photograph" in notes[9][2].lower()
    assert "after the last cup" in notes[9][2].lower()
    seal_instruction = selected_heads.replace("TEA", "SEA", 1)
    assert seal_instruction == "ASEALBIT"

    seal_raw = SEAL_SOURCE.read_bytes()
    assert hashlib.sha256(seal_raw).hexdigest() == SEAL_SHA256
    seal_records = [json.loads(line) for line in seal_raw.decode("utf-8").splitlines()]
    qualified = [
        row for row in seal_records
        if row.get("permit") == "PTW-417"
        and row.get("state") == "CLOSED"
        and row.get("fitment") == "AS_LEFT"
        and row.get("signed") is True
    ]
    bay_best = {}
    for row in qualified:
        bay = row["bay"]
        if bay not in bay_best or row["revision"] > bay_best[bay]["revision"]:
            bay_best[bay] = row
    witness_order = ["B", "D", "A", "C"]
    seal_serials = [bay_best[bay]["serial"].removeprefix("SG-") for bay in witness_order]
    assert seal_serials == ["D7DAD6BC", "9714519B", "7DAD0AD4", "BE8E87FD"]
    seal_bits = [int(serial, 16) & 1 for serial in seal_serials]
    seal_selector = sum(bit << index for index, bit in enumerate(seal_bits))
    assert seal_bits == [0, 1, 0, 1]
    assert seal_selector == 10
    assert seal_selector == exact[0][0]

    cup_notes = [
        number
        for number, _, content in notes
        if "cup" in [word.lower() for word in body_words(content)]
    ]
    assert cup_notes == [9, 10]
    assert "after the last cup" in notes[seal_selector - 1][2].lower()
    after_last_cup = seal_selector + 1
    assert after_last_cup == 11
    assert after_last_cup == exact[0][1]

    mail10_raw = MAIL10_SOURCE.read_bytes()
    assert hashlib.sha256(mail10_raw).hexdigest() == MAIL10_SHA256
    mail10 = mail10_raw.decode("utf-8")
    assert "X-Records-Reference: MAIL-10" in mail10
    assert "The node we want is 0x31." in mail10
    assert "copied exactly as stored" in mail10
    assert "CRC failures are expected" in mail10

    recorder_raw = RECORDER_SOURCE.read_bytes()
    assert hashlib.sha256(recorder_raw).hexdigest() == RECORDER_SHA256
    magic, version, record_size, record_count = struct.unpack_from("<8sHHI", recorder_raw, 0)
    assert (magic, version, record_size, record_count) == (b"TRP2DUMP", 2, 24, 88)
    route = json.loads(ROUTE_SOURCE.read_text("utf-8"))["K05"]
    assert route["node"] == 49 == 0x31
    assert route["event"] == 82 == 0x52
    start = datetime.fromisoformat(route["start_utc"])
    end = datetime.fromisoformat(route["end_utc_exclusive"])

    k05_rows: dict[int, tuple[int, bytes]] = {}
    for index in range(record_count):
        offset = 16 + index * 24
        row = recorder_raw[offset : offset + 24]
        assert len(row) == 24
        stored_crc = struct.unpack_from("<I", row, 20)[0]
        if zlib.crc32(row[:20]) & 0xFFFFFFFF != stored_crc:
            continue
        timestamp, node, event, latch, sequence = struct.unpack_from("<IHBBI", row, 0)
        when = datetime.fromtimestamp(timestamp, timezone.utc)
        if node != route["node"] or event != route["event"] or not (start <= when < end):
            continue
        control = row[12:16]
        if latch not in k05_rows or sequence > k05_rows[latch][0]:
            k05_rows[latch] = (sequence, control)

    assert sorted(k05_rows) == [0, 1, 2, 3]
    k05_sequences = [k05_rows[latch][0] for latch in range(4)]
    k05_controls = [k05_rows[latch][1] for latch in range(4)]
    assert k05_sequences == [300, 301, 302, 303]
    k05_component = b"".join(k05_controls)
    assert k05_component == ACCEPTED_K05

    k05_low_bits = [byte & 1 for byte in k05_component]
    k05_low_bytes = bytes(
        sum(k05_low_bits[offset + bit] << bit for bit in range(8))
        for offset in (0, 8)
    )
    assert k05_low_bytes == bytes([3, ord("C")])

    mail03_raw = MAIL03_SOURCE.read_bytes()
    assert hashlib.sha256(mail03_raw).hexdigest() == MAIL03_SHA256
    mail03 = mail03_raw.decode("utf-8")
    group_c_match = re.search(r"WN-14 / group C / ([0-9A-F]{8})", mail03)
    assert group_c_match is not None
    group_c = bytes.fromhex(group_c_match.group(1))
    assert group_c == bytes.fromhex("CD7C6023")
    group_c_low_bits = [byte & 1 for byte in group_c]
    group_c_selector = sum(bit << index for index, bit in enumerate(group_c_low_bits))
    assert group_c_low_bits == [1, 0, 0, 1]
    assert group_c_selector == 9

    mail09_raw = MAIL09_SOURCE.read_bytes()
    assert hashlib.sha256(mail09_raw).hexdigest() == MAIL09_SHA256
    mail09 = mail09_raw.decode("utf-8")
    assert "X-Records-Reference: MAIL-09" in mail09
    assert "map in\nthe back belongs to David" in mail09
    assert "tea receipt as a bookmark" in mail09

    selected_headings = [
        (number, heading(notes[number - 1][2]))
        for number in selected_notes
        if heading(notes[number - 1][2]) is not None
    ]
    m_headings = [
        (number, label)
        for number, label in selected_headings
        if label is not None and label.upper().startswith("M")
    ]
    assert m_headings == [(11, "Mug shelf")]

    print("SOURCE_SHA256", EXPECTED_SHA256)
    print("AUTHOR_BITS", "".join(map(str, emily_bits)))
    print("AUTHOR_BITS_DECODE", f"{word}{crew_number}")
    print("CREW_ORDER", ",".join(first_appearance))
    print("SELECTED_AUTHOR", selected_author)
    print("AUTHOR_COUNT_DECODES", ",".join(
        f"{author}:{count_decodes[author]}" for author in first_appearance
    ))
    print("DAVID_BODY_WORD_COUNTS", ",".join(map(str, david_body_counts)))
    print("DAVID_COUNT_DECODE", low)
    print("EMILY_HEADS", emily_heads)
    for original, replacement, initials, count_letters, instruction in lowered:
        print(
            "LOWER_ONE_ROW",
            f"N{original:02d}->N{replacement:02d}",
            initials,
            count_letters,
            instruction,
        )
    print("UNIQUE_ATEALBIT_LOWER", "N10->N11")
    print("SELECTED_COUNT_DECODE", "NLOWIF?V")
    print("SELECTED_MIXED_INSTRUCTION", "ALOWBIT")
    print("COUNT_CONTINUATION", "LOWIF", "EVEN")
    print("LOW_IF_EVEN_BITS", "".join(map(str, conditional_bits)))
    print("LOW_IF_EVEN_BYTE", f"0x{conditional_byte:02X}", chr(conditional_byte))
    print("A_SELECTOR_NOTE", f"N{selector_note:02d}", "tea->sea")
    print("PHOTOGRAPH_NOTES", ",".join(f"N{number:02d}" for number in photograph_notes))
    print("UNIQUE_TEA_PHOTOGRAPH", "N01")
    print("SEA_TEA_INSTRUCTION", seal_instruction)
    print("SEAL_SOURCE_SHA256", SEAL_SHA256)
    print("SEAL_SERIALS_BDAC", ",".join(seal_serials))
    print("SEAL_LOW_BITS", "".join(map(str, seal_bits)))
    print("SEAL_SELECTOR_NOTE", f"N{seal_selector:02d}")
    print("CUP_NOTES", ",".join(f"N{number:02d}" for number in cup_notes))
    print("AFTER_LAST_CUP", f"N{seal_selector:02d}->N{after_last_cup:02d}")
    print("ATEALBIT_LOW_BITS", "".join(map(str, low_bits)))
    print("ATEALBIT_LOW_BYTE", f"0x{low_byte:02X}", chr(low_byte))
    print("M_PLUS_SEAL_SELECTOR", f"{chr(low_byte)}{seal_selector}", "MAIL-10")
    print("MAIL10_SOURCE_SHA256", MAIL10_SHA256)
    print("K05_SELECTED_SEQUENCES", ",".join(map(str, k05_sequences)))
    print("K05_COMPONENT", k05_component.hex().upper())
    print("K05_ACCEPTED_CALIBRATION", "PASS")
    print("K05_LOW_BITS", "".join(map(str, k05_low_bits)))
    print("K05_LOW_BYTES", f"{k05_low_bytes[0]:02d}", chr(k05_low_bytes[1]), "MAIL-03/group-C")
    print("MAIL03_GROUP_C", group_c.hex().upper())
    print("GROUP_C_LOW_BITS", "".join(map(str, group_c_low_bits)))
    print("GROUP_C_SELECTOR", group_c_selector, "MAIL-09")
    print("MAIL09_CORROBORATION", "David", "tea-receipt-bookmark")
    print("UNIQUE_M_HEADING", "N11", "Mug shelf")


if __name__ == "__main__":
    main()
