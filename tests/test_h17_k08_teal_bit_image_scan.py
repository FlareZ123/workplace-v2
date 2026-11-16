from pathlib import Path
import hashlib
import hmac

import numpy as np
from PIL import Image

from work.h17_k08_teal_bit_image_scan import scan_image


def _commitment(phrase: str, nonce: bytes) -> str:
    normalized = " ".join(phrase.lower().split())
    component = hmac.new(nonce, normalized.encode(), hashlib.sha256).digest()[:16]
    return hashlib.sha256(component).hexdigest()


def test_green_lsb_phrase_roundtrip(tmp_path: Path):
    phrase = "the sea leaves room at the table"
    nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
    raw = phrase.encode("ascii")
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="big")
    width = 32
    height = (len(bits) + width - 1) // width
    pixels = np.full((height, width, 4), 128, dtype=np.uint8)
    flat = pixels[:, :, 1].reshape(-1)
    flat[: len(bits)] = (flat[: len(bits)] & 0xFE) | bits
    path = tmp_path / "teal-test.png"
    Image.fromarray(pixels, mode="RGBA").save(path)
    matches = scan_image(path, nonce, _commitment(phrase, nonce))
    assert any(m["phrase"] == phrase for m in matches)
