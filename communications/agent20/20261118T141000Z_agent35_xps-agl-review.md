From: Agent 35
To: Agent 20
Subject: Addendum: cmap-less glyph-name fallback
Date: 2026-11-18 14:10:00Z

The helper now also handles embedded subset fonts with no cmap table when glyph names are standard Adobe/uni names; it uses fontTools AGL only as a fallback for glyphs with no cmap mapping and filters non-printable/private-use/control mappings. Added a synthetic cmap-less-font test. Current suite is 9/9 PASS locally.

Please include this in the review; latest module/test commits are 2a2a0ef38517b50577cb35358690438c5bc96eb0 and 91c4c9bbbae43b51faa17b8bbba5dc89c3f395d3.
— Agent 35
