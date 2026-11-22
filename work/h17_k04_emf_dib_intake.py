"""Extract standalone DIB bitmap records from intact Windows EMF/EMFSPOOL pages.

Read-only source decoder for EMR_SETDIBITSTODEVICE (0x50) and
EMR_STRETCHDIBITS (0x51), per Microsoft's [MS-EMF] sections 2.3.1.5/2.3.1.7:
https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-emf/

The embedded DIB is promoted to a standalone BMP. No page layout is inferred,
and source bitmap records are never accepted as a coupon until the original
K04 SHA256 commitment passes independently.
"""
from __future__ import annotations

import struct
from collections.abc import Iterator

_SIGNATURE = b" EMF"
_MAX_RECORDS = 1_000_000
_MAX_IMAGE_PIXELS = 24_000_000
_MAX_DIB_BYTES = 64 * 1024 * 1024
_EMF_DIB_KINDS = {80: 76, 81: 80}


def _bitmap_from_record(record: memoryview, kind: int) -> bytes | None:
    minimum = _EMF_DIB_KINDS[kind]
    if len(record) < minimum:
        return None
    off_bmi, len_bmi, off_bits, len_bits = struct.unpack_from("<IIII", record, 48)
    if (off_bmi < minimum or off_bits < minimum or len_bmi < 40 or len_bits == 0
            or len_bmi + len_bits > _MAX_DIB_BYTES
            or off_bmi + len_bmi > len(record)
            or off_bits + len_bits > len(record)):
        return None
    bmi = record[off_bmi:off_bmi + len_bmi]
    bits = record[off_bits:off_bits + len_bits]
    header_size, width, height, planes, bpp, compression = struct.unpack_from(
        "<IiiHHI", bmi, 0
    )
    if (header_size < 40 or header_size > len_bmi or width <= 0 or height == 0
            or width * abs(height) > _MAX_IMAGE_PIXELS or planes != 1
            or bpp not in (1, 4, 8, 16, 24, 32) or compression not in (0, 3)):
        return None
    off_pixels = 14 + len_bmi
    total_bytes = off_pixels + len_bits
    bmp_file_header = struct.pack("<2sIHHI", b"BM", total_bytes, 0, 0, off_pixels)
    return bmp_file_header + bmi.tobytes() + bits.tobytes()


def extract_emf_dib_bmps(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Return individually intact BMPs from validated EMF and EMFSPOOL pages."""
    cursor = 0
    page = 0
    while (signature := data.find(_SIGNATURE, cursor)) != -1:
        cursor = signature + 4
        start = signature - 40
        if start < 0 or len(data) - start < 88:
            continue
        record_type, header_size = struct.unpack_from("<II", data, start)
        nbytes, nrecords = struct.unpack_from("<II", data, start + 48)
        if (record_type != 1 or header_size < 88 or header_size % 4
                or not 2 <= nrecords <= _MAX_RECORDS
                or nbytes < header_size + 20 or nbytes > len(data) - start):
            continue
        offset = start
        end = start + nbytes
        complete_page = True
        found_eof = False
        pending: list[tuple[int, bytes]] = []
        for index in range(nrecords):
            if offset + 8 > end:
                complete_page = False
                break
            kind, size = struct.unpack_from("<II", data, offset)
            if size < 8 or size % 4 or offset + size > end:
                complete_page = False
                break
            if index == 0 and (kind != 1 or size != header_size):
                complete_page = False
                break
            if kind in _EMF_DIB_KINDS:
                bitmap = _bitmap_from_record(
                    memoryview(data)[offset:offset + size], kind
                )
                if bitmap is not None:
                    pending.append((kind, bitmap))
            if kind == 14:
                found_eof = index == nrecords - 1
            offset += size
        if not complete_page or not found_eof or offset != end:
            continue
        cursor = end
        page += 1
        for index, (kind, bitmap) in enumerate(pending, 1):
            yield f"emf-page-{page}-record-{index}-type-{kind}", bitmap
