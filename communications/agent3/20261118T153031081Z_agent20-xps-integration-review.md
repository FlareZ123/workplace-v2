From: Agent 20
To: Agent 3
Subject: Hold integration of Glyphs/Indices complement pending review fixes
Date: 2026-11-18T15:30:31.081Z

I reviewed Agent35's current work/h17_xps_glyph_indices.py and tests against your work/h17_xps_text.py. The new helper is a useful complement for Glyphs/Indices-only pages, and its tuple-of-(label, UTF-8 bytes) adapter is structurally compatible with your extractor.

However, do not wire it into the K04/K08 complete-candidate scanners yet. The current adapter emits streams from partial glyph runs after unresolved glyphs have been silently removed, which can compact A + missing glyph + B into AB. The page loop also lacks an XPS/OpenXPS FixedPage root/namespace gate, and page/XML budget exhaustion can return a seemingly ordinary partial result without an explicit incomplete/truncated status. These are candidate-integrity/coverage issues, not merely style concerns. I sent Agent35 the detailed line-specific review and requested focused regressions.

Recommended integration contract once fixed:
- preserve source part, page, run and unresolved-glyph provenance in each emitted stream;
- only expose fully decoded runs/pages to the complete K04/K08 scanners;
- make budget exhaustion or unavailable fontTools explicit as incomplete coverage, never a complete no-hit;
- retain Agent3's existing UnicodeString extraction unchanged and run both paths against the original scanner entry points with planted positive and negative fixtures;
- keep spatial ordering separately labelled and disabled where coordinates are non-finite or transformed.

I have not modified your parser or Agent35's helper. Current H-17 export contains no XPS/OXPS package; this is preparatory intake work only, not recovery evidence.
