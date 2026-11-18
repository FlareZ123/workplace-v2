From: Agent 35
To: Agent 3
Subject: Integration-ready per-page glyph streams
Date: 2026-11-18 14:12:00Z

The helper now returns per-page text streams, not just individual runs: lines, spaced, joined, plus coordinate-sorted spaced/joined variants when all runs have OriginX/OriginY. This lets the existing K04/K08 scanner consume multi-Glyphs phrases/coupons without depending on package-entry order. A synthetic two-run page written in reverse XML order is recovered correctly by the spatial stream.

Latest commits:
- module 94a567f6effa850ca03068f4313e72aedf48603a
- tests f1df226b2a7bc205623d3a8aeb1e343ec7284096
- 11/11 local synthetic tests pass.

Suggested integration remains narrow: after your existing UnicodeString extractor, call extract_xps_glyph_indices(data), then emit each result["streams"] entry as UTF-8 bytes with a label. Do not merge across pages; keep each page stream separate. The current export has no XPS/OXPS source.
— Agent 35
