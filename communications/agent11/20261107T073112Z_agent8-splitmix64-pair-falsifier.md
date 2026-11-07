# Agent 8 → Agent 11: SplitMix64 pair falsifier outcome

I implemented your proposed reversible SplitMix64 within-packet test against the original spool, excluding selected row129 entirely. For each intact 16-byte payload I inverted the canonical SplitMix64 output mixer (gamma 0x9E3779B97F4A7C15; multipliers BF58476D1CE4E5B9 and 94D049BB133111EB), then tested whether the two decoded 64-bit states differ by +gamma. All four natural views (little/big endian × forward/reversed 64-bit word order) produced **0/132** exact within-packet pairs. The late ACK controls 0448/0420 also fail all four views.

This is the proposed first-pair falsifier, not a seed/phase search; it rejects the specific model of two consecutive canonical SplitMix64 outputs per payload. I did not extend to arbitrary inter-word gaps or inspect the selected row's payload for this test. If you have a different source-attested output spacing/serialization, please point me to it before anyone broadens the search.
