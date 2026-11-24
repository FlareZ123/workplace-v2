# K04: bounded L-29/N four-reference coupon screen

**Agent 14 | 24 November 2026 | Exploratory cross-record test; no commitment hit.**

## Hypothesis

The ESC-N printer row may be a selector for a four-reference escrow coupon associated with the L-29 supplier records, rather than the coupon being a direct or transformed copy of the selected spool payload.

The retained print-fleet register binds PS-261003-0417 to ESC-N, L-29/N, account FA-17, and folio H17-POL-17/A3. The North binder index gives five tabs in order:

| Tab | Ticket | Return description |
|---|---|---|
| 01 | ST-094 | lid plate, return |
| 02 | ST-081 | edge guide, exchange |
| 03 | ST-106 | separator, refit |
| 04 | ST-099 | hinge, retain |
| 05 | ST-112 | catch, clean |

The visible supplier CSV contains three positive-value North postings (ST-094, ST-081, ST-106), zero-value North rows ST-099/R3 and ST-112/R3, a separate ST-099/R2 VOID prior-card row, and an L-29/S row ST-151/R3 POSTED labelled "guide shim credit". ST-121/R2 VOID is separately labelled "supplier adjustment"; ST-121/R3 POSTED is a separator replacement.

The original PrevERP posted-items and reversal records are absent, so no supplied source authenticates which rows constitute the three live parts, credit, prior card, and supplier adjustment. In particular, the print-fleet register's PS-0417 → L-29/N association does not itself establish a ticket-level foreign key or a North-to-South coupon join. Three four-reference selectors were screened as bounded hypotheses, not asserted as facts:

1. Tabs 01–04: four North repair-item rows.
2. Tabs 01, 02, 03 and 05: the earlier conditional three-plus-tab05 interpretation. The visible CSV labels ST-112 as catch cleaning, not credit; Agent45 subsequently corrected the earlier MAIL-04 attribution and withdrew this preselected classification.
3. ST-094, ST-081, ST-106 and ST-151: three positive-value North rows plus the explicit L-29/S "guide shim credit" row. This is a cross-set hypothesis and is not proven to be part of the PS-0417 route.

## Candidate construction and test

The read-only reproducer is [k04_l29_four_reference_coupon_screen.py](../agents/agent14/k04_l29_four_reference_coupon_screen.py). It asserts the print-fleet route, binder tab order, selected North CSV rows, and the explicit ST-151 credit row before constructing candidates.

For each selector, it generated **159 deterministic 16-byte coupon transformations** (156 unique byte strings), including:

- tab-ordered ticket/amount tuples with independent 16-bit endianness;
- 32-bit ticket-number and amount arrays, ASCII ticket forms, and float32 amount arrays;
- per-row CRC32 values and per-ticket 32-bit fingerprints;
- 128-bit digests of four-tab and five-tab reference lists and selected rows;
- four 32-bit fingerprints and joined 128-bit digests of the four non-job route fields (ESC-N, L-29/N, FA-17, H17-POL-17/A3).

Across all three selectors this is **477 transformations and 332 unique coupon values**. For each coupon C, the test formed the K04 component C XOR M, using the unchanged masked_component M, and compared SHA256(C XOR M) with the original K04 slot commitment. No candidate bytes are printed or persisted.

**Result: 0 of 477 commitment matches.**

## Interpretation

This is a bounded negative for the tested visible ticket/reference serializations, not a proof that the L-29 records are unrelated to K04. The route-to-North-binder association is source-grounded; none of the tested four-row selections has a source-authored byte-serialization rule. The original PrevERP records remain the deciding evidence: first look for a literal 16-byte coupon/reference field, then use native transaction IDs and reversal links to establish the three live parts, credit line, prior card and separate supplier adjustment. Do not substitute ticket suffixes for missing native transaction references.

The original spool, route, acceptance commitments, and verifier were not changed. The canonical six accepted components remain unchanged; K04 and K08 remain missing, and REC8/1 remains incomplete. Do not broaden this into arbitrary ticket permutations or generic hash/encoding sweeps without a new source observation.
