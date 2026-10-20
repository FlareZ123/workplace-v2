# Agent 2: H-17 archive reconstruction

Claim: 2026-10-20T04:34:52Z. Normal research invocation, user expressly excluded Critic mode.

- Completed K01, K02, K03, K05, K06, K07, all six separately **PASS** against unmodified `resources/verify.py` and `resources/acceptance.json`. Candidate at `candidate.json`. Detailed reductions in `results/h17-verified-six-slots.md`; results index updated.
- K04 latest September `ESC-N` mapped job PS-261003-0417 ACK attempt 2 XOR mask fails. Entire spool tested, none passing; one and two byte corrections exhausted, none passing. Could be more significant corruption/unavailable payload provenance. See results note.
- K08 original keeper caption not found; surviving drafts / notes and Emily/Gabriel mail suggest sea, late watch, table, welcoming others. Final words required by HMAC. Search textually justified captions and avoid general permutations.
- Supplemental password-protected `BX25-08.pdf` opened with numeric scanner release `8131` via local brute force. It contains property references FA-17, H17-POL-17/A3, account named `Noyes Energy Group` and corporate correspondence pointer https://noyes-energy-group.pages.dev/ (unreachable from tested public web lookup). Cross-link to supplier L29 return records, does not itself recover K04.
- No local network to GitHub in runtime; GitHub connector supports writes. Important artifacts committed through connector.

Next actions: investigate whether PDF website can be read by alternative sanctioned tools; derive bounded K08 caption phrase; test possible K04 wrong-payload provenance beyond two-byte edit. Preserve source exports. Keep checkpoint and lease age check on every checkpoint.
