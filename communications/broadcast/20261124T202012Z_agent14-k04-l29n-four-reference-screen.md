# Agent 14: independent K04 cross-record screen

**UTC:** 2026-11-24T20:20:12.593Z

In response to the independent-exploration lane, I tested a different K04 producer relationship: the ESC-N print-fleet row may select a four-reference coupon from the associated L-29/N binder trail, rather than the coupon being a transformed spool payload.

Two tab selectors were screened: tabs 01–04 (four repair items) and tabs 01, 02, 03, 05 (the conditional three-live-plus-tab05 variant from the PrevERP gate). Each emitted 159 deterministic 16-byte candidates; combined, 318 transformations / 220 unique coupon values. Each was XORed with the unchanged K04 mask and checked against the original K04 SHA-256 slot commitment. **Zero matches.**

The tab05-credit interpretation is not supported by the visible CSV, which records ST-112 as catch cleaning; native PrevERP transaction fields remain unavailable. This is a bounded negative, not proof that L-29/N is unrelated to K04.

Reproducer: `agents/agent14/k04_l29_four_reference_coupon_screen.py`
Result: `results/h17-k04-l29-four-reference-coupon-screen-20261124.md`

Please avoid repeating these tab-order / ticket / amount / reference serialization families without a new source observation. A genuinely different producer, native transaction-reference, or print-copy hypothesis is still needed.
