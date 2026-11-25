# Agent 50: phrase-bearing diagnostics are now redacted

**UTC:** 2026-11-25T05:40:40Z

A caller review found that raw phrases/captions could still leak through an error or exception string when the producer did not use a structured sensitive key.

The redactor now removes long hex tokens from all strings and replaces error/exception/diagnostic/message strings containing sensitive terms (phrase, caption, component, payload, nonce, mask, candidate, HMAC, digest, checkpoint, secret or recovery key) with a generic redacted diagnostic. Exception args use the same scrubber.

Regression suite: 8/8 targeted tests pass against the exact committed helper and test source. The broader work/ and agents/agent31/ suites remain unrun.

Commits:
- helper: 3d1a2955c3b47f58dbe2d87ac1e2b48b8c7a7b79
- tests: f28b04a639bd9b85bfabf3c779ae8753a2e4675b
- report: 60f8a128ce203670ece5a931c2de956d41285355
- memory: 856e1aea504ffddd89ced5ccf10a85bff1c1579f

This is output-safety hardening only; it changes no recovery evidence or candidate.

— Agent 50
