# K04: node49 three-lane recorder stride and CRC-invalid original-control holdout

**Agent 10 | 3 November 2026 UTC | Independent reproduction and distinct CRC-invalid holdout protocol.** [Executable single-file test](../agents/agent10/k04_node49_crc_stride_sft.py). All acceptance commitments, selected 18:02 spool ACK, original evidence, candidate and verifier are unchanged. **No seventh PASS or independently authenticated selected K04 bit.**

## Provenance correction and specific different question

**Same-session prior art identified after this report was first committed:** [Agent50 had already published the underlying node49 three-cohort/four-latch lattice](h17-k04-node49-interleaved-cohort-latch-grid.md), including seven matching anchors, a different five-control 19-bit holdout, and exactly the same +128 rank/128-bit target quotient. The lattice, rank increment and general source-coupling inference **are not new discoveries of Agent10** and should be credited to Agent50. Agent10's separate experiment uses *six CRC-valid controls as placement anchors* and then evaluates the **two full 32-bit CRC-invalid seq901 and seq903 raw controls as withheld predictions**, with the competing control-field repair alternative explicitly rejected in the model. seq903's direct original printer relation was independently known from v1 Agent43. This is an alternative holdout/evidence-stage calibration of the same model, not 67 new target bits nor an independently authenticated producer. The tests were developed concurrently and do not constitute independent physical source corroboration.

## Question and construction

The source-pinned p951 hypothetical MT19937 printer model in [Agent49's basis](../agents/agent49/k04_p951_symbolic_basis.py) fixes a subset of native-state bits from **132 intact spool packets**, while excluding selected packet row129. Can the independently retained node49 recorder CONTROL words identify a structured *three-lane* ordering with source-predictive checks on the four CRC-invalid records?

Read the original 88-record TRP2 recorder binary, SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`, checking the original CRC32 of the first 20 bytes. All node49 seq200..203 and seq990..993 are CRC-valid. Original seq900..903 have the known common CRC syndrome `0x00000100`, previously diagnosed by [v1 Agent12](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-recorder-crc-syndrome.md). All sixteen CONTROL fields are read in original byte order and untempered as little-endian MT32 outputs.

Locate each **intact** CONTROL independently over MT native indices -1100..-2, requiring >=16 printer-fixed native bits matching. This discovers six *unique* positions:

| Intact CRC-valid CONTROL | Native position | Printer-fixed matching bits |
| --- | ---: | ---: |
| seq990 | -322 | 32 |
| seq991 | -319 | 16 |
| seq992 | -316 | 32 |
| seq993 | -313 | 31 |
| seq201 | -321 | 32 |
| seq203 | -315 | 32 |

These six positions are source-consistent with a proposed per-latch 3-step layout `seq200+latch → -324+3*latch`, `seq900+latch → -323+3*latch`, `seq990+latch → -322+3*latch`. The layout is **inferred post hoc from retained CRC-valid controls**, rather than an authenticated historical chronology. Importantly the four CRC-bad CONTROL values were not used to discover the positions.

## Four CRC-invalid heldouts and integrity alternatives

Freeze the six-anchor 3-step layout, then ask the unmodified *printer-only* model whether its fixed state bits agree with the original four invalid-CRC CONTROL values:

| Original CRC-invalid record | Predicted native position | Predicted bits agreeing with retained CONTROL |
| --- | ---: | ---: |
| seq900 | -323 | 2 / 2 |
| seq901 | -320 | **32 / 32**, retained `BA194782` |
| seq902 | -317 | 1 / 1 |
| seq903 | -314 | **32 / 32**, retained `F2595C84` |
| **Total** | | **67 / 67** |

The **seq903 full-word printer correspondence has previous source precedent** in [v1 Agent43's CRC-layer study](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-trp2-crc-single-bit-syndrome.md). This test's narrower incremental *validation protocol* is to freeze a six-**CRC-valid**-anchor layout and treat both **seq901 and seq903** CRC-invalid fullwords as heldouts, then discriminate v1 Agent43's competing CRC-repair layer. Agent50's earlier original lattice is the substantive structural antecedent. The 67 matches should not be interpreted as 67 independent random bits: p951 state recurrence and the retrospective index selection affect the statistical model. Explicit assessment of look-elsewhere and historical producer provenance remains open.

The alternative v1 Agent43 repaired-CONTROL hypothesis changes each damaged record's CONTROL by bytewise XOR `3F9B320D`, leaving the CRC stored. At the fully fixed seq901 and seq903 positions that alternative disagrees with printer-fixed native state at **14 of 32 bits** in each case. Thus **within this speculative shared-printer architecture**, the preserved original CONTROL bytes are better supported than those proposed control-field repairs. The four original CRCs remain invalid; K05 must continue to exclude them. Neither the model nor the checksum syndrome authenticates source integrity absolutely.

## Model consequences and limits

Insert the twelve original seq200/900/990 words at the per-latch positions into the 15,365-rank printer basis. They cause **no GF(2) contradiction** and increase rank to **15,493**, adding **128** independent *conditional source-state* constraints. Projecting onto the four withheld selected row129 native words at positions 951..954 still leaves **128 / 128 unconstrained selected coupon bits**, both before and after. No exact K04 payload is generated.

The different CRC-valid-anchor / CRC-invalid-heldout partition adds an integrity-stage comparison to the same node49 lattice investigated by Agent50; it is separate from K04 arbitrary ACK corruption repair and uses the prior CRC syndrome and seq903 direct printer fingerprint. It tests a **record-index structure derived from untouched controls**, and independently predicts a second, previously CRC-rejected full CONTROL. It does not establish a historical common RNG producer, a global recorder stage order, copied printer coupon integrity, or even a complete source-labelled index map. The K04 selected-event causal bridge remains absent. K08 was not touched.

## Reproduce and next discriminant

Run [the portable source-pinned SFT](../agents/agent10/k04_node49_crc_stride_sft.py) from the repository root, with the existing Agent49 basis. It recomputes the source-only 132-packet printer equations, checks each six-anchor unique index, tests four heldouts and the repaired-CONTROL alternative, then verifies the exact joint GF(2) rank and selected-target quotient. It reads no acceptance digest, K04 mask, K08 text or selected ACK bytes. Synthetic controls for the symbolic MT operations are documented in Agent49's antecedent work.

**Next highest-value test:** Use the record's source-labelled per-latch group identity to predict an *additional intact* node49 control without searching for its index by the heldout value, preferably across a distinct sequence family or a field emission boundary. Assess whether any indexing rule reaches a genuine selected-target ancestry window. Without that target reach, the new source-state constraints are valuable for discriminating producer models but do not recover the coupon.

**Archive status:** K01,K02,K03,K05,K06,K07 accepted previously; K04 and K08 missing, combined INCOMPLETE.
