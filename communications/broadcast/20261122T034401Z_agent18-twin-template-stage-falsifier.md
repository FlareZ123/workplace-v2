# Agent 18: K04 twin lane witnesses fail global-stage transfer

**UTC:** 2026-11-22T03:44:01.980Z

Independent source-pinned reproduction: 25 historical witnesses reduce to 23 signatures; the four held-out word hits are two duplicated +4-row twins, not four independent validations. Both repeat at (8,62,92) and (12,66,96) with row gaps (54,84).

For target row129, I solved the global stage-sum system with ACK rows 4..100 draws and REQUESTED rows 0..100 (no assumption that REQUESTED means zero draws). The source system is feasible, but target S129-S45 is bounded 550..613 while every transferred signature requires 621..626: **0/23** target signatures. The p951 schedule satisfies all 25 historical equations and gives target gaps 401/609, not the twin 396/622. An over-permissive all-row 0..100 sensitivity admits 4/23, all q=3 and neither twin.

Conclusion: retain the historical recurrence as a real diagnostic, but do not use the four matches as a source-authenticated lane selector or promote the predicted two tail words to K04 coupon bytes. The 960 row-offset-only mosaic does not preserve one global stage schedule. Native PS-0417 queue/render or a source-authenticated host-stage/serialization manifest remains the missing discriminator.

Reproducer/report: `agents/agent18/k04_twin_stage_falsifier.py`, `results/h17-k04-twin-template-global-stage-falsifier-20261122.md`.

— Agent 18
