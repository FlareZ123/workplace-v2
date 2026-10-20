# H-17 K04: dispatch ACK selection independent of damaged printer payload

**Agent 11, 20 October 2026, UTC.** Scope: readiness to validate newly obtained historical escrow-coupon witnesses against the unchanged REC8/1 verifier. This is an **intake correctness repair**, with **no new original K04 payload bytes**, no K08 final caption, and no change to six-of-eight acceptance.

## Original-source distinction

The custodian's `resources/evidence/records-custodian.txt` states that print-job acknowledgement proves receipt of a job, while payload bytes in reconstructed spool fragments are not independently validated. `resources/evidence/recovery-routing.json` requires the *last acknowledged attempt* for the incident-date logical ESC-N route. `resources/evidence/archive-labels.ini` maps ESC-N to job `PS-261003-0417`; the original `print/spool-reconstruction.log` has the selected `2026-10-03T18:02:00Z` attempt 2, `ACK`, `RECOVER`, plus a later **REQUESTED** attempt 3 that must remain excluded.

The first version of `work/h17_witness_intake.py:last_escrow_ack` used an entire-line regular expression requiring both `PAYLOAD=[0-9A-F]{32}` and `DEST=...` **before considering a job an ACK**. That silently equated integrity of the disputed reconstructed payload with integrity of the dispatch selector. If the selected attempt's payload was `CORRUPT` or absent while its header remained intact, the selector dropped that valid ACK; a valid independently obtained original coupon would be rejected or compared with the wrong attempt.

## Correction and bounded controls

The changed parser matches only the UTC timestamp and `JOB`, `ATTEMPT`, `STATE`, `CLASS` selector fields at the beginning of a spool line; it retains the matching `STATE=ACK` and `CLASS=RECOVER` filters and maximizes original attempt number. Payload bytes and destination remain outside the selector predicate. The change is confined to [the read-only intake checker](../work/h17_witness_intake.py), not the original evidence or official acceptance code.

The standalone [SFT](../work/test_h17_ack_selector_integrity.py) copies the original source to a temporary directory, alters only the selected ACK line in a disposable copy, and checks these cases:

| Test case | Expected historical selector |
| --- | --- |
| Unmodified spool | `PS-261003-0417`, attempt 2, `2026-10-03 18:02Z` |
| Selected ACK `PAYLOAD=CORRUPT` | Same selector |
| Selected ACK without payload/destination fields | Same selector |

A local method-equivalent smoke exercise against the unmodified extracted spool and labels passed all three cases using the new selector expression; the old complete-line expression did not match the two damaged-payload controls. The committed SFT is a portable standard-library regression test for execution in a checkout. An unchanged-source acceptance re-run is independent of this patch and still reports six PASS, K04 and K08 missing.

## Limits and interpretation

The change preserves dispatch selection when **payload data alone** is untrusted; it does not reconstruct the coupon, certify an ACK whose own job/time/attempt fields are damaged, or establish historical authenticity of a future source. It cannot turn a hash-only guess into an accepted component. The actual authentic `PS-261003-0417` attempt-2 RECOVER payload or an independent mask source and Emily's final K08 margin are still missing.

The original six accepted components, `resources/acceptance.json`, `resources/verify.py`, `resources/candidate.json`, `candidate.json` and every official `resources/evidence/` file remain untouched. **K04/K08 MISSING, combined INCOMPLETE.**
