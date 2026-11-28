#!/usr/bin/env python3
"""Source-only MHI-selected direct LOW BIT caption-channel falsifier.

Run with the original crew-notes file as the sole argument. No K08 target,
nonce, candidate, protected PDF or network inputs are consulted.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import re
import sys

SOURCE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"

def parse_notes(data: bytes) -> dict[int, str]:
    notes = {}
    for match in re.finditer(r"^N(\d{2}) / [^\n]+\n([^\n]+)", data.decode("utf8"), re.M):
        index, line = int(match.group(1)), match.group(2)
        notes[index] = line.split(":", 1)[-1].lstrip() if ":" in line else line
    assert set(notes) == set(range(1, 25))
    return notes

def pack(text: str, lsb_first: bool) -> bytes:
    bits = [ord(c) & 1 for c in text]
    return bytes(sum(bits[8*i+j] << (j if lsb_first else 7-j)
                     for j in range(8)) for i in range(len(bits)//8))

def main(path: str):
    raw = Path(path).read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA
    notes = parse_notes(raw)
    head = pack(notes[20][:24], True)
    assert head == b"MHI"
    selected = tuple(value - 64 for value in head)
    assert selected == (13, 8, 9)

    # Synthetic, independently controlled complete-text decoder fixture.
    plant = b"PLACE FOR ONE MORE AT THE TABLE!"
    assert len(plant) == 32
    synthetic = "".join("a" if byte & (1 << bit) else "b"
                        for byte in plant for bit in range(8))
    assert pack(synthetic, True) == plant
    assert pack(synthetic, False) != plant

    results = []
    for name, sep in [("contiguous", ""), ("space", " "), ("newline", "\n")]:
        joined = sep.join(notes[k] for k in selected)
        for order, lsb in [("LSB", True), ("MSB", False)]:
            payload = pack(joined, lsb)
            printable = sum(32 <= x <= 126 for x in payload)
            try:
                payload.decode("utf8", "strict")
                valid_utf8 = True
            except UnicodeDecodeError:
                valid_utf8 = False
            assert not valid_utf8
            assert printable < len(payload)
            results.append((name, order, len(payload), printable))
    assert results == [
        ("contiguous", "LSB", 31, 11),
        ("contiguous", "MSB", 31, 12),
        ("space", "LSB", 32, 10),
        ("space", "MSB", 32, 13),
        ("newline", "LSB", 32, 10),
        ("newline", "MSB", 32, 13),
    ]
    for row in results:
        print("%-11s %-3s bytes=%d printable=%d" % row)
    print("MHI source selector PASS; planted complete-text control PASS")
    print("Direct original valid UTF-8 captions 0/6; K08 commitment NOT READ")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: SCRIPT original_crew_notes.txt")
    main(sys.argv[1])
