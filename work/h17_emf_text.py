"""Read unencrypted text records from EMF pages, including Windows EMFSPOOL.

A bounded, non-rendering extractor. Glyph-index text, bitmap-rendered pages,
font-encoded outlines and unsupported record types require native rendering/OCR.
No filesystem or network access. See Microsoft [MS-EMF] sections 2.2.5,
2.3.4.2, 2.3.5.7, 2.3.5.8, 2.3.5.32, 2.3.5.33 and 2.3.5.37.
"""
from __future__ import annotations

import struct
from collections.abc import Iterator

_EMF_SIGNATURE = b" EMF"  # Header.Signature = 0x464D4520 at header byte 40
_MAX_RECORDS = 1_000_000
_MAX_CHARS = 1_000_000
_GLYPH_INDEX = 0x10
_SMALL_CHARS = 0x200
_NO_RECT = 0x100


def _record_text(record: memoryview, kind: int) -> list[str]:
    if kind == 108:  # EMR_SMALLTEXTOUT
        if len(record) < 36:
            return []
        chars, options = struct.unpack_from("<II", record, 16)
        if not 0 < chars <= _MAX_CHARS or options & _GLYPH_INDEX:
            return []
        width = 1 if options & _SMALL_CHARS else 2
        offset = 36 if options & _NO_RECT else 52
        if offset + chars * width > len(record):
            return []
        raw = record[offset:offset + chars * width].tobytes()
        try:
            decoded = raw.decode("latin1" if width == 1 else "utf-16-le")
        except UnicodeDecodeError:
            return []
        return [decoded] if decoded.strip() else []

    wide = kind in (84, 97)
    if kind in (83, 84):  # EMR_EXTTEXTOUTA/W
        starts = (36,)
        string_floor = 76
    elif kind in (96, 97):  # EMR_POLYTEXTOUTA/W
        if len(record) < 40:
            return []
        count = struct.unpack_from("<I", record, 36)[0]
        if count == 0 or count > (len(record) - 40) // 40:
            return []
        starts = range(40, 40 + 40 * count, 40)
        string_floor = 40 + 40 * count
    else:
        return []

    strings = []
    for start in starts:
        if start + 40 > len(record):
            continue
        chars, offset, options = struct.unpack_from("<III", record, start + 8)
        if (not chars or chars > _MAX_CHARS or options & _GLYPH_INDEX
                or options & _SMALL_CHARS):
            continue
        charwidth = 2 if wide else 1
        length = chars * charwidth
        if offset < string_floor or offset + length > len(record):
            continue
        if wide and offset % 2:
            continue
        chunk = record[offset:offset + length].tobytes()
        try:
            text = chunk.decode("utf-16-le" if wide else "cp1252")
        except UnicodeDecodeError:
            continue
        if text.strip():
            strings.append(text)
    return strings


def extract_emf_text(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Yield direct, space-joined and unspaced text for complete embedded pages.

    The search is anchored to a valid EMR_HEADER signature. Candidate pages
    must have bounded, four-byte-aligned records and a terminal EMR_EOF.
    This also finds EMF pages embedded in larger EMFSPOOL records.
    """
    cursor = 0
    page = 0
    while (signature := data.find(_EMF_SIGNATURE, cursor)) != -1:
        cursor = signature + len(_EMF_SIGNATURE)
        start = signature - 40
        if start < 0 or len(data) - start < 88:
            continue
        rtype, header_size = struct.unpack_from("<II", data, start)
        nbytes, nrecords = struct.unpack_from("<II", data, start + 48)
        if (rtype != 1 or header_size < 88 or header_size % 4
                or nbytes < header_size + 20 or nbytes > len(data) - start
                or not 2 <= nrecords <= _MAX_RECORDS):
            continue
        stop = start + nbytes
        offset = start
        strings: list[str] = []
        valid = True
        saw_eof = False
        for index in range(nrecords):
            if offset + 8 > stop:
                valid = False
                break
            kind, size = struct.unpack_from("<II", data, offset)
            if size < 8 or size % 4 or offset + size > stop:
                valid = False
                break
            if index == 0 and (kind != 1 or size != header_size):
                valid = False
                break
            if kind in (83, 84, 96, 97, 108):
                strings.extend(_record_text(memoryview(data)[offset:offset + size], kind))
            if kind == 14:  # EMR_EOF
                saw_eof = index == nrecords - 1
            offset += size
        if not valid or offset != stop or not saw_eof:
            continue
        cursor = stop
        page += 1
        if strings:
            variants = ("\n".join(strings), " ".join(strings), "".join(strings))
            seen: set[str] = set()
            for label, value in zip(("lines", "spaced", "joined"), variants):
                if value not in seen:
                    seen.add(value)
                    yield f"emf-page-{page}-{label}", value.encode("utf-8")
