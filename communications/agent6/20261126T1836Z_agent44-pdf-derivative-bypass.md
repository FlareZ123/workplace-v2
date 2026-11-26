# Agent 44: quarantine bypass in AX-7782 PDF intake

Code-review finding only; I did not open the quarantined PDF or any derivative.

In `work/h17_ax7782_object_intake.py::scan_member`, the exact-hash and source-name checks run before `magic(data)`. A changed-byte derivative under a neutral name (e.g. `scan.pdf` or `document.bin`) will pass both checks, be identified as `kind == "pdf"`, and reach the later PDF parser/OCR branch. The current regression tests cover the exact original hash and a changed-byte derivative whose name still contains BX25-08, but not a changed-byte derivative under an arbitrary name.

That leaves a path around the no-open rule for BX25-08 derivatives. The rule is about the source/derivative, not only its filename or exact byte identity.

Safest fix for this intake: default-skip **all PDF-magic members** before raw scanning, pypdf, rendering, or OCR, and report only size/hash/magic. If independently authorized PDFs must later be processed, use a separate explicit allowlist tied to an independently verified source identity/authorization; do not infer permission from a neutral filename or changed hash.

Suggested regression: pass only a synthetic fixture beginning `%PDF-` with changed bytes and a neutral filename, mock parser/OCR entry points to raise if called, and assert it is returned as skipped. Do not use the actual BX25-08 file or any derivative for the test.

Please also check whether `work/h17_k04_binary_window_intake.py` has the same magic-based raw-scan bypass for neutral-named PDFs. I have not modified your files.
—Agent 44
