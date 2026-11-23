import hashlib
import hmac
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from work.h17_profile_k08_phrase_scan import scan_inventory
from work.h17_ax7782_k08_phrase_intake import normalize, k08_component


NONCE = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
PHRASE = "the voices stayed around the table after the long watch"


def _commitment(value: str) -> bytes:
    return hashlib.sha256(k08_component(NONCE, normalize(value))).digest()


def _teal_png(path: Path, phrase: str, generic: bool = False) -> bytes:
    raw = phrase.encode("ascii")
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="big")
    pixels = np.empty((64, 64, 4), dtype=np.uint8)
    pixels[:, :, :] = (0, 180, 180, 255) if not generic else (128, 128, 128, 255)
    flat = pixels.reshape(-1, 4)
    for index, bit in enumerate(bits):
        if generic:
            flat[index, 1] = (int(flat[index, 1]) & 0xFE) | int(bit)
        else:
            channel = 1 if (index & 1) == 0 else 2
            bit_position = index & 1
            mask = 1 << bit_position
            flat[index, channel] = (
                (int(flat[index, channel]) & (0xFF ^ mask))
                | (int(bit) << bit_position)
            )
    Image.fromarray(pixels, mode="RGBA").save(path)
    return path.read_bytes()


def _inventory(root: Path, inventory_path: Path, paths: list[Path], wrong_hash: bool = False) -> None:
    records = []
    for path in paths:
        data = path.read_bytes()
        records.append({
            "path": path.relative_to(root).as_posix(),
            "size": len(data),
            "sha256": ("0" * 64) if wrong_hash else hashlib.sha256(data).hexdigest(),
            "categories": ["profile_metadata"],
        })
    inventory_path.write_text(json.dumps({
        "schema": "h17-profile-inventory/v1",
        "source_root": str(root),
        "files": records,
    }), encoding="utf-8")


class ProfileThumbcacheBridgeTests(unittest.TestCase):
    def test_exact_teal_phrase_is_recovered_from_cache_and_duplicate_is_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "profile"
            root.mkdir()
            image_path = base / "source.png"
            image_bytes = _teal_png(image_path, PHRASE)
            cache_a = root / "thumbcache_32.db"
            cache_b = root / "thumbcache_96.db"
            cache_a.write_bytes(b"H17-CACHE-A\\x00" + image_bytes + b"\\x00END-A")
            cache_b.write_bytes(b"H17-CACHE-B\\x00" + image_bytes + b"\\x00END-B")
            inventory_path = base / "inventory.json"
            _inventory(root, inventory_path, [cache_a, cache_b])

            before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (cache_a, cache_b)}
            result = scan_inventory(
                inventory_path,
                NONCE,
                _commitment(PHRASE),
                max_phrase_words=48,
                max_file_bytes=2 * 1024 * 1024,
                max_total_bytes=4 * 1024 * 1024,
            )
            after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (cache_a, cache_b)}

            self.assertEqual(before, after)
            self.assertEqual(result["thumbnail_cache"]["files_scanned"], 2)
            self.assertEqual(result["thumbnail_cache"]["images_found"], 2)
            self.assertEqual(result["thumbnail_cache"]["unique_images_scanned"], 1)
            self.assertEqual(result["thumbnail_cache"]["duplicate_images_reused"], 1)
            self.assertEqual(result["thumbnail_cache"]["image_hmac_hits"], 2)
            self.assertEqual(len(result["hits"]), 2)
            self.assertTrue(all(hit["phrase"] == PHRASE for hit in result["hits"]))
            self.assertTrue(all(hit["historical_authentication"] == "not established" for hit in result["hits"]))
            self.assertTrue(all("unresolved" in hit["source_link_status"] for hit in result["hits"]))

    def test_generic_non_teal_lsb_and_wrong_inventory_hash_are_not_admitted(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "profile"
            root.mkdir()
            image_path = base / "source.png"
            image_bytes = _teal_png(image_path, PHRASE, generic=True)
            cache = root / "thumbcache_32.db"
            cache.write_bytes(b"H17-CACHE\\x00" + image_bytes + b"\\x00END")
            inventory_path = base / "inventory.json"
            _inventory(root, inventory_path, [cache], wrong_hash=True)

            result = scan_inventory(
                inventory_path,
                NONCE,
                _commitment(PHRASE),
                max_file_bytes=2 * 1024 * 1024,
                max_total_bytes=4 * 1024 * 1024,
            )
            self.assertEqual(result["hits"], [])
            self.assertEqual(result["thumbnail_cache"]["files_scanned"], 0)
            self.assertTrue(any(item["reason"] == "sha256_changed_since_inventory" for item in result["skipped"]))


if __name__ == "__main__":
    unittest.main()
