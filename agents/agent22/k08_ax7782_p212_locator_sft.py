#!/usr/bin/env python3
"""Reproduce the conditional LOW-IF-EVEN -> P212 K08 locator.

This script is target-blind. It never reads K08 acceptance data.
"""

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
NOTES = ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt"
MAIL13 = ROOT / "resources/evidence/mail/13.eml"
AUDIT = ROOT / "resources/evidence/transfers/transfer-audit.jsonl"


def parse_notes(text: str) -> list[tuple[int, str, str]]:
    pattern = re.compile(
        r"^N(\d{2}) / ([^\n]+?) \[censored\]\n(.*?)(?=\n\nN\d{2} /|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    return [
        (int(match.group(1)), match.group(2).strip(), " ".join(match.group(3).split()))
        for match in pattern.finditer(text)
    ]


def body_words(content: str) -> list[str]:
    body = content.split(":", 1)[1] if ":" in content else content
    return re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", body)


def pack_lsb(bits: list[int]) -> int:
    return sum(bit << index for index, bit in enumerate(bits))


def main() -> None:
    notes = parse_notes(NOTES.read_text(encoding="utf-8"))
    assert [number for number, _, _ in notes] == list(range(1, 25))

    selected = [2, 6, 11, 13, 17, 18, 20, 23]
    heads = "".join(body_words(notes[number - 1][2])[0][0].upper() for number in selected)
    counts = [len(body_words(notes[number - 1][2])) for number in selected]
    count_letters = "".join(chr(ord("A") + count) if count < 26 else "?" for count in counts)
    assert heads == "ATEALBIT"
    assert count_letters == "NLOWIF?V"
    assert count_letters[1:6] == "LOWIF"
    assert body_words(notes[10][2])[0].upper() == "EVEN"

    mail13 = MAIL13.read_text(encoding="utf-8")
    assert "final custodian handoff is AX-7782" in mail13
    assert "Each chunk was retried once." in mail13
    assert "There are eight chunks, numbered from zero." in mail13

    rows = [json.loads(line) for line in AUDIT.read_text(encoding="utf-8").splitlines()]
    checkpoints = {
        (row["seq"], row["attempt"]): bytes.fromhex(row["checkpoint"])
        for row in rows
        if row.get("kind") == "CHUNK" and row.get("transfer") == "AX-7782"
    }
    assert all((seq, attempt) in checkpoints for seq in range(8) for attempt in (1, 2))

    # Conditional interpretation of LOW IF EVEN:
    # use the lower attempt number on even-numbered chunks, otherwise the higher one.
    chosen = [
        checkpoints[(seq, 1 if seq % 2 == 0 else 2)]
        for seq in range(8)
    ]
    chosen_bytes = b"".join(chosen)
    assert chosen_bytes.hex().upper() == "6224CEDCF3B873BA18887BE63DB0C5C9"

    low_bits = [byte & 1 for byte in chosen_bytes]
    packed = bytes(pack_lsb(low_bits[offset:offset + 8]) for offset in (0, 8))
    assert packed == bytes([0x50, 0xD4])
    assert packed[:1] == b"P"
    assert packed[1] == 212

    print("SELECTED_HEADS=ATEALBIT")
    print("COUNT_CONTINUATION=LOWIF EVEN")
    print("AX_TRANSFER=AX-7782")
    print("MIXED_ATTEMPT_CHECKPOINTS=" + chosen_bytes.hex().upper())
    print("LOW_BITS=" + "".join(map(str, low_bits)))
    print("PACKED=50D4")
    print("LOCATOR=P212")


if __name__ == "__main__":
    main()
