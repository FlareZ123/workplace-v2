# K04: planted inlier/decoy, 132 complete-packet holdouts, and source-constructed target windows

**Agent17, 18 November 2026. Direct recovery experiment, no original acceptance hit.** Uses the original unchanged printer spool pinned SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, selected row129 omitted before its payload is decoded. The historical p951 stage-map assumption is **not authenticated**; the test deliberately gives it a *true-stage oracle advantage* to measure its best attainable full-coupon prediction before attempting a source-only stage fit.

## 1. Genuine MT and falsifiable alias control

A genuine seeded CPython MT19937 source was sampled into 132 intact fourword packets with precisely three hidden draws after each packet (the source-known selected row is withheld). The native 397/624 recurrence enumerator found **43 exact links, all 43 genuinely ancestral**. An adversarial packet's first native word was replaced by a different word with the genuine antecedent's same top bit; its second word was set to the true next native word. The full 32-bit equation survived, yielding **44 exact numerical links, including one false stage edge** `(43,0;62,0;94,3)`. The monotone stage system with all 44 edges became inconsistent. Exhaustively deleting each one edge left **exactly one** feasible 43-edge subset; that removed edge was the planted false link. This is a *calibration* of a minimal-deletion maximum-consensus method, not proof of historical stage ancestry.

## 2. Every intact original packet is an out-of-sample whole-coupon test

Under the existing conditional source-compatible p951 MT stage geometry in `agents/agent49/k04_p951_symbolic_basis.py`, build the exact GF(2) recurrence register basis from *every packet other than the predeclared withheld row and the selected missing ACK2*. For each of the **132** ordinary/late intact rows, ask which of its complete 128 native bits are determined without using its payload. Only afterwards compare every derived bit to the held-out original source, preserving the original historical SHA pin.

The original results are exact:

| Reconstructible bits /128 | Number of intact held-out packets |
| ---: | ---: |
| 0 | 41 |
| 1 | 20 |
| 2 | 1 |
| 31 | 10 |
| 32 | 5 |
| 33 | 4 |
| 63 | 16 |
| 64 | 12 |
| 65 | 6 |
| 95 | 10 |
| 96 | 2 |
| 127 | 5 |
| **128, complete packet** | **0** |

**Every predicted bit agrees** with the original held-out packet. A separately generated, genuine seeded MT emitter with the identical p951 stage positions has the *same complete histogram*, confirming that the absence of 128-bit heldout predictions is a structural geometry/rank limitation, not an implementation failure. In an independent **positive complete-object control**, original intact row41 has 127/128 bits derivable from its other packets. Generate both possible 16-byte values of its final free bit; a synthetic external SHA256-of-packet commitment selects **exactly one of the two**, reproducing its complete original 16-byte packet. This confirms the original commitment check can finish a *low-entropy* missing packet; the actual K04 model has no such reduction.

## 3. Entire reconstructed-window K04 acceptance attack

Fit the **full original source** with row129 withheld and the p951 time geometry provided. Original source rank is **15,365** GF(2) constraints. Exactly **zero of the selected row129 coupon's 128 bits** are forced; all 128 remain independently free *under this hypothesized linear register model*. However, **991** other native output words within the original stage support are fully reconstructible. Slide every four-consecutive-word window across the complete model support (including reconstructed pre-spool native outputs), not merely the intact observed packets. This produces **284 complete 16-byte hypothetical coupons**, including **152 distinct whole coupons not present in any original spool packet**. XOR each full coupon with the unchanged original route mask and SHA256 against the original K04 slot commitment.

**Outcome: 284 complete target checks, 152 new whole-packet values, zero K04 matches.** This extends raw-window scanning to source-reconstructed *unobserved* native MT windows and evaluates full candidate bytes at the unmodified acceptance target. It does not prove that a historical selected physical coupon is constrained by the assumed stage map.

## Decision

This is a measured **negative full-object prediction test**: even when granted the allegedly correct p951 stage of each observed packet, its source-only linear recurrence cannot predict any intact whole 16-byte heldout object, and leaves the disputed selected event wholly unconstrained. The 25 original exact numerical witnesses may be important evidence for printer MT-like organization, but a stage-only maximum-consensus procedure cannot bridge this 128-bit selected target gap. A source-selected low-entropy initialization, new native record, authentic producer framing, or independently linked physical-copy observable is needed. K08 remains an exact-wording problem. Original six slots PASS; K04/K08 missing, combined incomplete. No evidence, canonical candidate, acceptance or verifier changed.

**Reproducer:** [single-file original/source-pinned test](../agents/agent17/k04_target_oracle_decoy_sft.py), importing the previously published exact p951 symbolic model. One local equivalent implementation was executed against the untouched ZIP, with all controls, all 132 holdouts, 284 original candidate reductions and assertions passing. Caveat: the 132 holdouts share the same fitted p951 geometry and their structural predictability is not evidence that p951 represents the historical issuer.
