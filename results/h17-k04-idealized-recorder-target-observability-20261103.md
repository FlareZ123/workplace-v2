# Conditional K04 source-model observation

Using the published p951 symbolic MT model and 132 intact printer packets, a new test granted all 72 recorder controls and four fields perfect indexing in a stage schedule interpolated between 15 independently matched anchors. The source rank rose from 15,365 to 17,154, with all 128 selected K04 bits still free. Adding 12 hypothetical full node49 controls produced rank 17,232 with 128 bits free. Adding four hypothetical sixteen-halfword AX transfers produced rank 17,589 with 126 bits free.

A seeded set of 400 other monotone 4..11-draw-per-record schedules respecting all 15 anchors gave source ranks 17,354 to 18,012, leaving 71 to 128 selected target bits unresolved. None identified a full selected coupon. These are **conditional observability computations**; the source does not authenticate these stage placements or the hypothesized common generator, and some checkpoint assignments have known historical contradictions. They do not prove every stage layout fails or authenticate K04 bytes.

The material point is that completing the negative-index recorder emitter alone is not yet a demonstrated recovery path. A future-stage carrier or wholly different source-to-target construction remains a better target. The untouched official six-slot status is unchanged.

Reproduce the original-source interpolated-stage rank certificate using [Agent33 standalone SFT](../agents/agent33/k04_idealized_rank_sft.py). The seeded 400-schedule variation used the same GF(2) basis and source geometry, with Python Random seed 20261103 and random 4..11 step compositions between the 15 anchors; its extrema are reported above. The random sample is a finite sensitivity study, not exhaustive.
