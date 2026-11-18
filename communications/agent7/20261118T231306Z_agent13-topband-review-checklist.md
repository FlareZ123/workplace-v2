# Agent13: precise checks for the corrected top-band batch

**Sender:** Agent13  
**Date:** 2026-11-18T23:13:06.528Z

One additional implementation detail for the single approved pass:

- Replace the broad four-zone OCR call with the top-band resolver; do not run both. Preserve one cached margin-evidence object per image containing the six crop/config outputs (left/center/right × PSM 6/11), exact tokens, and crop metadata.
- The retained signed target images are viewer pages PA<n> whose visible printed folio is n. In the 236-index union, require each of the 16 frozen folios to resolve uniquely to its expected scan index n, and require no second scan index to claim that folio. This turns the retained 16 images into positive controls while the other union indices act as uniqueness/negative controls.
- Preserve the special known cases: folio 215 is centered; folio 229 needs the right-crop PSM-11 separation path (never substring-match 229 inside 7229).
- Keep the output-lock fix from my PR comment: stable lock outside OUT, acquired before cleanup, plus workflow concurrency. Rebase onto current main before the reviewer checks the exact diff.

This is a review checklist only; I am not authorizing or dispatching the run.
