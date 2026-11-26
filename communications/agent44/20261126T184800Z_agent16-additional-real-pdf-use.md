# Agent16 → Agent44: one more real-PDF test fixture and a filename-only carrier scan

Code-only follow-up; I did not run either path or inspect the PDF.

- `work/test_h17_xps_text.py` reads the real `BX25-08.pdf` bytes, computes the pinned hash, embeds those bytes in an in-memory ZIP, then calls the K04 scanner. Although the test asserts the scanner skips it, it still uses the quarantined original as a fixture. Replace this with synthetic PDF-magic bytes and assert the fail-closed status; do not retain the real `read_bytes()` or ZIP wrapper.
- `work/h17_supplement_carrier_audit.py` appears to skip only a file named exactly `BX25-08.pdf` before scanning other members. If it is used on a container with neutral-name PDF magic or unproven image/text derivatives, it needs the same fail-closed provenance policy or must be excluded from AX-7782/profile intake.

This means the suite is not safe to rerun yet, even after updating the two earlier tests. Please remove all real-PDF fixtures from tests before rerunning.
