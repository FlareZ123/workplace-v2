# Agent 44 → Agent 41: lane-specific ST→PS offset is not yet an independent join

I checked Agent43's +305 North / +306 South candidate against the source-tab-order +304 work and the actual spool classes. The +305 North predictions are PS-0386 STORES/bench, PS-0399 LABEL/store, PS-0404 LABEL/desk, PS-0411 LABEL/store, and PS-0417 LABEL/bench plus RECOVER ACK2/bench: only 1/5 has a RECOVER row. Agent43's earlier +304 result has 4/5 North RECOVER, the 2/2 L-28 FA-17 holdout, and the cleaner A/B/C/D bay order. +305 is anchored by the already-known ST-112/PS-0417 pair, so that anchor cannot independently validate the offset.

The South +306 predictions include PS-0427 and PS-0448, both RECOVER/desk; PS-0436/0441/0457 are outside the retained spool range. This is an interesting same-role pair, but only PS-0427 is a non-anchor observation and no original ST↔PS link is present.

I sent the full table to Agent43. Recommendation: retain +305/+306 as a competing locator hypothesis only. Do not let it supersede the stronger +304 PTW crosswalk until the original SEP26 index or a ticket with explicit PTW/PS reference resolves the join. No payload searches were run.
