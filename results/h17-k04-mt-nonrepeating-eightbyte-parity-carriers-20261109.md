# K04: source-constrained MT 227-step nonrepeating eightbyte carrier search

**Agent 33 | 9 November 2026 | completed original-export computation; K04 unresolved.**

## Recovery route tested

The unselected original printer packets contain exact MT19937 output relationships under the previously published provisional p951 chronology. Such a producer would offer another way to recover the selected ESC-N fourword coupon if a **previously unrecognized pair of original MT words** survived in a separate source file. Previous paired-field screens primarily assembled explicit fourbyte recorder, procedure, and administrative values. This independent screen instead tests **every consecutive eightbyte window outside the printer file**, including the binary recorder and windows obtained by hex-decoding original long hexadecimal fields.

The selected `PS-261003-0417 ATTEMPT=2 ACK` copied buffer is excluded from generator fitting and completely excluded from the candidate window population. The acceptance hash, route XOR mask and K08 do not enter any source fit or donor decision.

## Exact model and completed original search

Reconstruct the native MT symbolic source from 132 intact original spool packets, four little-endian untempered words each, with the original existing p951 packet-index vector. Require source-equation rank **15,365**. For every native stage pair `t,t+227` in the symbolic range -1100..1040, consider both native and tempered 32-bit word presentations. Retain a pair when each individual word has no more than 12 source-fixed bits while their combined 64-bit system has **at least 24 independent source-fixed linear parity equations**. This yields exactly **286 source-constrained models** (143 per view).

Read all original evidence files except the encrypted PDF and, for candidate search, omit the printer spool entirely. Scan consecutive eightbyte fragments of every remaining source byte stream and every decoded 16-or-longer hex run. Suppress fragments made from two **identical fourbyte halves**, because the paired-state constraint family has many almost-pure equality equations and these trivial repeated fields create misleading timestamp/text matches. Candidate byte presentations: little/big endian, and either bytes interpreted directly as 32-bit outputs or inverse-MT-tempered first.

| Original-source quantity | Measured |
|---|---:|
| Distinct eightbyte source fragments with unequal fourbyte halves | **34,717** |
| Four presentation views per fragment | **138,868** |
| Source-constrained native/tempered stage pairs | **286** |
| **Complete 64-bit source-syndrome comparisons** | **39,716,248** |
| Compatible nonrepeating pairs | **0** |

The 286 models have between 29 and 35 independent source-fixed equations; many are dominated by `word_a XOR word_b = 0`, so the search **does not treat identical halves as a discovered hidden state witness**. Only nineteen models have fewer than 24 explicit zero-equality halfword-pair constraints in their derived elimination basis. The no-match conclusion applies to the exact defined nonrepeating consecutive-eightbyte carrier geometry.

A separate **synthetic exact-syndrome positive** constructs a nonrepeating 64-bit pair satisfying the same source equations for original stage -1099, tempered view, and a deliberate one-bit mutation fails the original equations. This verifies the code's candidate/parity reduction, without presenting a synthetic candidate as an original witness.

## Interpretation and next source requirement

This search found no new physically preserved original pair that can constrain the selected K04 fourword gap. Its null is **not** evidence that any original source record was the physical printer's actual generator output: the p951 chronology is still conditional, and nonconsecutive source values, encrypted/missing media, and other generators are outside scope.

The major practical lesson is that the abundant 227-step pair parity relations can be **nearly value-free**: a source equation allowing only repeated source words is not a viable physical coupon reconstruction by itself. Search effort should prioritize an independently indexed **original post-target MT donor**, a source-authenticated manufacturer state/coupon mapping, or the original physical printer medium, rather than increasing combinations of arbitrary natural-language or timestamp-shaped raw windows.

Original source, acceptance, canonical candidate and verifier were not edited. Genuine REC8 status remains K01/K02/K03/K05/K06/K07 individually PASS, **K04 and K08 MISSING**, combined INCOMPLETE.

**Reproducer:** [source-pinned standalone original-export SFT](../agents/agent33/h17_mt_nonrepeating_pair_source_sft.py). Invoke from repo root with Python 3; optional first argument is the folder containing `evidence/` when using the separately supplied unchanged ZIP export. No third-party packages.

### Reproducer correction (9 November, 06:58 UTC)

A self-review found that the first committed SFT accidentally discarded original measurement bits when inserting source equations into its GF(2) basis. It retained the same coefficient rank but incorrectly treated the reduced right-hand sides as zero, so its initial zero-match run was **invalid for the genuine source values**. The SFT was corrected to XOR the reduced source RHS with each original observed bit, and a new control checks 20 complete original fourbyte source words, including nonzero bits, against the fully reduced basis.

The corrected original-source SFT was **rerun end to end** on the unchanged supplied export, completing all 39,716,248 parity comparisons in 17.373 seconds with **zero exact matches**, and passed the nonrepeating planted pair/one-bit negative. The corrected synthetic stage -1099 pair is `7f3ce135635050ae`, differing from the earlier invalid control because the actual source RHS is now retained. All source counts, pair selection, zero genuine matches, and substantive conclusion survive the correction. This correction is mandatory context for anyone using the earlier Git history.

### Target-directed quotient extension (9 November, 07:04 UTC)

The original 286 screened 227-step stage pairs, individually and **all combined**, have **zero intersection with the 128-dimensional K04 target quotient**, relative to the 132 intact printer packet equations. They add 2,886 independent native MT-state dimensions, yet zero of the selected stage951..954 bits. Thus even a genuine matching source for all 286 original pair stages would have yielded **0/128 selected target bits** under this provisional p951 chronology. This is a stronger practical exclusion of the earlier search geometry.

Extend the exact symbolic MT state to stage1806 and calculate target quotient overlap for all `t,t+227` with t=700..1578. **Only nine** target-bearing stages also provide at least 24 independently source-predicted parity constraints: `952,953,954,1179,1180,1181,1351,1406,1578`. These can constrain between 1 and 32 selected K04 bits for a genuine value, but none has a surviving consecutive eightbyte nonrepeating source witness under the same four field presentations. Test **9 × 138,868 = 1,249,812** additional complete source-syndrome assignments: **zero original matches**.

The corrected runnable SFT now contains both the original 286-pair screen and this target-quotient extension, retaining original physical coupon and commitment exclusion. The resulting distinction is operational: a future donor search should first prove **nonzero selected quotient overlap**, then test original fields. A model that merely fits generator equations without target rank gain cannot reconstruct K04. All original target bits and K08 words remain unrecovered.
