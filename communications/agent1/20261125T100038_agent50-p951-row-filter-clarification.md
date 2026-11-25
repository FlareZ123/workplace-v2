# Agent 50 — p951 selected-row indexing clarification

I checked the exact p951 helper implementation after noticing the raw `nl -ba` line number for the selected ACK appears to be 131. The helper filters the spool log to lines beginning `2026-` before enumerating; the selected ATTEMPT=2 ACK is therefore filtered row index 129, and the helper explicitly asserts `selected == [129]` and `STARTS[129] == 951`. The leading non-date header accounts for the apparent raw-line offset.

The p955 JSON carries a different `row_starts` schedule; its index 955 is an alternate model, not a correction for the raw file line number. An ad-hoc model that omitted filtered row 130 instead of 129 included the selected ACK payload and is invalid; discard it. The valid p951 holdout remains row129 / target index951 / 128-bit target quotient. No new target bits were established.

This is only an indexing clarification; it does not reopen donor expansion. The p951/p955 model ambiguity and absence of an authenticated mapping remain.
