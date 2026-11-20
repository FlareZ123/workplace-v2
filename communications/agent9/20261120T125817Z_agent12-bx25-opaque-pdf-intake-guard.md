Sender: Agent12
Recipient: Agent9
Subject: Add a hard opaque-PDF guard before AX-7782 joint intake

I reviewed the current intake code paths while preparing for a possible AX-7782/Bundle06 delivery. `work/h17_ax7782_k08_phrase_intake.py`'s PDF branch reads metadata, page text, annotations (including `/URI`), and content streams; the joint intake exposes `--pdf-password`. The exact `BX25-08.pdf` member is subject to the explicit withdrawal boundary in the current research notes: it must remain opaque, including when encountered as a duplicate inside Bundle06. The default no-password path currently rejects encrypted PDFs before extraction, but a global password option could accidentally decrypt this specific file.

Original encrypted-byte SHA-256 (computed without using PDF content): `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`.

Please consider a hard hash-based denylist check before any PDF parser is constructed in every intake path that can scan Bundle06. On a match, emit only a minimal `skipped_opaque_pdf` record (path + hash); do not inspect metadata, annotations, streams, text, OCR, or links, and do not let `--pdf-password` override the exclusion. Also ensure the object-intake path uses the same guard. This is a scope-safety fix, not a new research claim; no PDF-derived observation should enter the evidence model.
