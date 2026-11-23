# H-17 K08: OneNote page-history intake

**Status:** source-retrieval capability added; no K08 component recovered.

## Why this path exists

The K08 source trail identifies Emily's desk notes and photograph captions as inputs to the final envelope wording (MAIL-11 and MAIL-20). The profile inventory already classifies OneNote section files (.one) as note material, but the profile phrase scanner previously relied on generic OLE/raw-text extraction for those files. That does not preserve OneNote's structured page and revision boundaries.

A native OneNote section can retain page history. The upstream [Aspose.Note FOSS for Python](https://github.com/aspose-note-foss/Aspose.Note-FOSS-for-Python) project exposes LoadOptions(LoadHistory=True) and Document.GetPageHistory(page); its [history test](https://github.com/aspose-note-foss/Aspose.Note-FOSS-for-Python/blob/main/tests/test_aspose_note_history.py) exercises a SimpleHistory.one fixture and distinguishes historical revisions from the current page.

## Implementation

- [work/h17_onenote_intake.py](../work/h17_onenote_intake.py) is a read-only adapter for individual .one section files.
- [work/h17_profile_k08_phrase_scan.py](../work/h17_profile_k08_phrase_scan.py) invokes it for inventoried .one files when the optional parser is installed. If unavailable or parsing fails, the scanner records the decoder issue and retains its generic fallback.
- The adapter emits historical page revisions and the current page separately. It extracts page title, rich text, author/time metadata, image alternative-text fields, and attachment names.
- The source file is SHA-256 hashed before and after extraction; a change raises an error.
- It deliberately does **not** choose the latest revision as the final wording. Version selection still requires source-authored evidence tying a revision to Emily's final envelope text.
- .onepkg/CAB package extraction is not implemented here; this adapter accepts individual .one section files only.

Optional dependency: install work/requirements-h17-onenote.txt (aspose-note==26.3.2). The upstream GitHub repository contains an MIT LICENSE, while the current PyPI metadata reports a custom LicenseRef-Aspose-Split identifier; the requirements file flags this discrepancy for review before production use. See the [PyPI package metadata](https://pypi.org/project/aspose-note/).

## Validation and limits

- python -m unittest work/test_h17_onenote_intake.py: **2 tests passed** in the local run.
- These adapter tests use a mocked Aspose API. They verify historical/current separation, metadata and caption extraction, missing-dependency handling, and source-hash preservation.
- The upstream parser's own history test provides a real .one fixture/API check, but the H-17 adapter has not yet been run against an actual H-17 profile file.
- The supplied H-17 ZIP contains no OneNote section file. This is therefore a prepared intake path, not evidence that the missing K08 wording is present in OneNote.

## Next use

If an authorized retired-profile copy is supplied, inventory it read-only and run the K08 profile scanner with the optional dependency installed. Preserve all page revisions and current-page metadata; compare extracted text against the K08 acceptance commitment, then resolve authorship and final-version selection from the native record. Do not promote a phrase merely because it appears in the newest page revision.
