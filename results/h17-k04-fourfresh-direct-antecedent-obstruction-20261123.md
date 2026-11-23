# K04: exact one-step MT antecedent obstruction across all 4-fresh source-witness schedules

**Agent 22 | 23 November 2026 | Positive original-source chronology; direct whole-coupon producer excluded within precisely stated model.**

## Question

Could a source-compatible native MT19937 chronology with fresh four-word emission at **every** printer row use previously retained packets as the three inputs needed to calculate all four native words of the selected physical coupon at **PS-261003-0417 / RECOVER ACK attempt2**? This would produce a complete 16-byte coupon without trusting the selected copied ACK payload.

The exact standard recurrence is:

```text
X[t+624] = X[t+397] XOR twist(X[t], X[t+1])
```

For selected lane p at native stage T=S129+p, the needed native antecedents are T−624, T−623 and **T−227**. The third antecedent is particularly important: even possessing both earlier words leaves a 32-bit native word unknown without the third.

## Source evidence and finite calculation

Source: immutable `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected row129 `PAYLOAD` is **not decoded or used**. The 132 remaining packets are parsed into 528 native 32-bit words by exact MT untempering. The source-wide equality extractor reconstructs **25 complete MT witness triples and 17 source-firstword partial witnesses**, yielding **49 distinct stage difference equalities**. These are constraints among historical packet starts, with no assumed target bytes.

A *four-fresh* model sets every consecutive historical packet start difference to an integer **4 through 16**. Difference-bound propagation over the 133 packet starts and 49 exact equalities computes the rigorous minimum/maximum possible stage separation for **every** historical packet/target pair. Every putative source row and 32-bit lane is screened for coincidence with T−227 for each of the four selected lanes: **4 × 132 × 4 = 2,112** placements.

**Finding: zero of the 2,112 possible placements can coincide with T−227 under all these constraints.** The nearest placement is row97 lane0 to selected lane3. It would require `S129−S97=224`, while the complete difference-constraint system permits only `219..222` native-word draws. The minimum discrepancy is two draws. An independent screen for T−624 finds **exactly one** possible individual first-antecedent placement across all 2,112 source packet/lane pairings: selected lane0's T−624 coincides with retained **row43 lane3** only if `S129−S43=627`. The preserved four-fresh positive history **does** realize this stage alias and nevertheless leaves the complete selected coupon quotient at rank **128**, so this isolated source word provides zero determinate target bits. The necessary consecutive T−623 input and the required T−227 remain unavailable for a direct one-step reconstruction. Consequently no selected lane, and hence no complete coupon, is reachable through this *single-step direct-intact-word recurrence* model.

The graph constraints are demonstrably satisfiable: the preserved four-fresh source chronology (Agent10's ten gap deltas relative to Agent11's all-42 chronology) has gaps **4..13**, selected stage **955**, and satisfies **all 49 source-derived equalities**. A historical full-source GF(2) witness for that same chronology reproduces all 528 original observations with source rank15,434. Thus the obstruction is an actual antecedent-placement result within a feasible source model rather than an inconsistent model artifact.

## Reproducer and decision

[Read-only single-file original-source SFT](../agents/agent22/k04_mt_fourfresh_target_antecedent_sft.py) derives the exact original historical witness equalities; computes four-fresh all-pairs difference bounds with standard-library integer arithmetic; tests all 2,112 third-antecedent placements; asserts the nearest gap and a concrete four-fresh positive schedule. An independent source-pinned local version returned `25 full / 17 partial / 49 unique / 0 third antecedent / minimum gap 2` with exit code zero.

**Scope:** This is an exclusion only for a *one-step native MT recurrence from intact packet words*, **all 42 previously extracted witness relations**, and **every packet using ≥4 and ≤16 fresh outputs**. Missing generator outputs could be derived via multiple recurrences, a different schedule outside these gap bounds, or a different printing issuer. Native printers need not use MT at all. A future intact external donor, or producer/copy-stage rule spanning more than one MT step, is not screened.

No original selected coupon bits were identified; **zero whole-coupon candidates were emitted**, so K04 SHA256 remains **NOT_EVALUATED** for this specific experiment. K04 and K08 remain MISSING and combined REC8/1 INCOMPLETE. Original source, acceptance, route, verifier and canonical candidate are unchanged.

**Next target-facing work:** Treat an alleged MT-based coupon predictor as a true producer only when it crosses the full selected 128-bit source-nullspace by a specified multistep relation or independent donor. A new gap schedule alone cannot do that; prioritize source-authenticated media/copy links or a different complete-coupon construction.
