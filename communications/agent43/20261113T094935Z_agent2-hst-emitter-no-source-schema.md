# Agent 2 → Agent 43: HST-4 full-emitter scope decision

I reviewed your 08:53 request, Agent36's 7 November proposal, the original export and the accumulated HST work. I am **not** launching another full variable-consumption emitter sweep on the present evidence.

The blocking issue is not merely that the +200 join is unverified. The source does not specify an HST PV writer/call schedule that can be frozen without inventing one:

- `evidence/telemetry/export-readme.txt` says the file is in retrieval order, timestamps are acquisition times, PV/unit fields are historian context, and `DIAG_WORD` is the recorder's unsigned raw field. It does not define PV `seq` as a printer-job foreign key.
- The arithmetic `PV seq + 200 = PS suffix` pairs 112 rows with 112 ACK jobs, but the spool jobs occur 07:00–16:15Z while PV acquisition timestamps are 21:12:31–21:14:19Z. It is a locator coincidence, not a temporal or content relation.
- The proposed emitter has no source-grounded field order, choice domains, timestamp range, value transform, rejection policy, or seed/phase. Allowing those to be inferred jointly from the same 96 training rows would make a flexible fit hard to distinguish from an arbitrary schedule.

Relevant prior work already covers the nearest discriminators:
- Agent23's 624-word HST/printer interleave: 180 complete models, 735,120 K04 commitment checks, zero hits and no late-packet predictions.
- Agent18's independent PV LCG producer and Agent34's PV-float/p951 source projection: neither yields a validated phase or target-bearing source constraint.
- Agent50's acquisition-time-ordered post-spool search: 712 eligible stages, only 14 individual PV matches, longest chronological chain 6/14; the strict five-output whole-record gate had no training fit.
- Agent14's full-record seed/field-embedding checks and your current one-gap tests are also negative within their stated scopes.

I agree your 16-row holdout is cleaner than the earlier contaminated reserve, but it cannot cure the missing source relation or supply a predeclared emitter schema. I would reopen this only if a native HST writer/schema, a source-authenticated seq↔job index, or an independently documented field/range/call schedule appears. Until then, do not spend another run fitting an unconstrained PV emitter or present any extrapolated seq212–227 values as K04 donor bytes.

This is a research-allocation decision, not a claim that every conceivable HST model is mathematically impossible. Keep the HST source caveat explicit and redirect effort to a materially different target-bearing route.
