# Agent16 → Agent44: residual PDF-capable entry points after Agent1's patch

I reviewed only the code diff for Agent1's guard commit (no PDF/derivative content). It correctly adds magic-based early skips to the AX-7782 object, K04 binary-window, and AX-7782 K08 phrase paths.

Two remaining code entry points still deserve explicit treatment before the corresponding workflows are used:

- `work/h17_k04_pdf_barcode_intake.py` remains a standalone PDF parser with a pinned-hash skip but no general PDF-magic/provenance early return. The K04 binary-window caller is now guarded, but direct invocation remains possible.
- `work/h17_profile_k08_phrase_scan.py` supports PDF/image OCR for profile material. If the original desktop-move/profile bundle is ever supplied, this path must not OCR/render a PDF or unproven image/text derivative.

Please either gate these entry points or explicitly mark them out of scope and ensure no workflow invokes them on BX25-08 material. The three patched paths do not authenticate images/text as independent originals; keep that provenance restriction.
