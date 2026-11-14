from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

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

    def test_rejects_non_sticky_notes_database_name(self) -> None:
        other = self.root / "History.sqlite"
        with sqlite3.connect(other) as connection:
            connection.execute("CREATE TABLE history (url TEXT)")
        with self.assertRaisesRegex(ValueError, "only an authorized file named plum.sqlite"):
            intake.extract_plum_database(other)


if __name__ == "__main__":
    unittest.main()
