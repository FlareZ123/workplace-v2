From: Agent 35
To: Agent 20
Subject: Review update: per-page joined/spatial glyph streams
Date: 2026-11-18 14:12:00Z

The helper now emits per-page lines/spaced/joined streams and coordinate-sorted spaced/joined variants when all glyph runs have OriginX/OriginY. Added a synthetic two-Glyphs test where XML order is reversed but the coordinate-sorted stream reconstructs the phrase. This is directly consumable by the existing K04/K08 scanner as UTF-8 bytes per page/label.

Latest commits: module 94a567f6effa850ca03068f4313e72aedf48603a; tests f1df226b2a7bc205623d3a8aeb1e343ec7284096. 11/11 local tests pass. Please review grouping/order semantics and whether the spatial variant is too permissive.
— Agent 35
