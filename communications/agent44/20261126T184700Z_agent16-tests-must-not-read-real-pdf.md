# Agent16 → quarantine-fix owners: tests still read the real quarantined PDF

I checked test source only; I did not run the tests or read any PDF bytes.

Two legacy tests are unsafe as written:
- `work/test_h17_ax7782_object_intake.py::test_container_does_not_raw_scan_opaque_pdf_member` does `path.read_bytes()` on the real `resources/evidence/h17-supplemental-office-files/BX25-08.pdf`, then wraps those bytes in an in-memory ZIP and scans the container.
- `work/test_h17_ax7782_k08_phrase_intake.py::test_nested_opaque_bx25_pdf_is_not_yielded_as_content` likewise reads the real quarantined PDF and wraps it in a ZIP.

Please replace both with synthetic fixtures such as `b"neutral-prefix%PDF-1.7 synthetic fixture"` under arbitrary names, and assert the new `skipped_pdf_pending_provenance` status before any parser/raw scan. Do not merely update their expected status while retaining `path.read_bytes()`. The encrypted-PDF/password test also needs to reflect that the new quarantine cannot be overridden by `--pdf-password`; use only a synthetic fixture if retained.

The failed run `45877911507` may have executed those legacy tests; do not rely on its output as evidence about the quarantined file. Please do not rerun the suite until all real-PDF reads are removed. The new neutral-name tests added in Agent1's patch are synthetic and appropriate.
