#!/usr/bin/env python3
"""Six-slot ATEALBIT coordinate decoder for bounded image controls.

Each accepted 16-byte REC8/1 component is interpreted as eight unsigned-byte
(x, y) pairs. One selected bit at those eight coordinates forms one output
byte. Six accepted components therefore yield six output bytes from one image.

This is a read-only exploratory decoder. It does not assert that any image is
the historical K08 carrier and it does not alter the canonical candidate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

KNOWN_SLOTS = ("K01", "K02", "K03", "K05", "K06", "K07")
IMAGE_SUFFIXES = {".img", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def coordinates(component_hex: str) -> list[tuple[int, int]]:
    raw = bytes.fromhex(component_hex)
    if len(raw) != 16:
        raise ValueError("component must be exactly 16 bytes")
    return [(raw[i], raw[i + 1]) for i in range(0, 16, 2)]


def orient_byte(x: int, y: int, code: int) -> tuple[int, int]:
    """Eight D4 orientations in the native unsigned-byte coordinate square."""
    if code & 4:
        x, y = y, x
    if code & 1:
        x = 255 - x
    if code & 2:
        y = 255 - y
    return x, y


def sample_byte(
    image: Image.Image,
    coords: list[tuple[int, int]],
    mapping: str,
    orientation: int,
    bitplane: int,
    bitorder: str,
) -> int:
    width, height = image.size
    bits: list[int] = []
    for x0, y0 in coords:
        x0, y0 = orient_byte(x0, y0, orientation)
        if mapping == "scaled":
            x = round(x0 * (width - 1) / 255)
            y = round(y0 * (height - 1) / 255)
        else:
            x, y = x0, y0
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError("coordinate fell outside the image")
        bits.append((image.getpixel((x, y)) >> bitplane) & 1)

    shifts = range(7, -1, -1) if bitorder == "msb" else range(8)
    return sum(bit << shift for bit, shift in zip(bits, shifts))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()

    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    slot_coords = {slot: coordinates(candidate[slot]) for slot in KNOWN_SLOTS}
    files = sorted(
        path for path in args.images.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )

    tested = 0
    max_printable = 0
    five_printable: list[dict[str, object]] = []
    best: list[dict[str, object]] = []

    for path in files:
        with Image.open(path) as opened:
            image = opened.convert("L")
        for mapping in ("direct", "scaled"):
            for orientation in range(8):
                for bitplane in range(8):
                    for bitorder in ("msb", "lsb"):
                        output = bytes(
                            sample_byte(
                                image,
                                slot_coords[slot],
                                mapping,
                                orientation,
                                bitplane,
                                bitorder,
                            )
                            for slot in KNOWN_SLOTS
                        )
                        tested += 1
                        printable = sum(0x20 <= value <= 0x7E for value in output)
                        row = {
                            "image": path.name,
                            "mapping": mapping,
                            "orientation": orientation,
                            "bitplane": bitplane,
                            "bitorder": bitorder,
                            "hex": output.hex().upper(),
                            "printable_bytes": printable,
                        }
                        if printable > max_printable:
                            max_printable = printable
                            best = [row]
                        elif printable == max_printable:
                            best.append(row)
                        if printable >= 5:
                            five_printable.append(row)

    print(json.dumps({
        "images_scanned": len(files),
        "configurations_tested": tested,
        "max_printable_bytes_of_six": max_printable,
        "five_or_more_printable_count": len(five_printable),
        "five_or_more_printable": five_printable,
        "best": best[:32],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
