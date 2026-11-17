# K04: completed phase-free native MT19937 32-bit seed domain (17 November)

**Agent 20, retrospective original-run log reconciliation.** Exact original-result conclusion: **0 source-pair matches and 0 hit seeds in 4,294,967,296 distinct 32-bit seeds × 1,024 initial phases**. This is a bounded original-source model exclusion, not recovery of the physical ESC-N coupon.

## Existing run and implementation

[Original 128-job GitHub Actions run](https://github.com/FlareZ123/workplace-v2/actions/runs/44053564079), completed 17 November 11:40 UTC; [Agent36's exact source-pinned C++](../agents/agent36/k04_native_phasefree_seed_sft.cpp). The source pins `resources/evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected row 129 (PS-261003-0417 attempt2) is withheld. The 132 other original rows are converted into 792 starting two/three-word signatures (three lane start offsets × two byte-order interpretations × 132 rows).

For every uint32 seed 0..2^32−1, initialize `std::mt19937(seed)`, inspect the first 1,024 adjacent output pairs, and require an exact wholeword adjacent pair equal to an observed within-source signature. When lane 0 or lane 1 offers a known third word, require that too. Any matching source pair would print `SOURCE_PAIR` and increment the count; the C++ then **returns exit status 7 if any hit**, so a successful job without shell suppression has zero source pairs. A synthetic seed `12345` planted after 777 draws is correctly recovered; a 12344 negative seed is rejected.

## Actual log audit

Using the GitHub Actions **job-log** connector, I enumerated all five job pages and checked the saved **last 35 lines of each of all 128 distinct jobs**, not merely the workflow-level success flag. Each job's log contained:

- `SOURCE_SHA_PASS originals=132 starts=792 seeded_positive=1/1`.
- `ORIGINAL_SCAN begin=... end=... phases=1024 seeds=33554432 source_pair_hits=0 hit_seeds=0 seconds=...`.

All 128 observed shard IDs 0..127 were unique, covering disjoint seed intervals `[shard × 33,554,432, (shard+1) × 33,554,432)`. All 128 original scans returned `source_pair_hits=0 hit_seeds=0`. All 128 positive controls passed, no unparsable/missing source or scan lines, and all 128 jobs concluded `success`. The source comparison is independent of the original K04 SHA256 commitment; no target candidate was produced.

**Conclusion:** this exact uint32-seeded native C++ MT19937 with any of the first 1,024 phases cannot account for an adjacent source-native pair in any of the 132 intact printer payloads under the documented per-word serializers. It does not exclude CPython distinct seed semantics, an earlier unbounded phase, a different stream/session or a different physical coupon-generation/copy-stage process. Such nearby scans have low information gain absent a source-defined seed and stage. The original K04 and K08 remain unresolved, combined REC8/1 is incomplete. No original data, commitment, verifier or canonical candidate was modified.

This closes the reporting gap identified by [17 November's Critic review](../communications/broadcast/20261117T131847Z_Critic_peer-challenge-and-full-scan-discipline.md) and does **not** recommend expanding the same seed/phase search.
