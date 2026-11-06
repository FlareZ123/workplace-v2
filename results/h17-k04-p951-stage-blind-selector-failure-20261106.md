# K04: source-only full-coupon prediction fails when printer stage selector is withheld

**Agent 2 | 6 November 2026 | new stage-unknown whole-packet discrimination.** Six REC8/1 components PASS; K04/K08 remain MISSING and the combined acceptance remains INCOMPLETE. This is a historical-original producer falsifier, **not** an additional recovered component.

## New question after five two-coupon heldout results

Agent4's five intact original packet holdouts (rows 12, 41, 66, 95, 125) each admit precisely two complete 16-byte values under the p951 MT19937 source basis **when that packet's native stage is supplied in advance**. The stage map, however, was discovered retrospectively from the original packet corpus. The new question is whether source-only rank/whole-packet identifiability can **select an unseen packet's native stage**, rather than allowing the correct answer to enter through that supplied map.

## Experiment

The untouched spool, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, contains 133 payloads. Reuse Agent49's p951 native MT affine model and its stage chronology. For each of **127 interior ordinary packet rows, 1..127**:

1. Withhold the complete chosen packet bytes and its native start stage from source fitting. Exclude disputed K04 row129 entirely. Build the GF(2) basis using the other 131 intact original packet values at their *conditional* stage starts.
2. Holding both neighboring starts fixed, permit every fourword start in the interval `previous_start+4 .. next_start-4`. Evaluate additional independent native bits (the logarithm base 2 of the number of possible complete 128-bit outputs) for each stage.
3. Choose stages minimizing the number of unknown native bits **without inspecting the withheld packet's value or correct start**. Only then compare the chosen stage set with its retrospective original stage, and compare any rank-zero full predictions against its original 16 bytes.

The source rank minimization is an *exploratory proposed selector*, not a historical printer rule. The fixed neighboring stages themselves are conditional retrospective assignments. The heldout target's actual stage is used only for evaluation after predictions.

## Executed source observations

| Criterion | Result |
| --- | ---: |
| Complete historical original withheld rows | 127 |
| Correct original start belongs to minimum-rank stage set | **26/127** |
| Correct original start is unique minimum-rank stage | **5/127** |
| Rows with a zero-free-bit alternate stage | **6** |
| Rows with rank-zero stage predictions actually equal to the withheld original whole packet | **0/6** |
| Selected K04 ACK2 source bits newly fixed | **0/128** |

The six false rank-zero rows are **44, 92, 93, 94, 95, 96**. For a particularly concrete control, withheld row95's retrospective stage is **710** and actual intact coupon is `9FB4B4D9CF1B2E598792CFFC58188B24`; the rank-minimizing alternative **stage711** is **128/128 fixed**, predicting `CF1B2E598792CFFC58188B249DD6C0AF`. It is an exact computable *wrong* packet. Row44 similarly selects stage333 in place of historical stage335 and produces a wrong full candidate `DFA270E6B852C62261EFD6108987EABC`. These failures cannot be rescued by generating more seeds at the wrong stage.

The five previously reported one-bit withheld rows also become stage-ambiguous when their stage is withheld, with 5–13 feasible local starts: stage95 (row12), 307 (row41), 491 (row66), 710 (row95), and 930 (row125) are only one option apiece. This does not invalidate the earlier *known-stage conditional rank calculations*; it identifies the missing selection condition needed before they become independently predictive printer experiments.

An additional exploratory **CLASS-conditioned interval-gap model** was frozen with Laplace smoothing and evaluated on 126 leave-one-stage-out rows. It attained 55 uniquely correct stages and log loss 151.35. In 2,000 frequency-preserving class-label permutations, the observed unique-accuracy tail was **p=0.115** and log-loss tail **p=0.244**. This particular metadata route supplies no convincing out-of-sample stage selector; the pilot is intentionally not presented as a new K04 key hypothesis. A separate class/destination-to-hidden-MT rejection-sampler family was **already** addressed in Agent26's earlier work and is not duplicated here.

## Reproduction, limits, and next intervention

[Read-only source-pinned SFT](../agents/agent2/k04_p951_stage_selector_rank_holdout_sft.py) imports the existing [p951 basis](../agents/agent49/k04_p951_symbolic_basis.py), never fits row129, and asserts the five decisive counts. The source analysis was independently executed on the uploaded original spool with equivalent native linear algebra. No acceptance hash, routing mask, accepted slot, or original source file was modified. This report evaluates a **chosen identifiability selector** on an already inferred stage chronology; it is not an exclusion of every possible source-only or metadata-supported stage-selection rule.

**Research decision:** before claiming a new whole-packet producer, require it to predict an intact *complete original packet and stage selector* while its original bytes and start remain withheld. A zero-free-bit native value at an unselected stage is a convincing-looking false-positive artifact. The selected ACK2 row129 still has stage951 and 128 unrestricted native bits under the p951 source-only fit. A genuinely independently linked copier/selection signal or alternative historical producer is necessary to reach selected physical K04; source-only rank minimization does not do so.
