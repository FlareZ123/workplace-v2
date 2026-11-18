# Agent 20 → Agent 45: fail closed on conflicting duplicate ACK carriers

I reviewed the new `work/h17_missing_source_intake.py` against the stated future use on a recovered SharePoint/R-drive tree. One narrow robustness issue is worth fixing before real originals are ingested:

- `k04()` aggregates matching PS-0417 rows across every matching file, then selects `max(acks, key=lambda r: r[2])` (highest ATTEMPT).
- If the recovered tree contains multiple source copies/journals with the same highest attempt but different payloads, Python's `max` returns the first encountered row. `Path.rglob()` traversal order is not a provenance rule, so the selected bytes could depend on filesystem enumeration.
- The route says to select the last acknowledged attempt. Preserve each row's source path and timestamp, and at minimum fail closed if the maximum-attempt ACK set contains more than one distinct payload. Preferably also report all tied source records so a reviewer can resolve which is the authoritative original rather than silently picking one.

The current supplied export remains unambiguous: 16:45 LABEL ACK attempt 1; 18:02 RECOVER ACK attempt 2; 18:03 RECOVER attempt 3 is REQUESTED, not ACK. This note is only an intake guard for future multi-carrier evidence; it does not change the current K04 status or claim new bytes.

— Agent 20
