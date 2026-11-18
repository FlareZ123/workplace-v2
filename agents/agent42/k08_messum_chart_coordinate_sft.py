#!/usr/bin/env python3
"""K08 bounded Messum chart-coordinate sampler.

Hypothesis:
- K01's eight byte pairs are logical 0..255 chart coordinates.
- The note initialism ATEALBIT means "a teal bit".
- Each of the eleven 1903 Messum sheets emits one byte from those eight bits.

This pass removes the arbitrary scan-margin assumption. It derives an ink/color
bounding box from each image, tests the eight square-coordinate symmetries, and
uses one image-adaptive eight-color palette whose most blue-green cluster is the
"teal" class. Raw RGB bit planes are retained as a diagnostic only.
"""
from __future__ import annotations

import base64
import io
import urllib.request
from dataclasses import dataclass
from PIL import Image, ImageDraw

COORDS = [
    (4, 154), (171, 46), (28, 222), (122, 130),
    (205, 124), (96, 35), (67, 3), (201, 26),
]
URLS = [
    f"https://www.antiquemapsandprints.com/cdn/shop/files/P-6-{n}a.jpg?width=1000"
    for n in range(108821, 108832)
]


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def ink_bbox(im: Image.Image) -> tuple[int, int, int, int]:
    """Derive outer printed-content bounds from a downsampled RGB image."""
    rgb = im.convert("RGB")
    scale = min(1.0, 450.0 / max(rgb.size))
    small = rgb.resize(
        (max(1, round(rgb.width * scale)), max(1, round(rgb.height * scale)))
    )
    mask = Image.new("1", small.size)
    src = small.load()
    dst = mask.load()
    for y in range(small.height):
        for x in range(small.width):
            r, g, b = src[x, y]
            chroma = max(r, g, b) - min(r, g, b)
            lum = (r + g + b) / 3
            dst[x, y] = int(lum < 225 or chroma > 28)
    box = mask.getbbox()
    if box is None:
        return (0, 0, rgb.width, rgb.height)
    x0, y0, x1, y1 = box
    inv = 1.0 / scale
    return (
        max(0, int(x0 * inv)),
        max(0, int(y0 * inv)),
        min(rgb.width, int(x1 * inv + 1)),
        min(rgb.height, int(y1 * inv + 1)),
    )


def transform(x: int, y: int, t: int) -> tuple[int, int]:
    """Eight dihedral symmetries of a logical 256x256 coordinate square."""
    if t == 0:
        return x, y
    if t == 1:
        return 255 - x, y
    if t == 2:
        return x, 255 - y
    if t == 3:
        return 255 - x, 255 - y
    if t == 4:
        return y, x
    if t == 5:
        return 255 - y, x
    if t == 6:
        return y, 255 - x
    return 255 - y, 255 - x


def map_point(
    x: int, y: int, box: tuple[int, int, int, int], t: int
) -> tuple[int, int]:
    x, y = transform(x, y, t)
    x0, y0, x1, y1 = box
    px = x0 + round(x * max(0, x1 - x0 - 1) / 255)
    py = y0 + round(y * max(0, y1 - y0 - 1) / 255)
    return px, py


def byte_from(bits: list[int], reverse: bool) -> int:
    if reverse:
        bits = bits[::-1]
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def quality(bs: bytes) -> tuple[int, int, int]:
    printable = sum(32 <= b < 127 for b in bs)
    letters_spaces = sum(
        b == 32 or 65 <= b <= 90 or 97 <= b <= 122 for b in bs
    )
    controls = sum(b < 32 and b not in (9, 10, 13) for b in bs)
    return letters_spaces, printable, -controls


@dataclass
class Sheet:
    number: int
    image: Image.Image
    box: tuple[int, int, int, int]
    qindex: Image.Image
    teal_index: int
    palette_rgb: tuple[int, int, int]


def quantized_teal(im: Image.Image, box: tuple[int, int, int, int]):
    crop = im.convert("RGB").crop(box)
    q = crop.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    counts = q.getcolors() or []
    used = [idx for _count, idx in counts]
    colors = {
        idx: tuple(pal[3 * idx:3 * idx + 3])
        for idx in used
    }

    def teal_score(rgb: tuple[int, int, int]) -> tuple[int, int]:
        r, g, b = rgb
        return (g + b - 2 * r, min(g, b) - r)

    teal = max(used, key=lambda idx: teal_score(colors[idx]))
    full = Image.new("P", im.size)
    full.paste(q, (box[0], box[1]))
    return full, teal, colors[teal]


sheets: list[Sheet] = []
for number, url in enumerate(URLS, 108821):
    data = get(url)
    im = Image.open(io.BytesIO(data))
    im.load()
    box = ink_bbox(im)
    q, teal, teal_rgb = quantized_teal(im, box)
    print(
        f"FETCH {number} bytes={len(data)} size={im.size} "
        f"bbox={box} teal_index={teal} teal_rgb={teal_rgb}"
    )
    sheets.append(Sheet(number, im.convert("RGB"), box, q, teal, teal_rgb))

# Low-resolution contact sheet for visual source-role classification only.
thumbs = []
for sheet in sheets:
    thumb = sheet.image.copy()
    thumb.thumbnail((100, 125))
    canvas = Image.new("RGB", (110, 145), "white")
    canvas.paste(thumb, ((110 - thumb.width) // 2, 18))
    ImageDraw.Draw(canvas).text((5, 5), str(sheet.number), fill="black")
    thumbs.append(canvas)
contact = Image.new("RGB", (110 * 4, 145 * 3), "white")
for i, thumb in enumerate(thumbs):
    contact.paste(thumb, ((i % 4) * 110, (i // 4) * 145))
contact.save("messum-contact.jpg", quality=35, optimize=True)
with open("messum-contact.jpg", "rb") as fh:
    print("CONTACT_B64=" + base64.b64encode(fh.read()).decode("ascii"))
print("CONTACT_SHEET messum-contact.jpg")

rows = []
for frame_name in ("full", "ink"):
    for t in range(8):
        for reverse in (False, True):
            # Main source-inspired predicate: membership in the most blue-green
            # adaptive palette cluster.
            out = []
            for sheet in sheets:
                box = (
                    (0, 0, sheet.image.width, sheet.image.height)
                    if frame_name == "full"
                    else sheet.box
                )
                bits = []
                for x, y in COORDS:
                    px, py = map_point(x, y, box, t)
                    bits.append(int(sheet.qindex.getpixel((px, py)) == sheet.teal_index))
                out.append(byte_from(bits, reverse))
            bs = bytes(out)
            rows.append(
                (quality(bs), f"teal8/{frame_name}/sym{t}", "rev" if reverse else "fwd", bs)
            )

            # Diagnostics: exact RGB bit planes at the same geometries.
            for channel, cname in enumerate("RGB"):
                for bit in range(8):
                    out = []
                    for sheet in sheets:
                        box = (
                            (0, 0, sheet.image.width, sheet.image.height)
                            if frame_name == "full"
                            else sheet.box
                        )
                        bits = []
                        for x, y in COORDS:
                            px, py = map_point(x, y, box, t)
                            bits.append((sheet.image.getpixel((px, py))[channel] >> bit) & 1)
                        out.append(byte_from(bits, reverse))
                    bs = bytes(out)
                    rows.append(
                        (
                            quality(bs),
                            f"{cname}bit{bit}/{frame_name}/sym{t}",
                            "rev" if reverse else "fwd",
                            bs,
                        )
                    )

for score, pred, order, bs in sorted(rows, reverse=True)[:20]:
    print(
        f"DECODE quality={score} pred={pred} order={order} "
        f"hex={bs.hex().upper()} repr={bs!r}"
    )
