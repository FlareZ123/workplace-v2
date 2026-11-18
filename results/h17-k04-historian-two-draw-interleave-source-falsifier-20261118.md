# K04 source-native MT19937 with two historian draws per routine spool row

**Agent 23 | 18 November 2026 | bounded producer hypothesis falsified; K04 remains unaccepted.**

## Different assumption tested

The retained historian has precisely 112 `PV` records with contiguous source `seq=100..211`. Hypothesize that each such PV consumed **two consecutive native MT19937 32-bit outputs**, analogous to a two-draw 53-bit floating sample, and that the 112 records were interleaved by sequence ordinal with the first 112 of 128 ordinary printer packets. Each printer packet consumes four successive native output words. The two unknown PV outputs may occur at any one of **five globally fixed word boundaries** within each corresponding ordinary printer packet. The last 16 ordinary printer packets have no assigned PV sampling operation.

This changes the earlier Agent23 **one-word raw-32 PV insertion** idea into a genuine **two-output floating-sampler clock**, tested against exact native recurrence identities rather than fitting an assumed PV value codec or attempting direct state initialization. The alignment is speculative: historian acquisition at 21:13 UTC does not attest interleaving with ordinary printer jobs earlier that day. The experiment tests this concrete source-indexed producer as a conditional mechanism, without asserting historical common issuance.

## Source and deterministic test

- The untouched printer buffer `resources/evidence/print/spool-reconstruction.log` has SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Only rows 0–127, jobs PS-261003-0300..0427, supply the 512 observed 32-bit words.
- The untouched historian `resources/evidence/telemetry/freeze-export.jsonl` has SHA256 `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`. Its 112 contiguous PV sequence identities determine the count and ordinal mapping; the PV numeric values are intentionally *not* fitted, making this recurrence preflight more permissive than a full floating-value test.
- The five locations of two unknown words and the four big/little-endian × forward/reversed-word printer serializers give **20 frozen layouts**, each exactly 736 native-output positions.
- Untemper known complete 32-bit printer words. For all four-known-position tests, check `X[i+624] = X[i+397] XOR twist(X[i], X[i+1])`, the exact native MT19937 full-word recurrence. A single original contradiction rules out that entire fixed layout for the source model.

## Actual results

| Model | Evaluated full-word identities | Matches | Contradictions |
| --- | ---: | ---: | ---: |
| Each of 4 serializer views, PV before packet word 0 | 56 | 0 | 56 |
| Each of 4 serializer views, PV after packet word 0 | 55 | 0 | 55 |
| Each of 4 serializer views, PV after packet word 1 | 55 | 0 | 55 |
| Each of 4 serializer views, PV after packet word 2 | 56 | 0 | 56 |
| Each of 4 serializer views, PV after packet word 3 | 57 | 0 | 57 |

Across the 20 layouts, **1,116 full-word MT comparisons, zero original matches**. A separate, actually executed seeded CPython MT19937 positive control generated 736 consecutive native words, hid the correct two per PV in the same five layouts and recovered **55–57 exact native identities with zero violations** in every layout. The script checks both original source digests, word counts and sequence identities.

**Executable source-pinned SFT:** [`agents/agent23/k04_hst_two_draw_interleave_sft.py`](../agents/agent23/k04_hst_two_draw_interleave_sft.py). No original K04 ACK2 or source-selected physical coupon bytes were used; the original mask/commitment, verifier, canonical candidate and source materials were not modified.

## Research consequence

The simple two-draw-per-PV interleave with one fixed insertion offset cannot be the writer of the observed routine printer words, regardless of the hidden PV numerical readings. It does **not** reject independent historian acquisition, two draws at different per-record positions, variable hidden draws or unknown chronology; those alternatives need a genuinely distinguishing source relation. Nothing here reconstructs a complete original physical K04 coupon or Emily's K08 wording. Existing six slot PASS; K04/K08 remain missing and combined REC8/1 incomplete.