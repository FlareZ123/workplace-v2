# K04: +304 North-ticket join conflicts with the ST-112 / PS-0417 return mapping

**Status:** empirical cross-source join with an unresolved source conflict. No K04 component recovered.

## Question

Does the L-29/N North binder ticket sequence map to PTW permit IDs and PS job IDs by a stable numeric offset, and does that mapping authenticate the ST-112 ↔ PS-0417 relationship used in the K04 route?

## Reproducible source method

The bounded read-only script is `agents/agent12/st_ptw_ps_offset_scan.py`. It reads the local supplier reconciliation CSV, PTW seal receipts, and reconstructed print spool. The corrected CSV field is `folio_or_jacket` (not `folio`). It fixes the L-29/N binder order as `ST-094, ST-081, ST-106, ST-099, ST-112`, checks the L-28 FA-17 holdout, and compares L-29/S LV-42 and Watch ST-09 as cross-account controls. It scans offsets +200 through +400 and scores North PTW coverage, distinct bays, holdout coverage, and PS-job coverage.

## Observed +304 pattern

- L-29/N FA-17: 4/5 tickets map to four distinct singleton PTW bays; all 5/5 map to PS jobs.
- L-28 FA-17 holdout: 2/2 map to PTW permits and PS jobs.
- L-29/S LV-42 control: only 1/5 map to PS jobs.
- Watch ST-09 control: 0/2 map to PS jobs.

In binder order, +304 gives:

| Supplier ticket | PTW / PS ID | PTW bay | PS job present |
|---|---:|---|---|
| ST-094 | 398 | A | yes |
| ST-081 | 385 | no singleton receipt | yes |
| ST-106 | 410 | B | yes |
| ST-099 | 403 | C | yes |
| ST-112 | 416 | D | yes |

This is a strong empirical cross-account pattern in the bounded scan, not an explicit source-authored foreign key. It supports using +304 as a candidate FA-17 ticket join; it does not prove that every ticket or every printer route follows that rule.

## Material conflict

The +304 pattern maps **ST-112 to PS-0416** and maps **PS-0417 to ST-113**. Separately, the print-fleet return register maps **PS-0417 to ST-112**. The supplier reconciliation extract contains both **ST-112 R3 / POSTED / A3** and **ST-112 R4 / HELD / A4**. These are distinct version/status records and must not be collapsed.

The incident-date archive-label route explicitly maps ESC-N to PS-261003-0417, and MAIL-16 says the September logical route is current. The return register is later corroboration, not the basis for the incident-date route selection. The +304 mapping is a strong empirical join but not an authoritative override of either the route file or the return register. It therefore does **not** justify silently replacing PS-0417 with PS-0416 for K04.

## Decision and next source

Do not run another payload/byte permutation against PS-0416 or substitute its ACK payload for the route-defined PS-0417 attempt. The next useful action is to resolve the ST-112 R3/R4 ↔ PS-0416/PS-0417 discrepancy from an independent source:

1. the native Stores return index at `R:/Stores/returns/SEP26/index.htm`;
2. the original ST-112 R3/POSTED/A3 and R4/HELD/A4 packet faces, attachments, and closeout;
3. the native PS-0416 and PS-0417 queue/job journals and output/collection records.

Only after that source-level relationship is authenticated should a job-to-coupon selection be changed. The +304 result improves the source join but does not emit the 16-byte K04 coupon and does not match the K04 acceptance commitment.

## Reproduction and limitations

- Script: [`agents/agent12/st_ptw_ps_offset_scan.py`](../agents/agent12/st_ptw_ps_offset_scan.py)
- Original report communication: [Agent 12's 2026-11-20 broadcast](../communications/broadcast/20261120T221452Z_agent12-north-ticket-offset-validation.md)
- This result uses only the local recovered supplier CSV, PTW receipts, and spool reconstruction. The offset is inferred from a bounded scan and holdout/control behavior; it is not a signed ticket/job cross-reference.
- Agent 12 reports that the resulting four-bay serial blocks and bounded complete-output constructions did not match the unchanged K04 commitment. No K04 candidate, canonical candidate, route, acceptance, or verifier was changed.
