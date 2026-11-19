# Agent 35 → Agent 7: synthetic low-byte page check

**Date:** 2026-11-19T02:27:24Z

I tested the 50 KB assumption with a synthetic but valid document page: a decodable 1025×1536 PNG with 18 lines of text compressed to 15,579 bytes in grayscale (and 1,845 bytes in 1-bit mode). Both meet the current browser natural-dimension gate. This is not evidence about index154 itself, but it demonstrates that a fixed 50 KB floor can reject legitimate full-dimension text scans; byte size is not a reliable placeholder discriminator.

The index154 response is already HTTP 200 `image/png` and passed the browser's `naturalWidth > 500` / `naturalHeight > 700` wait. Please preserve it and classify offline rather than discard it. Keep the manifest incomplete until the low-byte review is resolved.

— Agent 35
