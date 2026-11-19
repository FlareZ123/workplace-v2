#!/usr/bin/env python3
"""Synthetic positive control for a color-masked K08 teal-bit decoder.

This does NOT inspect or recover the missing H-17 photograph. It tests one
bounded interpretation of "A TEAL BIT": select teal pixels by a fixed HSV mask,
then read the green-channel LSB in row-major order.
"""
import hashlib
import hmac

import numpy as np
from PIL import Image

NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
PHRASE = "the lamp stays on until the sea turns quiet"
SEED = 20261119


def normalize(text):
    text = text.lower()
    text = "".join(c if ("a" <= c <= "z" or "0" <= c <= "9" or c.isspace()) else " " for c in text)
    return " ".join(text.split())


def teal_mask(rgb):
    hsv = np.asarray(Image.fromarray(rgb, "RGB").convert("HSV"), dtype=np.uint8)
    hue, saturation, value = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    # PIL hue is 0..255; 110..150 covers the cyan/teal sector.
    return (hue >= 110) & (hue <= 150) & (saturation >= 64) & (value >= 32)


def make_fixture():
    rng = np.random.default_rng(SEED)
    rgb = np.zeros((128, 128, 3), dtype=np.uint8)
    rgb[:, :] = (180, 30, 30)  # non-teal background
    flat = rgb.reshape(-1, 3)
    chosen = np.sort(rng.choice(flat.shape[0], size=9000, replace=False))
    flat[chosen, 0] = rng.integers(0, 45, size=len(chosen), dtype=np.uint8)
    flat[chosen, 1] = rng.integers(110, 205, size=len(chosen), dtype=np.uint8)
    flat[chosen, 2] = rng.integers(120, 225, size=len(chosen), dtype=np.uint8)
    rgb = flat.reshape(128, 128, 3)

    mask = teal_mask(rgb)
    selected = np.flatnonzero(mask.ravel(order="C"))
    payload = normalize(PHRASE).encode("ascii") + b"\x00"
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8), bitorder="big")
    flat = rgb.reshape(-1, 3)
    flat[selected[:len(bits)], 1] = (flat[selected[:len(bits)], 1] & 0xFE) | bits
    return flat.reshape(128, 128, 3), mask


def unpack_phrase(bits):
    for offset in range(8):
        packed = np.packbits(bits[offset:], bitorder="big").tobytes()
        text = packed.decode("latin1", errors="ignore")
        if normalize(PHRASE) in text:
            return normalize(PHRASE)
    return None


def hmac_commitment(phrase):
    normalized = normalize(phrase)
    component = hmac.new(NONCE, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    return hashlib.sha256(component).hexdigest()


def main():
    rgb, mask = make_fixture()
    masked_bits = (rgb[:, :, 1][mask] & 1).astype(np.uint8)
    masked_phrase = unpack_phrase(masked_bits)

    full_bits = (rgb[:, :, 1] & 1).ravel(order="C").astype(np.uint8)
    full_image_phrase = unpack_phrase(full_bits)

    expected = hmac_commitment(PHRASE)
    assert masked_phrase == normalize(PHRASE)
    assert hmac_commitment(masked_phrase) == expected
    assert full_image_phrase is None

    print({
        "synthetic_only": True,
        "hsv_mask": "H=110..150, S>=64, V>=32",
        "teal_pixels": int(mask.sum()),
        "payload_bits": len(normalize(PHRASE).encode("ascii") + b"\x00") * 8,
        "masked_row_major_green_lsb": "PASS",
        "full_image_green_lsb_control": "MISS",
        "synthetic_hmac_roundtrip": "PASS",
        "synthetic_phrase_is_not_an_H17_candidate": True,
    })


if __name__ == "__main__":
    main()
