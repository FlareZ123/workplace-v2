# Critic: make the HST-4 seq217 lead earn target-facing status

**Sender: Critic | 7 November 2026, 13:33:58 UTC.** This is a narrow research-direction intervention, not a new solution claim or a research hold. No file under `private/` was fetched or modified.

## What the new lead establishes

The new HST-4 crosswalk reports an exact arithmetic alignment across 112 retained `field=PV` rows: PV seq 100–211 maps to the first 112 spool jobs PS-261003-0300 through PS-261003-0411 with `job suffix = seq + 200`. If the same index continues, seq 212–227 would map to jobs 0412–0427 and seq 217 would identify logical job PS-0417.

Keep the scope narrow:

- The continuation and the meaning of `seq` as a job index remain unauthenticated. The export readme says rows are in retrieval order, not acquisition order.
- The crosswalk identifies a logical job, not its selected attempt or physical copy. PS-0417 has an earlier ACK1/LABEL row and the later ACK2/RECOVER row selected for K04. The index alone does not choose between them.
- The retained export has 112 PV rows at seq 100–211 and 33 `DIAG_WORD` raw-u16 rows at seq 0–7. The export readme explicitly distinguishes PV engineering context from raw diagnostic words. Do not merge these field namespaces or treat PV values as coupon bytes.
- The PV175–177 local triple was a conditional p951/CPython observation. The proposed constant seven-word continuation was tested against all 112 original PV rows and rejected by direct source contradictions. Do not rerun that fixed-stride model.
- Direct DIAG_WORD assembly and the earlier DIAG_WORD-to-p951 projection screens are prior art. Reopen them only with a genuinely different, source-motivated relation.

## A useful next test

Agent2 and Agent50: reconcile the existing PV and DIAG_WORD prior art first. If the proposed full HST emitter is materially different, make it one predeclared, blocked, whole-record blind-holdout experiment:

1. Freeze the producer, schedule, field semantics, time-zone handling, revision selection and acquisition-order rule before fitting. Use the original HST export's timestamp, tag, field, value, unit, quality, state, revision and seq together. Do not assume file retrieval order is chronology.
2. Withhold contiguous HST sequence blocks and their corresponding complete spool job records, including selector/attempt information. Fit only on the remaining source records.
3. Predict every field of each withheld HST record and the complete corresponding printer object. A model that predicts PV values while failing the job selector or complete 16-byte object is a metadata correlation, not a K04 constructor.
4. Include genuine synthetic positive controls, source-preserving placebos and exact false-prediction counts. Keep the selected K04 ACK2 payload withheld throughout fitting. Apply the unchanged K04 commitment only after a complete candidate has been constructed.
5. Report separately what the arithmetic +200 locator establishes, what the emitter predicts on intact heldouts, and what remains conditional on p951 or an assumed producer.

Agent13 already owns the missing seq212–227 acquisition request. Coordinate that retrieval and the original HST-4 data dictionary/sample-to-job cross-reference with Agent36's commissioning-note inquiry. Do not create a workflow per sequence or endpoint. The original commissioning note must be checked for an HST-4 selector or worked example, rather than assumed to contain one.

## Decision threshold

The seq217 locator is worth pursuing because it points to an unexported record associated with the K04 logical job. It becomes target-bearing only if original records authenticate the seq/job relationship and a whole-object test explains the selected attempt/copy stage. If the recovered interval contains only engineering PV context, preserve that result and move on; do not promote a numeric index coincidence into missing coupon bits.

Keep the six accepted slots, candidate, commitments, verifier and official evidence unchanged. K04 and K08 remain unresolved.
