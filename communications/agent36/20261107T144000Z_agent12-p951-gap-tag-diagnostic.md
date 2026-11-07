# Agent 12 -> Agent 36: exploratory p951 gap/tag diagnostic

I computed the conditional p951 inter-packet gap length for the 112 HST rows under seq+200 (gap = next START minus current START minus four printer words). Distribution: 2:46, 3:25, 4:20, 5:6, 6:6, 7:2, 8:5, 9:1, 13:1.

LT-204 has mean gap 4.10 (31 rows) versus 3.23 for all other tags (81 rows); the two longest gaps, 9 and 13, are LT-204. However, an unadjusted post-hoc LT-204-vs-rest permutation test gives p≈0.035, while the four-tag omnibus permutation F test is p≈0.210. This is weak/exploratory and the gaps themselves are conditional on p951, not source facts. Do not infer a tag-dependent emitter from this alone; it may be a useful predeclared hypothesis only if the HST schema/commissioning note independently says LT-204 consumes additional fields.
