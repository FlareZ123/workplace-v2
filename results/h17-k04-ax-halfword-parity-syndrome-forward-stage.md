# K04: full partial-checkpoint parity syndromes across future MT stages

**Agent 17 | 3 November 2026 | New source-only stage discriminator; no K04 recovery.**

## Mechanism and why it differs from previous AX scans

The original transfer audit has exactly 16 two-byte checkpoint values for each of AX-7778, AX-7781, AX-7782 and AX-7783, ordered by (seq 0..7, attempt 1..2). Under the published *hypothetical* p951 common-MT stream, a transfer could record 16 consecutive upper or lower 16-bit portions of MT19937 tempered output words, in either byte orientation.

Earlier Agent1/Agent50 transfer scans compared **individually determined checkpoint bits** against original source predictions. This experiment uses the **entire 256-bit checkpoint block** as a linear system, including parity relations among individual checkpoints that remain invisible to direct per-bit predictors. Thus it can exclude a prospective stage even when that stage has no individually reconstructed exact 16-bit checkpoint value.

Compute the 15,365-rank GF(2) source model from all 132 intact printer packets, expressly omitting the disputed row129 selected RECOVER/ACK2. Extend its exact native MT twist recurrence to stage5315. For each candidate stage, reduce the 256 projected checkpoint bits against the original source equations and then each other, retaining every parity consistency equation (a source-derived syndrome). A 16-halfword stream must satisfy **all** such equations to be an observed output of that model. A violation rules out that one transfer/stage/view assignment, irrespective of the true target commitment.

Source pins: printer reconstruction SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, original transfer audit SHA256 `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`. No K04 mask, target digest or selected copier bytes enter discovery.

## Two independent controls

1. **Actual original cross-carrier positive:** AX-7778, the preincident drill, matches **all 126** independent source/within-block parity checks when its 16 two-byte original checkpoints are read little-endian as the tempered upper16 at native stage **−157**. Its opposite byte order violates **60/126**; lower16 at the same stage violates **58/126** with little-endian. This reuses the prior Agent50/Agent1 selected original stage but tests a stronger whole-vector observable than their per-checkpoint source-fixed bit comparisons. It is powerful conditional evidence for that cross-source correlation; historical producer identity remains unproven.
2. **Seeded model-consistent synthetic positive:** Construct a random full 19,968-bit MT initial state satisfying all 15,365 actual original printer equations. Generate a 16-halfword burst at native1347. Its **94** original/within-block syndrome equations all pass. A one-bit mutation of a parity-constrained checkpoint is detected. These controls check the bit-order, affine right sides, recurrence, and rejection of inconsistent data.

## Complete future-stage negative under explicitly bounded architecture

Scan every contiguous 16-native-output window beginning **1040 through 5300 inclusive** (4,261 stages), for both upper/lower tempered 16-bit projections; compare each independently with all 16 checkpoints from each of **three later AX transfers 7781, 7782, 7783**, in little/big byte order. Require at least 16 independent parity constraints to classify a stage as *source-testable*.

| Minimum independent syndrome equations | Exact original transfer/stage/view assignments | Smallest number of violated equations | Zero-violation matches |
|---:|---:|---:|---:|
| 16 | 36,672 | 3 | **0** |
| 24 | 34,248 | 4 | **0** |
| 32 | 27,084 | 9 | **0** |
| 64 | 12,984 | 20 | **0** |
| 128 | 1,692 | 53 | **0** |

There are 6,112 (stage, high/low projection) models with at least16 independent equations, each compared against six original (transfer, endian) candidates. The right side of every check derives from **unaltered original printer and transfer values**, with the selected K04 event withheld.

An additional candidate-construction feasibility pilot assessed three 16-halfword future donor bursts at native stages **1179, 1347 and 1574**. Their hypothetical joint linear observation span would fix **112 of the 128 selected MT coupon dimensions**, leaving 16 for exact commitment enumeration, a potentially computationally tractable end-to-end hypothesis *if* genuine stage-indexed donor sources existed. However individually assigning any of the three actual late AX checkpoint streams at those anchor stages yields tens of source-parity violations (minimum for these fixed starts and tested views 37), so **this actual AX-to-donor stage assignment is false under the model**. No K04 candidates or original hashes were generated from contradictory donor inputs.

## Scope, next move and reproducibility

This is a strict negative for *contiguous 16-checkpoint halfword bursts* on the conditional p951 MT stream, at native starts1040..5300, observed high/low tempered bits, both byte orders, and with at least16 original-source parity checks. Stages with fewer than16 constraints remain **unclassified**, as do different generator seeds, capture clocks, noncontiguous/strided output mapping, buffering/copy transforms, and the actual physically printed coupon. A universal negative for AX transfer data would be unsupported.

Portable original-source-pinned [SFT](../agents/agent17/k04_ax_future_halfword_syndrome_sft.py) uses [Agent49's shared symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py), reconstructs the original 126-parity positive and source-consistent synthetic control, then exhausts the stated future-stage classes. It leaves original evidence, acceptance commitments, verifier and six-pass candidate untouched.

**Archive status:** original K01/K02/K03/K05/K06/K07 accepted, K04 and K08 unresolved, combined INCOMPLETE. This stage discriminator adds **zero authenticated selected coupon bits**, but it substantially reduces the scope for a late transfer to act as a missing donor under the claimed p951 producer and explains why individual-bit stage scans were insufficient.
