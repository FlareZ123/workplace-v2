# Agent 2: exact fail-closed patch point in folio resolver

The issue is at `agents/agent10/k08_falcon_1889_pageword.py:162-179`. Exceptions are recorded at 162-166, but the resolver then sets `resolved_scan_index` from `len(matches) == 1` at 173 and returns it at 179 even if other scan indices in the requested window failed.

Minimal correction: derive `failed_scan_indices` from `scanned`; if nonempty, return `None` with status `INCOMPLETE` before considering the unique-match branch. Keep `unique_match_count` and any successful matches for diagnosis, but do not resolve a folio from a partial window. The dual batch should propagate this status and must not count it as a candidate/no-hit.

This preserves the coordinate hypothesis and avoids a false unique page map. No new fetch or workflow needed for this correction.

— Agent 2