# K04: original AX transfer chains under bounded nonuniform MT output gaps

**Agent 23, 3 November 2026. Conditional producer experiment; no recovered K04 input.**

## Question and distinct mechanism

[Agent50's prior contiguous-window AX comparison](h17-k04-six-geometry-ax-7778-source-selection-and-grid-coupon.md) found an excellent 16-checkpoint AX-7778 run at source position -157, but could not place AX-7781/82/83 as **consecutive** 16-word runs. A distinct producer may consume unpredictable extra draws for chunk framing or rejection sampling, so equal-spaced or contiguous enumeration is insufficient.

This experiment uses the existing p951 printer-only hypothetical MT19937 source representation (rank **15,365** from 132 retained intact printer packets; disputed row129 excluded). For each original 16-checkpoint AX transfer group, it finds the *highest-scoring monotonically increasing stage path* with independently variable gaps **1..4, 1..8, 1..16, 1..32 or 1..64** between successive checkpoints. It evaluates five stable record orderings (seq/attempt ascending and descending, attempt/seq ascending and descending, retained file order), both global checkpoint byte orders, and both upper/lower16 tempered word orientations. All underlying original bytes are pinned by the reusable source module and original AX SHA-256.

For each path, a candidate stage is allowed only if **every originally printer-fixed bit** agrees with the checkpoint value. Its score is the number of agreeing source-fixed bit *positions* across the 16 checkpoints, optimized by exact sliding-window Viterbi dynamic programming. Scores are descriptive, **not** independent-information counts or a post-selection significance test.

## Original-source result

| Transfer | Best fixed-bit score | Best source path |
|---|---:|---|
| AX-7778 | **122** | seq ascending/attempt ascending, byte-swapped upper16, consecutive stages -157..-142 |
| AX-7781 | 51 | seq descending, direct lower16, 1..64 variable gaps |
| AX-7782 (committed K07 source) | 45 | seq descending, byte-swapped upper16, 1..64 variable gaps |
| AX-7783 | 48 | retained file order, byte-swapped lower16, 1..64 variable gaps |

The original AX-7778 chain remains the uniquely strong source-anchored transfer in this tested architecture. In **100 fixed-seed shuffled AX-7778 checkpoint-order controls**, the strongest dynamic-path score was **79**, mean **54.43**, against the original **122**. The other three transfers remain at control-like source-anchored scores despite nonuniform stage spacing. This expands the contiguous-window comparison to a bounded sequence-scheduling alternative with genuine conditional positive and negative controls.

**Reproducer:** [single-file, standard-library SFT](../agents/agent23/k04_ax_transfer_variable_gap_sft.py). It imports the earlier [p951 symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py), recomputes original record constraints and all four transfer searches, asserts the exact outputs, and regenerates the 100 permutation controls. It neither uses the disputed original selected ACK as data nor queries the K04 commitment.

## Interpretation and next attack

The positive AX-7778 relation is evidence for a **candidate shared source-generation stage** inside this fitted geometry. It does not establish historical live-stream chronology: the printer and recorder event timestamps are inconsistent with a strictly time-ordered single stream, as Agent10 and Agent50 previously noted. The absence of a strong AX-7782 path means that **adding short, monotonically gapped checkpoint emissions** does not provide the missing selected-stage donor under this bounded model. Different staging, PRNG resets, larger jumps, nonlinear transformations, and an independent event-specific producer remain untested.

The selected four native MT coupon words at 951..954 have **zero individually printer-fixed source bits** in the reused conditional basis, consistent with the already established 128-bit selected quotient. This experiment does not reconstruct them or constrain K08's wording. Six individual REC8/1 slots pass; K04 and K08 remain missing, and combined acceptance remains incomplete.
