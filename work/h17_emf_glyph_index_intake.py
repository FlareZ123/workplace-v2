#!/usr/bin/env python3
"""Read-only EMF glyph-index intake for H-17 native spool recovery.

Extracts raw WORD glyph IDs from standard EMF text records, preserving font
handles, LOGFONTW face names, page/record offsets and source SHA-256. It does
not guess Unicode or claim to render the page. Bitmap, path/font-outline,
transform, clipping and EMF+ driver-string glyph content remain render work.
"""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

EMF_SIGNATURE = b" EMF"
ETO_GLYPH_INDEX = 0x0010
ETO_NO_RECT = 0x0100
MAX_RECORDS = 1_000_000
MAX_GLYPHS = 1_000_000


def _face_name(record):
    # EMR_EXTCREATEFONTINDIRECTW = 8-byte header + handle + EXTLOGFONTW.
    if len(record) < 332:
        return ""
    try:
        return record[40:104].decode("utf-16-le").split("\0", 1)[0].strip()
    except UnicodeDecodeError:
        return ""


def _word_run(record, count, offset, floor, meta):
    if count <= 0 or count > MAX_GLYPHS or offset < floor or offset + count * 2 > len(record):
        return {**meta, "status": "invalid-glyph-span", "glyph_ids": []}
    glyphs = list(struct.unpack_from("<" + "H" * count, record, offset))
    return {**meta, "status": "raw-glyph-ids", "string_offset": offset, "glyph_ids": glyphs}


def _poly_runs(record, page, index, record_offset, font_handle, face, kind=97):
    if len(record) < 40:
        return [], True
    count = struct.unpack_from("<I", record, 36)[0]
    if count <= 0 or count > (len(record) - 40) // 40:
        return [], True
    floor = 40 + count * 40
    runs, malformed = [], False
    for sub, start in enumerate(range(40, floor, 40)):
        x, y = struct.unpack_from("<ii", record, start)
        n, off, options = struct.unpack_from("<III", record, start + 8)
        if not options & ETO_GLYPH_INDEX:
            continue
        meta = {"page": page, "record_index": index, "record_offset": record_offset,
                "record_type": kind, "sub_index": sub, "font_handle": font_handle,
                "font_face": face, "x": x, "y": y}
        run = _word_run(record, n, off, floor, meta)
        malformed |= run["status"] == "invalid-glyph-span"
        runs.append(run)
    return runs, malformed


def _has_emfplus_glyph_indices(record):
    if len(record) < 16:
        return False
    data_size, identifier = struct.unpack_from("<II", record, 8)
    if identifier != 0x2B464D45 or data_size < 4 or data_size + 12 > len(record):
        return False
    cursor, end = 16, data_size + 12
    while cursor + 12 <= end:
        kind, _flags, size, payload_size = struct.unpack_from("<HHII", record, cursor)
        if size < 12 or size % 4 or cursor + size > end or payload_size > size - 12:
            return False
        if kind == 0x4036 and payload_size >= 16:
            options = struct.unpack_from("<I", record, cursor + 16)[0]
            # CmapLookup=1 means Unicode code points; unset means glyph IDs.
            if not options & 1:
                return True
        cursor += size
    return False


def parse_spool_binding(log_text, job_id, attempt, state="ACK", job_class=None, dest=None):
    """Bind metadata only; the reconstruction log's PAYLOAD is not integrity evidence."""
    matches = []
    for line_no, line in enumerate(log_text.splitlines(), 1):
        fields = dict(re.findall(r"([A-Z_]+)=([^\s]+)", line))
        if fields.get("JOB") != job_id or fields.get("STATE") != state:
            continue
        try:
            if int(fields.get("ATTEMPT", "-1")) != attempt:
                continue
        except ValueError:
            continue
        if job_class is not None and fields.get("CLASS") != job_class:
            continue
        if dest is not None and fields.get("DEST") != dest:
            continue
        matches.append({"line": line_no, "timestamp": line.split()[0],
                        "job_id": job_id, "attempt": attempt,
                        "state": state, "class": fields.get("CLASS"),
                        "dest": fields.get("DEST"),
                        "status": "matched-reconstruction-log-metadata-only"})
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {job_id} attempt {attempt} row; found {len(matches)}")
    return matches[0]


def extract_emf_glyph_indices(data, binding=None):
    runs, reasons = [], []
    coverage = {"complete": True, "full_render": False, "pages_seen": 0,
                "pages_processed": 0, "records_seen": 0,
                "unsupported_rendering": ["bitmap records", "font outlines/paths", "transforms", "clipping"],
                "reasons": reasons}
    cursor = page_no = 0
    while True:
        sig = data.find(EMF_SIGNATURE, cursor)
        if sig < 0:
            break
        cursor = sig + 4
        start = sig - 40
        if start < 0 or len(data) - start < 88:
            continue
        rtype, header_size = struct.unpack_from("<II", data, start)
        if rtype != 1 or header_size < 88 or header_size % 4:
            continue
        nbytes, nrecords = struct.unpack.from("<II", data, start + 48)
        if nbytes < header_size + 20 or nbytes > len(data) - start or not 2 <= nrecords <= MAX_RECORDS:
            continue
        coverage["pages_seen"] += 1
        stop, offset = start + nbytes, start
        fonts, selected = {}, None
        page_runs, valid, saw_eof = [], True, False
        for index in range(nrecords):
            if offset + 8 > stop:
                valid = False
                break
            kind, size = struct.unpack.from("<II", data, offset)
            if size < 8 or size % 4 or offset + size > stop:
                valid = False
                break
            rec = data[offset:offset + size]
            coverage["records_seen"] += 1
            if index == 0 and (kind != 1 or size != header_size):
                valid = False
                break
            if kind == 82 and size >= 332:  # EXTCREATEFONTINDIRECTW
                handle, = struct.unpack.from("<I", rec, 8)
                face = _face_name(rec)
                if face:
                    fonts[handle] = face
            elif kind == 37 and size >= 12:  # SELECTOBJECT
                handle, = struct.unpack_from("<I", rec, 8)
                selected = None if handle & 0x80000000 else handle
            elif kind == 40 and size >= 12:  # DELETEOBJECT
                handle, = struct.unpack_from("<I", rec, 8)
                fonts.pop(handle, None)
                if selected == handle:
                    selected = None
            elif kind in (83, 84):  # EXTTEXTOUTA/W
                if size >= 76:
                    x, y = struct.unpack_from("<ii", rec, 36)
                    n, off, options = struct.unpack.from("<III", rec, 44)
                    if options & ETO_GLYPH_INDEX:
                        meta = {"page": page_no + 1, "record_index": index,
                                "record_offset": offset, "record_type": kind,
                                "font_handle": selected, "font_face": fonts.get(selected),
                                "x": x, "y": y}
                        page_runs.append(_word_run(rec, n, off, 76, meta))
            elif kind in (96, 97):  # POLYTEXTOUTA/W
                poly, malformed = _poly_runs(rec, page_no + 1, index, offset,
                                              selected, fonts.get(selected), kind)
                page_runs.extend(poly)
                if malformed:
                    coverage["complete"] = False
                    reasons.append("malformed-polytext-record")
            elif kind == 108 and size >= 36:  # SMALLTEXTOUT
                n, options = struct.unpack_from("<II", rec, 16)
                if options & ETO_GLYPH_INDEX:
                    x, y = struct.unpack_from("<ii", rec, 8)
                    off = 36 if options & ETO_NO_RECT else 52
                    meta = {"page": page_no + 1, "record_index": index,
                            "record_offset": offset, "record_type": kind,
                            "font_handle": selected, "font_face": fonts.get(selected),
                            "x": x, "y": y}
                    page_runs.append(_word_run(rec, n, off, off, meta))
            elif kind == 70 and _has_emfplus_glyph_indices(memoryview(rec)):
                coverage["complete"] = False
                reasons.append("emfplus-driver-string-glyph-indices-not-decoded")
            if kind == 14:
                saw_eof = index == nrecords - 1
            offset += size
        if not valid or offset != stop or not saw_eof:
            coverage["complete"] = False
            reasons.append("malformed-or-incomplete-emf-page")
            continue
        if any(run["status"] == "invalid-glyph-span" for run in page_runs):
            coverage["complete"] = False
            reasons.append("invalid-glyph-span")
        page_no += 1
        coverage["pages_processed"] += 1
        runs.extend(page_runs)
        cursor = stop
    status = "no-glyph-index-runs" if not runs else "raw-glyph-indices" if coverage["complete"] else "partial"
    return {"status": status, "source_sha256": hashlib.sha256(data).hexdigest(),
            "binding": binding or {}, "runs": runs, "coverage": coverage}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("emf", type=Path)
    p.add_argument("--job-id")
    p.add_argument("--attempt", type=int)
    p.add_argument("--state", default="ACK", help="spool state to bind (default: ACK)")
    p.add_argument("--class", dest="job_class")
    p.add_argument("--dest")
    p.add_argument("--spool-log", type=Path)
    a = p.parse_args()
    if (a.job_id is None) != (a.attempt is None):
        p.error("--job-id and --attempt must be supplied together")
    if a.spool_log and a.job_id is None:
        p.error("--spool-log requires --job-id and --attempt")
    binding = {"job_id": a.job_id, "attempt": a.attempt, "state": a.state,
               "class": a.job_class, "dest": a.dest}
    binding = {k: v for k, v in binding.items() if v is not None}
    if a.spool_log:
        try:
            binding = parse_spool_binding(a.spool_log.read_text(encoding="utf-8"), a.job_id,
                                           a.attempt, a.state, a.job_class, a.dest)
        except (OSError, UnicodeError, ValueError) as exc:
            p.error(str(exc))
    result = extract_emf_glyph_indices(a.emf.read_bytes(), binding)
    print(json.dumps(result, indent=2))
    return 0 if result["coverage"]["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
