# K04: source-selective four-field recorder order survives metadata-label shuffles

**Agent 2 | 3 November 2026 ~21:36 UTC.** This is a *new independent source-model signal* under a provisional MT19937 printer/recorder chronology. It **does not recover** K04, K08 or a seventh accepted component. Original six PASS; K04/K08 missing; combined INCOMPLETE.

## Distinct hypothesis and mechanistic reason

Prior Agent47 recorder seq47 metadata screening and Agent2 exact joint-GF2 cut tested a *contiguous* EVENT→LATCH→CONTROL→AUX model with possible rejects. That geometry disfavored the sole parity-bearing seq47 CONTROL stage -523; 19 of 54 placed recorder rows had no matching accepted fields with LATCH *immediately* preceding CONTROL.

The new hypothesis instead allows **unknown additional native draws between source field readings**, while retaining a source-common shared MT state and an order of each row's four fields. This is a materially distinct producer architecture, potentially reflecting unexported internal data. The original evidence does not attest such draws. With free placements one risks making every order fit every record, so the contribution is a **pre-existing original source-label shuffle discriminator** rather than raw search volume.

Source: original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; recorder raw SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`, all original recorder CRCs valid. Fitted printer rank15365 from the **132 source printer rows excluding selected K04 ACK2**; provisionally placed 56 original node50 recorder CONTROL words give joint rank16663. No original K04 acceptance hash, missing coupon, component, route mask or K08 words enter fitting, selection or calibration.

## Frozen source-selected experiment

Use only **13 independently source-indexed interior anchor rows** `seq[9,12,13,14,24,25,41,43,44,45,61,63,64]` for producer-order selection. Original source-specified stage boundaries are adjacent CONTROL stage placements in the provisional 56-row chronology. Every candidate order of `E=EVENT, L=LATCH, C=CONTROL, A=AUX` (24 permutations) is enumerated.

For each anchor row, independently select strictly ordered native stages for the other three fields inside the neighbor CONTROL interval, allowing any number of unobserved outputs between accepted draws. Enforce **all** metadata highbits simultaneously in the exact source GF(2) model: EVENT source bit width6 code `event-1`; LATCH width3 code `latch`; AUX width13 code `aux-2000`. This accepted-code test is a *necessary* condition for an actual CPython `randrange` producer; it does not assert that skipped codes are genuine rejects.

The best of 24 orders is scored by number of the 13 source-indexed anchor records with at least one compatible full trio. The original metadata assignments yield **ELCA=12/13** (only original seq12 fails), with 416 raw accepted placements; next `LECA=11/13`, `LCAE=11/13`, `ECAL=10/13`. All 24 original counts and each matrix row degree are printed in the SFT.

## Two nested null controls and real executions

The new standalone [source-only SFT](../agents/agent2/k04_recorder_order_meta_permutation_sft.py) builds a 13×13 *binary compatibility matrix* for **each of 24 orders**, mapping source stage windows to every other anchor row's complete original `(event,latch,aux)` tuple. It shuffles metadata *triples* as blocks, leaving the source CONTROL stage windows, original source values, and the 24-order search fixed.

- Exact single-order **retrospective** permutation probability for frozen `ELCA`: `2,217,600 / 6,227,020,800 = 0.00035612535612535614` reach >=12 matches.
- **Post-selection corrected 24-order maximum:** across **20,000 seeded shuffled-label permutations**, exactly **13** give maximum matching anchor support at least the original **12**; conservative add-one Monte Carlo p estimate `14/20,001 = 0.0006999650`. Histograms: max24 support 7→104, 8→5,097, 9→10,865, 10→3,603, 11→318, 12→13.
- A direct zero-rejection four-field contiguous model had at most **7 of 15** original pre-indexed anchors under ELCA, illustrating why the new result depends on allowing intermediate native draws.

**Execution verified on unmodified repo source:** [GitHub Actions run 41723054478](https://github.com/FlareZ123/workplace-v2/actions/runs/41723054478), original source SHA checks, all source-required assertions, clean workflow/job conclusion. SFTs `agents/agent2/k04_recorder_all_order_accepted_anchors_sft.py` and `agents/agent2/k04_recorder_order_meta_permutation_sft.py`; source of original 24-order basic pilot `agents/agent2/k04_recorder_field_order_source_calibration_sft.py`.

## Direct selected-stage implications

Only after the 13-record source ranking selected `ELCA`, hold out **seq47** as the target-adjacent *source* test (its CONTROL is still in the provisional 56-row fitted basis), with four original source-compatible CONTROL positions:

| Seq47 native CONTROL | Exact compatible accepted field-stage triples |
| --- | ---: |
| -523 | 5 |
| -522 | 8 |
| -521 | 12 |
| -520 | 14 |

Thus the earlier conditional -523 parity stage is **no longer ruled out by a free-intermediate-draw ELCA model**, but it is far from independently selected. Multiple target-stage alternatives remain and each has 128 unconstrained target bits except -523's one conditional parity. No historical selected coupon bit is authenticated.

## Why this is a lead, not an accepted component

The producer's code and true number of hidden draws are **unknown**, as is whether the printer and recorder share the same MT state. The 56-row provisional CONTROL chronology is source-fitted and contains 41 non-anchor placements. The source-label null tests conditional compatibility against this chronology; they do not independently prove the chronology. The original source-preindexed anchor metadata was also used retrospectively to choose the field order (corrected by the 24-order shuffled-placebo comparison).

Next useful discrimination: freeze a *finite actual draw-consumption mechanism*, e.g. a constant number of internally discarded draws between LATCH and CONTROL and CPython `randrange` rejection inequalities, calibrated against the 13 source-indexed anchors before checking seq47. Accept only a model that predicts its heldout stage or supplies the actual 128-bit selected coupon. An arbitrary positive accepted code placement is weaker evidence than a full rejection-history witness.

The original resources, source ZIP, acceptance and verifier are unchanged.


## Exact rejection follow-up: the loose accepted-position signal narrows to a zero-hidden-draw writer

A newly executed and substantially stricter [fixed-hidden-gap SFT](../agents/agent2/k04_recorder_hidden_gap_reject_sft.py) tests one global hidden native-draw count `h=0..8` between accepted LATCH and CONTROL. Every row is allowed **0..3 actual CPython `randrange` rejected draws per EVENT, LATCH and AUX**, with exact conditional high6/high3/high13 *range* constraints enforced jointly over the same GF(2) source state. Fitted source **13 pre-indexed anchor** scores (and total exactly feasible histories) are:

| h | Anchors with a full exact rejection history | Total histories across 13 anchors |
| ---: | ---: | ---: |
| 0 | **11/13** | 142 |
| 1 | 4/13 | 74 |
| 2 | 3/13 | 57 |
| 3 | 6/13 | 78 |
| 4 | 4/13 | 43 |
| 5 | 1/13 | 6 |
| 6 | 1/13 | 12 |
| 7 | 2/13 | 7 |
| 8 | 0/13 | 0 |

The winning finite model is **h=0**; other hidden-gap lengths explain many fewer source-indexed records. This source-selected h=0 model gives original seq47 -523 and -522 **zero** exact rejection histories, while -521 gives three and -520 six. Thus the earlier tentative target-parity rescue by allowing an arbitrary four-word post-latch gap loses support under this finite mechanism. The h0 anchor misses are original seq12 and seq61; the model remains unable to explain every source anchor, and 0..3 per-field rejection limit leaves longer nonzero rejection chains outside tested scope. Source-selected h0 alone does not authenticate physical writer behavior or the selected K04 coupon.

[Execution: GitHub Actions run 41723556202](https://github.com/FlareZ123/workplace-v2/actions/runs/41723556202), job completed successfully, 13 anchor source rows, all 9 hidden-gap families, four seq47 stages. **No original key component or target byte recovered.** The source-only label-shuffle signal in the earlier section remains valid as a retrospective necessary-condition observation, while this follow-up exposes the absence of a universal constant hidden gap greater than zero.
