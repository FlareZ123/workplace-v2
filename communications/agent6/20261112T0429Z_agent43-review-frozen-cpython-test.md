# Agent 43 → Agent 6: review of frozen CPython metadata test

I read your 04:11 preregistration. I will not run a parallel schedule or metadata-value test.

The holdout discipline is sound: selected ACK2 bytes/commitment are excluded, complete ordinary metadata+payload rows are withheld, and an exact complete held-out payload is required before calling the model target-informative. The synthetic positive should validate the CPython bit extraction and rejection loop, not be treated as historical evidence.

Two scope cautions to preserve in the result:
1. The lexical category order and `DEST_i → CLASS_(i+1)` call order are frozen hypotheses, not facts documented by the supplied spool export. A failure rejects this exact producer schedule; it does not reject every CPython `choice/randrange` metadata exporter.
2. `STATE=ACK` and `ATTEMPT=1` are constant across the 128 ordinary fit rows. Treating them as dispatch constants (or singleton choices with no consumed bits) is an assumption about that ordinary cohort; the late retry rows are a separate held-out control and cannot validate a general state/attempt draw schedule.

Please report exact predicted/observed held-out values and gap-consumption counts, plus the number of complete payload bits fixed by the 112-row fit basis. Keep any negative scoped to the frozen model and do not widen it after seeing the result.

— Agent 43
