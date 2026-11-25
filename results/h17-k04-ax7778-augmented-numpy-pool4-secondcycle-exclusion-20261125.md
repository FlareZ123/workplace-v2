# K04: AX-7778-augmented NumPy SeedSequence pool4 second-cycle exclusion

**Agent 50 | 25 November 2026 | Conditional source-model exclusion; original K04 remains unresolved.**

## Question

Does the original AX-7778 checkpoint run, when aligned to the p951 printer chronology, provide enough source-pinned information to make the later-cycle NumPy MT19937 four-word `SeedSequence` pool inversion a bounded complete-output construction?

This test combines the exact p951 relative schedule with the complete AX-7778 checkpoint block. It is not a generic seed sweep and does not assume an MT prehistory before NumPy's initialized state.

## Source inputs and conditional alignment

- Printer input SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Transfer audit SHA256: `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`.
- All 132 intact printer packets were used; selected row129 was set to `None` before payload parsing and was never read.
- The 16 AX-7778 checkpoint halfwords were sorted by `(seq, attempt)`, from 0/1 through 7/2. Their byte-swapped high-16 interpretation matches the previously established p951 relative stages **-157..-142**.
- The p951 schedule has `STARTS[0]=0`, `STARTS[129]=951`, and `STARTS[132]=963`. For NumPy second-cycle phase `p`, printer row0 begins at raw output index `604+p`; the AX block therefore occupies raw indices `447+p..462+p`.
- The NumPy initialized state `S[0..623]` is the symbolic origin. Its mandatory `S[0]=0x80000000` condition is applied directly. No source state is assumed to exist before that initialized window.

The AX-to-printer relationship and p951 schedule remain conditional source geometry, not historical authentication that AX-7778 was the printer's generator or source object.

## Method

A GF(2) MT19937 symbolic recurrence was built forward from the 624-word NumPy initialized state. The source basis imposed:

1. all four untempered words from each of the 132 intact printer packets at the p951 `STARTS` positions; and
2. all 16 high-16 tempered AX-7778 observations at relative positions -157..-142.

The printer-only basis has rank **15,365**. The AX checkpoint block contributes **130 additional independent equations**, giving rank **15,495** before the NumPy `S[0]` condition. This agrees with the independent AX projection result in [Agent32's report](h17-k04-ax7778-16-checkpoint-target-projection.md).

For each phase, the NumPy initialization equation for state word `S[i]` was inverted against source-determined bits. Since every word with `i mod 4 = 0` must derive from the same pool word `pool[0]`, multiple fully determined words in that residue provide a direct consistency test. The algorithm also checks other source-fixed bits when a pool word is uniquely determined.

## Results

<badge color="success">393 / 393 phases excluded</badge>

| Result | Count |
| --- | ---: |
| Phases tested | **393** (0..392 inclusive) |
| Contradict NumPy's fixed `S[0]` | **47** |
| Remaining phases with incompatible `pool[0]` derivations | **346** |
| Phases with a viable pool4 candidate | **0** |
| Underdetermined phases | **0** |

For each of the 346 non-`S[0]`-contradictory phases, fully source-determined `S[i]` words with `i mod 4 = 0` imply **12–39 distinct values** for the single required `pool[0]` word. The contradictions therefore do not depend on a bounded partial-word completion search. The 47 `S[0]`-contradictory phases are:

`17, 22, 42, 44, 55, 68, 72, 84, 92, 99, 101, 109, 112, 114, 140, 149, 150, 191, 208, 210, 214, 220, 262, 269, 276, 277, 282, 286, 294, 301, 302, 304, 308, 318, 319, 323, 328, 330, 335, 341, 342, 346, 353, 374, 375, 376, 380`.

All 393 phase records have source-basis rank 15,495 before imposing `S[0]`; after that condition, 297 have rank 15,527 and 96 have rank 15,526. No original phase produced a pool, so the full-source candidate gate was never entered.

### Synthetic calibration

**25/25** independently planted controls passed: seeds `1234, 17, 5, 5489, 42` crossed with phases `0, 13, 99, 218, 390`. Each recovered the exact four-word NumPy pool and reproduced all **132/132** intact synthetic printer packets with the selected row withheld. This also exercises phases on both sides of the first/second-twist boundary.

Runtime: Python 3.13.5, NumPy 2.3.5. The deterministic source SFT is [`agents/agent50/k04_numpy_pool4_ax_basis_sft.py`](../agents/agent50/k04_numpy_pool4_ax_basis_sft.py), SHA256 `b847d0ad86ef127cfebfc4a54802e5965c34e050fe01d8825f0a44a9e2f575b0`.

## Interpretation and limits

This closes only the **NumPy MT19937 SeedSequence pool-size-4 second-cycle model with phases 0..392**, conditional on the p951 schedule and AX-7778 relative-stage bridge. It does not exclude other pool widths, other seed constructors, scalar or multiword initialization, other generator families, reseeding, different output epochs, or a physical coupon/capture mechanism. It does not establish that the AX-7778 drill export historically seeded the printer.

No selected ACK2 payload, K04 route mask, K04 acceptance commitment, candidate component, or K08 target was used in this run. The candidate gate is present in the SFT only for a future complete-source pool; because every original phase was excluded, it did not execute. The original K04 and K08 components therefore remain **MISSING**, and REC8/1 remains **INCOMPLETE**.

The result redirects effort away from this particular later-cycle NumPy pool4 family and back toward source-authenticated PS-0417 queue/job/coupon records or a materially different complete-output construction.
