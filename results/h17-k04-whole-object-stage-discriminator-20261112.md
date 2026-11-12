# K04 early whole-object control extension (2026-11-12)

**Agent 6 | Extension to Agent 2's 12 November selected-stage holdout.** Agent 2's result, [K04 selected-stage whole-object holdout](h17-k04-selected-stage-whole-object-holdout-20261112.md), already tests the late-Z controls (rows 128–132) and establishes that none selects p950/p951/p952. This note records only the additional earlier whole-object controls; it is not a second report of the late-tail experiment.

## Method

Using the same Agent 49 MT19937 symbolic basis and the six late-cohort-contiguous schedules that survive the source equations with target row 129 withheld, I withheld one earlier complete 16-byte packet at a time and reduced its four native words against the remaining affine basis. A bit is counted as fixed only when its form reduces to a constant. The tested schedules include q=950 (one), q=951 (two), and q=952 (three).

## Additional controls

| Zero-based row | Selector | Fixed bits of held-out 128-bit payload | Result |
|---:|---|---:|---|
| 44 | PS-261003-0344, STORES / ACK / attempt 1 / desk | 95 | All fixed bits match; no q discrimination |
| 66 | PS-261003-0366, STORES / ACK / attempt 1 / bench | 127 | All fixed bits match; no q discrimination |
| 96 | PS-261003-0396, RECOVER / ACK / attempt 1 / store | 95 | All fixed bits match; no q discrimination |
| 121 | PS-261003-0421, LABEL / ACK / attempt 1 / bench | 63 | All fixed bits match; no q discrimination |

None of these whole objects is fully predicted, and the fixed projections are the same across the surviving q schedules. Row 66 is the strongest partial control (127/128), but its final bit remains free and does not choose a stage.

## Decision

This extension adds no selected-stage discriminator and does not change Agent 2's conclusion. Do not repeat the same late-tail or early-packet holdout family. The target row 129 remains underdetermined; p951 and the (328, 724) two-gap pair remain conditional, not recovered historical values. A genuinely new result requires an absolute phase anchor, authenticated selected-coupon bytes, or a source-backed copy-stage relation not present in these retained packets.
