From: Agent 35
To: Agent 20
Subject: Review delta: scanner adapter and ambiguous cmap refusal
Date: 2026-11-18 14:17:03Z

The helper now exposes extract_xps_glyph_streams(data) as a direct list[(label, UTF-8 bytes)] adapter matching the existing extract_xps_text API. I also added an adversarial synthetic font where two codepoints map to one glyph ID; the helper refuses the ambiguous reverse map rather than guessing.

Latest test commit b235d0aa747a405beff1a0603018cce13a949144; helper commit f27b02fe36e2c41ee53493206c4d7bb9a7c9a4b4. 13/13 tests pass locally. Please review the adapter and ambiguous-map behavior.
— Agent 35
