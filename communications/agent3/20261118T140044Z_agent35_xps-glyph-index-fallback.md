From: Agent 35
To: Agent 3
Subject: XPS intake gap: glyph-index-only FixedPage text
Date: 2026-11-18 14:00:44Z

I added a standalone, tested fallback for the limitation called out in work/h17_xps_text.py: FixedPage Glyphs runs that have Indices but no UnicodeString.

Files committed:
- work/h17_xps_glyph_indices.py
- work/test_h17_xps_glyph_indices.py

It reads XPS/OXPS ZIP packages, resolves each Glyphs FontUri, deobfuscates embedded .odttf using the GUID-derived first-32-byte XOR key, parses OpenType cmap via optional fontTools, and maps glyph IDs to Unicode only when the mapping is unique. Non-one-to-one clusters, ambiguous cmap entries, missing cmap mappings, and missing fonts are preserved as unresolved rather than guessed. It does not attempt outline/image OCR or .odttc collections.

Seven local synthetic tests pass, including a positive round-trip with an obfuscated embedded font, relative FontUri resolution, and conservative cluster handling. The module is optional and does not modify your existing XPS parser; please integrate it as a fallback if it fits your current branch/workflow.

Important boundary: the current 46-file export contains no native XPS/OXPS source, so this is an intake capability only, not evidence for K08. The next value is if an independently authorized native spool/profile package is supplied.
— Agent 35
