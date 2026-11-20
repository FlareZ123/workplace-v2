#!/usr/bin/env python3
"""Synthetic controls for raw EMF glyph-index extraction; not a renderer."""
import struct
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_emf_glyph_index_intake as m


def rec(kind, body=b""):
    size = (8 + len(body) + 3) & ~3
    return struct.pack("<II", kind, size) + body + bytes(size - 8 - len(body))


def header_record(nbytes=88, nrecords=1):
    header = bytearray(88)
    struct.pack_into("<I", header, 0, 1)
    struct.pack_into("<I", header, 4, 88)
    header[40:44] = b" EMF"
    struct.pack_into("<II", header, 48, nbytes, nrecords)
    return bytes(header)


def build_emf():
    gids = [17, 42, 99]
    header = header_record()

    # EXTLOGFONTW: LOGFONTW face name begins at record offset 40.
    logfont = bytearray(320)
    face = "Synthetic Barcode".encode("utf-16-le")
    logfont[28:28 + len(face)] = face
    font = rec(82, struct.pack("<I", 1) + bytes(logfont))
    select = rec(37, struct.pack("<I", 1))

    # EXTTEXTOUTW: glyph WORD array at record offset 76.
    ext_body = bytearray(68 + 2 * len(gids))
    struct.pack_into("<ii", ext_body, 28, 100, 200)
    struct.pack_into("<III", ext_body, 36, len(gids), 76, m.ETO_GLYPH_INDEX)
    struct.pack_into("<I", ext_body, 64, 0)
    struct.pack_into("<" + "H" * len(gids), ext_body, 68, *gids)
    ext = rec(84, bytes(ext_body))

    # POLYTEXTOUTW: cStrings at record offset 24; one 40-byte EMRTEXT
    # descriptor starts at 28 and its glyph WORD array starts at 68.
    poly_body = bytearray(60 + 2 * len(gids))
    struct.pack_into("<I", poly_body, 16, 1)
    struct.pack_into("<ii", poly_body, 20, 300, 400)
    struct.pack_into("<III", poly_body, 28, len(gids), 68, m.ETO_GLYPH_INDEX)
    struct.pack_into("<I", poly_body, 56, 0)  # offDx
    struct.pack_into("<" + "H" * len(gids), poly_body, 60, *gids)
    poly = rec(97, bytes(poly_body))

    # SMALLTEXTOUT with ETO_NO_RECT: glyphs begin at record offset 36.
    small_body = bytearray(28 + 2 * len(gids))
    struct.pack_into("<ii", small_body, 0, 500, 600)
    struct.pack_into("<III", small_body, 8, len(gids), m.ETO_GLYPH_INDEX | m.ETO_NO_RECT, 0)
    struct.pack_into("<" + "H" * len(gids), small_body, 28, *gids)
    small = rec(108, bytes(small_body))
    eof = rec(14, struct.pack("<III", 0, 0, 20))

    records = [header, font, select, ext, poly, small, eof]
    blob = b"".join(records)
    h = bytearray(header)
    struct.pack_into("<II", h, 48, len(blob), len(records))
    return bytes(h) + b"".join(records[1:]), gids


blob, gids = build_emf()
result = m.extract_emf_glyph_indices(
    blob, {"job_id": "PS-261003-0417", "attempt": 1, "class": "LABEL"}
)
assert result["status"] == "raw-glyph-indices", result
assert [run["record_type"] for run in result["runs"]] == [84, 97, 108], result
assert [run["glyph_ids"] for run in result["runs"]] == [gids, gids, gids], result
assert [run["string_offset"] for run in result["runs"]] == [76, 68, 36], result
assert all(run["font_face"] == "Synthetic Barcode" for run in result["runs"]), result
assert result["coverage"]["pages_processed"] == 1
assert result["coverage"]["full_render"] is False
assert len(result["source_sha256"]) == 64

# An offset into the EMRTEXT/EXTTEXTOUT descriptor rather than its trailing
# string is rejected; the other two valid records remain visible.
bad = bytearray(blob)
text_start = 88 + 332 + 12
struct.pack_into("<I", bad, text_start + 48, 8)
bad_result = m.extract_emf_glyph_indices(bytes(bad))
assert bad_result["status"] == "partial", bad_result
assert any(run["status"] == "invalid-glyph-span" for run in bad_result["runs"]), bad_result
assert bad_result["coverage"]["complete"] is False

# No EMF page is a fail-closed incomplete result, not a complete negative.
empty = m.extract_emf_glyph_indices(b"not an EMF page")
assert empty["coverage"]["complete"] is False, empty
assert empty["status"] == "partial", empty
assert "no-emf-header" in empty["coverage"]["reasons"], empty

# Spool-log binding is exact and metadata-only; PAYLOAD is not integrity proof.
log = (
    "2026-10-03T16:45:00Z JOB=PS-261003-0417 ATTEMPT=1 STATE=ACK "
    "CLASS=LABEL PAYLOAD=E1E60D5F6B6DD2225FA6D5A2A63AD932 DEST=bench\n"
    "2026-10-03T18:01:00Z JOB=PS-261003-0417 ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER "
    "PAYLOAD=CD3E4F216ADB2FB180DA2AA90B33F7A4 DEST=bench\n"
)
binding = m.parse_spool_binding(
    log, "PS-261003-0417", 1, state="ACK", job_class="LABEL", dest="bench"
)
assert binding["status"] == "matched-reconstruction-log-metadata-only"
assert binding["class"] == "LABEL" and binding["dest"] == "bench"
expected = False
try:
    m.parse_spool_binding(log, "PS-261003-0417", 2, state="ACK")
except ValueError:
    expected = True
assert expected

# EMF+ DrawDriverString with CmapLookup unset is an unhandled glyph-index path.
emfplus_payload = struct.pack("<IIII", 1, 0, 0, 1)
emfplus_record = struct.pack("<HHII", 0x4036, 0, 28, 16) + emfplus_payload
comment_body = (
    struct.pack("<I", 32)
    + struct.pack("<I", 0x2B464D45)
    + emfplus_record
)
emfplus_comment = rec(70, comment_body)
header = header_record()
eof = rec(14, struct.pack("<III", 0, 0, 20))
records = [header, emfplus_comment, eof]
blob = b"".join(records)
h = bytearray(header)
struct.pack_into("<II", h, 48, len(blob), len(records))
blob = bytes(h) + b"".join(records[1:])
plus = m.extract_emf_glyph_indices(blob)
assert plus["coverage"]["complete"] is False, plus
assert "emfplus-driver-string-glyph-indices-not-decoded" in plus["coverage"]["reasons"]
# A truncated EMF+ comment is malformed, not a complete negative.
malformed_comment = rec(
    70, struct.pack("<I", 32) + struct.pack("<I", 0x2B464D45) + b"\x00" * 8
)
header = header_record()
eof = rec(14, struct.pack("<III", 0, 0, 20))
records = [header, malformed_comment, eof]
blob = b"".join(records)
h = bytearray(header)
struct.pack_into("<II", h, 48, len(blob), len(records))
blob = bytes(h) + b"".join(records[1:])
malformed = m.extract_emf_glyph_indices(blob)
assert malformed["coverage"]["complete"] is False, malformed
assert "malformed-emfplus-comment" in malformed["coverage"]["reasons"], malformed

print("PASS: EMF glyph-index extraction, POLYTEXTOUT offsets, fail-closed controls and spool metadata binding")
