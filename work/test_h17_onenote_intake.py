"""Tests for the optional read-only OneNote intake adapter."""
from __future__ import annotations

import hashlib
import sys
import tempfile
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_onenote_intake as intake


class FakeRichText:
    def __init__(self, text: str):
        self.Text = text


class FakeImage:
    def __init__(self, title: str, description: str):
        self.AlternativeTextTitle = title
        self.AlternativeTextDescription = description
        self.FileName = "shift-photo.jpg"
        self.HyperlinkUrl = ""
        self.Tags = []


class FakeAttachedFile:
    def __init__(self, filename: str):
        self.FileName = filename
        self.Tags = []


class FakeTitleText:
    def __init__(self, text: str):
        self.Text = text


class FakeTitle:
    def __init__(self, text: str):
        self.TitleText = FakeTitleText(text)


class FakePage:
    def __init__(self, title: str, body: str, author: str, modified: datetime):
        self.Title = FakeTitle(title)
        self.Author = author
        self.CreationTime = datetime(2026, 10, 1, tzinfo=timezone.utc)
        self.LastModifiedTime = modified
        self.nodes = {
            FakeRichText: [FakeRichText(body)],
            FakeImage: [FakeImage("sea after watch", "voices at the table")],
            FakeAttachedFile: [FakeAttachedFile("caption-revision.txt")],
        }

    def GetChildNodes(self, node_type):
        return self.nodes.get(node_type, [])


class FakeHistory:
    def __init__(self, historical, current):
        self._historical = historical
        self.Current = current

    def __iter__(self):
        return iter(self._historical)


class FakeDocument:
    current = None
    historical = None

    def __init__(self, source, load_options):
        self.source = source
        self.load_options = load_options

    def GetChildNodes(self, node_type):
        return [self.current]

    def GetPageHistory(self, page):
        return FakeHistory(self.historical, self.current)


class FakeLoadOptions:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class OneNoteIntakeTests(unittest.TestCase):
    def _fake_module(self):
        historical = FakePage(
            "Desk caption draft",
            "older wording before the final shift",
            "Emily",
            datetime(2026, 10, 2, tzinfo=timezone.utc),
        )
        current = FakePage(
            "Desk caption final",
            "the final wording after the night watch",
            "Emily",
            datetime(2026, 10, 3, tzinfo=timezone.utc),
        )
        FakeDocument.current = current
        FakeDocument.historical = [historical]

        note = types.ModuleType("aspose.note")
        note.Document = FakeDocument
        note.LoadOptions = FakeLoadOptions
        note.Page = FakePage
        note.RichText = FakeRichText
        note.Image = FakeImage
        note.AttachedFile = FakeAttachedFile
        parent = types.ModuleType("aspose")
        parent.note = note
        return {"aspose": parent, "aspose.note": note}

    def test_extracts_history_current_text_and_caption_metadata_read_only(self):
        raw = b"synthetic-one-note-fixture"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "desk-notes.one"
            path.write_bytes(raw)
            with patch.dict(sys.modules, self._fake_module()):
                result = intake.extract_onenote_document(path, "OneNote/desk-notes.one")

        self.assertEqual(result["pages"], 1)
        self.assertEqual(result["historical_revisions"], 1)
        self.assertEqual(result["source_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(path.read_bytes(), raw)
        sources = [stream["source"] for stream in result["streams"]]
        texts = [stream["text"] for stream in result["streams"]]
        self.assertTrue(any("revision=0:historical" in source for source in sources))
        self.assertTrue(any("revision=1:current" in source for source in sources))
        self.assertTrue(any("author=Emily" in source for source in sources))
        self.assertIn("older wording before the final shift", texts)
        self.assertIn("the final wording after the night watch", texts)
        self.assertIn("sea after watch | voices at the table | shift-photo.jpg", texts)
        self.assertIn("caption-revision.txt", texts)

    def test_reports_missing_optional_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "desk-notes.one"
            path.write_bytes(b"synthetic-one-note-fixture")
            with patch.dict(sys.modules, {"aspose.note": None}):
                with self.assertRaises(intake.OneNoteDependencyUnavailable):
                    intake.extract_onenote_document(path)


if __name__ == "__main__":
    unittest.main()
