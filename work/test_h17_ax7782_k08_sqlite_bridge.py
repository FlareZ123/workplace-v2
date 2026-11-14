from __future__ import annotations

import gzip
import hashlib
import io
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_ax7782_k08_sqlite_bridge as bridge
import h17_ax7782_k08_phrase_intake as phrase_intake


class SQLiteBridgeTests(unittest.TestCase):
    def _nested_zip_with_database(self, root: Path, include_wal: bool = True,
                                  database_name: str = "plum.sqlite") -> tuple[bytes, str]:
        database = root / "plum.sqlite"
        connection = sqlite3.connect(database)
        if include_wal:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA wal_autocheckpoint=0")
        connection.execute("CREATE TABLE Note (Id TEXT PRIMARY KEY, Text TEXT)")
        phrase = "the keeper leaves the lamp for the next watch"
        connection.execute("INSERT INTO Note VALUES (?, ?)", ("n1", phrase))
        connection.commit()
        if include_wal:
            connection.execute("DELETE FROM Note WHERE Id='n1'")
            connection.commit()
        wal_path = Path(str(database) + "-wal")
        shm_path = Path(str(database) + "-shm")
        if not include_wal:
            connection.close()
        db_bytes = database.read_bytes()
        wal_bytes = wal_path.read_bytes() if include_wal and wal_path.exists() else b""
        shm_bytes = shm_path.read_bytes() if include_wal and shm_path.exists() else b""

        inner = io.BytesIO()
        with zipfile.ZipFile(inner, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr(f"profile/{database_name}", db_bytes)
            if include_wal:
                archive.writestr("profile/plum.sqlite-wal", wal_bytes)
                archive.writestr("profile/plum.sqlite-shm", shm_bytes)
        outer = io.BytesIO()
        with zipfile.ZipFile(outer, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("snapshot/profile.zip", inner.getvalue())
        connection.close()
        return outer.getvalue(), phrase

    def test_nested_zip_deleted_note_in_wal_is_recovered(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_bytes, phrase = self._nested_zip_with_database(root, include_wal=True)
            before = hashlib.sha256(archive_bytes).hexdigest()
            nonce = bytes(range(16))
            component = phrase_intake.k08_component(nonce, phrase)
            target = hashlib.sha256(component).digest()

            result = bridge.scan_sqlite_members(archive_bytes, "AX-7782.zip", nonce, target, 16)

            self.assertEqual(result["plum_databases_found"], 1)
            self.assertTrue(result["databases"][0]["wal_present"])
            self.assertEqual(result["databases"][0]["logical_row_count"], 0)
            self.assertTrue(result["databases"][0]["snapshot_source_unchanged"])
            wal_hits = [hit for hit in result["original_k08_commitment_hits"]
                        if hit["normalized_phrase"] == phrase]
            self.assertTrue(wal_hits)
            self.assertTrue(any("plum.sqlite-wal" in hit["source"] and
                                hit.get("char_start") == 3 and
                                isinstance(hit.get("byte_offset"), int)
                                for hit in wal_hits))
            self.assertEqual(hashlib.sha256(archive_bytes).hexdigest(), before)

    def test_logical_sticky_note_row_is_scanned_without_wal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_bytes, phrase = self._nested_zip_with_database(root, include_wal=False)
            nonce = bytes(range(16))
            target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()

            result = bridge.scan_sqlite_members(archive_bytes, "AX-7782.zip", nonce, target, 16)

            self.assertEqual(result["plum_databases_found"], 1)
            self.assertFalse(result["databases"][0]["wal_present"])
            self.assertGreater(result["databases"][0]["logical_row_count"], 0)
            self.assertTrue(any(hit["normalized_phrase"] == phrase
                                for hit in result["original_k08_commitment_hits"]))

    def test_gzipped_database_and_sidecars_keep_their_logical_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            nested, phrase = self._nested_zip_with_database(root, include_wal=True)
            with zipfile.ZipFile(io.BytesIO(nested)) as outer:
                inner_bytes = outer.read("snapshot/profile.zip")
            with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
                db = inner.read("profile/plum.sqlite")
                wal = inner.read("profile/plum.sqlite-wal")
                shm = inner.read("profile/plum.sqlite-shm")
            compressed = io.BytesIO()
            with zipfile.ZipFile(compressed, "w", compression=zipfile.ZIP_STORED) as archive:
                archive.writestr("profile/plum.sqlite.gz", gzip.compress(db))
                archive.writestr("profile/plum.sqlite-wal.gz", gzip.compress(wal))
                archive.writestr("profile/plum.sqlite-shm.gz", gzip.compress(shm))
            nonce = bytes(range(16))
            target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()

            result = bridge.scan_sqlite_members(compressed.getvalue(), "AX-7782.zip", nonce, target, 16)

            self.assertEqual(result["plum_databases_found"], 1)
            self.assertTrue(result["databases"][0]["wal_present"])
            self.assertTrue(any(hit["normalized_phrase"] == phrase
                                for hit in result["original_k08_commitment_hits"]))

    def test_object_wrapper_merges_base_scanner_and_sqlite_hits_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_bytes, phrase = self._nested_zip_with_database(root, include_wal=False)
            object_path = root / "AX-7782.zip"
            object_path.write_bytes(archive_bytes)
            before = hashlib.sha256(object_path.read_bytes()).hexdigest()
            nonce = bytes(range(16))
            target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()
            base = {
                "object": {"sha256": before},
                "K08_search": {
                    "original_commitment_hits": [],
                    "normalized_contiguous_spans_tested": 7,
                    "text_streams_scanned": 2,
                },
            }
            with patch.object(bridge.phrase_intake, "inspect_object", return_value=base), \
                 patch.object(bridge.phrase_intake, "load_k08_rules", return_value=(nonce, target)):
                result = bridge.inspect_object(object_path, root, max_phrase_words=16)
            self.assertTrue(result["sqlite_intake"]["source_object_unchanged"])
            self.assertEqual(result["sqlite_intake"]["source_object_sha256"], before)
            self.assertGreater(result["K08_search"]["normalized_contiguous_spans_tested"], 7)
            self.assertEqual(result["K08_search"]["text_streams_scanned"], 2)
            self.assertGreater(result["K08_search"]["sqlite_text_inputs_scanned"], 0)
            self.assertTrue(any(hit["normalized_phrase"] == phrase
                                for hit in result["K08_search"]["original_commitment_hits"]))
            self.assertEqual(hashlib.sha256(object_path.read_bytes()).hexdigest(), before)

    def test_unrelated_sqlite_filename_is_not_opened(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_bytes, phrase = self._nested_zip_with_database(
                root, include_wal=False, database_name="History.sqlite"
            )
            nonce = bytes(range(16))
            target = hashlib.sha256(phrase_intake.k08_component(nonce, phrase)).digest()
            result = bridge.scan_sqlite_members(archive_bytes, "AX-7782.zip", nonce, target, 16)
            self.assertEqual(result["plum_databases_found"], 0)
            self.assertEqual(result["original_k08_commitment_hits"], [])

    def test_non_sqlite_plum_file_is_reported_not_opened(self):
        inner = io.BytesIO()
        with zipfile.ZipFile(inner, "w") as archive:
            archive.writestr("profile/plum.sqlite", b"not a database")
        nonce = bytes(range(16))
        target = bytes(32)
        result = bridge.scan_sqlite_members(inner.getvalue(), "AX-7782.zip", nonce, target, 16)
        self.assertEqual(result["plum_databases_found"], 0)
        self.assertTrue(any("lacks SQLite format 3 header" in item["error"]
                            for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
