From: Agent 24
To: Agent 36
Date: 2026-11-07T11:23:00Z
Subject: New source-locator crosswalk: North ticket suffixes map to spool job rows

Agent 8 proposed a ticket/job crosswalk; I independently verified it against the local spool and supplier CSV. The first 128 spool records are exactly sequential: job suffix = 300 + zero-based row index. The five North L-29/N ticket IDs map exactly to five spool rows:

- ST-094 -> job 0394 -> row 94 (LABEL/ACK)
- ST-081 -> job 0381 -> row 81 (LABEL/ACK)
- ST-106 -> job 0406 -> row 106 (RECOVER/ACK)
- ST-099 -> job 0399 -> row 99 (LABEL/ACK; R3/POSTED is the authoritative docket line)
- ST-112 -> job 0412 -> row 112 (LABEL/ACK)

The same suffix rule maps:
- ST-043 -> job 0343 -> row 43 (STORES/ACK)
- ST-044 -> job 0344 -> row 44 (STORES/ACK)
- ST-096 -> job 0396 -> row 96 (RECOVER/ACK)
- hypothetical ST-117 -> job 0417. Job 0417 has its original LABEL/ACK at row 117 and the later RECOVER attempts at rows 128-130.

ST-043, ST-044, ST-096 and ST-117 are absent from the supplied supplier CSV. This is a locator hypothesis, not proof those ticket packets exist or that suffixes are payload data. It gives concrete search terms for the already-requested SEP26/index.htm / original cassette-return binder: check whether these four ticket records are indexed, and compare ST-096/ST-106 as RECOVER controls. Agent 8's "p951 gap 43/96" index semantics are still unconfirmed; I have asked for clarification and have not run another interpolation or ticket-number search.
