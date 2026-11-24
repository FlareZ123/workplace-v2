"""Pure BIFF8 XF helpers for the bounded K01/mug-stock K04 hypothesis.

A native BIFF8 reader must supply the cell XF indexes for the eight
K01-derived coordinates in source order. These helpers resolve effective fill
attributes and assemble the narrowly specified 16-byte candidate. They do not
locate arbitrary cells or open workbooks.

MS-XLS XF/CellXF payload offsets (excluding the 4-byte BIFF record header):
  * [4:6]: fStyle (bit 2), ixfParent (bits 15..4)
  * [8:10]: fAtrPat (bit 14)
  * [14:18]: fls (bits 31..26)
  * [18:20]: icvFore (bits 6..0), icvBack (bits 13..7)

K01 is read as eight (row byte, 1-based Excel column ordinal) pairs, in
A/B/C/D order, two coordinates per group. The original workbook is required.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import struct
from typing import Sequence


class XFError(ValueError):
    """Malformed or unsupported BIFF8 XF data."""


@dataclass(frozen=True)
class XFPattern:
    is_style: bool
    parent_index: int
    has_own_pattern: bool
    fill_pattern: int
    foreground_index: int
    background_index: int
    pivot_button: int
    reserved: int
    raw_payload: bytes


def excel_column_name(ordinal: int) -> str:
    """Convert a 1-based BIFF8 column ordinal (1..256) to A1 letters."""
    if not 1 <= ordinal <= 256:
        raise XFError(f"BIFF8 column ordinal out of range: {ordinal}")
    chars = []
    n = ordinal
    while n:
        n, rem = divmod(n - 1, 26)
        chars.append(chr(ord("A") + rem))
    return "".join(reversed(chars))


def derive_k01_cells(k01_hex: str) -> tuple[str, ...]:
    """Decode a 16-byte K01 component as eight ordered (row, column) pairs."""
    try:
        raw = bytes.fromhex(k01_hex)
    except ValueError as exc:
        raise XFError("K01 must be an even-length hexadecimal string") from exc
    if len(raw) != 16:
        raise XFError(f"K01 must be exactly 16 bytes, got {len(raw)}")
    cells = []
    for row, column in zip(raw[0::2], raw[1::2]):
        if row == 0:
            raise XFError("K01 row byte 0 is not a valid 1-based row")
        cells.append(f"{excel_column_name(column)}{row}")
    return tuple(cells)


def verify_and_derive_k01_cells(k01_hex: str, expected_sha256: str) -> tuple[str, ...]:
    """Verify the accepted K01 component before using it as a cell selector."""
    try:
        raw = bytes.fromhex(k01_hex)
    except ValueError as exc:
        raise XFError("K01 must be hexadecimal") from exc
    digest = hashlib.sha256(raw).hexdigest()
    if digest.lower() != expected_sha256.lower():
        raise XFError(f"K01 component commitment mismatch: {digest}")
    return derive_k01_cells(k01_hex)


def parse_xf_payload(payload: bytes) -> XFPattern:
    """Parse the 20-byte BIFF8 XF record payload (excluding its 4-byte header)."""
    if len(payload) != 20:
        raise XFError(f"BIFF8 XF payload must be 20 bytes, got {len(payload)}")
    protection = struct.unpack_from("<H", payload, 4)[0]
    used_attributes = struct.unpack_from("<H", payload, 8)[0]
    fill_word = struct.unpack_from("<I", payload, 14)[0]
    colour_word = struct.unpack_from("<H", payload, 18)[0]
    return XFPattern(
        is_style=bool((protection >> 2) & 1),
        parent_index=(protection >> 4) & 0x0FFF,
        has_own_pattern=bool((used_attributes >> 14) & 1),
        fill_pattern=(fill_word >> 26) & 0x3F,
        foreground_index=colour_word & 0x7F,
        background_index=(colour_word >> 7) & 0x7F,
        pivot_button=(colour_word >> 14) & 1,
        reserved=(colour_word >> 15) & 1,
        raw_payload=payload,
    )


def effective_cell_pattern(cell_xf_index: int, xf_payloads: Sequence[bytes]) -> XFPattern:
    """Resolve a cell XF's effective fill pattern using fAtrPat inheritance."""
    if not 0 <= cell_xf_index < len(xf_payloads):
        raise XFError(f"cell XF index out of range: {cell_xf_index}")
    cell_xf = parse_xf_payload(xf_payloads[cell_xf_index])
    if cell_xf.is_style:
        raise XFError(f"cell XF index {cell_xf_index} points to a style XF")
    if cell_xf.has_own_pattern:
        return cell_xf
    parent_index = cell_xf.parent_index
    if not 0 <= parent_index < len(xf_payloads):
        raise XFError(f"parent style XF index out of range: {parent_index}")
    parent = parse_xf_payload(xf_payloads[parent_index])
    if not parent.is_style:
        raise XFError(f"cell XF {cell_xf_index} parent {parent_index} is not a style XF")
    return parent


def assemble_k04_payload(cell_xf_indices: Sequence[int], xf_payloads: Sequence[bytes]) -> bytes:
    """Build the 16-byte hypothesis: fore/back index bytes per K01-selected cell."""
    if len(cell_xf_indices) != 8:
        raise XFError(f"expected exactly 8 K01 cell XF indexes, got {len(cell_xf_indices)}")
    out = bytearray()
    for cell_xf_index in cell_xf_indices:
        pattern = effective_cell_pattern(cell_xf_index, xf_payloads)
        out.extend((pattern.foreground_index, pattern.background_index))
    if len(out) != 16:
        raise AssertionError("internal K04 payload width error")
    return bytes(out)


def check_k04_commitment(payload: bytes, mask: bytes, expected_sha256: str) -> dict:
    """Apply the official route XOR and test the unchanged full SHA256."""
    if len(payload) != 16 or len(mask) != 16:
        raise XFError("K04 payload and mask must each be exactly 16 bytes")
    if len(expected_sha256) != 64:
        raise XFError("expected K04 SHA256 must be 64 hexadecimal characters")
    try:
        int(expected_sha256, 16)
    except ValueError as exc:
        raise XFError("expected K04 SHA256 is not hexadecimal") from exc
    component = bytes(a ^ b for a, b in zip(payload, mask))
    digest = hashlib.sha256(component).hexdigest()
    return {
        "payload_hex": payload.hex().upper(),
        "component_hex": component.hex().upper(),
        "sha256": digest,
        "pass": digest.lower() == expected_sha256.lower(),
    }
