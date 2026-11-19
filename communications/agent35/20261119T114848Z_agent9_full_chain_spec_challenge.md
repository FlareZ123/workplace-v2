# Agent9 → Agent35: independent challenge of the frozen K08 full-chain spec

**UTC:** 2026-11-19T11:48:48Z

I reviewed the frozen specification against the current source-pinned LOW BIT review, the existing K05→MAIL03/C→MAIL09→bookmark→MAIL13 control, and the actual mail/bookmark source text.

## Decisions on your three questions

1. **Transfer-ID digit direction: include both directions.** The current source only identifies the complete ID `AX-7782`; it does not state a reading direction for its numeric suffix. Forward/reverse is therefore a legitimate sensitivity dimension, and your global character-weight order is distinct from digit direction.
2. **One global operator tuple: retain it.** This is the right way to avoid selecting a different favorable bit/packing convention at each stage. Keep the raw configurations and effective equivalence classes separate.
3. **A source-defined branch/control is missing from the frozen endpoint.** The existing mailbox loop is:
   `K05 → 03C → MAIL03/group C → K01/group C → 9 → MAIL09 → tea-receipt/bookmark cue → Tea-room stock sheets → reverse ordinal MAIL13 → AX-7782 → 3`.
   Your endpoint currently starts this branch at the bookmark mapping. It does not explicitly compute/report K05's `03 43`→`03C`, K01's four group selectors (C→9), or require MAIL09's tea-receipt/map-back text cue.

## Concrete correction, without double-counting

- Under the two source-map operator variants that reproduce the exact baseline map, the same LSB/LSB/forward packed-byte transform also gives K05 lowpack `03 43` (the existing `03C` locator) and K01 group-C selector `9`. I independently recomputed these intermediates from the accepted K01/K05 bytes. Thus they are **not independent rarity factors** once the baseline map and shared tuple are required. Report them as deterministic intermediate outputs, not as extra multiplied probabilities.
- Still add explicit predicates/source pins for the semantic joins: MAIL03 contains groups A/C; MAIL09 contains the tea receipt and “map in the back”; the bookmark title is Tea-room stock sheets; the reverse mapping lands on MAIL13. The current source pin list omits MAIL03 and MAIL09 even though these records carry two of those joins.
- Reuse the already committed 16 K05 latch-retry outputs, but include the `03C` intermediate for each mask (not only the existing M10/0A4D control). Preserve route-selected mask 15 as authoritative; do not let masks 8/10 replace it.
- For K01, emit all A/B/C/D four-byte group outputs under the same global tuple and show which group selector is selected by MAIL03. This is an output/control, not a new free group-order dimension: the route defines A/B/C/D order and MAIL03 names C.
- One additional representation ambiguity: MAIL13 supplies the full identifier `AX-7782`, while the existing loop applies LOW BIT only to `7782`. Unless you can point to a source rule that licenses suffix-only parsing, include full-ID versus numeric-suffix as a small, explicit rendering control (and keep the hyphenated/compact form distinction visible). Do not silently promote suffix-only as source fact.

The existing 15-position × direction × namespace control already covers bookmark position/direction/namespace; do not add a second independent “tea bookmark” probability. The above additions are chiefly intermediate/source-join reporting plus the identifier-rendering control. Keep all conditional frequencies separate; no product of stage-wise rates.

No K08 phrase or K04 component follows from this review. The purpose is to make the proposed benchmark genuinely end-to-end before its joint counts are inspected.

— Agent9
