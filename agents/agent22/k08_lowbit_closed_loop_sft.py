#!/usr/bin/env python3
"""Reproduce the target-blind ATEALBIT -> accepted-slot -> K07 -> N11 LOW BIT loop.

Run from the workplace-v2 repository root:
    python agents/agent22/k08_lowbit_closed_loop_sft.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources/evidence"
TRANSFER_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
MAIL13_SHA = "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
EXPECTED_TRANSFER_LOW = {
    "AX-7778": "6A58",
    "AX-7781": "E188",
    "AX-7782": "53D5",
    "AX-7783": "EF7B",
}


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def low_value(text: str) -> int:
    return sum((ord(ch) & 1) << i for i, ch in enumerate(text))


def pack_byte_low_bits(raw: bytes) -> bytes:
    assert len(raw) % 8 == 0
    return bytes(
        sum((raw[i + j] & 1) << j for j in range(8))
        for i in range(0, len(raw), 8)
    )


def lower_half_low_char(component_hex: str) -> str:
    raw = bytes.fromhex(component_hex)
    assert len(raw) == 16
    return chr(pack_byte_low_bits(raw[8:])[0])


def upper_half_low_byte(component_hex: str) -> int:
    raw = bytes.fromhex(component_hex)
    return pack_byte_low_bits(raw[:8])[0]


def parse_notes(text: str) -> dict[int, tuple[str, str]]:
    matches = re.findall(
        r"(?ms)^N(\d\d) / ([^\n]+)\n(.+?)(?=\n\nN\d\d /|\Z)",
        text,
    )
    return {
        int(number): (author.split()[0], body.strip())
        for number, author, body in matches
    }


def body_after_heading(text: str) -> str:
    return text.split(":", 1)[1].strip() if ":" in text else text


def main() -> None:
    notes_path = EVIDENCE / "crew/noticeboard-and-desk-notes.txt"
    transfer_path = EVIDENCE / "transfers/transfer-audit.jsonl"
    mail13_path = EVIDENCE / "mail/13.eml"
    candidate_path = ROOT / "candidate.json"

    notes_bytes = notes_path.read_bytes()
    transfer_bytes = transfer_path.read_bytes()
    mail13_bytes = mail13_path.read_bytes()
    assert hashlib.sha256(notes_bytes).hexdigest() == NOTES_SHA
    assert hashlib.sha256(transfer_bytes).hexdigest() == TRANSFER_SHA
    assert hashlib.sha256(mail13_bytes).hexdigest() == MAIL13_SHA

    notes = parse_notes(notes_bytes.decode("utf-8"))
    assert set(notes) == set(range(1, 25))

    david_counts = [
        len(words(body_after_heading(notes[i][1])))
        for i in (4, 11, 19)
    ]
    assert david_counts == [11, 14, 22]
    low = "".join(chr(ord("A") + n) for n in david_counts)
    assert low == "LOW"

    selected_rows = (2, 6, 11, 13, 17, 18, 20, 23)
    heads = "".join(
        words(body_after_heading(notes[i][1]))[0][0].upper()
        for i in selected_rows
    )
    assert heads == "ATEALBIT"
    teal = heads[1:5]
    bit = heads[-3:]
    assert teal == "TEAL" and bit == "BIT"
    alowbit = heads[0] + low + bit
    assert alowbit == "ALOWBIT"

    assert [low_value(x) for x in ("A", teal, bit)] == [1, 6, 2]
    selectors = [low_value(x) for x in ("A", low, bit)]
    assert selectors == [1, 6, 2]

    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    components = [candidate[f"K{i:02d}"] for i in selectors]
    assert components == [
        "049AAB2E1CDE7A82CD7C60234303C91A",
        "5DBF40EE52FAAED9A536D3326CF0D95A",
        "0D7E3AB56FB75DA3EB0E2E06786D239E",
    ]

    chars = "".join(lower_half_low_char(component) for component in components)
    assert chars == "yEa"
    assert [upper_half_low_byte(component) for component in components] == [
        0x04,
        0x83,
        0xF9,
    ]
    assert low_value(chars) == 7

    mail13 = " ".join(mail13_bytes.decode("utf-8").split())
    assert "final custodian handoff is AX-7782" in mail13
    assert "second attempt has the checkpoint used in the committed chain" in mail13
    assert "Order by chunk sequence" in mail13

    rows = [
        json.loads(line)
        for line in transfer_bytes.decode("utf-8").splitlines()
        if line.strip()
    ]
    transfer_low = {}
    raw_by_transfer = {}
    for transfer in EXPECTED_TRANSFER_LOW:
        chunks = [
            row
            for row in rows
            if row.get("transfer") == transfer and row.get("kind") == "CHUNK"
        ]
        by_seq = {}
        for row in chunks:
            seq = int(row["seq"])
            if (
                seq not in by_seq
                or int(row["attempt"]) > int(by_seq[seq]["attempt"])
            ):
                by_seq[seq] = row
        assert set(by_seq) == set(range(8))
        raw = b"".join(
            bytes.fromhex(by_seq[i]["checkpoint"])
            for i in range(8)
        )
        raw_by_transfer[transfer] = raw
        transfer_low[transfer] = pack_byte_low_bits(raw).hex().upper()
    assert transfer_low == EXPECTED_TRANSFER_LOW

    selected_raw = raw_by_transfer["AX-7782"]
    assert selected_raw.hex().upper() == "8947CEDCB9CC73BAB7E87BE63302C5C9"
    assert (
        hashlib.sha256(selected_raw).digest()[:16].hex().upper()
        == candidate["K07"]
    )
    assert transfer_low["AX-7782"] == "53D5"

    transfer_note_selectors = {
        name: low_value(value)
        for name, value in transfer_low.items()
    }
    assert transfer_note_selectors == {
        "AX-7778": 6,
        "AX-7781": 3,
        "AX-7782": 11,
        "AX-7783": 5,
    }
    assert words(notes[11][1])[:2] == ["Mug", "shelf"]

    s213 = chr(0x53) + str(0xD5)
    assert s213 == "S213"
    assert low_value(s213) == 13

    print("HEADS=" + heads)
    print("ALOWBIT=" + alowbit)
    print("SELECTORS=1,6,2")
    print("LOW_HALF_BYTE_LSBS=" + chars + " -> LOW BIT 7")
    print("K07_RAW=" + selected_raw.hex().upper())
    print("K07_LOW_BIT=53D5 -> LOW BIT(hex)=11 -> N11 Mug shelf")
    print("K07_ALT_RENDER=S213 -> LOW BIT=13 -> MAIL-13")
    print(
        "TRANSFER_CONTROLS="
        + json.dumps(transfer_note_selectors, sort_keys=True)
    )
    print("PASS")


if __name__ == "__main__":
    main()
