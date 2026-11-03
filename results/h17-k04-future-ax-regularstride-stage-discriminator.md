# K04 future AX checkpoint search: new stage coverage, no selected coupon recovery

**Agent 4, 3 November 2026. Original-source model test, conditional on the published p951 MT19937 producer geometry.** Six existing REC8 slots remain PASS; K04/K08 missing, combined incomplete.

## Hypothesis

The other three 16-checkpoint AX transfer chains might be delayed or regularly skipped samples from the printer's hypothetical common MT stream, including the **post-observation interval** where descendants of the selected K04 words could be exposed. Earlier AX-7781/82/83 checks tested consecutive alignments only within native stages -1100..1025. This new test extends the symbolic model to +1800 and examines per-checkpoint strides 1..8, with two original 16-value layouts and two 8-value attempt cohorts. It is deliberately not another copied-ACK or thematic-caption search.

## Evidence, computation and independent control

Original printer spool: `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The held-out selected row129 is **excluded** throughout. Original transfer checks: `resources/evidence/transfers/transfer-audit.jsonl`; all four transfers include exactly eight seq × two attempt checkpoint values.

Reproduce with [the source-only SFT](../agents/agent4/k04_future_ax_stage_sft.py), which imports the established [Agent49 exact symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py) and extends its MT recurrence. This makes the same source-only printer rank **15,365**. As an original-source positive control, existing AX-7778 sorted (seq,attempt) with byte-swapped 16-bit values at native stages -157..-142 agrees with **122/122** individually printer-fixed halfword bits. Imposing its 16 checkpoint halves raises joint rank to **15,495**, consistent with prior work. The target ACK remains excluded.

The expanded comparison scans AX-7781, AX-7782 and AX-7783 independently over the full **native -1100..1800 interval**, in either global byte order and the original-source orderings (seq,attempt), (attempt,seq), attempt1 only and attempt2 only, with each consecutive checkpoint separated by any fixed stride **1..8**. Each transfer receives **182,496 complete placements**; all three together **547,488**. An accepted alignment must agree with **at least 40 already source-fixed bit positions** and have zero contradictions. There are **zero** accepted alignments for any of the three transfers. Best disagreements are at least nine errors over 40+ source-fixed bits on this family. This excludes only the tested regular-stride same-stream interpretation; nonlinear transforms, independent generators and irregular sampling remain available.

## What future observations would buy

The p951 printer+AX7778 source state still leaves **128/128** original-selected coupon bits free. While scanning post-1040 stages, original source fixes zero upper-halfword bits at individual native stages 1179..1181, 1347..1348 and 1574..1575; hence a **hypothetical** placement of a transfer there cannot be selected through direct source agreement.

Nevertheless, rank analysis demonstrates that three 16-checkpoint blocks hypothetically placed at starts **(1179,1347,1574)** would add 325 independent joint-source equations and decrease selected coupon quotient rank from **128 to 16 bits**. This is a *conditional algebraic opportunity*, not an accepted stage assignment. The actual AX transfer checkpoints contradict the tested regular-stride alignments where source-fixed bits exist. The calculation must not be promoted into authentic recovered K04 bits, an authenticated producer timeline or K04 candidate.

## Implication

Future effort should target **an independently evidenced irregular transfer layout or alternative transform with a source-visible heldout prediction in the target-descendant stage**, rather than assume a sequential offset or increase hash-search radius. A complete payload still requires enough independent information to resolve the remaining target quotient and the physical ACK copy stage. No K08 final words were recovered.
