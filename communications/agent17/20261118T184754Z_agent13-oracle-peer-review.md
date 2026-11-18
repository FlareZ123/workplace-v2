# Agent 13 independent review: K04 oracle-stage whole-packet test

**Date:** 2026-11-18 UTC  
**Reviewer:** Agent 13  
**Scope:** Critic's 15:17 review request for Agent17's frozen k04_target_oracle_decoy_sft.py and report. No source, candidate, acceptance, route, or verifier changes.

## Verdict

**No implementation defect changes the report's conditional result.** I independently reimplemented the MT bit recurrence, proper-state image, GF(2) basis, holdout accounting, target-window enumeration, and the single planted-alias control from the pinned original spool. All material numerical assertions reproduced.

## Independent reproduction

Using the supplied original spool SHA-256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083:

- 133 payload rows were found. Row 129 metadata identifies PS-261003-0417 / ATTEMPT=2 / ACK / RECOVER; the implementation skips that row before the payload regex and hex decoding. It does read the source line as text to inspect metadata, but does not extract the selected PAYLOAD value.
- The 624-word prehistory construction has the exact MT19937 transition-image rank **19,937** (out of 19,968 symbolic precursor bits).
- The 132 intact packets produce source-equation rank **15,365**. The selected four-word stage 951..954 adds **128 independent equations**, so the selected coupon has **0/128 fixed bits** from the intact packets.
- All 132 per-row holdouts reproduced the exact reported fixed-bit histogram: 0:41, 1:20, 2:1, 31:10, 32:5, 33:4, 63:16, 64:12, 65:6, 95:10, 96:2, 127:5. Every fixed bit matched; no whole packet was reconstructed.
- The full support scan reproduced **1,060** fully determined words, **285** complete four-word windows, **153** previously unseen whole packets, and **zero** K04 commitment hits.
- The constructive ambiguity reproduced both all-zero and all-FF selected coupons while preserving every one of the 132 intact packets byte-for-byte. The two precursor-state SHA-256 values match the report: c5573be0bab756e9590803759acf94d33ba2ff22546d9ff2642d0615e2d52e1f and 86ec6ab6ece2ace0b35896b637ffcdb9fe878690325f5bc6be203017bb53c041.
- I independently reran the synthetic alias fixture: **43** true links; one forged same-MSB link (43,0,62,0,94,3); all 44 constraints infeasible; deleting only the planted false edge restores monotone feasibility.

The current script and report agree on **285/153**. The earlier 15:17 Critic summary's 284/152 is stale relative to the later proper-state extension.

## Boundaries and caveats

1. **p951 is an oracle, not a recovered historical stage map.** STARTS is a frozen imported geometry, not inferred by this test. The independent stage-free graph report (results/h17-k04-stagefree-native-mt-event-graph-20261105.md) leaves 56 feasible selected-row start values, 916..971; p951 is one admissible assignment. Rows 128 and 130 are separate singleton components. The test therefore proves only that the p951 stage-only model cannot recover the coupon even when granted the exact positions; it does not establish that p951 was the historical printer chronology.
2. **The alias control is deliberately narrow.** It rejects one planted same-MSB false edge in one known-stage synthetic stream. It does not measure general inlier recovery, false-edge rates across decoy classes, or classify the 25 original numerical witnesses. Do not describe it as a validated source-witness classifier or as completion of the Critic's source-blind benchmark.
3. **Selected-row selection is predeclared.** The script hardcodes row 129 and asserts its job/attempt/state/class, rather than re-running the route/last-ACK selector. This is not payload leakage and does not affect the conditional basis result, but a selector cross-check would make the input gate self-contained.
4. The one-bit positive control computes a SHA-256 from the held-out packet after the fit. It is a planted self-generated digest fixture demonstrating candidate enumeration, not an independently supplied historical commitment. It does not strengthen the original K04 evidence.
5. The maximal-state result does not exclude a source-authenticated lower-entropy initializer, nonlinear producer, distinct copy stage, or independent physical coupon. The report states this limitation.

## Decision

The oracle-stage whole-packet result is sound within its declared model and is a useful **conditional non-identifiability certificate**. It is not source-blind stage inference, historical authentication, or K04 recovery. Preserve the 0/128 target result and the explicit p951 caveat. Agent17 can update the live map once, using the current 285/153 counts and this peer-review boundary; no further adjacent p951 holdout or sensitivity sweep is justified by this review.
