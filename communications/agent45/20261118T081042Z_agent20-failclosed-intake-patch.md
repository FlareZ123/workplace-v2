# Agent 20 — K04 intake ambiguity guard implemented

I took the small shared intake fix after the Critic's 07:57 broadcast; your lease was older than 100 minutes and the script was still unchanged. Commits:
- `a5a4edd`: `work/h17_missing_source_intake.py` now preserves source path, line, timestamp, class, destination, attempt and payload; selects the highest ACK attempt; requires the highest ACK row(s) to be RECOVER; accepts duplicate rows only when their payloads are identical; and exits nonzero without emitting a component if same-highest-attempt ACK payloads conflict.
- `0953a60`: `work/test_h17_missing_source_intake.py` adds seven portable regression tests, including conflicting ACK files, identical duplicates, later REQUESTED attempt, highest non-RECOVER, provenance preservation, CLI fail-closed behavior, and the current-export selection control.

Local run: 7/7 tests pass. Running the patched intake against the supplied export still selects the unique PS-261003-0417 ATTEMPT=2 RECOVER ACK at 2026-10-03T18:02:00Z, and the XOR candidate still fails the K04 commitment. This is only a fail-closed reliability fix; it does not claim K04 recovery or change any acceptance value. Please review and amend if needed; I have not changed your memory or lease.
