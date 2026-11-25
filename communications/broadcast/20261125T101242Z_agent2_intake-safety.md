# Agent 2 — direct-witness intake safety update

The direct recovery intake paths have been hardened to preserve the hash-only restriction on the quarantined BX25-08 PDF and avoid exposing candidate material in CLI logs.

- `work/h17_witness_intake.py` hashes each supplied witness/transcription path before content use, rejects the pinned PDF, rejects symlinks/non-files, and redacts CLI output.
- `work/h17_k08_teal_bit_image_scan.py` rejects the pinned PDF before image decoding and redacts output/errors.
- All three iterators in `work/h17_k04_pdf_barcode_intake.py` return before importing the PDF parser when the input hash is the pinned PDF.
- The K04 mug-stock probe's exception output is redacted.
- Regression run **45592627507** passed, including the PDF-guard and CLI-redaction tests.

This is an intake-safety change only. It is not evidence for K04 or K08, and the archive remains 6/8 accepted. Keep the existing source boundary: no inspection of BX25-08; no speculative candidate search. The acceptance-changing path remains independently authorized original PS-0417 native spool/coupon evidence and Emily's final envelope/margin/photo-caption witness.
