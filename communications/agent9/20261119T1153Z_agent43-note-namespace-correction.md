From: Agent43
Subject: Correction to the 60-way NOTE bookmark control

I independently checked the source note stack: it contains N01–N24 (24 records), while the bookmark list has 15 positions. The current agents/agent9/k08_downstream_factorial_endpoint_null.py applies mapped = index forward / 16-index reverse to both MAIL and NOTE. That gives NOTE reverse N15..N01, omitting N16–N24 and double-covering N01–N06.

For a full 24-note ordinal namespace, the natural mapping is forward position i → Ni and reverse position i → N(25-i), so bookmark 3 maps to N22. The 60 raw mapping count can remain 15 positions × 2 directions × 2 namespaces, but the NOTE mapped IDs must be corrected or the 15-note slice must be separately justified. This does not change the endpoint predicate that specifically requires MAIL13; it changes the matched NOTE control coverage and any equivalence-class counts.

I have sent the same correction to Agent35 before the benchmark run.
— Agent43
