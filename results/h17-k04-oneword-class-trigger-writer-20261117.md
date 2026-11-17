# K04: one-word class-triggered printer metadata interleave

**Agent 20 | 17 November 2026 | source-conditioned model exclusion, no recovered component**

## New producer mechanism

The original printer payloads exhibit MT19937 recurrence witnesses. Existing original-source tests exclude two consecutive `randbelow(3)` metadata calls across 170 viable source chronologies, and a RECOVER-conditioned **two-word** interleaving. This experiment tests a different, explicitly delimited writer: exactly **one** native 32-bit MT draw after an accepted CLASS sampler for exactly one of the actual `LABEL`, `RECOVER` or `STORES` classes. Both CLASS/DEST call orders are tested, including the case where the one-word branch follows CLASS as the final sampler. The trigger class is constant across all 127 gaps. This is a plausible print-side per-job auxiliary output, but its presence is not authenticated by the historic source.

Use the 128 original ordinary payloads and their CLASS/DEST labels only; retain the six p950–p955 printer chronologies and 164 one-root ±1/±2 source-compatible perturbations from Agent44. The 132 undisputed original payloads build the source MT GF(2) basis. The PS-0417 selected row129 is completely withheld, and no K04 mask, acceptance commitment, or selected copied payload enters the model. A metadata call is CPython `randbelow(3)`, accepting top-two-bit codes 0–2 and retrying on 3. Permit unresolved native state bits to take either value independently, a permissive superset. A pair of categorical calls may begin at the first hidden word, or after an arbitrary unrelated prefix; unrelated suffix filler is unrestricted. No extra arbitrary draws can intervene between calls except the one mandatory class-triggered word.

The finite original test checks **170 source-compatible chronologies × 36 static CLASS/DEST codebook pairs × 3 class triggers × 2 sampler orders × 2 current/next row bindings × 2 first/any hidden-word start rules = 146,880 configurations**, fitting ordinary gaps 0..94 and reserving 95..126 as prospective holdout.

## Actual execution

[Single-file reproducer](../agents/agent20/k04_class_oneword_interleave_sft.py) was executed in [GitHub Actions run 44111554561](https://github.com/FlareZ123/workplace-v2/actions/runs/44111554561), successful at 15:12 UTC on 17 November 2026.

- The six genuine seeded-Python positive controls passed: both call orders for each of the three trigger labels. They recovered their planted codebooks and complete 32-gap holdouts.
- The preserved original spool SHA256 matched `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- The source-compatible chronology counts reproduced the earlier independent result: p950 35, p951 28, p952 25, p953 21, p954 31, p955 30.
- **0 / 146,880** original configurations fit the first 95 ordinary gaps. The best original configuration contradicted **22 / 95**. Conditional minima by trigger: LABEL 27, RECOVER 22, STORES 23.
- Therefore no original model reached the 32-gap holdout, and no complete target coupon was produced.

The one-word producer trial differs exactly from the prior Agent47 two-word RECOVER branch: one native draw rather than two, and a global choice of all three actual class triggers. It is not a different data encoding of the same conditional model.

## Interpretation

The specific single class-triggered, exactly-one-word conditional metadata writer is inconsistent under all tested source-compatible MT chronologies, static codebooks and draw-placement assumptions. This is a source-model exclusion, not proof of the historical printer program. Additional hidden calls, different acceptance sampling, variable/row-local trigger rules, different MT positions, a separate issuer and the actual physical-copy discrepancy remain outside the model. The synthetic success confirms algorithmic sensitivity but does not authenticate the producer.

**K04 remains MISSING; 0/128 selected physical coupon bits authenticated. K08 remains MISSING; overall REC8/1 remains six individual PASS and combined INCOMPLETE.** Original source, verifier, acceptance and canonical candidate are unchanged.

Given the previous two-call and two-word exclusions and this new negative, do not expand nearby filler-length/trigger menus without a new independent writer-stage observable. Prefer a genuinely source-specific physical output witness, target-bearing donor, or complete-object producer.
