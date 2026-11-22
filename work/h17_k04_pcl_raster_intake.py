"""Recover monochrome PCL5 raster coupons from native printer spool streams.

Uses only documented PCL5 commands: ESC*r#S / #T / #A / B/C,
ESC*b#M (0 unencoded, 1 RLE, 2 TIFF PackBits), ESC*b#W row bytes and
ESC*b#Y blank row advance. Compound parameter continuation is supported.

HP PCL 5 reference, raster graphics chapter:
https://www.hp.com/ctg/Manual/bpl13210.pdf

The output is image evidence, never an accepted K04 component by itself.
A barcode extracted from the raster still must pass the untouched original
masked-coupon SHA256 check. No PDF rendering or OCR is performed here.
"""
from __future__ import annotations

import io
import re
from collections.abc import Iterator

_MAX_PIXELS = 24_000_000
_MAX_WIDTH = 8192
_MAX_HEIGHT = 8192
_MAX_ROWS = 8192
_MAX_COMMANDS = 1_000_000
_MAX_IMAGES = 48
_COMMAND_ARG = re.compile(rb"([+-]?\d*)([A-Za-z])")


def _expand_row(payload: bytes, mode: int, width_bytes: int) -> bytes | None:
    if mode == 0:
        out = payload
    elif mode == 1:
        if len(payload) % 2:
            return None
        out = bytearray()
        for offset in range(0, len(payload), 2):
            out.extend(bytes([payload[offset + 1]]) * (payload[offset] + 1))
            if len(out) > width_bytes:
                return None
    elif mode == 2:
        out = bytearray()
        offset = 0
        while offset < len(payload):
            command = payload[offset]
            offset += 1
            if command < 128:
                count = command + 1
                if offset + count > len(payload):
                    return None
                out.extend(payload[offset:offset + count])
                offset += count
            elif command > 128:
                if offset >= len(payload):
                    return None
                out.extend(bytes([payload[offset]]) * (257 - command))
                offset += 1
            if len(out) > width_bytes:
                return None
    else:
        return None
    if len(out) > width_bytes:
        return None
    return bytes(out) + bytes(width_bytes - len(out))


def extract_pcl_raster_images(data: bytes) -> Iterator[tuple[str, bytes]]:
    """Yield complete, bounded, standalone PNGs from native PCL5 raster rows."""
    try:
        from PIL import Image
    except ImportError:
        return
    width = height = 0
    mode = 0
    active = False
    row_width = 0
    rows: list[bytes] = []
    cursor = 0
    emitted = 0
    commands = 0
    while commands < _MAX_COMMANDS and emitted < _MAX_IMAGES:
        found = data.find(b"\x1b*", cursor)
        if found < 0:
            return
        cursor = found + 2
        if cursor >= len(data) or data[cursor] not in (ord("r"), ord("b")):
            continue
        group = data[cursor]
        cursor += 1
        for _ in range(16):
            match = _COMMAND_ARG.match(data, cursor)
            if match is None:
                break
            commands += 1
            number = int(match.group(1) or b"0")
            letter = chr(match.group(2)[0])
            command = letter.upper()
            cursor = match.end()
            if group == ord("r"):
                if command == "S":
                    width = number
                elif command == "T":
                    height = number
                elif command == "A":
                    active = bool(
                        0 < width <= _MAX_WIDTH
                        and 0 < height <= _MAX_HEIGHT
                        and width * height <= _MAX_PIXELS
                    )
                    row_width = (width + 7) // 8
                    rows = []
                elif command in ("B", "C") and active:
                    if len(rows) == height and len(rows) <= _MAX_ROWS:
                        # PCL: 1 bit denotes ink. Pillow mode 1: 0 denotes ink.
                        ink = b"".join(rows)
                        image = Image.frombytes(
                            "1", (width, height),
                            bytes(byte ^ 255 for byte in ink),
                        )
                        buffer = io.BytesIO()
                        image.save(buffer, "PNG")
                        emitted += 1
                        yield f"pcl-raster-{emitted}-mode-{mode}", buffer.getvalue()
                    active = False
                    rows = []
            elif group == ord("b"):
                if command == "M":
                    mode = number
                elif command == "Y" and active:
                    if 0 <= number <= height - len(rows):
                        rows.extend([bytes(row_width)] * number)
                    else:
                        active = False
                elif command == "W":
                    if number < 0 or number > 2 * _MAX_WIDTH:
                        active = False
                        break
                    if cursor + number > len(data):
                        return
                    compressed = data[cursor:cursor + number]
                    cursor += number
                    if active:
                        row = _expand_row(compressed, mode, row_width)
                        if row is None or len(rows) >= height:
                            active = False
                        else:
                            rows.append(row)
            if letter.isupper():
                break
