# K04: complete 33-bit affine coupon reconstruction from two late copied-ACK MT stages

**Agent38, 3 November 2026, completed original-target computation.** Under the specified hypothetical common MT19937 printer chronology, reinterpret the *unverified selected ACK2 copied buffer* as a later native output quartet at stage 1178 or 1405, rather than its historical p951 stage. Both placements are linearly consistent with the 132 retained other spool packets. Each fixes 95 individual target native bits and yields an exact **33-dimensional affine space** for the physical selected K04 component. **Both entire 2^33 candidate spaces have been exhausted against the original K04 commitment; zero matches in 17,179,869,184 full SHA256 checks.** Six official slots stay PASS, K04/K08 MISSING, combined INCOMPLETE.

## Source roles and provenance constraint

The source-first symbolic test uses original `evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected historical route is ESC-N, job `PS-261003-0417`, attempt2 ACK RECOVER at 18:02 UTC, copied `P=A9A9DC5731A5E2AE879C47215C2559D5`, route mask `M=8556C8CB6140A7F9A5123AC7571BEE1C`. Original K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The **p951 common-MT stream model is analytic, historically unconfirmed**. We use Agent49's exact p951 GF(2) source symbolization, fit **all 132 original unselected spool rows**, explicitly withholding selected row129 before accessing its bytes. This gives rank **15,365** over unconstrained initial-state variables and leaves all 128 native selected bits free. Introduce 128 additional equations claiming copied P was physically produced at stage 1178 (=951+227) or 1405 (=951+454). In each case, all equations are compatible and rank increases to **15,493**. The two stages surfaced in a speculative initial stage-displacement screen because they carry 95 independently fixed target bits under the *same* assumed MT chronology. Neither stage has an original spool route, job number or authentic copier chronology proving that it was where the selected ACK2 was produced. This is a deliberately **post-selected model exploration**.

## Full affine construction and correctness

For each stage, reduce the 128 target native bit vectors against the source-plus-copy row-echelon GF(2) basis. Collect their residual free-variable forms. The target residual image has **rank exactly 33**, with a 33-independent-generator set; 95 individual target native bits have zero residual. For each generated native target quaternion, apply the standard MT tempering, serialize four 32-bit words as little-endian copied payload, XOR original M, then compare SHA256 of the resulting 16-byte complete K04 component.

The source-derived baseline components are:
- Stage **1178**: `820D12B8963277724971459D09D2C57B`.
- Stage **1405**: `36599B5016311A82EE508B57B54AD73C`.

Both spaces have **the same 33 linearly independent 16-byte XOR deltas**, touching only the first eight component bytes; their fixed last eight bytes differ, so the two sets are **disjoint**, giving exactly 2 × 2^33 globally distinct complete component values. The source derivation is reproducible by the [standalone Python source SFT](../agents/agent38/k04_copied_ack_late_affine_sft.py), building on [Agent49's exact source basis](../agents/agent49/k04_p951_symbolic_basis.py). It verifies **all 132 original intact source packet bytes** and hypothetical late-copy bytes against an explicitly constructed consistent full MT internal state; it also changes 11 original-state free variables to check regenerated selected target packets match the affine map. Finally it checks all 33 generators' independent rank. The source SFT never reads the K04 acceptance hash, so candidate data are built without target feedback.

## Exhaustive target execution

The [C11 OpenSSL/OpenMP verifier](../agents/agent38/k04_33bit_late_stage_sft.c) reads both generated affine data files, independently enforces equal deltas and distinct fixed suffixes, and checks full original K04 SHA256 for both components at each of 2^33 Gray-coded states. A planted complete synthetic component is independently built at Gray-code index `0x123456789` for **each stage**. The verifier expects exactly one planted hit per stage in the containing shard and zero elsewhere; any mismatch or genuine original hit makes the job return nonzero.

[Manual-only Actions workflow](../.github/workflows/agent38-k04-late-copy-affine-manual.yml) recomputes **both** source affine data files from the unchanged repository originals in *each* job, then exhausts the interval `[shard×2^29, (shard+1)×2^29)` with 16 disjoint shards, no gaps or overlaps.

**[Completed run 41738907033](https://github.com/FlareZ123/workplace-v2/actions/runs/41738907033)**, 3 November 2026, 23:24–23:28 UTC: **16/16 jobs success, all 17,179,869,184 original-target candidate hashes negative.** Examined shard9 log: `states=536870912 complete_hashes=1073741824 K04_stage1178=0 K04_stage1405=0 synthetic1178=1 synthetic1405=1 expect_each=1`. Other 15 jobs succeeded under the same explicit original-versus-synthetic assertions.

## Historical calibration and next action

An independent source-only role-mate check provisionally excludes **both** ACK2 rows (selected row129 and 18:25 row132) from the p951 source fit (new base rank **15,300**), then reintroduces both copied ACK2 values at a common +227 or +454 generator-stage displacement. **Both same-offset assignments contradict** the surviving 131 other packet equations; assigning different +227/+454 offsets to the two rows also contradicts. Restoring intact 0420 row132 to normal stage p963 remains compatible with the single-selected displacement, illustrating the weaker **selected-only anomaly** assumption that the exhaustive model used. This is conditional on the p951 model, not a refutation of actual physical printer copying.

The exact 33-bit affine cosets are **now closed**. Their 17.18b negatives exclude this bounded speculative delayed-ACK source mechanism without certifying a selected physical byte. The role-mate check weakens a generic attempt2-shared-delay causal explanation. No genuine recovered K04 or K08 value has been produced; prioritize an independently authenticated physical selected ACK2, separate original medium, or direct keeper-final caption witness over multiplying post hoc generator stages.
