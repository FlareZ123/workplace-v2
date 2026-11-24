# K04: bounded L-29/N four-reference coupon screen

**Agent 14 | 24 November 2026 | Exploratory cross-record test; no commitment hit.**

## Hypothesis

The ESC-N printer row may be a selector for a four-reference escrow coupon derived from the associated L-29/N binder trail, rather than the coupon being a direct or transformed copy of the selected spool payload. This challenges the assumption that the spool PAYLOAD field is the only possible source of the coupon.

The retained print-fleet register binds PS-261003-0417 to ESC-N, L-29/N, account FA-17, and folio H17-POL-17/A3. The binder index gives five tabs in order:

| Tab | Ticket | Return description |
|---|---|---|
| 01 | ST-094 | lid plate, return |
| 02 | ST-081 | edge guide, exchange |
| 03 | ST-106 | separator, refit |
| 04 | ST-099 | hinge, retain |
| 05 | ST-112 | catch, clean |

The visible CSV has R3 POSTED rows for all five tickets under FA-17 / H17-POL-17/A3. It records tab 05 as catch cleaning, not as a credit. Two four-tab selectors were therefore tested without asserting that either is authoritative:

1. Tabs 01–04: the four repair-item interpretation.
2. Tabs 01, 02, 03 and 05: the conditional three-live-parts-plus-tab-05 interpretation raised in the separate PrevERP transaction-status source gate. Its hypothesized credit role for tab 05 is not supported by the visible CSV and remains conditional.

## Candidate construction and test

The read-only reproducer is [k04_l29_four_reference_coupon_screen.py](../agents/agent14/k04_l29_four_reference_coupon_screen.py). It asserts the route row, binder tab order, and selected CSV rows before constructing candidates.

For each four-tab selector, it generated **159 deterministic 16-byte coupon transformations** (156 unique byte strings), including:

- tab-ordered ticket/amount tuples with independent 16-bit endianness;
- 32-bit ticket-number and amount arrays, ASCII ticket forms, and float32 amount arrays;
- per-row CRC32 values and per-ticket 32-bit fingerprints;
- 128-bit digests of four-tab and five-tab reference lists and selected rows;
- four 32-bit fingerprints and joined 128-bit digests of the four non-job route fields (ESC-N, L-29/N, FA-17, H17-POL-17/A3).

Across both selectors this is **318 transformations and 220 unique coupon values**. For each coupon C, the test formed the K04 component C XOR M, using the unchanged masked_component M, and compared SHA256(C XOR M) with the original K04 slot commitment. No candidate bytes are printed or persisted.

**Result: 0 of 318 commitment matches.**

## Interpretation

This is a bounded negative for the tested L-29/N ticket/reference serializations, not a proof that the binder records are unrelated to K04. The route-to-binder association is present in the retained records; neither four-tab selection has a source-authored byte-serialization rule. The conditional tab-05 credit interpretation additionally requires the missing native PrevERP transaction record. A different coupon producer, source object, or native print/copy stage remains possible.

The original spool, route, acceptance commitments, and verifier were not changed. The canonical six accepted components remain unchanged; K04 and K08 remain missing, and REC8/1 remains incomplete. Do not broaden this into arbitrary ticket permutations or generic hash/encoding sweeps without a new source observation.
