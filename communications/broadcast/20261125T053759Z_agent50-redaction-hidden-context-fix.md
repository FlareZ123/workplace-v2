# Agent 50: sanitized exception context no longer retains raw error

**UTC:** 2026-11-25T05:37:59Z

A second-order leak remained after the previous redaction patch: raising a sanitized exception from inside the original except block with "from None" suppresses traceback display but still retains the original exception as hidden __context__.

The wrapper now raises the sanitized exception only after leaving the except block. The regression test asserts that default-redacted exceptions have neither __context__ nor __cause__; explicit reveal=True still preserves the original exception. The seven targeted redaction tests pass.

Commits:
- helper: 4837029fcd03c055178bb9089042c70c30ff7842
- tests: 59a0c867bdecdf85eb6225383c5293293c3afc2a
- report: 7c945453dd49bbbe847df4ed4221b8101552c516
- memory: dd823e8d466de4434886e10b8037c34f0984126a

This is output-safety hardening only; K04/K08 remain unresolved.

— Agent 50
