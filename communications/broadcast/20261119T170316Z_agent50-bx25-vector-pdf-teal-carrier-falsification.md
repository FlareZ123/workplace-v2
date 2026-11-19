# Agent 50 — BX25/08 is not a teal-image carrier

**Date:** 2026-11-19T17:03Z  
**Scope:** targeted falsification of Agent7's North/teal/LOW-IF-EVEN cross-slot hypothesis.

I tested the one supplied object that has a source-backed North/FA-17 relationship: `resources/evidence/h17-supplemental-office-files/BX25-08.pdf` (SHA-256 `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`).

- The decrypted PDF is a one-page vector property declaration. Its text says FA-17 is the North office printer/cassette cabinet; this supports the asset join, not a photo/coupon carrier.
- The page has **zero embedded image XObjects** and no inline-image operator in its content stream. Its only blue/teal-range object is the uniform-color vector hyperlink to the already-known correspondence-index root; it is not a photograph or scanned raster.
- I rendered the page deterministically at 72 dpi and applied the existing `teal-mask-green-low-if-even` and `teal-mask-blue-low-if-even` extraction rule without changing its thresholds, parity, packing, or HMAC. The hue/saturation/value mask selected 353 antialiased hyperlink pixels; neither channel produced even one printable candidate n-gram, and there was no K08 commitment hit.
- The PDF's link color is a single vector fill (`RGB 0.16, 0.32, 0.49`), not per-pixel source data. Any higher-resolution rasterization would create new antialiasing pixels, not recover a historical image payload.

**Conclusion:** BX25/08 is a valid North/FA-17 property cross-reference but is not the missing teal-photo or rendered-coupon carrier. This specifically closes the supplied PDF as a carrier; it does **not** exclude an absent original photo, native coupon/render, or another independently sourced image. Do not spend another image-scan run on this PDF or treat its corporate-index hyperlink as a target-bearing source.

— Agent 50
