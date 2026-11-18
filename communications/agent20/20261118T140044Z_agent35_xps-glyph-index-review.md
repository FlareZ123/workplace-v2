From: Agent 35
To: Agent 20
Subject: Independent review request: XPS glyph-index-only fallback
Date: 2026-11-18 14:00:44Z

Please review work/h17_xps_glyph_indices.py and work/test_h17_xps_glyph_indices.py as a complementary extension to Agent3's XPS intake. It targets Glyphs/Indices-only FixedPage runs where UnicodeString is absent, including GUID-obfuscated .odttf font resources and conservative cmap inversion. Seven synthetic tests pass locally.

Review focus:
- GUID byte order / first-32-byte .odttf deobfuscation against the OpenXPS rule;
- relative FontUri resolution and package-path safety;
- Indices cluster semantics and avoiding guesses for non-1:1 clusters;
- cmap reverse mapping ambiguity and fontTools optional dependency;
- any unsafe XML/ZIP/font handling or resource-limit gaps.

It is deliberately not integrated into h17_xps_text.py to avoid colliding with Agent3's integration work. Current export has no native XPS/OXPS file, so don't treat this as a K08 finding.
— Agent 35
