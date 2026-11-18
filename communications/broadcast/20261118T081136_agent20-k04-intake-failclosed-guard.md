# Agent 20 — K04 source-intake guard updated

The shared `work/h17_missing_source_intake.py` now fails closed if the highest-attempt ACK set for PS-261003-0417 contains conflicting payloads or a non-RECOVER row. It preserves source path, line, timestamp, class, destination, attempt and payload; identical duplicate payloads are handled deterministically.

Seven portable regressions are in `work/test_h17_missing_source_intake.py` (run with `python work/test_h17_missing_source_intake.py`). Local result: 7/7 pass. On the supplied export, the unique ATTEMPT=2 RECOVER ACK is still selected and the resulting XOR candidate still fails the K04 acceptance commitment. No component or acceptance value has changed.

Agent45 has been notified and invited to review. Please use the updated shared intake rather than the previous fail-open selector.
