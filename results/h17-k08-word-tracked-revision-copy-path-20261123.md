# K08 Word tracked-revision and copy-path intake (2026-11-23)

## Question

Can retained WordprocessingML revision records reconstruct the editor's final visible wording separately from prior/deleted text, while preserving which author/date/id contributed each change?

## Result

**A revision-aware Word text path is now integrated into the K08 intake. Synthetic version/copy controls pass. No real H-17 phrase was recovered.**

The previous OOXML intake extracted paragraph text from `w:t` nodes but did not expose the original revision view or attribute individual insert/delete/move events. The new companion reader in `work/h17_ooxml_text_intake.py` reconstructs:
- **Final view:** ordinary text plus `w:ins` and `w:moveTo`; excludes `w:del` and `w:moveFrom`.
- **Original view:** ordinary text plus deleted/moved-from text; excludes inserted/moved-to text.
- **Revision events:** each insert, delete, move-from and move-to as a separate source stream labelled with Word's retained revision id, author and date.
- **Comment streams:** comment text with comment id, author and date.

The final paragraph reader also preserves tab and line-break separators. `work/h17_ax7782_k08_phrase_intake.py` now emits the revision and comment streams alongside the existing final-view OOXML text. This is a version/copy reconstruction path, not a new phrase dictionary.

## Why the distinction matters

A phrase found in a deleted revision or original-view paragraph is not automatically the wording finally placed on the envelope. The source label now distinguishes those cases. An exact HMAC match in the final view is stronger candidate evidence than a match confined to a deleted revision, but neither alone proves the document was the source of the envelope caption. The author/date/id fields preserve the evidence needed to evaluate that link.

## Validation

`tests/test_h17_ooxml_revision_intake.py` builds a synthetic DOCX with:
- a final sentence assembled across normal text and an inserted run;
- a deleted prior wording;
- a move-from / move-to edit;
- an Emily-attributed comment with date metadata.

The test verifies that the final view reconstructs the exact normalized phrase, the original view remains distinct, revision events retain author/date/id labels, and the final phrase's synthetic K08 commitment matches the final view rather than the original view.

The full targeted K08 suite, including the thumbnail-cache bridge and profile-scanner self-test, passed on [GitHub Actions run 45093401174](https://github.com/FlareZ123/workplace-v2/actions/runs/45093401174).

## Application and limits

The supplied `h17-archive-dump.zip` contains no DOCX/Word document. This mechanism therefore does not recover K08 from the current export. It is relevant only if an already-authorized profile-refresh source contains an original Word package with retained revisions/comments.

The parser does not claim that a Word file existed, that a particular revision was copied to the envelope, or that a Word author named Emily is the envelope author. A source-authenticated link to the envelope/caption is still required. Do not promote a hit from an original/deleted stream as final wording.

## Confidence

- **High:** final/original Word views and attributed revision-event streams are reconstructed as specified by the synthetic tests.
- **High:** the targeted K08 regression suite and profile scanner self-test passed.
- **None:** no real K08 component or historical Word source was recovered in this run.
