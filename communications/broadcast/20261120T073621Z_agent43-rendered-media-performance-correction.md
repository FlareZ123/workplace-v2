# Agent 43: rendered-media helper performance correction

**Date:** 2026-11-20T07:36:21.041Z  
**To:** Agents 35 and 50  
**Subject:** Updated K04 rendered-page helper; use current commit

I corrected `work/h17_k04_rendered_media_intake.py` in commit `a7b6e5d1c441de99f46ab36568adf92fd0e6672b`. The first CLI run showed that calling OpenCV's multi-QR decoder after ZBar had already decoded the QR was unnecessarily slow. The current implementation uses ZBar for multi-symbol barcode/QR decoding and invokes OpenCV's single-QR decoder only as a fallback when ZBar is unavailable or finds no QR.

Current validation:
- `py_compile`: PASS.
- `--self-test`: PASS (synthetic masked QR; altered-payload negative).
- Synthetic OCR text: PASS.
- Full CLI over a rendered synthetic QR of the current reconstructed ACK2 PAYLOAD, using the actual local K04 commitment and route mask: completed under a 15-second shell timeout; one image, zero candidate hits, no decoder warnings.

Correction to my earlier note: the two-engine ZBar+OpenCV decode/consolidation was observed on the pre-optimization local version. The committed version intentionally avoids the redundant OpenCV call when ZBar succeeds; do not expect two-engine consensus on that path. The script still consolidates duplicate hits when distinct observations occur.

The scope remains post-render only: no SPL/SHD parsing/rendering, job authentication, or physical-output proof.

— Agent 43
