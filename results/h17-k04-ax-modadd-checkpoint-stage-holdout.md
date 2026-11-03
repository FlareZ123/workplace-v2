# K04: 16-bit modular-addition AX checkpoint stage-model holdout

**Agent 7 | 3 November 2026 | Original-source conditional negative; K04 unrecovered.**

## Distinct model and target relevance

Agent 50's original AX-7778 checkpoint sequence can be aligned with the hypothetical p951 MT19937 printer source at native stages -157 through -142, using byte-swapped **upper 16 bits of tempered outputs**. Agent 1 subsequently tested direct 16-bit output views and a transfer-specific fixed XOR salt, including strides 1–16 and stages through 5300. A **fixed addition modulo 65536** is algebraically different from XOR whitening because carries couple the bits. As a possible checksum-style checkpoint emitter, it is a concrete additional producer hypothesis.

For each transfer, posit that the retained checkpoint in source (seq, attempt) order is:

    checkpoint[j] = (16bit_view(MT_output[start + j*stride]) + salt) mod 65536

The salt is one unknown, fixed 16-bit integer per transfer. The output view is one of native/tempered × low/high 16 bits × two byte orientations. Stride is fixed 1..16. Original source records do not establish that checkpoint firmware uses this additive law, a shared printer MT, or a source-generator timestamp corresponding to the retained event timestamp. This test seeks an independently predictive **second** transfer-to-source stage, which might eventually supply K04-relevant information.

## Actual source and exact solver

The source-only p951 model imported from [Agent 49](../agents/agent49/k04_p951_symbolic_basis.py) conditions on the **132 intact/nonselected printer rows**, excludes row129's disputed 18:02 ACK coupon entirely, SHA-pins the original printer export 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083 and has rank **15,365**. The AX source reader inherited from [Agent 1](../agents/agent1/k04_ax_extended_source_sft.py) SHA-pins transfer audit 32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf and supplies **16 original checkpoints per transfer**, sorted by source sequence and retry.

For each fixed stage, stride, view and transfer, the first **eight** checkpoints alone must expose at least **32 source-predicted individual bits**. Solve the entire fixed salt family exactly by progressively extending its 16 low-order bits. At each step, discard a salt prefix when any source-predicted bit disagrees with (observed minus salt) modulo 65536. Unpredicted MT bits remain free; no unknown stage bits are assigned from desired target hashes. This is an exact finite constraint solver for the assumed additive emitter.

The remaining eight checkpoints are held out from salt/index fitting. To call an alignment source-supported, require **zero held-out bit disagreements and at least 24 printer-fixed held-out bits**. The original selected K04 packet, route mask and K04 commitment are never read for stage/model selection.

## Results

Across four original transfers, four MT word views, both checkpoint byte orientations, stage starts within -1100..5300 and strides 1..16, **1,636,072** source-fixed-bit-qualified training window assignments were evaluated. Exactly **six** transfer/view/stage/salt assignments fit the first eight checkpoint observations. All six are shown, including the uninformative heldout case.

| Transfer | View and checkpoint byte order | Native start | Stride | Additive salt (decimal) | Fixed training bits | Heldout agree / disagree |
|---|---|---:|---:|---:|---:|---:|
| AX-7782 | native low16, swapped | 2107 | 15 | 52630 | 32 | 14 / 18 |
| AX-7783 | native low16, swapped | 2244 | 15 | 45606 | 32 | 22 / 26 |
| AX-7781 | tempered low16, swapped | 1327 | 6 | 20402 | 32 | 24 / 21 |
| **AX-7778** | **tempered upper16, swapped** | **-157** | **1** | **0** | **45** | **77 / 0** |
| AX-7782 | tempered upper16, original | 2616 | 5 | 47114 | 32 | 10 / 3 |
| AX-7783 | tempered upper16, original | 3150 | 9 | 47167 | 32 | **0 / 0 (no independent test bits)** |

**Only the previously known AX-7778 zero-salt alignment passes the heldout evidence threshold.** Neither original AX-7782 custodian transfer nor the two other AX streams furnish a newly source-indexed donor under this additive model. The sixth chance fit has no original fixed heldout bits and is explicitly unassessed by the heldout constraint.

## Reproducibility and boundaries

[The repository SFT](../agents/agent7/k04_ax_modadd_sft.py) imports Agent 1's and Agent 49's SHA-pinned read-only source implementations. It asserts the source rank, model-window count, six training fits and the exact known AX-7778 heldout result. Positive controls generate a nonzero 0xAB3D additive salt on a synthetic sixteen-word trace; recover it exactly, reject a corrupted withheld bit and verify partial-known-bit arithmetic. A source-equivalent self-contained local SFT ran to completion on the original 46-member ZIP with these exact observations, and the new import-based committed version is not independently claimed as executed by CI.

This is a bounded exclusion of **constant-stride, fixed-view, fixed-additive-salt AX checkpoint production** in the stated stage/index horizon and first-eight training-information floor. It does not cover time-varying salts, nonlinear chunk digests, irregular draws, independently seeded sources, unseen stage ranges or a historical firmware/capture selector. The established source timestamp paradox for original printer versus later recorder remains: even a strong conditional MT coincidence does not certify the proposed indices as a live shared RNG chronology.

**Actual outcome:** K04 independently authenticated selected payload bits remain **0/128**; K08 still lacks verbatim final Emily words. K01, K02, K03, K05, K06 and K07 remain PASS, K04/K08 MISSING, combined REC8/1 INCOMPLETE. No evidence, verifier, candidate, nonce, mask or commitment was modified.
