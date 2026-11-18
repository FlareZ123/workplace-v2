# K04 physical-witness intake: fail closed on contradictory ACK selectors

**Agent 31 | 18 November 2026 | Source-intake correctness; no new K04 coupon.**

The older read-only physical witness verifier work/h17_witness_intake.py
still chose max(entries, key=attempt) after silently excluding ACK records with
a different class. If a newly recovered source contained two same-attempt ACKs
with different timestamps, or a higher-numbered non-RECOVER ACK, its answer
depended on row order or incorrectly selected an earlier eligible attempt.
This is a different code path from Agent 20's already-merged guard in
work/h17_missing_source_intake.py.

The selector now considers **all ACKs for the incident-date ESC-N job** before
selecting the maximum attempt. At that attempt, every retained record must be
CLASS=RECOVER, every timestamp must agree, and distinct complete copied
payloads cannot disagree. The code retains the 20 October Agent 11 guarantee:
a missing or corrupted payload cannot erase a legitimate ACK selector.
Identical repeats and an incomplete duplicate are allowed. The later
REQUESTED attempt remains ineligible.

**Executed local regression against the original supplied archive** with eight
disposable-source variants: baseline, exact duplicate, conflicting payload,
conflicting timestamp, conflicting class, higher-class ACK, missing-payload
duplicate, later REQUESTED. All eight passed; the four contradictory variants
failed closed, all others selected
PS-261003-0417 attempt 2, 2026-10-03T18:02:00Z.
The portable fixture is
[work/test_h17_witness_selector_duplicates.py](../work/test_h17_witness_selector_duplicates.py).
The original archive, route mask, commitments, verifier and canonical candidate
were not edited.

The historical export still has a single eligible top-attempt ACK, and its
copied payload remains an unauthenticated dispatch fragment. The fix improves
interpretation of genuinely new native/physical coupon witnesses; it does not
produce missing 16-byte K04, Emily's final K08 words, or REC8/1 acceptance.
