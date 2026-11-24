# K04: adversarial cross-review of the two L-29/N candidate constructions

**Date:** 2026-11-24  
**Reviewer:** Agent 1  
**Decision:** two distinct candidate generators, one shared uncertain source association; both negative. Do not expand the L-29/N branch with adjacent variants.

## Question

Are Agent14's direct four-reference coupon serialization screen and Agent50's four-fresh future-donor MT screen the same experiment, genuinely independent evidence, or overlapping candidate spaces?

## Source operands and selectors

| Dimension | Agent14 direct coupon screen | Agent50 four-fresh donor screen |
|---|---|---|
| Primary source | L-29/N supplier reconciliation CSV plus print-fleet retirement note | Same CSV and print-fleet note, plus Agent10's source-pinned spool/recorder/telemetry/transfer/accepted-component model |
| Row state | R3 / POSTED rows; ST-112 R4 / HELD is not selected | Same R3 / POSTED selection; ST-112 R4 / HELD is not selected |
| Selectors | Three: tabs 01–04; tabs 01–02–03–05 (conditional ST-112 substitution); three positive North rows plus the explicit L29S South credit | Two: tabs 01–04; tabs 01–02–03–05 (conditional ST-112 substitution) |
| Order | Binder tab order for each selector | Binder tab order for each selector |
| Source relationship | PS-0417 is associated with the L-29/N *set*, not an individual ticket | Same set-level association; the script explicitly disclaims a ticket-to-job foreign key |

Both constructions depend on the same uncertain L-29/N cohort association and tab-order premise. Neither has an authenticated ticket-to-PS-0417 join, native PrevERP transaction IDs, the original five-tab physical binder, or a native printer/coupon object.

## Fixed transformations and candidate spaces

### Agent14: direct coupon serialization

Source: `agents/agent14/k04_l29_four_reference_coupon_screen.py`; result: `results/h17-k04-l29-four-reference-coupon-screen-20261124.md`.

For each of three selectors, the script enumerates 159 deterministic 16-byte constructions from ticket numbers, amount cents, full-row/reference CRC32 values, per-field digests, concatenated reference strings, route references, abbreviations, and float encodings. Each proposed coupon is XORed with the published K04 mask and checked against the immutable K04 SHA-256 commitment.

- 477 transformations
- 332 distinct pre-mask coupon values across the selectors
- zero commitment hits
- no synthetic positive control

This is a direct serializer screen. Its transformations are plausible encodings of visible supplier fields, not a source-authenticated coupon-generation rule.

### Agent50: four-fresh future-state donor construction

Source: `agents/agent50/k04_l29n_fourfresh_donor_sft.py`, reusing Agent10's `agents/agent10/k04_fourfresh_future_source_donor_sft.py` and its all42 MT19937 state model.

The six L-29/N donor blocks are three 4-word big-endian numeric forms (ticket suffixes, amount cents, and `(suffix << 16) | amount_cents`) across two selectors. They are added to eleven existing 16-byte source/accepted-component donor blocks, for 17 donor objects total.

The existing GF(2) model selects two future four-word donor starts (1409 and 1863) by target observability. Each donor is presented in 96 ways (24 word permutations × 2 byte orders × 2 native/untemper interpretations), mapped to the unobserved target state, MT-tempered, XORed with the K04 mask, and checked against the commitment.

- 3,264 complete candidate components
- 3,072 distinct component values
- zero K04 commitment hits
- zero overlap with the earlier 748 source-stage coupon set
- selected copied PS-0417 ACK2 payload was **not loaded**
- original printer-source rank 15,434; 128 target bits remain unresolved without a donor

This is not a direct coupon serializer. It is a conditional MT19937 state-reconstruction/donor model. Its two donor positions are selected by GF(2) observability, not by an authenticated printer event, ticket-to-job mapping, or native source-stage record.

Workflow evidence: run `45491557581`, artifact `k04-l29n-fourfresh-result` (artifact ID `14965054470`, SHA-256 `c1fbcfc1a4f500ee6aed739b8ac3866becda0a0be74c1756f4e9ae6c891aa66f`). The sanitized artifact reports both synthetic donor reconstructions succeeded and no original commitment match.

## Prior-art overlap and independence

The constructions are materially different at the transformation layer:

- Agent14 directly serializes/hashes L-29/N row fields into 16-byte coupon candidates.
- Agent50 uses L-29/N numeric fields as hypothetical 128-bit donors to a future MT state and derives the 16-byte output through a GF(2) mapping and MT tempering.

However, they are **not independent evidence for the L-29/N source association**: both use the same binder order, same cohort-level PS-0417 reference, and same non-native supplier CSV. Agent50's reported `OVERLAP_WITH_PREVIOUS_748 = 0` compares its candidates with Agent10's prior source-stage-window set; it does **not** report the intersection with Agent14's 332 distinct masked coupon candidates. The exact cross-set intersection was not computed. Therefore, do not describe the two candidate sets as disjoint or infer that zero overlap with 748 establishes zero overlap with Agent14.

The two searches are complementary, not duplicate implementations, but they belong to one coordinated L-29/N branch. Their negative results do not strengthen the source association itself.

## What the positive controls establish

- **Agent50:** the planted synthetic MT state reconstructs the selected 128-bit coupon exactly through both future donor starts. This validates the GF(2) mapping and implementation under the assumed MT19937 chronology. It does not establish that the historical printer used this emitter, that the selected target occupied the inferred stage, or that L-29/N numeric fields were actual future-state donors.
- **Agent14:** no synthetic control is present. A meaningful positive control would require a known complete coupon from a same-route/same-schema source, with its four reference rows and actual output both preserved. No such control is in the supplied export.

## Adversarial assessment and next decision

1. Preserve both bounded negatives; do not collapse them into one algorithm or call them independent confirmation.
2. Do not extend the L-29/N branch with another tab selector, amount/ID serialization, donor encoding, or future-state presentation. The current two models produce no accepted K04 value and share the same unresolved source premise.
3. The next useful work must use a genuinely different source/producer relation or native evidence: original PS-0417 `.SPL/.SHD`/printer media and physical coupon, native PrevERP transaction records, or the original profile-refresh/desk source objects. If the missing object is not available, keep K04 unresolved rather than converting a conditional synthetic model into a historical claim.
4. The live decision map need not change: this review consolidates interpretation but does not change the best next decision.

**Confidence:** high on the comparison of the two scripts and the reported bounded outcomes; low on any historical interpretation of the L-29/N-to-K04 relationship.
