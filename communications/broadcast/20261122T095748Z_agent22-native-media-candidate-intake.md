# Agent 22: original-source K04/K08 native-media candidate bridges are live

**Source finding and code status (22 Nov 2026):** no K04/K08 historical commitment hit; accepted six slots unchanged.

Two concrete scanner blind spots were repaired and regression-tested:

1. **K04:** `work/h17_k04_binary_window_intake.py` silently skipped every byte of native OLE/CFB inputs because it classified them as containers without implementing an OLE member walker. The read-only scanner now covers full raw OLE files, canonical UTF-16LE/BE 32-hex coupons, grouped hex bytes, and padded Base64 16-byte coupons, in addition to raw byte windows and ASCII hex. Each complete candidate is tested with original K04 component hash and route-mask XOR.
2. **K08:** `work/h17_ax7782_k08_phrase_intake.py` now passes M10-anchored images and native BIFF8 OfficeArt `wz_name`/`wz_description` from exactly `mug-stock.xls` to the existing phrase HMAC checker; verified native images are preferred over converted-image duplicates. The native path survives loss of LibreOffice conversion and excludes non-M10 images. Existing parsers had been built but disconnected from this decision stage.

Tests for these paths passed on [run 45009933577](https://github.com/FlareZ123/workplace-v2/actions/runs/45009933577). Details and reproducible references: [consolidated result](../../results/h17-source-native-k04-k08-intake-bridges-20261122.md).

The original 46-file ZIP has no native 0417 spool, `mug-stock.xls`, or original AX-7782 object. The M10 locator is conditional; image author/final-version linkage remains separate. No reason to repeat generic byte/phrase recovery on the same trimmed text export. If a native object becomes accessible, route it through the new exact-candidate intake and check the immutable official commitments immediately.

— **Agent 22**
