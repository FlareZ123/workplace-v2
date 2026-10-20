# Agent 2: H-17 archive reconstruction

Claim: 2026-10-20T04:34:52Z. Normal research invocation, user expressly excluded Critic mode.

- Completed K01, K02, K03, K05, K06, K07, all six separately **PASS** against unmodified `resources/verify.py` and `resources/acceptance.json`. Candidate at `candidate.json`. Detailed reductions in `results/h17-verified-six-slots.md`; results index updated.
- K04 latest September `ESC-N` mapped job PS-261003-0417 ACK attempt 2 XOR mask fails. Entire spool tested, none passing; one and two byte corrections exhausted, none passing. Could be more significant corruption/unavailable payload provenance. See results note.
- K08 original keeper caption not found; surviving drafts / notes and Emily/Gabriel mail suggest sea, late watch, table, welcoming others. Final words required by HMAC. Search textually justified captions and avoid general permutations.
- Supplemental encrypted property folio corroborates FA-17 / H17-POL-17/A3 provenance for the north printer cabinet but does not reveal an authenticated spool payload. Do not propagate source-redacted corporate identifiers, portal links, or document passcodes in public research artifacts.
- K04 further exhaustive testing: no passing candidate with any three changed hex digits or any three adjacent changed bytes. No local network to GitHub in runtime; GitHub connector supports writes. Important artifacts committed through connector.

Next actions: derive bounded K08 caption phrase; test possible K04 wrong-payload provenance beyond two-byte edit. Preserve source exports. Keep checkpoint and lease age check on every checkpoint.


## 20 Oct 2026, 19:21 UTC: predeclared direct job-ID digest producer test (new branch)

Original observation: each of the 128 5-minute regular printer spool rows carries a deterministic sequential `PS-261003-03xx/04xx` job identifier, an ATTEMPT=1 value and a full 16-byte opaque PAYLOAD. Distinct mechanism to the many studied MT/seed/gap hypotheses: a deterministic unkeyed MD5 or truncated SHA-256 *of the original recorded job or timestamp fields*, rather than a stateful pseudorandom stream. No source explicitly attests such a producer, so this is a strict tiny falsifier, not an assertion. Nearest predecessor: v1 spool MT/PRNG and hash-independent bitplane/carrier investigations; I found no producer result linking the exact structured JOB field to direct digest output in the cited equivalence gate. I will predefine a small set of canonical field serialization candidates, compare them only to the first three **intact** ordinary spool lines, and stop on failure. If any formula matches those three, predict lines 3..127 as withheld intact validation before ever deriving the **excluded** selected 18:02 attempt-2 coupon; a genuine formula would constrain all 128 missing K04 bits and allow the unmodified commitment to test the result. A digest mismatch is only rejection of these exact serializers and does not identify the actual producer. K08 is not implicated.
