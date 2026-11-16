"""SFT: native EMF/EMFSPOOL text extraction for exact H-17 K08 screening."""
from __future__ import annotations

import hashlib
import hmac
import struct

from h17_emf_text import extract_emf_text


def record(kind: int, pieces: list[str], *, glyph: bool = False, bad_offset: bool = False) -> bytes:
    wide = kind in (84, 97)
    poly = kind in (96, 97)
    count = len(pieces)
    floor = 40 + 40 * count if poly else 76
    content = bytearray(floor)
    if poly:
        struct.pack_into("<I", content, 36, count)
    for i, phrase in enumerate(pieces):
        anchor = 40 + 40 * i if poly else 36
        raw = phrase.encode("utf-16-le" if wide else "cp1252")
        offset = len(content) if not bad_offset else len(content) + len(raw) + 8
        struct.pack_into("<III", content, anchor + 8, len(phrase), offset, 0x10 if glyph else 0)
        content += raw
    content.extend(bytes(-len(content) % 4))
    struct.pack_into("<II", content, 0, kind, len(content))
    return bytes(content)


def small_record(text: str, *, compact: bool = False, no_rect: bool = False, glyph: bool = False) -> bytes:
    options = (0x200 if compact else 0) | (0x100 if no_rect else 0) | (0x10 if glyph else 0)
    encoded = text.encode("latin1" if compact else "utf-16-le")
    prefix = 36 if no_rect else 52
    payload = bytearray(prefix)
    struct.pack_into("<II", payload, 16, len(text), options)
    payload += encoded
    payload.extend(bytes(-len(payload) % 4))
    struct.pack_into("<II", payload, 0, 108, len(payload))
    return bytes(payload)


def page(*records: bytes) -> bytes:
    h = bytearray(88)
    struct.pack_into("<II", h, 0, 1, 88)
    h[40:44] = b" EMF"
    footer = struct.pack("<IIIII", 14, 20, 0, 0, 0)
    struct.pack_into("<II", h, 48, 88 + sum(map(len, records)) + len(footer), len(records) + 2)
    return bytes(h) + b"".join(records) + footer


def main() -> None:
    caption = "The sea and the last watch still have a place at the table"
    pieces = ["The sea and the last watch ", "still have a place at the table"]
    first = page(record(84, pieces[:1]), record(97, pieces[1:]))
    second = page(record(83, ["Simple ASCII proof"]), record(96, ["west ", "desk"]))
    envelope = b"EMFSPOOL read-only test\0\0" + first + b"SPACER" + second
    results = list(extract_emf_text(envelope))
    assert len(results) >= 4, results
    assert caption.encode("utf-8") in [v for _, v in results], results
    assert any(b"west desk" in v for _, v in results), results
    print("PASS embedded Unicode/ASCII EMFSPOOL pages and two-string PolyTextOut")

    small = page(small_record("Café blue mug", compact=True, no_rect=True),
                 small_record("marée nocturne", compact=False, no_rect=False))
    small_streams = list(extract_emf_text(small))
    assert any(value == "Café blue mug marée nocturne".encode("utf-8")
               for _, value in small_streams), small_streams
    assert list(extract_emf_text(page(small_record("glyph", glyph=True)))) == []
    print("PASS EMR_SMALLTEXTOUT both text widths and bounding rectangle alternatives")

    nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
    prehash = hmac.new(nonce, caption.lower().encode("utf-8"), hashlib.sha256).digest()[:16]
    target = hashlib.sha256(prehash).digest()
    hits = [label for label, value in results
            if hashlib.sha256(hmac.new(nonce, value.lower(), hashlib.sha256).digest()[:16]).digest() == target]
    assert len(hits) == 1 and hits[0].endswith("joined"), hits
    print("PASS original K08 HMAC16-to-SHA256 reduction matches synthetic complete text")

    assert list(extract_emf_text(page(record(84, ["secret glyph text"], glyph=True)))) == []
    assert list(extract_emf_text(page(record(84, ["secret bad offset"], bad_offset=True)))) == []
    tampered = bytearray(first)
    struct.pack_into("<I", tampered, 52, 1000)  # Implausible record count
    assert list(extract_emf_text(bytes(tampered))) == []
    assert list(extract_emf_text(b" EMF" + b"\x00" * 300)) == []
    print("PASS glyph indexes, false signatures, bad offsets and malformed headers rejected")


if __name__ == "__main__":
    main()
