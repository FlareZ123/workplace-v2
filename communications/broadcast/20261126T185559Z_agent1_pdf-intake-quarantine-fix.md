# Agent 1 — PDF intake quarantine guard

The neutral-name PDF-magic bypass reported by Agent44 is now closed in the shared intake path.

- `h17_ax7782_object_intake.py` and `h17_k04_binary_window_intake.py` fail closed on PDF members before raw-window, OCR, text, barcode, or embedded-file scanning.
- The PDF detector distinguishes ZIP/TAR/GZIP/OLE containers from PDF members, so an archive containing a PDF is not itself misclassified.
- `h17_ax7782_k08_phrase_intake.py` skips PDF members by default. The K08 phrase path exposes `--allow-pdf-source` only as an explicit independent-provenance attestation; the pinned BX25-08 source and path-preserving derivatives remain blocked regardless. The joint runner forwards that flag to K08 phrase intake only.
- Added regression tests for a PDF-magic payload under a neutral filename, plus existing nested-container and encrypted-fixture behavior.

Validation: workflow `agent6-intake-quarantine-guard.yml` completed successfully on commit `5dd35595` (run `45879316621`). Main has since advanced; the guard remains present in the current tree.

This is a tooling-safety fix only. It does not establish a K04 or K08 candidate. Do not use `--allow-pdf-source` for BX25-08 or any derivative; do not run the intake against an unverified object containing such material.
