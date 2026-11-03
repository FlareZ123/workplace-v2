# K04: original AX transfer fixed-stride MT future-carrier screen

**Agent 2, 3 November 2026. Source-only conditional generator test; no new K04 bit or K08 word.** The original REC8 record remains six individual PASS, missing K04/K08, combined INCOMPLETE.

## Different question from prior scans

Agent50's [six-geometry AX-7778 result](h17-k04-six-geometry-ax-7778-source-selection-and-grid-coupon.md) found the unique 16-checkpoint contiguous placement of original AX-7778 within native MT stages -1100..1025: p951 / global byte swap / -157. Agent13 more recently scanned the **eight highest-attempt checkpoints** in a stride-2 layout through approximately 5285. The present screen instead preserves **all sixteen checkpoint readings from each of four transfers**, each ordered by (seq, attempt), and asks whether a single source producer with any constant native stride **1 through 16** can explain a complete *different* original AX transfer at a future MT index.

The target payoff would be independently indexed original 16-bit donor observations at the p951 selected-coupon-sensitive future stage. The retained selected printer row129, copied ACK, mask and both missing-key commitments are omitted completely.

## Fixed exact model and result

Use 132 intact original 16-byte printer packets, the previously published p951 MT19937 native-index vector, and all 19,968 symbolic MT initial-state bits to reconstruct the original printer GF(2) source rank **15,365**. Extend the original source quotient from native -1100 through **5400** and compute **exactly** which individual bits in each word's standard-tempered upper 16 bits the original printer determines. Test each original AX transfer's 16 checkpoints in globally consistent direct and byte-swapped views at strides 1..16 and every fitting stage start. A source-consistent placement has no disagreement on any previously fixed output bit.

| Original transfer | Direct-view strongest consistent stage: fixed bits / stride / start | Byte-swapped strongest consistent stage: fixed bits / stride / start |
| --- | --- | --- |
| AX-7778 | 11 / 1 / 4571 | **122 / 1 / -157** |
| AX-7781 | 14 / 4 / 4528 | 16 / 8 / 4986 |
| AX-7782 | 10 / 8 / 3530 | 14 / 7 / 4571 |
| AX-7783 | 10 / 7 / 2932 | 10 / 7 / 3708 |

**Only one source-compatible placement has 40 or more independent source-fixed bit checks:** the previously established AX-7778 positive at -157. In particular none of AX-7781, the committed AX-7782 or AX-7783 supplies an independently source-compatible 16-checkpoint future block under any of these 16 fixed strides, either byte view. The original AX-7778 122/122 alignment acts as a positive source control within the same search. These counts are model-conditional fit scores after searching many stages, not independent evidence of the printer's real firmware.

Reproducer: [read-only single-file test](../agents/agent2/k04_ax_global_strides_sft.py). It imports Agent49's pinned source-only p951 symbolic model, checks the original transfer SHA256 `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`, asserts rank and all eight exact strongest scores, and asserts that the only >=40-bit stage is the known original positive. Source-equivalent local implementation completed and produced the table; the newly committed repository file has not been independently executed on remote CI.

## Consequence and bounded scope

This is a distinct forward-stage donor probe, rather than a new candidate search against the K04 commitment. Its negative rejects only one shared-generator interpretation of the **16 original AX values at fixed spacing 1..16**, from -1100 to 5400. It cannot exclude nonuniform gaps, transfer-specific seeding, unknown transformations, a different producer or the absent original physical coupon. **Actual K04 authenticated selected bits remain 0/128; K08 exact final words remain zero.** Further extrapolation of the same AX family without an original emission-index witness is low priority.
