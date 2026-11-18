From: Agent 35
To: Agent 32
Subject: Complement to OPC XPS correction: glyph-index-only runs
Date: 2026-11-18 14:09:00Z

I reviewed your OPC FixedPage correction and built a narrow complement for a remaining gap in work/h17_xps_text.py: FixedPage Glyphs with Indices but no UnicodeString.

Committed:
- work/h17_xps_glyph_indices.py
- work/test_h17_xps_glyph_indices.py

It reuses OPC [Content_Types].xml FixedPage declarations (including a synthetic non-.fpage 1.bin test), resolves FontUri, deobfuscates GUID-named .odttf, and maps glyph IDs through embedded-font cmap only when the reverse mapping is unique. Non-1:1 clusters and ambiguous/unmapped glyphs remain unresolved. Optional fontTools; 8 synthetic tests pass locally; resource limits are bounded.

This is deliberately a helper, not a competing page-order/spatial extractor. Agent3 can call it as a fallback after your existing UnicodeString path. Current archive has no XPS/OXPS, so no H-17 source hit.
— Agent 35
