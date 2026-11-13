#!/usr/bin/env python3
"""Bounded CCITT T.6 Group-4 first-line test for H-17 K04.

Reads the pinned local source files, decodes only a 128x1 Group-4 line using
the standard all-white initial reference row, and checks the unchanged K04
commitment. No source file or verifier is modified.
"""
from __future__ import annotations

import hashlib
import io
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PINS = {
    "evidence/print/spool-reconstruction.log":
        "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/recovery-routing.json":
        "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json":
        "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
    "evidence/crew/noticeboard-and-desk-notes.txt":
        "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
}

# CCITT T.4/T.6 Modified-Huffman terminating codes, run lengths 0..63.
W_TERMINATING = """
00110101 000111 0111 1000 1011 1100 1110 1111
10011 10100 00111 01000 001000 000011 110100 110101
101010 101011 0100111 0001100 0001000 0010111 0000011 0000100
0101000 0101011 0010011 0100100 0011000 00000010 00000011 00011010
00011011 00010010 00010011 00010100 00010101 00010110 00010111 00101000
00101001 00101010 00101011 00101100 00101101 00000100 00000101 00001010
00001011 01010010 01010011 01010100 01010101 00100100 00100101 01011000
01011001 01011010 01011011 01001010 01001011 00110010 00110011 00110100
""".split()

B_TERMINATING = """
0000110111 010 11 10 011 0011 0010 00011
000101 000100 0000100 0000101 0000111 00000100 00000111 000011000
0000010111 0000011000 0000001000 00001100111 00001101000 00001101100 00000110111 00000101000
00000010111 00000011000 000011001010 000011001011 000011001100 000011001101 000001101000 000001101001
000001101010 000001101011 000011010010 000011010011 000011010100 000011010101 000011010110 000011010111
000001101100 000001101101 000011011010 000011011011 000001010100 000001010101 000001010110 000001010111
000001100100 000001100101 000001010010 000001010011 000000100100 000000110111 000000111000 000000100111
000000101000 000001011000 000001011001 000000101011 000000101100 000000101101 000000110010 000000110011
""".split()

assert len(W_TERMINATING) == 64
assert len(B_TERMINATING) == 64

WHITE_RUNS = {code: (n, False) for n, code in enumerate(W_TERMINATING)}
BLACK_RUNS = {code: (n, False) for n, code in enumerate(B_TERMINATING)}
WHITE_RUNS.update({"11011": (64, True), "10010": (128, True)})
BLACK_RUNS.update({"0000001111": (64, True), "000011001000": (128, True)})

# Standard T.6 2D mode codes. Extension mode is deliberately excluded.
MODES = {
    "1": ("V", 0),
    "011": ("V", 1),
    "010": ("V", -1),
    "000011": ("V", 2),
    "000010": ("V", -2),
    "0000011": ("V", 3),
    "0000010": ("V", -3),
    "0001": ("P", None),
    "001": ("H", None),
}
EOFB = "000000000001000000000001"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_source_pins() -> None:
    for rel, expected in SOURCE_PINS.items():
        actual = sha256_file(ROOT / rel)
        if actual != expected:
            raise SystemExit(f"source pin mismatch: {rel}: {actual} != {expected}")


def selected_payload() -> bytes:
    text = (ROOT / "evidence/print/spool-reconstruction.log").read_text()
    pattern = (
        r"^2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 "
        r"STATE=ACK CLASS=RECOVER PAYLOAD=([0-9A-F]{32}) DEST=bench$"
    )
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    if len(matches) != 1:
        raise SystemExit(f"expected one exact selected ACK2 row, found {len(matches)}")
    return bytes.fromhex(matches[0])


def parse_mh_run(bits: str, pos: int, table: dict[str, tuple[int, bool]]):
    total = 0
    while True:
        found = None
        for end in range(pos + 1, min(len(bits), pos + 13) + 1):
            code = bits[pos:end]
            if code in table:
                found = (table[code], end)
                break
        if found is None:
            return None
        (run, makeup), pos = found
        total += run
        if total > 128:
            return None
        if not makeup:
            return total, pos


def decode_t6_first_line(bits: str, width: int = 128):
    """Decode one T.6 line against the standard all-white reference row.

    Coordinate convention: a0 starts at -1 (left of pixel 0); with an
    all-white reference row, b1=b2=width-1. Horizontal run lengths are
    current color then opposite color. Pass/vertical modes update a0 and
    coding color per T.6. A successful result must assign all 128 pixels.
    The returned sample polarity is the PhotometricInterpretation=1
    convention used by the independent libtiff fixtures (white=1, black=0).
    """
    pixels = [None] * width
    a0 = -1
    color = 0
    b1 = b2 = width - 1
    pos = 0
    steps = 0

    while a0 < width - 1 and steps < 400:
        steps += 1
        mode = None
        for end in range(pos + 1, min(len(bits), pos + 8) + 1):
            code = bits[pos:end]
            if code in MODES:
                mode = MODES[code]
                pos = end
                break
        if mode is None:
            return None

        kind, offset = mode
        if kind == "P":
            a1 = b2
            if a1 <= a0 or a1 >= width:
                return None
            for x in range(a0 + 1, a1 + 1):
                pixels[x] = color
            a0 = a1

        elif kind == "V":
            a1 = b1 + offset
            if a1 < a0 or a1 >= width:
                return None
            for x in range(a0 + 1, a1 + 1):
                pixels[x] = color
            a0 = a1
            color ^= 1

        else:  # horizontal
            first_table = WHITE_RUNS if color == 0 else BLACK_RUNS
            second_table = BLACK_RUNS if color == 0 else WHITE_RUNS
            first = parse_mh_run(bits, pos, first_table)
            if first is None:
                return None
            n1, pos = first
            second = parse_mh_run(bits, pos, second_table)
            if second is None:
                return None
            n2, pos = second

            a1 = a0 + n1
            a2 = a1 + n2
            if a1 < a0 or a2 <= a0 or a2 >= width:
                return None
            for x in range(a0 + 1, a1 + 1):
                pixels[x] = color
            for x in range(a1 + 1, a2 + 1):
                pixels[x] = color ^ 1
            a0 = a2

    if a0 < width - 1 or any(pixel is None for pixel in pixels):
        return None
    return pixels, pos


def bitstream(data: bytes, fillorder: int) -> str:
    if fillorder == 1:
        return "".join(f"{byte:08b}" for byte in data)
    if fillorder == 2:
        return "".join(f"{byte:08b}"[::-1] for byte in data)
    raise ValueError(fillorder)


def reverse_bits_each_byte(data: bytes) -> bytes:
    return bytes(int(f"{byte:08b}"[::-1], 2) for byte in data)


def pack_pixels(pixels, invert: bool = False, lsb_first: bool = False) -> bytes:
    values = [pixel ^ int(invert) for pixel in pixels]
    out = bytearray()
    for offset in range(0, 128, 8):
        group = values[offset:offset + 8]
        if lsb_first:
            group = group[::-1]
        out.append(int("".join(str(value) for value in group), 2))
    return bytes(out)


def decode_strip(data: bytes, fillorder: int):
    bits = bitstream(data, fillorder)
    tails = [("no-eofb", pad, "0" * pad) for pad in range(8)]
    tails += [("eofb", pad, EOFB + "0" * pad) for pad in range(8)]
    framing_matches = []
    parses = []
    for kind, pad, tail in tails:
        if tail and not bits.endswith(tail):
            continue
        framing_matches.append((kind, pad))
        encoded = bits[:-len(tail)] if tail else bits
        decoded = decode_t6_first_line(encoded)
        if decoded is None:
            continue
        pixels, used = decoded
        if used != len(encoded):
            continue
        parses.append((kind, pad, pixels, used))
    return framing_matches, parses


def verify_fixture(strip_hex: str, expected_hex: str, expected_pad: int) -> None:
    strip = bytes.fromhex(strip_hex)
    expected = bytes.fromhex(expected_hex)
    matches, parses = decode_strip(strip, 1)
    assert len(parses) == 1, (strip_hex, matches, len(parses))
    kind, pad, pixels, _ = parses[0]
    assert (kind, pad) == ("eofb", expected_pad), (kind, pad)
    assert pack_pixels(pixels) == expected, (pack_pixels(pixels).hex(), expected.hex())

    # FillOrder=2 is the same bitstream with each stored byte bit-reversed.
    strip_lsb = reverse_bits_each_byte(strip)
    matches_lsb, parses_lsb = decode_strip(strip_lsb, 2)
    assert len(parses_lsb) == 1, (strip_hex, matches_lsb, len(parses_lsb))
    pixels_lsb = parses_lsb[0][2]
    assert pack_pixels(pixels_lsb) == expected
    assert reverse_bits_each_byte(pack_pixels(pixels_lsb, lsb_first=True)) == expected


def run_optional_pillow_controls() -> int | None:
    try:
        from PIL import Image
    except ImportError:
        return None

    rng = random.Random(20261113)
    for index in range(100):
        samples = [rng.randrange(2) for _ in range(128)]  # 0=black, 1=white
        image = Image.new("1", (128, 1))
        image.putdata([255 if sample else 0 for sample in samples])
        output = io.BytesIO()
        image.save(output, format="TIFF", compression="group4")
        tiff = output.getvalue()
        reopened = Image.open(io.BytesIO(tiff))
        tags = reopened.tag_v2
        offsets = tags[273]
        counts = tags[279]
        strip_offset = offsets[0] if isinstance(offsets, tuple) else offsets
        strip_count = counts[0] if isinstance(counts, tuple) else counts
        strip = tiff[strip_offset:strip_offset + strip_count]
        expected = reopened.tobytes()

        _, parses = decode_strip(strip, 1)
        if len(parses) != 1 or pack_pixels(parses[0][2]) != expected:
            raise AssertionError(f"Pillow Group-4 FillOrder=1 control failed at row {index}")

        _, parses_lsb = decode_strip(reverse_bits_each_byte(strip), 2)
        if len(parses_lsb) != 1 or pack_pixels(parses_lsb[0][2]) != expected:
            raise AssertionError(f"Pillow Group-4 FillOrder=2 control failed at row {index}")
    return 100


def main() -> None:
    verify_source_pins()

    # Independent Pillow/libtiff fixtures supplied by Agent 43:
    # 17-byte strip: alternating 8-pixel runs, byte-aligned EOFB.
    verify_fixture(
        "3314CC53314CC53314CC53314CC5001001",
        "00FF00FF00FF00FF00FF00FF00FF00FF",
        expected_pad=0,
    )
    # Exact-16-byte strip: EOFB begins at bit offset 100, then 4 pad bits.
    verify_fixture(
        "26A3290183832E060CCCF07050010010",
        "FE0000003FFFE0FE7FFFFFC03E07FF87",
        expected_pad=4,
    )

    pillow_controls = run_optional_pillow_controls()

    payload = selected_payload()
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    required = acceptance["slot_sha256"]["K04"]

    framing_count = 0
    strict_parses = []
    unique_candidates = {}
    for fillorder in (1, 2):
        framing_matches, parses = decode_strip(payload, fillorder)
        framing_count += len(framing_matches)
        for kind, pad, pixels, used in parses:
            strict_parses.append((fillorder, kind, pad, used))
            # Both photometric polarities and both output bit-packing orders.
            for invert in (False, True):
                for lsb_first in (False, True):
                    coupon = pack_pixels(pixels, invert=invert, lsb_first=lsb_first)
                    component = bytes(a ^ b for a, b in zip(coupon, mask))
                    unique_candidates.setdefault(component, (fillorder, kind, pad, invert, lsb_first))

    hits = [
        (component, spec)
        for component, spec in unique_candidates.items()
        if hashlib.sha256(component).hexdigest() == required
    ]

    print(f"selected_payload={payload.hex().upper()}")
    print(f"k04_mask={mask.hex().upper()}")
    print(f"k04_required_sha256={required}")
    print(f"framing_matches={framing_count}")
    print(f"strict_128px_parses={len(strict_parses)}")
    print(f"unique_coupon_candidates={len(unique_candidates)}")
    print(f"k04_commitment_hits={len(hits)}")
    print(f"optional_pillow_random_controls={pillow_controls if pillow_controls is not None else 'skipped (Pillow unavailable)'}")
    if strict_parses:
        print(f"strict_parse_specs={strict_parses}")
    if hits:
        for component, spec in hits:
            print(f"HIT component={component.hex().upper()} spec={spec}")
        raise SystemExit("unexpected K04 commitment hit: review the result")
    print("RESULT: no strict T.6 Group-4 128x1 all-white-reference parse; no K04 candidate")


if __name__ == "__main__":
    main()
