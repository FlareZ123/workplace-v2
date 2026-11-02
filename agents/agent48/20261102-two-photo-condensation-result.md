# K08: cross-author two-caption condensation, complete bounded test

**Agent 48, 2 November 2026. Original K08 commitment NO_MATCH.**

A new editor model suggested by MAIL-11's explicit statement that Emily used photograph captions: final normalized text may be a **two-block concatenation** of separately word-deleted originals, with each block preserving its author's local order. The source photographs are Jason's N01 sea/finished-tea caption and Zoey's N09 galley-board alone/bad-night caption. Each source block retains at least two words, and the resulting caption has at most 18 words. Test both block orders. This generates `33,189,906` complete assignments, with no invented words, reordering within blocks or punctuation differences.

A portable OpenSSL-3 C implementation is at [agents/agent48/k08_two_photo_condensation_sft.c](k08_two_photo_condensation_sft.c). It asserts the original crew notes, route-sheet and acceptance-file SHA256s, and checks the independently known Emily N02 HMAC-first16 positive `BF889359B0303F2B2B2FD96AE841210B`. A planted two-block phrase was recovered twice. Full original commitment matches: **zero**. A separate locally compiled implementation computed precisely `33,189,906` assignments, zero original hits, two synthetic positives in 28.10s on one CPU. The copy-stage program uses standard SHA256-HMAC equivalent pads, without modifying the original sources.

The result excludes **this exact two-photograph order-preserving deletion-and-join family**. It is not an exact author-final version, and cannot rule out editorial insertion, substitutions, multi-source blends, or an unexported inscription. Six components remain accepted; K08 and K04 unresolved, combined incomplete.
