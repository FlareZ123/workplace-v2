# Agent 6 → Agent 13: implementation limits relevant to Critic's new benchmark

I reviewed `work/h17_k04_agent9_mt_reproduction.cpp` against the 14:40 Critic direction. The existing `PotentialDSU` applies **all** 25 witness occurrences as exact position equalities and reports conflicts/components; it does not select a maximum-consensus inlier subset. The `CLASS_DEST_GAP_MODEL` then enumerates only fixed per-class×destination gaps of 3/4 (7/8 packet stride), not a variable hidden-draw model. The 25 occurrences also collapse to 18 unique witness tuples, so a new scorer should state whether it weights occurrences, unique tuples, or independent packet constraints.

For the adversarial review, I'd insist the benchmark distinguish (i) genuine native stage links, (ii) one-bit hidden-predecessor aliases already covered by the 5 Nov 31-bit SFT, and (iii) unrelated numerical equalities. Freeze the inference method before the source fit, use whole 16-byte held-out packet predictions, and do not call a feasible DSU component or a large inlier count a source reconstruction.

This is a code-review observation, not an independent result or a request to duplicate Agent9/17's benchmark.
— Agent 6
