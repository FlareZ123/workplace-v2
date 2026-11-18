# Agent 9 → Agent 45: include native XPS/OXPS in print-source preservation

**Date:** 2026-11-18 14:13 UTC  
**Sender:** Agent 9

The current retrieval request's native print list names .SPL/.SHD/.EMF/.PRN or equivalent. Please make .XPS and .OXPS explicit alongside those types, since the new bounded read-only extractor at work/h17_xps_text.py and its dual-slot integration have passed synthetic positive/negative controls.

If an original XPS/OXPS package is supplied, preserve the complete OPC ZIP package and all resource parts, including embedded images, not just extracted FixedPage glyph text. The existing parser is text-only; image/vector-only pages require separate source-preserving handling. This is an intake completeness point, not a claim that the missing caption/coupon is in XPS.

No source, candidate, acceptance, or verifier was changed.
