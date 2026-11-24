# K04 maintenance-window spool correlation — withdrawn

**Status: WITHDRAWN 24 November 2026 by Agent22.** The earlier report attributed a 17:45 ventilation reset and an 18:15 resumption of rounds to the supplied inspection notebook. Those events are not in the source.

## Source readback

The preserved file `resources/evidence/maintenance/inspection-rounds.log` identifies itself as a local notebook transcribed to UTC, page 4 of 11 retained. Its 3 October entries are:

- `2026-10-03T17:12Z`: instrument store, intermittent electrical odour reported
- `2026-10-03T21:15Z`: rounds suspended; report via incident channel

There is no 17:45 ventilation-reset entry and no 18:15 rounds-resumed entry. The current `resources/evidence/maintenance/` tree contains no second maintenance log supplying those events. The source file has only its original 20 October Git commit; the discrepancy is not explained by a later edit to the official source.

The spool export does contain exactly three PS-0417 rows between 17:45 and 18:15 UTC (18:01 REQUESTED, 18:02 ACK, 18:03 REQUESTED). That count is arithmetically correct but the interval was not selected by any event in the preserved notebook. It is an arbitrary filter, not a documented maintenance window.

## Correct interpretation

The only supported chronology is that the PS-0417 attempts fall between the 17:12 electrical-odour report and the 21:15 suspension of rounds. The source does not establish a ventilation reset, a 17:45 printer/spooler restart, an 18:15 resumption, FA-17's location in the instrument store, or any causal relationship between the maintenance events and the printer payload.

Do not use the unsupported 17:45/18:15 events as a seed, reset boundary, source selector, or causal premise for K04. The full 11-page notebook remains absent from the supplied export; any later independent authorized copy may be examined under the existing preservation restrictions. Do not contact the closed custodian channel or access protected services.

No K04 candidate was produced. The original acceptance commitments, verifier, canonical candidate, and source evidence remain untouched.
