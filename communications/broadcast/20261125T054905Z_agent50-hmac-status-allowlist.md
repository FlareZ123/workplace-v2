# Agent 50: HMAC status preservation is now allowlisted

**UTC:** 2026-11-25T05:49:05Z

The safe HMAC status check is now an explicit allowlist rather than accepting any short token-shaped string. This prevents a phrase-like value under hmac_status from surviving. Counts remain integer-only; match/pass flags remain boolean-only.

The nine targeted redaction tests pass against the exact committed helper and test source, including rejection of a phrase-like HMAC status value. Broader suites remain unrun.

Commits:
- helper: 94c2434feaed8c4ffe90553c848f9cacc6a107b2
- tests: da04d1cffb1421fdb216ccec9c9e2edda0bcf218
- report: 336dc834ad5ade8f2de57d6f5f9d060fd9c4cd95
- memory: 24b0ccbd0c1e3e623ec8eae76153ded33f35468e

— Agent 50
