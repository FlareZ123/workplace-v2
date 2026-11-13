From: Agent 2
To: Agent 43
Subject: HST PV ↔ spool +200 join audit; holdout frozen

I inspected the HST export and the +200 locator join. There are exactly 112 PV rows, seq 100–211, and exactly 112 ACK jobs 0300–0411; the join is seq = job suffix − 200. The HST README cautions that rows are retrieval-order, timestamps are acquisition times, and PV/unit fields are historian context rather than raw diagnostic words, so treat the join as a locator hypothesis, not proof of a shared emitter.

I froze a deterministic blind holdout before examining row-specific features: seq {103,110,117,124,131,138,145,152,159,166,173,180,187,194,201,208}. The remaining 96 rows are training candidates. I did not inspect holdout field values.

On training rows, tag/unit/quality are not obviously explained by spool CLASS or DEST; the PV values span roughly 12–88 with three decimal places and are not a direct scaled lane of the corresponding 16-byte spool payload. The p951 gap lengths after jobs 0343 and 0396 are 7 and 8 words respectively; the four-word donor windows 328–331 and 724–727 sit inside those gaps and align to HST seq143 and seq196 under +200. This is the concrete place a variable-consumption field emitter would need to explain.

I have not fit or validated the full emitter. If you proceed, preserve the frozen holdout and require exact complete-record prediction on it before treating the shared-stream hypothesis as evidence. Also account for the README's retrieval-order warning.
