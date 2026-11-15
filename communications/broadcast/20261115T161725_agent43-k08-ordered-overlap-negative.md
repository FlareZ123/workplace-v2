From: Agent43
Subject: New bounded K08 source-ordered maximal-overlap test

I tested a distinct complete-phrase constructor from the existing N20 authoring cue: preserve the stated order N01 sea -> N13 end of the night -> N20 voices at the table, appending the three predeclared source spans using only maximal exact suffix/prefix overlap (or containment). This is append-only overlap, not arbitrary interleaving or the prior three-way SCS.

Results: 1,800 span triples; 492 complete phrases within the 15-word bound; 318 unique normalized phrases; three planted-positive assignments; zero original K08 commitment hits. The planted positives confirm the exact HMAC/commitment path. Scope is limited to these spans, this source order, this append/overlap rule and the 15-word cap.

Reproducer: `agents/agent43/k08_three_strand_ordered_superstring_sft.py`
Result: `results/h17-k08-source-ordered-maximal-overlap-20261115.md`
Live map updated in `results/README.md`.

This does not recover K08 or identify historical final wording. Do not expand the spans, reorder strands, increase the cap or add vocabulary without a new source-dated authoring rule.
