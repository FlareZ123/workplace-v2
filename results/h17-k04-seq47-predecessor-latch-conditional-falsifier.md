# K04: original latch holdout falsifies one seq47 parity-stage producer, without authenticating an alternate stage

**Agent 8 | 3 November 2026 | original-source, target-blind source-discriminator.**

## Question and independent observation

The new [56-CONTROL chronology](h17-k04-first-conditional-target-parity-seq47-stage-ambiguity.md) produces a *conditional* K04 payload parity only if node50 seq47 CONTROL originated at p951 native MT stage **−523**. The same other 55 original controls also permit seq47 stages **−522, −521, −520**, with 128/128 selected coupon bits free. Can an intact source field select a stage?

The original CRC-valid node50 seq47 recorder entry has **latch = 1** (001 as a 3-bit integer). The [15 source-indexed recorder anchors](h17-k04-node50-fifteen-ordered-prng-word-chain.md) motivate a testable conditional producer architecture: CPython getrandbits(3) emitted the latch **immediately before** each 32-bit CONTROL. This is a proposed stage interpretation, not an authenticated recorder firmware implementation. Latches are held out of the native CONTROL-chronology construction.

The [reproducer](../agents/agent8/k04_seq47_latch_source_discriminator_sft.py) rebuilds the original 132-intact-printer p951 GF(2) basis (rank 15,365; disputed row129 excluded) and then inserts all 56 CRC-valid recorder CONTROL values under each original-source-compatible seq47 placement. It reads the original recorder latches separately. It **never uses** the selected copied ACK2 bytes, the K04 acceptance digest, the official XOR mask, or a K08 phrase.

## Target-reaching discrimination

| seq47 CONTROL stage | Joint source rank | Source-fixed bits of native preceding 3-bit latch | Original latch agreement | Selected K04 free bits |
|---|---:|---:|---|---:|
| −523 | 16,663 | 2 | **1/2** | 127 |
| −522 | 16,664 | 0 | indeterminate | 128 |
| −521 | 16,664 | 0 | indeterminate | 128 |
| −520 | 16,664 | 0 | indeterminate | 128 |

At **−523**, the conditional model predicts the preceding high three output bits as **?00** (high-to-low). Original latch 1 is **001**; its low bit contradicts the corresponding **source-fixed** prediction. This is a genuine, independent 1-bit contradiction *under the immediate-predecessor latch producer*. The only stage furnishing the new K04 parity therefore fails that specific supplementary producer rule. The three alternatives remain unranked by this latch test because their preceding latch bits are all free. The original K04 remains unknown.

## Is the preceding-latch rule itself reliable?

Use all 56 CONTROL-selected native placements, without fitting on any latches, and score the independently recorded 3-bit latches. The actual original-source test gives:

| Source stratum | Testable source-fixed latch bits | Correct bits |
|---|---:|---:|
| 15 previously source-indexed anchors | 36 | **35** |
| 41 subsequently placed CONTROL rows, including seq47 | 53 | **33** |
| All 56 | 89 | **68** |

For the 41 subsequently placed rows, a fixed-seed 100,000-permutation shuffle of original latch labels among those same 41 rows produced **7,479** shuffles scoring at least 33 correct, a conditional tail around **0.075**. The corresponding 15-anchor permutation produced one equal-or-better shuffle out of 100,000 (stronger source relation, but these anchors were already discovered and some were separately checked using metadata). A 20,000-permutation all-row calibration gave two equal-or-better shuffles at 68/89. Thus the overall 68/89 result is driven substantially by the **previously successful anchor stratum**, and does not validate the immediate-predecessor producer on the 41 newer stage placements. These are conditional retrospective permutation diagnostics, not universal p-values or independent evidence of original firmware.

Negative stage-offset controls on the exact same 56 selected source positions show preceding offsets −7 to −2 at **40.2–53.3%** fixed-bit accuracy, while −1 yields 68/89 = **76.4%**. Offsets +1..+7 give **41.8–51.5%**, reinforcing the concentration of observed associations at −1 but not removing anchor-selection effects.

The original seq47 latch is also **compatible with a different nearby possible timing**: absolute stage **−528** predicts high three bits 0?1, agreeing with both fixed bits of latch 1. This is relative offset −5, −6, −7 or −8 respectively for the four candidate CONTROL positions. A producer with variable interleaving could therefore permit the parity-bearing −523 stage. Neither chronology nor observed metadata uniquely assigns that latch stage.

## Conclusion and next constructive step

The conditional seq47 −523 parity has acquired a **concrete, source-testable caveat**: it contradicts an immediate-before-CONTROL latch producer that is strongly supported on earlier individually source-indexed anchors. The broader newly placed 41-row stratum has not validated the same producer, so the result **must not be reported as an independently recovered K04 parity bit or as proof that −523 is impossible**. It changes what needs testing: identify a consistent **latch/CONTROL interleaving selector** among the previously nonanchored node50 rows, preferably from an original independent field or a genuinely withheld control, and compare it across seq47 −523..−520. Only then can a K04 target-quotient parity be promoted.

The original six keys remain individually PASS; K04 and K08 remain MISSING, and combined REC8/1 remains INCOMPLETE. All original evidence, commitments, verifier and canonical candidate are untouched.

### Reproduction

- [Single-file source-pinned SFT](../agents/agent8/k04_seq47_latch_source_discriminator_sft.py), which imports the established original-source exact p951 model and the existing 56-row chronology.
- Local independently executed source-equivalent scratch tests reproduced the exact rows/accuracy counts and the 100,000-label nulls above. The committed SFT is a shorter reusable variant; a separate remote execution of its exact bytes is not claimed.
- Printer SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083; recorder SHA256 5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba.
