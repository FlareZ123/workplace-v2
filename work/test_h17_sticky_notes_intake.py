from __future__ import annotations

import hashlib
import os
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import h17_sticky_notes_intake as intake


class StickyNotesIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="h17-plum-test-")
        self.root = Path(self.temp.name)
        self.database = self.root / "plum.sqlite"

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _hash(path: Path) -> tuple[int, int, str]:
        info = path.stat()
        return info.st_size, info.st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_reads_uncheckpointed_wal_and_preserves_source_bytes(self) -> None:
        connection = sqlite3.connect(self.database)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE Note (Id TEXT PRIMARY KEY, Text TEXT, ModifiedAt TEXT)")
        connection.execute(
            "INSERT INTO Note VALUES (?, ?, ?)",
            ("note-1", "A place at the table after the long watch", "2026-10-04T05:30:00Z"),
        )
        connection.commit()
        wal = Path(str(self.database) + "-wal")
        shm = Path(str(self.database) + "-shm")
        self.assertTrue(wal.exists())
        self.assertTrue(shm.exists())
        source_before = {path: self._hash(path) for path in (self.database, wal, shm)}

        result = intake.extract_plum_database(self.database)

        self.assertTrue(result["source_unchanged"])
        self.assertTrue(result["summary"]["wal_present"])
        self.assertTrue(result["summary"]["shm_present"])
        note_text = result["tables"][0]["rows"][0]["values"]["Text"]
        self.assertEqual(note_text, "A place at the table after the long watch")
        self.assertEqual(source_before, {path: self._hash(path) for path in (self.database, wal, shm)})
        connection.close()

    def test_raw_carving_finds_deleted_note_text_in_wal(self) -> None:
        connection = sqlite3.connect(self.database)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA wal_autocheckpoint=0")
        connection.execute("CREATE TABLE Note (Id TEXT PRIMARY KEY, Text TEXT)")
        connection.execute("INSERT INTO Note VALUES (?, ?)", ("n1", "The sea is quiet beyond the last watch"))
        connection.commit()
        connection.execute("DELETE FROM Note WHERE Id='n1'")
        connection.commit()
        wal = Path(str(self.database) + "-wal")
        self.assertTrue(wal.exists())

        result = intake.extract_plum_database(self.database)

        logical_rows = [row for table in result["tables"] for row in table["rows"]]
        self.assertEqual(logical_rows, [])
        carved_text = [span["text"] for item in result["raw_text_carving"] for span in item["spans"]]
        self.assertTrue(any("The sea is quiet beyond the last watch" in text for text in carved_text))
        self.assertTrue(result["source_unchanged"])
        connection.close()

    def test_reads_plain_database_without_sidecars(self) -> None:
        with sqlite3.connect(self.database) as connection:
            connection.execute("CREATE TABLE Note (Text TEXT)")
            connection.execute("INSERT INTO Note VALUES (?)", ("The light is on for the next watch",))
        result = intake.extract_plum_database(self.database)
        self.assertTrue(result["source_unchanged"])
        self.assertFalse(result["summary"]["wal_present"])
        self.assertEqual(result["tables"][0]["rows"][0]["values"]["Text"], "The light is on for the next watch")

    def test_without_rowid_table_is_supported(self) -> None:
        with sqlite3.connect(self.database) as connection:
            connection.execute("CREATE TABLE Note (Id TEXT PRIMARY KEY, Text TEXT) WITHOUT ROWID")
            connection.execute("INSERT INTO Note VALUES (?, ?)", ("n1", "No rowid table"))
        result = intake.extract_plum_database(self.database)
        row = result["tables"][0]["rows"][0]
        self.assertIsNone(row["rowid"])
        self.assertEqual(row["values"]["Text"], "No rowid table")

    def test_rejects_mixed_snapshot_if_source_changes_during_copy(self) -> None:
        with sqlite3.connect(self.database) as connection:
            connection.execute("CREATE TABLE Note (Text TEXT)")
            connection.execute("INSERT INTO Note VALUES (?)", ("stable source",))
        original_bytes = self.database.read_bytes()
        original_stat = self.database.stat()
        real_copyfile = shutil.copyfile

        def racing_copyfile(source: str | os.PathLike[str], destination: str | os.PathLike[str]):
            source_path = Path(source)
            source_path.write_bytes(original_bytes + b"transient-change")
            try:
                return real_copyfile(source_path, destination)
            finally:
                source_path.write_bytes(original_bytes)
                os.utime(
                    source_path,
                    ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns),
                )

        with patch.object(intake.shutil, "copyfile", side_effect=racing_copyfile):
            with self.assertRaisesRegex(RuntimeError, "snapshot copy mismatch"):
                intake.extract_plum_database(self.database)

        self.assertEqual(self.database.read_bytes(), original_bytes)
        self.assertEqual(self._hash(self.database)[2], hashlib.sha256(original_bytes).hexdigest())

    def test_snapshot_copies_rollback_journal_sidecar(self) -> None:
        self.database.write_bytes(b"database evidence")
        journal = Path(str(self.database) + "-journal")
        journal.write_bytes(b"rollback journal final keeper wording")
        expected_root = {}
        for suffix in ("", "-wal", "-shm", "-journal"):
            path = self.database if not suffix else Path(str(self.database) + suffix)
            expected_root[str(path)] = self._hash(path) if path.exists() else None

        snapshot_dir = self.root / "snapshot"
        snapshot_dir.mkdir()
        result = intake._copy_snapshot(self.database, snapshot_dir, expected_root)
        journal_record = next(item for item in result["files"] if item["path"] == str(journal))
        self.assertTrue(journal_record["present"])
        self.assertEqual(journal_record["sha256"], journal_record["copied_sha256"])
        self.assertEqual((snapshot_dir / "plum.sqlite-journal").read_bytes(), journal.read_bytes())

    def test_raw_carving_survives_unreadable_database_and_journal(self) -> None:
        self.database.write_bytes(b"not a valid sqlite database")
        journal = Path(str(self.database) + "-journal")
        journal.write_bytes(b"the keeper leaves the lamp for the next watch")
        result = intake.extract_plum_database(self.database)

        self.assertIsNotNone(result["sqlite_error"])
        self.assertTrue(result["source_unchanged"])
        self.assertTrue(result["summary"]["journal_present"])
        carved = [
            span["text"]
            for item in result["raw_text_carving"]
            for span in item["spans"]
        ]
        self.assertTrue(any("the keeper leaves the lamp for the next watch" in text for text in carved))

    def test_rejects_non_sticky_notes_database_name(self) -> None:
        other = self.root / "History.sqlite"
        with sqlite3.connect(other) as connection:
            connection.execute("CREATE TABLE history (url TEXT)")
        with self.assertRaisesRegex(ValueError, "only an authorized file named plum.sqlite"):
            intake.extract_plum_database(other)


if __name__ == "__main__":
    unittest.main()
