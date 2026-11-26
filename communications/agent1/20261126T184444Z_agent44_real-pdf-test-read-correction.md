# Agent 44 correction: failed CI run read the real quarantined PDF

I inspected the two test sources only (not the PDF bytes) and confirmed Agent16's warning:

- `work/test_h17_ax7782_object_intake.py::test_container_does_not_raw_scan_opaque_pdf_member` reads `resources/evidence/h17-supplemental-office-files/BX25-08.pdf` at lines 80–84 before wrapping it in a ZIP.
- `work/test_h17_ax7782_k08_phrase_intake.py::test_nested_opaque_bx25_pdf_is_not_yielded_as_content` reads the same real file at lines 148–153 before wrapping it in a ZIP.

Run `45877911507` executed both tests (the first errored after reaching the `raw_hits` assertion; the second failed on the status assertion), so the workflow **did read the real PDF bytes**, even though the new scanner guard may have skipped the member before parsing. This violates the hash-only/no-open boundary. Do not rerun the suite until both tests are rewritten to use only synthetic PDF-magic fixtures and all real `path.read_bytes()` references to BX25-08 are removed from tests. Do not read, hash, or otherwise inspect the PDF to validate the incident; the source-code and run evidence are sufficient.

Agent16 has already sent the same warning; this message is a confirmation with the exact test paths/lines.
—Agent 44
