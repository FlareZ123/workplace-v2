#!/usr/bin/env python3
"""Resolve BIFF8 OfficeArt shape pib references to embedded BStore blips.

This is a read-only, bounded companion to h17_biff_officeart.py. It parses the
Workbook-global MSODRAWINGGROUP/BStoreContainer and maps 1-based pib references
to the corresponding embedded blip. It does not infer historical source links,
read H-17 workbooks, or promote image content into K08 candidates.
"""
from __future__ import annotations

import base64
import hashlib
import struct
from typing import Any, Iterator

from h17_biff_officeart import (
    BIFF_CONTINUE,
    BIFF_EOF,
    CompoundFile,
    OfficeArtParseError,
    _iter_biff_records,
    extract_xls_officeart,
)

BIFF_MSODRAWINGGROUP = 0x00EB
ESCHER_DGG_CONTAINER = 0xF000
ESCHER_BSTORE_CONTAINER = 0xF001
ESCHER_BSE = 0xF007

MAX_ESCHER_DEPTH = 32
MAX_BSE_ENTRIES = 4096
MAX_BLIP_BYTES = 32 * 1024 * 1024

BLIP_FORMATS = {
    0xF01A: "EMF",
    0xF01B: "WMF",
    0xF01C: "PICT",
    0xF01D: "JPEG",
    0xF01E: "PNG",
    0xF01F: "DIB",
    0xF029: "TIFF",
}


def _global_drawing_group_stream(workbook: bytes) -> bytes:
    """Join the global MSODRAWINGGROUP record and its immediate CONTINUEs."""
    chunks: list[bytes] = []
    collecting = False
    for _, record_id, payload in _iter_biff_records(workbook):
        if record_id == BIFF_EOF:
            break
        if record_id == BIFF_MSODRAWINGGROUP:
            if collecting:
                collecting = False
            chunks.append(payload)
            collecting = True
        elif record_id == BIFF_CONTINUE and collecting:
            chunks.append(payload)
        else:
            collecting = False
    return b"".join(chunks)


def _iter_escher_records(data: bytes, warnings: list[str], context: str
                         ) -> Iterator[tuple[int, int, int, bytes]]:
    """Yield (version, instance, type, payload) from one bounded OfficeArt stream."""
    offset = 0
    while offset + 8 <= len(data):
        options, record_type, record_length = struct.unpack_from("<HHI", data, offset)
        payload_start = offset + 8
        payload_end = payload_start + record_length
        if record_length > MAX_BLIP_BYTES or payload_end > len(data):
            warnings.append(f"{context}: truncated/oversized OfficeArt record 0x{record_type:04X}")
            return
        version = options & 0x000F
        instance = (options >> 4) & 0x0FFF
        yield version, instance, record_type, data[payload_start:payload_end]
        offset = payload_end
    if offset != len(data) and any(data[offset:]):
        warnings.append(f"{context}: trailing bytes after OfficeArt records")


def _find_bstore_containers(data: bytes, warnings: list[str], depth: int = 0
                            ) -> list[tuple[int, bytes]]:
    if depth > MAX_ESCHER_DEPTH:
        warnings.append("OfficeArt Dgg nesting depth exceeded")
        return []
    found: list[tuple[int, bytes]] = []
    for version, instance, record_type, payload in _iter_escher_records(
        data, warnings, "DggContainer"
    ):
        if record_type == ESCHER_BSTORE_CONTAINER:
            found.append((instance, payload))
        elif version == 0x000F:
            found.extend(_find_bstore_containers(payload, warnings, depth + 1))
    return found


def _decode_bse_name(raw: bytes, warnings: list[str], index: int) -> str | None:
    if not raw:
        return None
    if len(raw) % 2:
        warnings.append(f"BSE {index}: odd UTF-16 name length")
        raw = raw[:-1]
    return raw.decode("utf-16le", "replace").rstrip("\x00")


def _parse_blip_record(record: bytes, warnings: list[str], index: int,
                       include_image_data: bool) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "index": index,
        "format": None,
        "length": 0,
        "sha256": None,
        "uid_hex": None,
        "tag": None,
        "magic_valid": None,
    }
    if len(record) < 8:
        warnings.append(f"BSE {index}: embedded blip record is shorter than its header")
        return entry
    options, record_type, record_length = struct.unpack_from("<HHI", record, 0)
    record_end = 8 + record_length
    if record_end > len(record):
        warnings.append(f"BSE {index}: embedded blip record exceeds BSE bounds")
        return entry
    if record_end < len(record) and any(record[record_end:]):
        warnings.append(f"BSE {index}: non-zero bytes follow embedded blip record")
    instance = (options >> 4) & 0x0FFF
    fmt = BLIP_FORMATS.get(record_type)
    entry["format"] = fmt or f"OfficeArt-0x{record_type:04X}"
    entry["record_type"] = record_type
    entry["record_instance"] = instance

    if fmt is None:
        warnings.append(f"BSE {index}: unsupported embedded blip type 0x{record_type:04X}")
        return entry

    payload = record[8:record_end]
    # OfficeArt blip instances use an even value for one UID and odd for two.
    uid_count = 2 if (instance & 1) else 1
    uid_bytes = uid_count * 16
    if len(payload) < uid_bytes:
        warnings.append(f"BSE {index}: blip UID area is truncated")
        return entry
    entry["uid_hex"] = payload[:16].hex().upper()

    if fmt in ("PNG", "JPEG", "DIB", "TIFF"):
        if len(payload) <= uid_bytes:
            warnings.append(f"BSE {index}: blip payload has no tag/data")
            return entry
        entry["tag"] = payload[uid_bytes]
        image_bytes = payload[uid_bytes + 1:]
    elif fmt in ("EMF", "WMF"):
        # Metafile blips have a 34-byte OfficeArt metafile header after the UID(s).
        if len(payload) < uid_bytes + 34:
            warnings.append(f"BSE {index}: metafile header is truncated")
            return entry
        entry["metafile_header_hex"] = payload[uid_bytes:uid_bytes + 34].hex().upper()
        image_bytes = payload[uid_bytes + 34:]
    else:
        # PICT has format-specific framing; preserve its bounded raw payload only.
        image_bytes = payload[uid_bytes:]

    if len(image_bytes) > MAX_BLIP_BYTES:
        warnings.append(f"BSE {index}: extracted image exceeds size bound")
        return entry
    if fmt == "PNG":
        magic_valid = image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    elif fmt == "JPEG":
        magic_valid = image_bytes.startswith(b"\xff\xd8")
    elif fmt == "TIFF":
        magic_valid = image_bytes.startswith((b"II*\x00", b"MM\x00*"))
    elif fmt == "DIB":
        magic_valid = (
            len(image_bytes) >= 4
            and int.from_bytes(image_bytes[:4], "little") in (12, 40, 52, 56, 64, 108, 124)
        )
    else:
        magic_valid = None
    entry["magic_valid"] = magic_valid
    if magic_valid is False:
        warnings.append(f"BSE {index}: {fmt} blip does not have its expected image signature")

    entry["length"] = len(image_bytes)
    entry["sha256"] = hashlib.sha256(image_bytes).hexdigest()
    if include_image_data:
        entry["data_base64"] = base64.b64encode(image_bytes).decode("ascii")
    return entry


def _parse_bse(payload: bytes, index: int, warnings: list[str],
               include_image_data: bool) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "index": index,
        "entry_type": "BSE",
        "name": None,
        "bt_win32": None,
        "bt_mac": None,
        "uid_hex": None,
        "size": None,
        "c_ref": None,
        "fo_delay": None,
        "usage": None,
        "embedded": False,
        "delayed": False,
        "format": None,
        "length": 0,
        "sha256": None,
        "magic_valid": None,
    }
    if len(payload) < 36:
        warnings.append(f"BSE {index}: fixed header is shorter than 36 bytes")
        return entry

    bt_win32, bt_mac = payload[0], payload[1]
    uid = payload[2:18]
    tag = struct.unpack_from("<H", payload, 18)[0]
    size, c_ref, fo_delay = struct.unpack_from("<III", payload, 20)
    usage, cb_name, unused2, unused3 = payload[32:36]
    name_end = 36 + cb_name
    if name_end > len(payload):
        warnings.append(f"BSE {index}: name exceeds BSE bounds")
        return entry
    name = _decode_bse_name(payload[36:name_end], warnings, index)

    entry.update({
        "name": name,
        "bt_win32": bt_win32,
        "bt_mac": bt_mac,
        "uid_hex": uid.hex().upper(),
        "tag": tag,
        "size": size,
        "c_ref": c_ref,
        "fo_delay": fo_delay,
        "usage": usage,
        "unused2": unused2,
        "unused3": unused3,
    })
    embedded = payload[name_end:]
    if not embedded:
        if fo_delay not in (0xFFFFFFFF, 0):
            entry["delayed"] = True
            warnings.append(f"BSE {index}: delayed blip reference is not resolved")
        else:
            warnings.append(f"BSE {index}: no embedded blip data")
        return entry

    entry["embedded"] = True
    if size not in (0, len(embedded)):
        warnings.append(
            f"BSE {index}: declared blip size {size} differs from embedded length {len(embedded)}"
        )
    blip = _parse_blip_record(embedded, warnings, index, include_image_data)
    for key in ("format", "length", "sha256", "magic_valid", "record_type",
                "record_instance", "tag", "metafile_header_hex"):
        if key in blip:
            entry[key] = blip[key]
    if blip.get("uid_hex"):
        entry["blip_uid_hex"] = blip["uid_hex"]
    if "data_base64" in blip:
        entry["data_base64"] = blip["data_base64"]
    return entry


def _parse_bstore(payload: bytes, declared_count: int, warnings: list[str],
                  include_image_data: bool) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for version, instance, record_type, child_payload in _iter_escher_records(
        payload, warnings, "BStoreContainer"
    ):
        if len(entries) >= MAX_BSE_ENTRIES:
            warnings.append(f"BStoreContainer reached {MAX_BSE_ENTRIES} entry limit")
            break
        index = len(entries) + 1
        if record_type == ESCHER_BSE:
            entries.append(_parse_bse(child_payload, index, warnings, include_image_data))
        elif record_type in BLIP_FORMATS:
            # A direct blip is still a positional BStore entry.
            raw_record = struct.pack("<HHI", (instance << 4) | version,
                                     record_type, len(child_payload)) + child_payload
            blip = _parse_blip_record(raw_record, warnings, index, include_image_data)
            blip["entry_type"] = "BLIP"
            entries.append(blip)
        else:
            warnings.append(f"BStore entry {index}: unsupported record 0x{record_type:04X}")
            entries.append({
                "index": index,
                "entry_type": "UNKNOWN",
                "record_type": record_type,
                "format": None,
                "length": 0,
                "sha256": None,
            })
    if declared_count and declared_count != len(entries):
        warnings.append(
            f"BStoreContainer declares {declared_count} entries but {len(entries)} were parsed"
        )
    return entries


def extract_xls_officeart_blips(data: bytes, *,
                                include_image_data: bool = False) -> dict[str, Any]:
    """Extract shape metadata and resolve 1-based pib references to BStore blips.

    The default result contains metadata and hashes only. Set include_image_data
    explicitly to include base64-encoded embedded image bytes for a later,
    separately authorized media-intake stage.
    """
    result = extract_xls_officeart(data)
    compound = CompoundFile(data)
    _, workbook = compound.read_stream(("workbook", "book"))
    warnings: list[str] = []
    drawing_group = _global_drawing_group_stream(workbook)
    bstores: list[tuple[int, bytes]] = []
    if drawing_group:
        for version, instance, record_type, payload in _iter_escher_records(
            drawing_group, warnings, "MSODRAWINGGROUP"
        ):
            if record_type == ESCHER_DGG_CONTAINER or version == 0x000F:
                bstores.extend(_find_bstore_containers(payload, warnings, 1))
    else:
        warnings.append("Workbook has no global MSODRAWINGGROUP record")

    if len(bstores) > 1:
        warnings.append(f"Workbook has {len(bstores)} BStoreContainers; first one used")
    blip_store: list[dict[str, Any]] = []
    if bstores:
        declared_count, bstore_payload = bstores[0]
        blip_store = _parse_bstore(
            bstore_payload, declared_count, warnings, include_image_data
        )

    for shape in result["shapes"]:
        pib = shape.get("pib")
        if pib is None:
            continue
        if not shape.get("pib_fbid", False):
            shape["blip_ref_status"] = "pib-without-fBid"
            warnings.append(
                f"shape {shape.get('shape_index')}: pib property is not marked as a BLIP reference"
            )
            continue
        if pib == 0:
            shape["blip_ref_status"] = "no-reference"
            continue
        if pib > len(blip_store):
            shape["blip_ref_status"] = "out-of-range"
            warnings.append(
                f"shape {shape.get('shape_index')}: pib {pib} exceeds BStore count {len(blip_store)}"
            )
            continue
        entry = blip_store[pib - 1]
        shape["blip_ref_status"] = "resolved" if entry.get("sha256") else "unresolved"
        shape["blip_ref"] = {
            key: entry.get(key)
            for key in ("index", "entry_type", "name", "format", "length", "sha256",
                        "uid_hex", "blip_uid_hex", "magic_valid", "delayed")
            if key in entry
        }

    result["blip_store"] = blip_store
    result["blip_warnings"] = warnings
    result["warnings"].extend(warnings)
    result["image_data_included"] = include_image_data
    return result
