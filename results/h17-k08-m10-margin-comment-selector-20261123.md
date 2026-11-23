# K08 M10 margin/comment selector (2026-11-23)

## Question

Could N23's reference to wording in a margin correspond to an Excel cell note/comment attached to the separately identified M10 workbook candidate, rather than the eight selected cell values alone?

## Result

**A narrowly bounded M10 comment path is now integrated into the mug-stock workbook selector. No real phrase was recovered.**

The existing `work/h17_xls_lo_fallback.py` already emits legacy XLS cell comments as text streams. It now also preserves the comment author from the converted cell object. `work/h17_k08_mug_stock_cell_selector.py` adds `evaluate_m10_comments`, which checks only:
- the exact `M10<comment>` source stream;
- on the explicitly selected worksheet, or the sole worksheet when the workbook has one;
- under the unchanged K08 normalization, nonce/HMAC and SHA-256 commitment.

It does not search other cells' comments, infer a worksheet order, or scan arbitrary workbook text. A comment-author field is retained as a clue, not identity authentication. The existing eight-cell PS-0323 selector is unchanged.

## Validation

- `tests/test_h17_k08_m10_comment_selector.py` checks exact M10 selection, author retention, rejection of M9/other-sheet comments, rejection of ordinary cell text, and fail-closed behavior when no sheet mapping exists.
- `work/test_h17_k08_mug_stock_cell_selector.py` now includes a synthetic end-to-end M10 comment match alongside the existing eight-cell HMAC control. Its optional real legacy-XLS round-trip also plants an Emily-attributed M10 comment and checks that the fallback preserves it.
- The targeted K08 workflow now runs both the `tests/` suite and the workbook-selector test script; the real LibreOffice integration remains conditional on LibreOffice availability.

## Source limits

The supplied archive contains no `mug-stock.xls`. No M10 comment, author, phrase, or K08 match was observed in a real workbook. The "margin" interpretation is a source-motivated hypothesis, not an established fact. If an already-authorized original workbook becomes available, the M10 comment result should be evaluated separately from the eight-cell selector and any native OfficeArt/BLIP hits; none should be promoted without the original workbook hash and independent source linkage.

## Confidence

- **High:** the M10-only selection and HMAC path are covered by synthetic tests.
- **Medium:** the LibreOffice-converted legacy-XLS comment-author path is covered only if the optional real-XLS integration runs in an environment with LibreOffice.
- **None:** no real workbook or K08 phrase recovered.
