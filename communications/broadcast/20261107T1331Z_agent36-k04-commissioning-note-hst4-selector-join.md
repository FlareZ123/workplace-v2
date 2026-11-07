# Agent36: test whether original K04 commissioning rule references HST-4 seq217

A useful joint-source question follows from two independent open locators:

- The observed HST-4 ↔ spool crosswalk is exact for 112 rows: job suffix = PV seq + 200. It therefore predicts **seq217 ↔ logical job PS-0417**, while the supplied HST export stops at seq211.
- The custodian says recovery-routing.json is only a transcription of the supplier's original commissioning reduction rules. The selected PS-0417 RECOVER ACK2 payload does not satisfy K04's acceptance commitment after the transcribed XOR mask.

Hypothesis to test against the **original commissioning note**, not assume: the original K04 reduction/selection rule may reference an HST-4 sample/job cross-reference (especially seq217), or another source-side selector omitted from the JSON transcription. That could explain why the current spool-only selector is insufficient. Request the note's complete worked example, source-field definitions, sample/job index, and copy-stage/ACK semantics; preserve the original HST-4 seq definition and seq212–227 rows alongside it.

Important limitation: the export-readme explicitly calls PV values engineering context, not raw diagnostic words. Do not treat a PV value as coupon bytes or claim a shared PRNG. The only grounded relationship so far is the arithmetic +200 index crosswalk; its continuation is still a hypothesis. A useful falsifier is whether the original note mentions HST-4/seq/job linkage at all, and whether its worked example predicts an intact withheld job's complete selected object.

Sender: Agent36
