# K04 source chronology: PS-0417 is the only spool activity inside the 17:45–18:15 rounds window

**Status:** empirical chronology observation; not a K04 candidate or causal finding.

## Question

Does the retained inspection-rounds page establish a time window that intersects the selected PS-0417 print activity, and is that activity unique within the retained spool export?

## Source facts

- `evidence/maintenance/inspection-rounds.log` identifies itself as page 4 of 11 and states that the remaining pages are not included in the export. On 2026-10-03 it records an instrument-store electrical-odour report at 17:12 UTC, a ventilation reset at 17:45 UTC, and rounds resuming at 18:15 UTC.
- `evidence/print/spool-reconstruction.log` timestamps are UTC. It contains 133 parsed spool rows.
- The three PS-261003-0417 events are 18:01 attempt 1 REQUESTED, 18:02 attempt 2 ACK, and 18:03 attempt 3 REQUESTED; all are RECOVER / bench.
- Those three PS-0417 rows are the **only three of 133 spool rows** in the half-open interval [17:45, 18:15) UTC on 2026-10-03.
- The nearest surrounding spool activity is PS-261003-0426 and PS-261003-0427 at 17:30 and 17:35, followed by PS-261003-0448 and PS-261003-0420 at 18:24 and 18:25. The print-fleet note maps PS-0417 to the North office FA-17 / ESC-N route, PS-0448 to the South office FA-22 / ESC-S route, and PS-0420 to WATCH-SPARE; these are not interchangeable device controls.

## Method

Parsed the ISO-8601 timestamps and job/attempt/state fields from all non-header rows in `spool-reconstruction.log`; normalized `Z` to UTC offset `+00:00`; selected rows whose UTC timestamp fell on 2026-10-03 and satisfied `17:45 <= time < 18:15`. Result: exactly the three PS-0417 events above. No payload bytes, KDFs, PRNGs, or acceptance candidates were tested.

## Interpretation and limits

The temporal overlap is exact and unusual within this retained spool export. It makes the complete original 11-page inspection-rounds notebook a concrete chronology/custody intake target: pages 1–3 and 5–11 may clarify what was being inspected, where the instrument store and North office were relative to one another, and whether the PS-0417 attempts were observed during the rounds suspension.

It does **not** establish that FA-17 was in the instrument store, that the ventilation reset affected the printer, or that any spool payload is corrupt. The print-fleet note places FA-17 in the North office; the retained page refers to the instrument store. No location join is present. No K04 bytes are recovered by this analysis.

## Next evidence

If an independently authorized local copy appears, compare all 11 original notebook pages (including annotations and attachments) with the PS-0417 18:01–18:03 window and preserve the page order. Obtain the native PS-0417 queue/spool artifacts for all three attempts to establish which payload was actually rendered. Do not contact the custodian or probe R:/SharePoint.

See also `work/h17_sharepoint_retrieval_request.md` for the bounded intake targets.
