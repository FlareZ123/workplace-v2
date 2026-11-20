#!/usr/bin/env python3
"""Read OfficeArt shape metadata from the original BIFF8 stream in an XLS file.

This module deliberately runs before any LibreOffice conversion: Excel's BIFF
OfficeArt FOPT records can carry wzName/wzDescription strings that a conversion
round-trip may discard. It is a bounded, read-only intake helper, not evidence
that a particular workbook contains a caption or that a shape is historically
linked to a recovery envelope.

Format references:
- MS-XLS 2.4.170: MsoDrawing record (0x00EC) contains OfficeArtDgContainer.
- MS-XLS 2.5.193: OfficeArtClientAnchorSheet (0xF010), 18-byte payload.
- MS-ODRAW 2.2.14/2.2.9: SpContainer/FOPT hierarchy.
- MS-ODRAW 2.3.4.1-2.3.4.4: wzName (0x0380) and wzDescription (0x0381).
"""
from __future__ import annotations

import math
import struct
from typing import Any, Iterator

CFB_SIGNATURE = bytes.fromhex("D0CF11E0A1B11AE1")
FREESECT = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT = 0xFFFFFFFD
DIFSECT = 0xFFFFFFFC

MAX_XLS_BYTES = 64 * 1024 * 1024
MAX_WORKBOOK_STREAM_BYTES = 64 * 1024 * 1024
MAX_DIRECTORY_BYTES = 8 * 1024 * 1024
MAX_SHAPES = 20_000
MAX_ESCHER_DEPTH = 32

BIFF_BOUNDSHEET = 0x0085
BIFF_EOF = 0x000A
BIFF_MSODRAWING = 0x00EC
BIFF_CONTINUE = 0x003C

ESCHER_SP_CONTAINER = 0xF004
ESCHER_SP = 0xF00A
ESCHER_OPT = 0xF00B
ESCHER_CLIENT_ANCHOR = 0xF010

PROP_WZ_NAME = 0x0380
PROP_WZ_DESCRIPTION = 0x0381
PROP_PIB = 0x0104


class OfficeArtParseError(ValueError):
    """Malformed or unsupported CFB/BIFF/OfficeArt input."""


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _u64(data: bytes, offset: int) -> int:
    return struct.unpack_from("<Q", data, offset)[0]


def _column_name(zero_based: int) -> str:
    n = zero_based + 1
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def _cell_name(row_zero_based: int, col_zero_based: int) -> str:
    if row_zero_based < 0 or col_zero_based < 0:
        return ""
    return f"{_column_name(col_zero_based)}{row_zero_based + 1}"


class CompoundFile:
    """Small read-only CFB reader for the Workbook/Book stream in .xls files."""

    def __init__(self, data: bytes):
        if not isinstance(data, bytes) or len(data) < 512:
            raise OfficeArtParseError("input is too short to be a CFB file")
        if data[:8] != CFB_SIGNATURE:
            raise OfficeArtParseError("input does not have the OLE CFB signature")
        self.data = data
        self.major_version = _u16(data, 26)
        byte_order = _u16(data, 28)
        sector_shift = _u16(data, 30)
        mini_sector_shift = _u16(data, 32)
        if byte_order != 0xFFFE:
            raise OfficeArtParseError("unsupported CFB byte order")
        if self.major_version not in (3, 4):
            raise OfficeArtParseError(f"unsupported CFB major version {self.major_version}")
        if sector_shift not in (9, 12) or mini_sector_shift != 6:
            raise OfficeArtParseError("unsupported CFB sector geometry")
        if (1 << sector_shift) != (512 if self.major_version == 3 else 4096):
            raise OfficeArtParseError("CFB version/sector-size mismatch")
        self.sector_size = 1 << sector_shift
        self.mini_sector_size = 1 << mini_sector_shift
        self.num_fat_sectors = _u32(data, 44)
        self.first_directory_sector = _u32(data, 48)
        self.mini_stream_cutoff = _u32(data, 56)
        self.first_mini_fat_sector = _u32(data, 60)
        self.num_mini_fat_sectors = _u32(data, 64)
        self.first_difat_sector = _u32(data, 68)
        self.num_difat_sectors = _u32(data, 72)
        self._sectors = max(0, (len(data) // self.sector_size) - 1)
        if self.num_fat_sectors <= 0 or self.num_fat_sectors > self._sectors:
            raise OfficeArtParseError("invalid CFB FAT sector count")
        if self.num_difat_sectors > self._sectors:
            raise OfficeArtParseError("invalid CFB DIFAT sector count")
        if self.mini_stream_cutoff <= 0 or self.mini_stream_cutoff > 1_048_576:
            raise OfficeArtParseError("invalid CFB mini-stream cutoff")
        self.fat = self._load_fat()
        directory_bytes = self._read_regular_chain(
            self.first_directory_sector, max_bytes=MAX_DIRECTORY_BYTES
        )
        self.directory = self._parse_directory(directory_bytes)
        self.root = next((entry for entry in self.directory if entry["type"] == 5), None)
        if self.root is None:
            raise OfficeArtParseError("CFB root directory entry is missing")
        self.mini_fat = self._load_mini_fat()
        self.root_mini_stream = self._read_regular_stream(
            self.root["start_sector"], self.root["size"], MAX_WORKBOOK_STREAM_BYTES
        )

    def _sector(self, sector_id: int) -> bytes:
        if sector_id < 0 or sector_id >= self._sectors:
            raise OfficeArtParseError(f"CFB sector {sector_id} is outside the file")
        start = (sector_id + 1) * self.sector_size
        end = start + self.sector_size
        if end > len(self.data):
            raise OfficeArtParseError(f"CFB sector {sector_id} is truncated")
        return self.data[start:end]

    def _load_fat(self) -> list[int]:
        entries_per_sector = self.sector_size // 4
        difat_values = list(struct.unpack_from("<109I", self.data, 76))
        fat_sector_ids = [value for value in difat_values if value not in (FREESECT, ENDOFCHAIN)]
        next_difat = self.first_difat_sector
        seen_difat: set[int] = set()
        for _ in range(self.num_difat_sectors):
            if next_difat in (FREESECT, ENDOFCHAIN):
                raise OfficeArtParseError("CFB DIFAT chain ended before its declared length")
            if next_difat in seen_difat:
                raise OfficeArtParseError("cycle in CFB DIFAT chain")
            seen_difat.add(next_difat)
            sector = self._sector(next_difat)
            values = struct.unpack("<" + "I" * entries_per_sector, sector)
            fat_sector_ids.extend(value for value in values[:-1] if value not in (FREESECT, ENDOFCHAIN))
            next_difat = values[-1]
        if len(fat_sector_ids) < self.num_fat_sectors:
            raise OfficeArtParseError("CFB DIFAT does not reference enough FAT sectors")
        fat: list[int] = []
        for sector_id in fat_sector_ids[: self.num_fat_sectors]:
            fat.extend(struct.unpack("<" + "I" * entries_per_sector, self._sector(sector_id)))
        return fat

    def _chain(self, start_sector: int, table: list[int], max_sectors: int,
               physical: bool = True) -> list[int]:
        if start_sector in (FREESECT, ENDOFCHAIN):
            return []
        result: list[int] = []
        seen: set[int] = set()
        current = start_sector
        while current not in (FREESECT, ENDOFCHAIN):
            if current in seen:
                raise OfficeArtParseError("cycle in CFB sector chain")
            if current >= len(table):
                raise OfficeArtParseError("CFB sector chain points outside allocation table")
            if len(result) >= max_sectors:
                raise OfficeArtParseError("CFB sector chain exceeds size bound")
            if physical and current >= self._sectors:
                raise OfficeArtParseError("CFB sector chain points outside file")
            seen.add(current)
            result.append(current)
            current = table[current]
        return result

    def _read_regular_chain(self, start_sector: int, max_bytes: int) -> bytes:
        max_sectors = min(self._sectors, math.ceil(max_bytes / self.sector_size) + 1)
        chain = self._chain(start_sector, self.fat, max_sectors)
        raw = b"".join(self._sector(sector_id) for sector_id in chain)
        if len(raw) > max_bytes + self.sector_size:
            raise OfficeArtParseError("CFB regular stream exceeds size bound")
        return raw

    def _read_regular_stream(self, start_sector: int, size: int, max_bytes: int) -> bytes:
        if size < 0 or size > max_bytes:
            raise OfficeArtParseError("CFB stream size exceeds bound")
        if size == 0:
            return b""
        raw = self._read_regular_chain(start_sector, max_bytes)
        if len(raw) < size:
            raise OfficeArtParseError("CFB regular stream is shorter than declared size")
        return raw[:size]

    def _parse_directory(self, data: bytes) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for offset in range(0, len(data) - 127, 128):
            record = data[offset : offset + 128]
            name_length = _u16(record, 64)
            object_type = record[66]
            if object_type == 0:
                continue
            if name_length < 2 or name_length > 64 or name_length % 2:
                name = ""
            else:
                name = record[: name_length - 2].decode("utf-16le", "replace")
            entries.append({
                "name": name,
                "type": object_type,
                "start_sector": _u32(record, 116),
                "size": _u64(record, 120),
            })
        return entries

    def _load_mini_fat(self) -> list[int]:
        if self.num_mini_fat_sectors == 0:
            return []
        max_bytes = self.num_mini_fat_sectors * self.sector_size
        raw = self._read_regular_chain(self.first_mini_fat_sector, max_bytes)[:max_bytes]
        if len(raw) < max_bytes:
            raise OfficeArtParseError("CFB mini FAT is shorter than declared size")
        return list(struct.unpack("<" + "I" * (len(raw) // 4), raw))

    def _read_mini_stream(self, start_sector: int, size: int) -> bytes:
        if size == 0:
            return b""
        if not self.mini_fat:
            raise OfficeArtParseError("CFB mini stream is required but mini FAT is absent")
        needed = math.ceil(size / self.mini_sector_size)
        chain = self._chain(start_sector, self.mini_fat, needed + 1, physical=False)
        chunks: list[bytes] = []
        for mini_sector in chain:
            start = mini_sector * self.mini_sector_size
            end = start + self.mini_sector_size
            if end > len(self.root_mini_stream):
                raise OfficeArtParseError("CFB mini sector is outside the root mini stream")
            chunks.append(self.root_mini_stream[start:end])
        raw = b"".join(chunks)
        if len(raw) < size:
            raise OfficeArtParseError("CFB mini stream is shorter than declared size")
        return raw[:size]

    def read_stream(self, names: tuple[str, ...]) -> tuple[str, bytes]:
        entry = next((item for item in self.directory
                      if item["type"] == 2 and item["name"].casefold() in names), None)
        if entry is None:
            raise OfficeArtParseError("CFB Workbook/Book stream is missing")
        if entry["size"] > MAX_WORKBOOK_STREAM_BYTES:
            raise OfficeArtParseError("CFB Workbook stream exceeds size bound")
        if entry["size"] < self.mini_stream_cutoff:
            payload = self._read_mini_stream(entry["start_sector"], entry["size"])
        else:
            payload = self._read_regular_stream(
                entry["start_sector"], entry["size"], MAX_WORKBOOK_STREAM_BYTES
            )
        return entry["name"], payload


def _iter_biff_records(data: bytes, start: int = 0) -> Iterator[tuple[int, int, bytes]]:
    offset = start
    while offset + 4 <= len(data):
        record_id, length = struct.unpack_from("<HH", data, offset)
        payload_start = offset + 4
        payload_end = payload_start + length
        if payload_end > len(data):
            return
        yield offset, record_id, data[payload_start:payload_end]
        offset = payload_end


def _sheet_offsets(workbook: bytes) -> list[tuple[int, str]]:
    sheets: list[tuple[int, str]] = []
    for _, record_id, payload in _iter_biff_records(workbook):
        if record_id == BIFF_BOUNDSHEET and len(payload) >= 8:
            offset = _u32(payload, 0)
            char_count = payload[6]
            unit = 2 if payload[7] & 0x01 else 1
            raw = payload[8 : 8 + char_count * unit]
            sheet_name = raw.decode("utf-16le" if unit == 2 else "latin1", "replace")
            sheets.append((offset, sheet_name or f"Sheet{len(sheets) + 1}"))
        if record_id == BIFF_EOF:
            break
    return sorted(sheets, key=lambda item: item[0])


def _decode_officeart_string(data: bytes) -> str:
    if len(data) % 2:
        data = data[:-1]
    return data.decode("utf-16le", "replace").rstrip("\x00")


def _parse_fopt(payload: bytes, instance: int, shape: dict[str, Any] | None,
                warnings: list[str]) -> None:
    count = instance
    table_bytes = count * 6
    if count > 4096 or table_bytes > len(payload):
        warnings.append("FOPT property table exceeds record bounds")
        return
    complex_offset = table_bytes
    for index in range(count):
        opid, value = struct.unpack_from("<HI", payload, index * 6)
        property_id = opid & 0x3FFF
        if not (opid & 0x8000):
            if property_id == PROP_PIB and shape is not None:
                shape["pib"] = value
                shape["pib_fbid"] = bool(opid & 0x4000)
                if not shape["pib_fbid"]:
                    warnings.append("FOPT pib property is missing the fBid BLIP-reference flag")
            continue
        end = complex_offset + value
        if end > len(payload):
            warnings.append(f"FOPT complex property 0x{property_id:04X} exceeds record bounds")
            return
        raw = payload[complex_offset:end]
        complex_offset = end
        if property_id in (PROP_WZ_NAME, PROP_WZ_DESCRIPTION):
            if value % 2:
                warnings.append(f"FOPT property 0x{property_id:04X} has odd UTF-16 byte length")
            if shape is not None:
                key = "wz_name" if property_id == PROP_WZ_NAME else "wz_description"
                shape[key] = _decode_officeart_string(raw)


def _parse_client_anchor(payload: bytes, shape: dict[str, Any] | None,
                         warnings: list[str]) -> None:
    if len(payload) != 18:
        warnings.append(f"ClientAnchorSheet has payload length {len(payload)} (expected 18)")
        return
    flags, col_left, dx_left, row_top, dy_top, col_right, dx_right, row_bottom, dy_bottom = struct.unpack(
        "<H H h H h H h H h", payload
    )
    anchor = {
        "flags": flags,
        "col_left": col_left,
        "dx_left": dx_left,
        "row_top": row_top,
        "dy_top": dy_top,
        "col_right": col_right,
        "dx_right": dx_right,
        "row_bottom": row_bottom,
        "dy_bottom": dy_bottom,
        "top_left_cell": _cell_name(row_top, col_left),
        "bottom_right_cell": _cell_name(row_bottom, col_right),
    }
    if shape is not None:
        shape["anchor"] = anchor
        shape["anchor_cell"] = anchor["top_left_cell"]


def _parse_escher_records(data: bytes, sheet_name: str, shapes: list[dict[str, Any]],
                          warnings: list[str], depth: int = 0,
                          active_shape: dict[str, Any] | None = None) -> None:
    if depth > MAX_ESCHER_DEPTH:
        warnings.append("OfficeArt nesting depth exceeded")
        return
    offset = 0
    while offset + 8 <= len(data):
        options, record_type, record_length = struct.unpack_from("<HHI", data, offset)
        record_version = options & 0x000F
        record_instance = (options >> 4) & 0x0FFF
        payload_start = offset + 8
        payload_end = payload_start + record_length
        if payload_end > len(data):
            warnings.append(f"truncated OfficeArt record 0x{record_type:04X}")
            return
        payload = data[payload_start:payload_end]
        if record_type == ESCHER_SP_CONTAINER:
            shape: dict[str, Any] = {
                "sheet": sheet_name,
                "shape_index": len(shapes) + 1,
                "shape_type": None,
                "shape_id": None,
                "shape_flags": None,
                "anchor_cell": None,
                "anchor": None,
                "wz_name": None,
                "wz_description": None,
            }
            _parse_escher_records(payload, sheet_name, shapes, warnings, depth + 1, shape)
            if any(shape.get(key) is not None for key in (
                "shape_type", "anchor", "wz_name", "wz_description"
            )):
                shape["is_picture_shape"] = shape.get("shape_type") == 75
                shapes.append(shape)
                if len(shapes) >= MAX_SHAPES:
                    warnings.append(f"shape count reached {MAX_SHAPES} limit")
                    return
        elif record_version == 0x000F:
            _parse_escher_records(payload, sheet_name, shapes, warnings, depth + 1, active_shape)
        elif record_type == ESCHER_SP and active_shape is not None:
            if len(payload) >= 8:
                active_shape["shape_type"] = record_instance
                active_shape["shape_id"] = _u32(payload, 0)
                active_shape["shape_flags"] = _u32(payload, 4)
            else:
                warnings.append("OfficeArtSp record is shorter than 8 bytes")
        elif record_type == ESCHER_OPT:
            _parse_fopt(payload, record_instance, active_shape, warnings)
        elif record_type == ESCHER_CLIENT_ANCHOR:
            _parse_client_anchor(payload, active_shape, warnings)
        offset = payload_end


def _sheet_drawing_stream(workbook: bytes, start: int) -> bytes:
    chunks: list[bytes] = []
    previous_drawing = False
    for _, record_id, payload in _iter_biff_records(workbook, start):
        if record_id == BIFF_EOF:
            break
        if record_id == BIFF_MSODRAWING:
            chunks.append(payload)
            previous_drawing = True
        elif record_id == BIFF_CONTINUE and previous_drawing:
            chunks.append(payload)
        else:
            previous_drawing = False
    return b"".join(chunks)


def extract_xls_officeart(data: bytes) -> dict[str, Any]:
    """Extract BIFF8 OfficeArt shape names/descriptions and worksheet anchors.

    All bytes are read from the original input. No conversion or file writes are
    performed. A workbook with no OfficeArt drawings returns an empty shape list.
    """
    if not isinstance(data, bytes) or not data:
        raise OfficeArtParseError("XLS input must be non-empty bytes")
    if len(data) > MAX_XLS_BYTES:
        raise OfficeArtParseError(f"XLS input exceeds {MAX_XLS_BYTES} byte limit")
    compound = CompoundFile(data)
    stream_name, workbook = compound.read_stream(("workbook", "book"))
    if len(workbook) > MAX_WORKBOOK_STREAM_BYTES:
        raise OfficeArtParseError("Workbook stream exceeds size bound")
    sheet_offsets = _sheet_offsets(workbook)
    shapes: list[dict[str, Any]] = []
    warnings: list[str] = []
    for start, sheet_name in sheet_offsets:
        if start < 0 or start >= len(workbook):
            warnings.append(f"sheet {sheet_name} offset is outside Workbook stream")
            continue
        drawing_stream = _sheet_drawing_stream(workbook, start)
        if drawing_stream:
            _parse_escher_records(drawing_stream, sheet_name, shapes, warnings)
    return {
        "format": "BIFF8/OfficeArt",
        "workbook_stream": stream_name,
        "workbook_stream_bytes": len(workbook),
        "sheet_count": len(sheet_offsets),
        "shapes": shapes,
        "warnings": warnings,
        "source_bytes": len(data),
    }
