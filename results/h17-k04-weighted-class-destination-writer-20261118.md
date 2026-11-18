# K04: weighted four-way CLASS plus three-way DEST MT writer has no source survivor

**Agent 13 | 18 November 2026 | original-source-only bounded negative**

## Question

The ordinary spool has a visibly nonuniform CLASS count (LABEL 52, STORES 41, RECOVER 35) while DEST is close to uniform. A concrete writer could therefore choose CLASS from a four-entry list containing one duplicated class and choose DEST from a three-entry list. Under CPython's `Random._randbelow_with_getrandbits`, the class choice consumes 3-bit draws until a value 0..3 is accepted, while the destination choice consumes 2-bit draws until 0..2 is accepted.

This is materially different from the previously tested pair of uniform three-way `randbelow(3)` calls. The selected PS-261003-0417 ACK2 row is withheld before source fitting, and no K04 mask, copied selected bytes, or K04 commitment participates in model selection.

## Executed source test

The reproducer is `agents/agent13/k04_weighted_class_dest_sampler_sft.py`.

It pins the original printer spool SHA-256:

`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`

and evaluates all 170 source-compatible members of the established six selected-stage / one-root-perturbation family:

- p950: 35
- p951: 28
- p952: 25
- p953: 21
- p954: 31
- p955: 30

For each chronology it tests all 36 onto assignments of four raw CLASS codes to the three observed class labels, all six DEST codebooks, all four current/next record bindings, and both call orders. The two sampler calls must account for the complete ordinary inter-payload gap. The first 95 gaps are training; the remaining 32 are untouched holdout. Synthetic mixed-sampler accept/reject controls pass.

GitHub Actions run `44396458374`, job `135127545795`, completed successfully on the committed SFT.

## Result

Across the complete bounded family:

- source-compatible chronologies: **170**
- first-95 training survivors: **0**
- best training mismatch count: **18 / 95**
- zero-error 32-gap holdout survivors: **0**
- even before assigning labels, the best chronology/order still has **8 / 95** training gaps in which the exact source-projected draw domains cannot realize the required two-call consumption pattern.

The selected row remains withheld and this experiment authenticates **0 K04 target bits**.

## Consequence

The attractive draw-rate explanation does not survive the original printer source: a four-entry weighted CLASS `choice` plus a three-entry DEST `choice`, consuming each full inter-packet gap, cannot be the historical writer anywhere in the tested 170-chronology family.

This does not exclude a different printer chronology, a non-CPython sampler, shared/reused outputs, extra source-defined fields, or a physical copy/render-stage mechanism. It supplies no selected coupon bytes. Further work should require a new source constraint on the selected physical/rendered stage or a complete source-defined object constructor rather than widening adjacent sampler parameterizations.
