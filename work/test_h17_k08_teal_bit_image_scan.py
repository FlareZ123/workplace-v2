#!/usr/bin/env python3
"""Synthetic positive control for the bounded teal-mask / LOW IF EVEN image rule."""
import hashlib
import hmac
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_k08_teal_bit_image_scan as scanner


PHRASE = "the lamp stays on until the sea turns quiet"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")


def make_fixture():
    rng = np.random.default_rng(20261119)
    rgb = np.zeros((128, 128, 3), dtype=np.uint8)
    rgb[:, :] = (180, 30, 30)  # non-teal background
    flat = rgb.reshape(-1, 3)
    chosen = np.sort(rng.choice(flat.shape[0], size=9000, replace=False))
    flat[chosen, 0] = rng.integers(5, 30, size=len(chosen), dtype=np.uint8)
    flat[chosen, 1] = rng.integers(140, 180, size=len(chosen), dtype=np.uint8)
    flat[chosen, 2] = rng.integers(150, 190, size=len(chosen), dtype=np.uint8)
    rgb = flat.reshape(128, 128, 3)

    hsv = np.asarray(Image.fromarray(rgb, "RGB").convert("HSV"), dtype=np.uint8)
    teal = ((hsv[:, :, 0] >= 110) & (hsv[:, :, 0] <= 150)
            & (hsv[:, :, 1] >= 64) & (hsv[:, :, 2] >= 32))
    indices = np.flatnonzero(teal.ravel(order="C"))
    payload = scanner.normalize_phrase(PHRASE).encode("ascii") + b"\x00"
    payload_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8), bitorder="big")
    flat = rgb.reshape(-1, 3)
    for bit_index, bit in enumerate(payload_bits):
        pixel_index = int(indices[bit_index])
        bit_plane = pixel_index & 1  # even -> bit 0; odd -> bit 1
        old = int(flat[pixel_index, 1])
        flat[pixel_index, 1] = (old & ~(1 << bit_plane)) | (int(bit) << bit_plane)
    rgb = flat.reshape(128, 128, 3)

    # Ensure embedding did not move pixels out of the fixed teal mask.
    hsv_after = np.asarray(Image.fromarray(rgb, "RGB").convert("HSV"), dtype=np.uint8)
    teal_after = ((hsv_after[:, :, 0] >= 110) & (hsv_after[:, :, 0] <= 150)
                  & (hsv_after[:, :, 1] >= 64) & (hsv_after[:, :, 2] >= 32))
    assert np.array_equal(teal, teal_after)
    return Image.fromarray(rgb, "RGB")


class TealMaskLowIfEvenTests(unittest.TestCase):
    def test_conditional_teal_bit_recovers_planted_phrase(self):
        normalized = scanner.normalize_phrase(PHRASE)
        component = hmac.new(NONCE, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
        commitment = hashlib.sha256(component).hexdigest()

        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "synthetic-teal.png"
            make_fixture().save(image_path)
            matches = scanner.scan_image(image_path, NONCE, commitment)

        self.assertTrue(any(
            match["phrase"] == normalized
            and match["layout"] == "teal-mask-green-low-if-even"
            for match in matches
        ))
        self.assertFalse(any(
            match["phrase"] == normalized and match["layout"] == "green-bit0"
            for match in matches
        ))


if __name__ == "__main__":
    unittest.main()
