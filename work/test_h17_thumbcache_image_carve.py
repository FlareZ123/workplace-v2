import hashlib
import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

import h17_thumbcache_image_carve as carve


def make_image(fmt: str, color=(23, 111, 147)) -> bytes:
    stream = BytesIO()
    Image.new("RGB", (13, 9), color).save(stream, format=fmt)
    return stream.getvalue()


class ThumbcacheCarveTests(unittest.TestCase):
    def test_carves_all_supported_formats_byte_exact(self):
        payloads = {
            "jpeg": make_image("JPEG"),
            "png": make_image("PNG"),
            "gif": make_image("GIF"),
            "bmp": make_image("BMP"),
            "webp": make_image("WEBP"),
        }
        for kind, blob in payloads.items():
            with self.subTest(kind=kind):
                found = carve.carve_bytes(b"header\x00" * 3 + blob + b"\x00trailer", "synthetic")
                self.assertEqual(len(found), 1)
                self.assertEqual(found[0].format, kind)
                self.assertEqual(found[0].length, len(blob))
                self.assertEqual(found[0].sha256, hashlib.sha256(blob).hexdigest())

    def test_extracts_from_cache_directory_and_deduplicates(self):
        image = make_image("PNG")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "profile"
            out = Path(temp) / "out"
            (root / "AppData" / "Local").mkdir(parents=True)
            a = root / "AppData" / "Local" / "thumbcache_32.db"
            b = root / "AppData" / "Local" / "Thumbs.db"
            a.write_bytes(b"cache-A" + image + b"tail-A")
            b.write_bytes(b"cache-B" + image + b"tail-B")
            before = {p: p.read_bytes() for p in (a, b)}
            result = carve.extract([root], out)
            self.assertEqual(result["source_files_scanned"], 2)
            self.assertEqual(result["image_occurrences"], 2)
            self.assertEqual(result["unique_images_extracted"], 1)
            self.assertTrue((out / "images" / (hashlib.sha256(image).hexdigest() + ".png")).exists())
            self.assertEqual({p: p.read_bytes() for p in (a, b)}, before)
            manifest = json.loads((out / "carve_manifest.json").read_text())
            self.assertEqual(manifest["schema"], "h17-thumbcache-image-carve/v1")

    def test_ignores_truncated_and_false_signatures(self):
        blob = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64 + b"BMnot-a-bitmap"
        self.assertEqual(carve.carve_bytes(blob, "bad-cache"), [])

    def test_output_must_be_outside_source_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "profile"
            root.mkdir()
            (root / "thumbcache_32.db").write_bytes(b"not-an-image")
            with self.assertRaises(ValueError):
                carve.extract([root], root / "extracted")

    def test_explicit_file_source_is_supported(self):
        image = make_image("JPEG")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "profile"
            root.mkdir()
            cache = root / "thumbcache_96.db"
            cache.write_bytes(b"prefix" + image)
            found = carve.carve_file(cache, carve.DEFAULT_MAX_IMAGE_BYTES, carve.DEFAULT_MAX_PIXELS)
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].format, "jpeg")


if __name__ == "__main__":
    unittest.main()
