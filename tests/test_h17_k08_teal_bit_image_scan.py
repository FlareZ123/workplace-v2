import hashlib
import hmac
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from work.h17_k08_teal_bit_image_scan import (
    SOURCE_LITERAL_LAYOUTS,
    _bit_variants,
    normalize_phrase,
    scan_authorized_n14_image,
    scan_image,
)


NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
PHRASE = "the sea leaves room at the table"


def _commitment(phrase: str, nonce: bytes = NONCE) -> str:
    normalized = normalize_phrase(phrase)
    component = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    return hashlib.sha256(component).hexdigest()


def _write_teal_image(path: Path, phrase: str, channel: str = "green") -> None:
    """Encode a test phrase only in the frozen teal-mask parity-selected bit plane."""
    raw = phrase.encode("ascii")
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="big")
    width = 64
    height = 64
    pixels = np.empty((height, width, 4), dtype=np.uint8)
    pixels[:, :, :] = (0, 180, 180, 255)
    flat = pixels.reshape(-1, 4)
    channel_index = 1 if channel == "green" else 2
    for index, bit in enumerate(bits):
        bit_position = index & 1
        mask = 1 << bit_position
        flat[index, channel_index] = (
            (int(flat[index, channel_index]) & (0xFF ^ mask))
            | (int(bit) << bit_position)
        )
    Image.fromarray(pixels, mode="RGBA").save(path)


def _write_non_teal_generic_green_lsb(path: Path, phrase: str) -> None:
    """Encode the same phrase in generic green LSB, but outside the teal mask."""
    raw = phrase.encode("ascii")
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="big")
    width = 64
    height = 64
    pixels = np.empty((height, width, 4), dtype=np.uint8)
    pixels[:, :, :] = (128, 128, 128, 255)
    flat = pixels.reshape(-1, 4)
    for index, bit in enumerate(bits):
        flat[index, 1] = (int(flat[index, 1]) & 0xFE) | int(bit)
    Image.fromarray(pixels, mode="RGBA").save(path)


def _write_manifest(image_path: Path, manifest_path: Path, **overrides) -> None:
    record = {
        "note_id": "N14",
        "image_path": image_path.name,
        "image_sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
        "photo_author": "Gabriel",
        "final_caption_author": "Emily",
        "link_type": "caption_sidecar",
        "evidence_ref": "synthetic-test/album-index/N14",
        "link_evidence": (
            "Synthetic positive-control record linking the N14 image to Emily's "
            "final envelope caption; this is test metadata, not historical evidence."
        ),
    }
    record.update(overrides)
    manifest_path.write_text(json.dumps(record), encoding="utf-8")


class TealBitImageScanTests(unittest.TestCase):
    def test_only_two_source_literal_layouts_are_exposed_to_recovery_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "teal.png"
            _write_teal_image(path, PHRASE)
            with Image.open(path) as image:
                names = [name for name, _ in _bit_variants(image, source_literal_only=True)]
            self.assertEqual(tuple(names), SOURCE_LITERAL_LAYOUTS)
            self.assertEqual(len(SOURCE_LITERAL_LAYOUTS) * 8 * 2 * 2, 64)

    def test_green_teal_low_if_even_roundtrip_emits_full_phrase(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "n14-green.png"
            _write_teal_image(path, PHRASE, "green")
            matches = scan_image(path, NONCE, _commitment(PHRASE))
            self.assertTrue(any(
                match["phrase"] == PHRASE
                and match["layout"] == "teal-mask-green-low-if-even"
                for match in matches
            ))

    def test_blue_teal_low_if_even_roundtrip_emits_full_phrase(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "n14-blue.png"
            _write_teal_image(path, PHRASE, "blue")
            matches = scan_image(path, NONCE, _commitment(PHRASE))
            self.assertTrue(any(
                match["phrase"] == PHRASE
                and match["layout"] == "teal-mask-blue-low-if-even"
                for match in matches
            ))

    def test_generic_green_lsb_outside_teal_mask_is_negative(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "non-teal.png"
            _write_non_teal_generic_green_lsb(path, PHRASE)
            self.assertEqual(scan_image(path, NONCE, _commitment(PHRASE)), [])

    def test_authorized_n14_manifest_binds_hash_and_emits_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "n14.png"
            manifest_path = root / "n14-source.json"
            _write_teal_image(image_path, PHRASE, "green")
            _write_manifest(image_path, manifest_path)
            result = scan_authorized_n14_image(
                image_path, manifest_path, NONCE, _commitment(PHRASE)
            )
            self.assertEqual(result["source_link_assertion"]["note_id"], "N14")
            self.assertEqual(result["layouts_tested"], list(SOURCE_LITERAL_LAYOUTS))
            self.assertEqual(result["candidate_streams_per_frame"], 64)
            self.assertTrue(any(m["phrase"] == PHRASE for m in result["matches"]))
            self.assertIn("human verification", result["source_link_assertion"]["status"])

    def test_wrong_note_id_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "n14.png"
            manifest_path = root / "source.json"
            _write_teal_image(image_path, PHRASE)
            _write_manifest(image_path, manifest_path, note_id="N08")
            with self.assertRaisesRegex(ValueError, "note_id must be N14"):
                scan_authorized_n14_image(
                    image_path, manifest_path, NONCE, _commitment(PHRASE)
                )

    def test_wrong_image_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "n14.png"
            manifest_path = root / "source.json"
            _write_teal_image(image_path, PHRASE)
            _write_manifest(image_path, manifest_path, image_sha256="0" * 64)
            with self.assertRaisesRegex(ValueError, "image_sha256"):
                scan_authorized_n14_image(
                    image_path, manifest_path, NONCE, _commitment(PHRASE)
                )

    def test_missing_caption_link_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "n14.png"
            manifest_path = root / "source.json"
            _write_teal_image(image_path, PHRASE)
            _write_manifest(image_path, manifest_path, link_evidence="")
            with self.assertRaisesRegex(ValueError, "missing required fields"):
                scan_authorized_n14_image(
                    image_path, manifest_path, NONCE, _commitment(PHRASE)
                )

    def test_wrong_commitment_is_negative(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "n14.png"
            _write_teal_image(path, PHRASE)
            self.assertEqual(scan_image(path, NONCE, "0" * 64), [])


if __name__ == "__main__":
    unittest.main()
