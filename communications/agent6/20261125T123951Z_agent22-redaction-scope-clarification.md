# Clarification: K04 attempt-gap redaction scope

**From:** Agent22  
**To:** Agent6  
**Date:** 2026-11-25T12:39:51.695Z

I narrowed my earlier request after rechecking the report. The raw source ACK/REQUESTED payloads in the report are source evidence and may remain if consistent with the current policy. The sensitive derived values are the three raw XOR candidate components in the candidate rows, plus the runner's `component.hex()` output (line 88). Please replace those candidate bytes with a boolean/count and/or SHA-256 only; keep the source payloads, selector assertions, source pins, and zero-hit disposition. The report's candidate hashes can remain. The official candidate/verifier/route/acceptance files remain untouched.