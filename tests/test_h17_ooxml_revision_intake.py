import hashlib
import io
import unittest
import zipfile

from work.h17_ax7782_k08_phrase_intake import iter_text_streams, k08_component, normalize
from work.h17_ooxml_text_intake import (
    iter_ooxml_revision_units,
    iter_ooxml_text_units,
)


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
FINAL_PHRASE = "The last watch leaves room for every voice."
ORIGINAL_PHRASE = "The last watch keeps the room empty for every voice."
NONCE = bytes.fromhex("00112233445566778899AABBCCDDEEFF")


def _docx_bytes() -> bytes:
    document = f"""<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p>
      <w:r><w:t xml:space="preserve">The last watch </w:t></w:r>
      <w:del w:id="1" w:author="Emily" w:date="2026-10-02T17:00:00Z">
        <w:r><w:delText xml:space="preserve">keeps the room empty</w:delText></w:r>
      </w:del>
      <w:ins w:id="2" w:author="Emily" w:date="2026-10-02T17:30:00Z">
        <w:r><w:t xml:space="preserve">leaves room </w:t></w:r>
      </w:ins>
      <w:r><w:t>for every voice.</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t xml:space="preserve">the next </w:t></w:r>
      <w:moveFrom w:id="3" w:author="Emily" w:date="2026-10-02T17:40:00Z">
        <w:r><w:delText>watch</w:delText></w:r>
      </w:moveFrom>
      <w:moveTo w:id="4" w:author="Emily" w:date="2026-10-02T17:41:00Z">
        <w:r><w:t>pair of hands</w:t></w:r>
      </w:moveTo>
      <w:r><w:tab/><w:t>is ready.</w:t></w:r>
    </w:p>
  </w:body>
</w:document>""".encode("utf-8")
    comments = f"""<?xml version="1.0" encoding="UTF-8"?>
<w:comments xmlns:w="{W_NS}">
  <w:comment w:id="7" w:author="Emily" w:date="2026-10-02T17:45:00Z">
    <w:p><w:r><w:t>Keep the sea outside and the voices together.</w:t></w:r></w:p>
  </w:comment>
</w:comments>""".encode("utf-8")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", "<Types/>")
        package.writestr("word/document.xml", document)
        package.writestr("word/comments.xml", comments)
    return buffer.getvalue()


class OoxmlRevisionIntakeTests(unittest.TestCase):
    def test_final_and_original_views_are_reconstructed_separately(self):
        data = _docx_bytes()
        final_units = dict(
            (label, payload.decode("utf-8"))
            for label, payload in iter_ooxml_text_units(data)
        )
        revision_units = dict(
            (label, payload.decode("utf-8"))
            for label, payload in iter_ooxml_revision_units(data)
        )

        final = next(text for label, text in final_units.items()
                     if label == "word/document.xml#authored-unit-0")
        original = revision_units["word/document.xml#original-unit-0"]
        self.assertEqual(final, FINAL_PHRASE)
        self.assertEqual(original, ORIGINAL_PHRASE)
        self.assertNotEqual(final, original)

        inserted = [
            (label, text) for label, text in revision_units.items()
            if "#revision-ins-" in label
        ]
        deleted = [
            (label, text) for label, text in revision_units.items()
            if "#revision-del-" in label
        ]
        self.assertTrue(any(text == "leaves room " and "author-Emily" in label
                            for label, text in inserted))
        self.assertTrue(any(text == "keeps the room empty" and "author-Emily" in label
                            for label, text in deleted))
        self.assertTrue(any("#revision-moveTo-" in label and text == "pair of hands"
                            for label, text in revision_units.items()))
        self.assertTrue(any("#revision-moveFrom-" in label and text == "watch"
                            for label, text in revision_units.items()))

    def test_final_phrase_commitment_matches_only_the_final_revision_view(self):
        data = _docx_bytes()
        final_text = next(
            payload.decode("utf-8")
            for label, payload in iter_ooxml_text_units(data)
            if label == "word/document.xml#authored-unit-0"
        )
        revision_units = list(iter_ooxml_revision_units(data))
        original_text = next(
            payload.decode("utf-8")
            for label, payload in revision_units
            if label == "word/document.xml#original-unit-0"
        )
        commitment = hashlib.sha256(
            k08_component(NONCE, normalize(FINAL_PHRASE))
        ).hexdigest()
        self.assertEqual(final_text, FINAL_PHRASE)
        self.assertEqual(
            hashlib.sha256(k08_component(NONCE, normalize(final_text))).hexdigest(),
            commitment,
        )
        self.assertNotEqual(
            hashlib.sha256(k08_component(NONCE, normalize(original_text))).hexdigest(),
            commitment,
        )

    def test_k08_intake_emits_revision_and_comment_attribution_labels(self):
        data = _docx_bytes()
        streams = list(iter_text_streams(
            "caption-history.docx", data, 0, [0], [], None, None, []
        ))
        labels = [label for label, _ in streams]
        self.assertTrue(any("revision-ins-id-2-author-Emily" in label for label in labels))
        self.assertTrue(any("revision-del-id-1-author-Emily" in label for label in labels))
        self.assertTrue(any("revision-moveTo-id-4-author-Emily" in label for label in labels))
        self.assertTrue(any("comment-id-7-author-Emily" in label for label in labels))


if __name__ == "__main__":
    unittest.main()
