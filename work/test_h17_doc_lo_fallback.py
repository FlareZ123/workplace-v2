"""Synthetic test that legacy .doc conversion preserves Word margin comments."""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

try:
    from docx import Document
    from lxml import etree
except ImportError:  # pragma: no cover - environment-dependent
    Document = None

from h17_doc_lo_fallback import convert_doc_bytes  # noqa: E402
try:
    from h17_ax7782_k08_phrase_intake import iter_text_streams  # noqa: E402
except ImportError:  # standalone helper test outside the repository
    iter_text_streams = None


class LegacyDocFallbackTests(unittest.TestCase):
    @unittest.skipUnless(
        (shutil.which("libreoffice") or shutil.which("soffice")) and Document,
        "LibreOffice, python-docx and lxml are required",
    )
    def test_legacy_doc_conversion_preserves_margin_comment(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h17-doc-test-") as tmp_name:
            root = Path(tmp_name)
            docx_path = root / "note.docx"
            doc_dir = root / "doc"
            doc_dir.mkdir()
            profile = root / "lo-create-profile"
            profile.mkdir()

            document = Document()
            paragraph = document.add_paragraph()
            paragraph.add_run("Anchor text for the margin comment.")
            document.save(docx_path)
            unpacked = root / "unpacked"
            unpacked.mkdir()
            with zipfile.ZipFile(docx_path) as archive:
                archive.extractall(unpacked)

            ns = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
                "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
            }
            document_xml = unpacked / "word/document.xml"
            tree = etree.parse(str(document_xml))
            run = tree.getroot().find(".//w:r", ns)
            parent = run.getparent()
            index = parent.index(run)
            start = etree.Element("{%s}commentRangeStart" % ns["w"])
            start.set("{%s}id" % ns["w"], "0")
            end = etree.Element("{%s}commentRangeEnd" % ns["w"])
            end.set("{%s}id" % ns["w"], "0")
            reference = etree.Element("{%s}r" % ns["w"])
            ref = etree.SubElement(reference, "{%s}commentReference" % ns["w"])
            ref.set("{%s}id" % ns["w"], "0")
            parent.insert(index, start)
            parent.insert(index + 2, end)
            parent.insert(index + 3, reference)
            tree.write(str(document_xml), xml_declaration=True, encoding="UTF-8", standalone="yes")

            comments = etree.Element("{%s}comments" % ns["w"], nsmap={"w": ns["w"]})
            comment = etree.SubElement(comments, "{%s}comment" % ns["w"])
            comment.set("{%s}id" % ns["w"], "0")
            comment.set("{%s}author" % ns["w"], "Emily")
            comment.set("{%s}date" % ns["w"], "2026-10-03T12:00:00Z")
            para = etree.SubElement(comment, "{%s}p" % ns["w"])
            comment_run = etree.SubElement(para, "{%s}r" % ns["w"])
            text = etree.SubElement(comment_run, "{%s}t" % ns["w"])
            text.text = "the final envelope caption"
            (unpacked / "word/comments.xml").write_bytes(
                etree.tostring(comments, xml_declaration=True, encoding="UTF-8", standalone="yes")
            )

            rels_path = unpacked / "word/_rels/document.xml.rels"
            rels = etree.parse(str(rels_path))
            relationship = etree.SubElement(
                rels.getroot(),
                "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship",
            )
            relationship.set("Id", "rId999")
            relationship.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments")
            relationship.set("Target", "comments.xml")
            rels.write(str(rels_path), xml_declaration=True, encoding="UTF-8", standalone="yes")

            types_path = unpacked / "[Content_Types].xml"
            types = etree.parse(str(types_path))
            override = etree.SubElement(
                types.getroot(),
                "{http://schemas.openxmlformats.org/package/2006/content-types}Override",
            )
            override.set("PartName", "/word/comments.xml")
            override.set("ContentType", "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml")
            types.write(str(types_path), xml_declaration=True, encoding="UTF-8", standalone="yes")

            commented_docx = root / "commented.docx"
            with zipfile.ZipFile(commented_docx, "w", zipfile.ZIP_DEFLATED) as archive:
                for item in unpacked.rglob("*"):
                    if item.is_file():
                        archive.write(item, item.relative_to(unpacked).as_posix())

            converter = shutil.which("libreoffice") or shutil.which("soffice")
            proc = subprocess.run(
                [
                    converter, "--headless", "--nologo", "--nodefault", "--nolockcheck",
                    "--norestore", "--nofirststartwizard",
                    f"-env:UserInstallation={profile.as_uri()}",
                    "--convert-to", "doc:MS Word 97", "--outdir", str(doc_dir),
                    str(commented_docx),
                ],
                capture_output=True, text=True, timeout=60, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            source_doc = doc_dir / "commented.doc"
            self.assertTrue(source_doc.is_file(), proc.stderr or proc.stdout)
            original = source_doc.read_bytes()
            original_hash = hashlib.sha256(original).hexdigest()

            converted = convert_doc_bytes(original, "WN-14.doc")
            self.assertEqual(hashlib.sha256(source_doc.read_bytes()).hexdigest(), original_hash)
            with zipfile.ZipFile(__import__("io").BytesIO(converted)) as archive:
                self.assertIn("word/comments.xml", archive.namelist())
                comments_xml = archive.read("word/comments.xml").decode("utf-8", "replace")
                self.assertIn("the final envelope caption", comments_xml)
                self.assertIn("Emily", comments_xml)

            # Exercise the repository dispatcher when its sibling modules
            # are available; standalone helper tests may run outside the repo.
            if iter_text_streams is not None:
                budget = [0]
                errors = []
                streams = list(iter_text_streams(
                    "AX-7782!/WN-14.doc", original, 0, budget, errors
                ))
                extracted = [payload.decode("utf-8", "replace") for _, payload in streams]
                self.assertTrue(any("the final envelope caption" in text for text in extracted))
                self.assertFalse(any("Word conversion failed" in e.get("error", "") for e in errors))


if __name__ == "__main__":
    unittest.main()
