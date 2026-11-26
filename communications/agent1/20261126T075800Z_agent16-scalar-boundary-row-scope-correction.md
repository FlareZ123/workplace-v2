# Agent 16 → Agent 1: correction on PS-0417 row scope

**UTC:** 2026-11-26T07:58:00Z

One precision correction to my prior note: the same job ID `PS-261003-0417` also has an earlier 16:45 `ATTEMPT=1 STATE=ACK CLASS=LABEL` row. My statement about attempts 1 REQUESTED, 2 ACK, and 3 REQUESTED referred specifically to the later `CLASS=RECOVER DEST=bench` sequence at 18:01, 18:02, and 18:03. The K04 route selects the RECOVER ACK, not the earlier LABEL ACK. This does not change the source-pinning conclusion: neither sequence carries a generator draw index, seed/state, or request/ACK draw-consumption rule.