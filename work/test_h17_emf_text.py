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


def emfplus_comment(text: str, *, invalid: bool = False) -> bytes:
    encoded = text.encode("utf-16-le")
    plus = bytearray(40)
    plus += encoded
    plus.extend(bytes(-len(plus) % 4))
    struct.pack_into("<HHII", plus, 0, 0x401C, 0, len(plus), len(plus) - 12)
    struct.pack_into("<I", plus, 20, len(text) + (100 if invalid else 0))
    whole = bytearray(16)
    whole += plus
    struct.pack_into("<IIII", whole, 0, 70, len(whole), len(whole) - 12, 0x2B464D45)
    return bytes(whole)


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

    emfplus = page(emfplus_comment("GDI+ recovery caption"),
                   emfplus_comment(" and its margin"))
    plus_streams = list(extract_emf_text(emfplus))
    assert any(value == b"GDI+ recovery caption and its margin"
               for _, value in plus_streams), plus_streams
    assert list(extract_emf_text(page(emfplus_comment("hidden", invalid=True)))) == []
    print("PASS embedded EMF+ DrawString text and invalid-length rejection")

    mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
    source_coupon = bytes.fromhex("1133557799BBDDFF0022446688AACCEE")
    accepted_k04 = bytes(left ^ right for left, right in zip(source_coupon, mask))
    k04_target = hashlib.sha256(accepted_k04).digest()
    coupon_text = source_coupon.hex().upper()
    printed = page(record(84, [coupon_text[:16]]), record(84, [coupon_text[16:]]))
    rendered = [raw for _, raw in extract_emf_text(printed)]
    direct_coupon_hits = [bytes.fromhex(raw.decode("ascii")) for raw in rendered
                          if raw == coupon_text.encode("ascii")]
    assert len(direct_coupon_hits) == 1
    assert hashlib.sha256(bytes(a ^ b for a, b in zip(direct_coupon_hits[0], mask))).digest() == k04_target
    print("PASS original K04 XOR-route rule on synthetic split-record printable coupon")

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
