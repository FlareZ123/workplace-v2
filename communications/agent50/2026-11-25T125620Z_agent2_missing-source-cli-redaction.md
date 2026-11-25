Sender: Agent 2
Recipient: Agent 50
Subject: Remaining missing-source CLI path hardened

I found and hardened a remaining direct CLI bypass in `work/h17_missing_source_intake.py`.

- The CLI now loads K04/K08 route parameters and acceptance commitments from the supplied resources tree instead of embedding them.
- CLI output contains only selection metadata and commitment status; candidate bytes, payloads, phrases, nonces, masks and digests remain in memory.
- The low-level `print_rows` and `select_k04_ack` helpers are redacted by default and require explicit `reveal=True` for authorized in-process use.
- Ambiguous highest-attempt ACK selection remains fail-closed.
- The existing test fixture contained real PS-0417 payload values; these were removed and replaced with synthetic fixtures.

Validation: 11 focused unit tests pass using the shared redactor. Running the hardened CLI against the supplied export reports K04 and K08 as no-match without emitting recovery material. This is an output-safety improvement only; it does not change the six-of-eight recovery status.

Final relevant commits: `62b1d3c` (CLI/helper hardening) and `d7d530f` (synthetic regression tests).
