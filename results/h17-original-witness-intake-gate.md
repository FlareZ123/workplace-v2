# H-17: reproducible intake gate for missing original witnesses

**Agent 8 | 20 October 2026 UTC.** Scope: historical record-preservation evidence intake, using the **unchanged** REC8/1 acceptance commitments and verifier. The gate does not claim a seventh accepted slot. Current source result: **six PASS, K04/K08 unverified**, combined not accepted.

## Question and practical constraint

Both workplaces preserve an identical original archive export and considerable negative target research. The source-bound next event is acquisition of an original ESC-N RECOVER coupon/buffer and/or Emily's final keeper-margin wording, possibly via the indexed offline records drive. The existing checker accepts eight raw hex components, while incoming material may be a source image plus a human reading. A repeatable transition from newly received source to original acceptance is useful so one does not accidentally treat a job ACK, arbitrary transcript, or thematic caption as authenticated evidence.

## Deliverables and original-source constraints

- [`work/h17_witness_intake.py`](../work/h17_witness_intake.py) is **read-only**: it accepts an external original-source file and separately prepared transcription for either or both missing slots. It computes SHA-256 of both sets of **original bytes** and their **transcriptions**. Those hashes are chain-of-custody anchors, not independent authenticity certificates.
- K04 transcription is one JSON object with `job`, `attempt`, `state`, `class`, `timestamp_utc`, `payload_hex`. Its logical job is loaded from the 1 September route in the original appliance labels; the selected attempt and timestamp are independently read from the original surviving `print/spool-reconstruction.log` as the greatest acknowledged RECOVER attempt for that job. Incorrect selector values, duplicate JSON keys and any payload other than 16 bytes are rejected *before* deriving the XOR component. The record's content still must be authenticated by a real original coupon or journal.
- K08 transcription is a UTF-8 exact caption; the code performs precisely the route-defined lowercase, non-alphanumeric replacement and whitespace collapse, then HMAC-SHA256 with the original nonce to derive its first 16 bytes. The source must actually prove that these were the **final incident envelope** words. The tool cannot authenticate this from a thematic description.
- The unchanged repository's six verified components are used as baseline. The code calls the original `resources/verify.py` evaluator with its original `resources/acceptance.json` for each new candidate. It emits a **complete eight-slot candidate only after eight individual PASS results and combined PASS**. It never writes to `resources/`, `candidate.json`, the newly supplied source, or any target commitment.

## Reproducible falsification controls

[`work/test_h17_witness_intake.py`](../work/test_h17_witness_intake.py) is one offline standard-library test file. It executed successfully against the provided export, checking:

1. The preserved ACK attempt-2 spool value (`A9A9DC5731A5E2AE879C47215C2559D5`) and a preserved Emily draft both return `NO_MATCH`; the original six still PASS.
2. Source-original and transcription SHA-256 are computed separately.
3. A falsely selected attempt 3 and ambiguous duplicate coupon JSON keys are rejected before comparison.
4. Case, punctuation and whitespace are normalized consistently.
5. **Positive control with wholly synthetic commitments isolated in a temporary directory:** modified test-only K04/K08 digests and combined digest yield eight PASS, combined PASS and a printed complete candidate. **This control never touched the actual targets and is explicitly not historical recovery.**
6. Five original evidence/acceptance/candidate file digests are unchanged after the test.

No real, historical original K04 coupon or quoted final K08 margin was supplied with this run. Tests demonstrate *mechanical correctness of the intake path*, not evidence authenticity or key recovery. Target verification remains K01/K02/K03/K05/K06/K07 PASS; K04/K08 unknown.

## Minimum acceptable new input

Custodian should provide original unmodified bytes for either source (scan/photo, original printer journal, or contemporaneous caption document) and a transcription sufficiently precise to identify the exact 16-byte coupon or final normalized words. Preserve acquisition time, originating record ID, redaction status and actual custody history in a separate memo. For K04, `PS-261003-0417`, attempt 2, ACK 03 Oct 18:02 UTC must be supported *independently* of the questionable spool payload. For K08, incident envelope identity and **final**, rather than draft, wording must be supported. Any accepted component remains merely hash-matched until provenance is separately established.

The gate avoids further blind permutation searches and preserves the exact acceptance boundary for new source releases. See [Source intake issue #1](https://github.com/FlareZ123/workplace-v2/issues/1) and [v1 prior-art coverage](h17-v1-prior-art-gate.md).
