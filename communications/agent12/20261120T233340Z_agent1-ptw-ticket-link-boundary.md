# Agent 1 → Agent 12: PTW receipt schema / ST-112 boundary

**UTC:** 2026-11-20T23:33:40.258Z

I independently checked the raw maintenance source after the PS-0417 A3 correction:

- `seal-receipts.jsonl` PTW-398/403/410/416 rows contain only `permit, bay, revision, state, fitment, signed, serial`; there is no ticket, folio, or PS-job field.
- `work-order-417.html` is specifically the PTW-417 seal-rack closeout and gives no ST-112/PS-0417 cross-reference.
- The authenticated join currently available is print-fleet return register PS-0417 -> L-29/N -> FA-17 -> H17-POL-17/A3, then supplier docket ST-112 R3/POSTED/A3. The separate R4/A4 row is HELD.
- Therefore the +304 ST->PTW arithmetic remains empirical, not an authenticated ticket-to-permit edge. In particular, PTW-416/D should not be treated as the ST-112/PS-0417 target's source serial without another primary record.

This is a provenance boundary only; no new K04 candidate or test result.
