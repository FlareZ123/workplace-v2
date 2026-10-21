# H-17 archive recovery: work on the two missing components

**Acceptance status:** original REC8/1 verifies **K01, K02, K03, K05, K06, K07**. **K04 and K08 are missing; combined acceptance is INCOMPLETE.** Newly authenticated selected K04 payload bits: **0/128**. Newly attested exact K08 final caption words: **0**. Only eight individual PASS checks, combined PASS and `accepted=true` from the **unmodified** `resources/verify.py` establish full key recovery. Historical provenance must be reported separately from cryptographic acceptance.

## Where the two missing values would come from

- **K04:** the selected historical record is ESC-N / `PS-261003-0417` / `RECOVER` / attempt 2 / 2026-10-03 18:02 UTC. The surviving spool ACK payload is **not integrity-certified**; applying the recorded mask produces a value rejected by the original slot commitment. Look for an independent original coupon or authenticated copy, or a genuinely discriminating producer/copy-stage relationship **that reaches this specific attempt**, rather than another explanation of intact printer rows.
- **K08:** the target is Emily's **exact final H-17 keeper-margin caption**, distinct from the surviving drafts N02/N06 and earlier standby/commissioning labels N17/N18. The final words are unquoted in the supplied export. Look for a genuinely independent final-text/version witness or a source-supported selection/editing rule that identifies **the exact normalized words**. A thematic paraphrase cannot substitute for missing wording.

The original export was deliberately trimmed. The maintainer says recovery is solvable, but [whether this particular export is self-contained remains unanswered](https://github.com/FlareZ123/workplace-v2/issues/1#issuecomment-6297603819). Do not assume either sufficiency or impossibility. **Human source-intake route closed:** in a [21 October 2026 final reply](https://github.com/FlareZ123/workplace-v2/issues/1#issuecomment-6313937514), the maintainer explicitly said no missing records or archival referrals can be provided, no further human answers or assistance should be expected, and the objective remains unchanged. The [existing issue](https://github.com/FlareZ123/workplace-v2/issues/1) documents prior requests but supplies no authenticated coupon or final margin. Pursue independently accessible lawful original evidence and source-grounded target-constraining recovery mechanisms; do not duplicate human requests or infer access to protected systems. This is historical read-only records work, never facility operation.

## Research decision before a new cracking run

A **small, original-source-anchored discovery pilot is allowed even when the proposed mechanism is unproved**. Before computing, write briefly in your own working notes:

1. Which exact *previously underused original observation* is being tested, and which recent **v1 and v2** experiment is the closest mathematical superset or equivalent?
2. What physical producer, copy, encoding, revision or editorial-selection relation could carry information to **the selected K04 attempt** or **the final K08 words**?
3. What intact original observation will be **predicted blind**, without looking at the disputed target or its commitment?
4. How many missing bits/words would success conditionally constrain, what is the finite small stop budget, and what outcome stops the family?

Only escalate beyond that pilot when the held-out evidence actually discriminates the mechanism **and** its source-to-target edge warrants the cost. **Target-analogue transfer gate (21 Oct):** before scaling, test whether a model can blindly reconstruct a withheld *intact original from the same provenance class* as the missing target, or supply an independent documentary bridge explaining why routine-to-exceptional producer/copy or draft-to-final editing rules transfer. See [Critic's counterfactual recovery test](communications/broadcast/20261021T1811Z_Critic_target-analogue-transfer-gate.md). A routine-only prediction or draft grammar does not establish the actual selected missing value.

**Singular-target candidate exception (21 Oct):** A one-off damaged coupon or final-margin edit may have no intact same-class analogue. For a proposed **event-specific** deterministic repair or selection, a *small direct commitment check* is permissible without such a holdout **only** if at least two functionally independent contemporaneous original constraints fix a finite source-bounded candidate map for the **selected full K04 reducer input** or the **exact normalized K08 final words**. One constraint must specify the actual copy/edit operation; an anomaly plus a general warning or anecdote does not. Freeze the original lines, precise transformation, small candidate budget, nearest cross-repo logical equivalents and stop rule before testing; a miss closes that one map without expanding into adjacent variants. Shared producer/editorial laws still require blind target-analogue validation and a specific historical bridge. See [Critic's singular-exception threshold](communications/broadcast/20261021T211042Z_Critic_singular-exception-evidence-threshold.md) and [v1's initial exception rationale](https://github.com/FlareZ123/workplace-v1/blob/main/communications/broadcast/20261021T202231Z_Critic_singular-target-candidate-lane.md). No such exception is itself historical source proof or REC8 acceptance.

A generator/seed/corruption name, new caption wordlist, larger brute-force radius or a new algorithm on the **same** printer/metadata observations is rarely a new test. Many such families already failed; some apparent novelties were subsets of **same-day** tests. Inspect recent identity memories/commits as well as [v2's equivalence gate](results/h17-experiment-equivalence-gate.md) and [v1's original-observation collision index](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-prior-art-collision-index.md) **before** an expensive run.

**Avoid process-only output.** Ordinary stopped pilots belong compactly in identity memory; do not create predeclare/result commit pairs, standalone six-PASS or no-hit headlines, tiny-test CI jobs, or duplicate intake issues. Preserve any genuinely useful positive mechanism, independent target-bearing observation, reproducible proof or contradiction as a result. Allocate real discovery attention to K08's final-version problem as well as K04, without inventing phrases or speculative custody.

## Research and evidence map

- [Current slot status, evidence and verification](results/README.md)
- [Detailed six-slot recovery and K04/K08 source boundaries](results/h17-recovery-status.md)
- [Cross-repository prior-art equivalence and logical-subset gate](results/h17-experiment-equivalence-gate.md)
- [Intake requirements and offline witness validation](results/h17-original-witness-intake-gate.md)
- [Archived earlier v2 policy and Critic reasoning](README.policy-history-through-20261021.md)
- [Latest simplified v1 research guidance](https://github.com/FlareZ123/workplace-v1/blob/main/README.md)

**Maintainer rule:** do not create a GitHub Actions workflow triggered on every commit; it would exhaust the shared CI budget. The maintainer explicitly states that the problem is solvable. This repository is a shared research workplace and its design conventions may evolve.
