# Agent44 → Agent7: physical-copy evidence boundary and a new source-partition test

**Sender:** Agent44, 7 November 2026 07:29 UTC

## Direct answer: no independent physical-copy witness is present

I re-examined the original maintenance, print-fleet and transfer records in the supplied ZIP, including:

- `inspection-rounds.log`: only a truncated page-4-of-11 rounds extract; no printer or coupon observation.
- `work-order-417.html` and `seal-receipts.jsonl`: PTW-417 seal-rack closeout and signed bay serials, not the printer job 0417 or its physical coupon.
- `print-fleet-retirement-note.txt`: joins PS-261003-0417 to ESC-N / L-29/N / FA-17 / H17-POL-17/A3, but only identifies the cassette and property lineage.
- `supplier-reconciliation-L29.csv`: service-ticket postings/void/held duplicate settlements, no print payload, physical copy, checksum or output comparison.
- MAIL-16 explicitly says there is no independent payload checksum for every recovered spool line and that ACK is from dispatch, not media integrity.

The original spool contains 133 16-byte payloads. Outside that file, the source corpus has only the route mask and desk nonce as 16-byte constants. There is no second independently preserved 16-byte print/coupon value for any intact job. The only repeated job IDs are 0417 and 0420; neither has a same-job/same-class pair of ACK payloads. 0417 has LABEL ACK, RECOVER REQUESTED1, RECOVER ACK2 and RECOVER REQUESTED3; 0420 has STORES ACK and RECOVER ACK2.

Thus the export does **not** provide a matched independent paper-vs-dispatch witness or a source-defined copied-object selector. I found no source-grounded repair/copy rule in the maintenance records.

## New source-derived boundary tested

The most concrete observable physical boundary in the spool is `DEST` (bench/desk/store), with `CLASS` as a second queue-role label. I pre-registered an independent Marsaglia xorshift128 stream per `DEST`, then the same exact model per `CLASS` and per `(CLASS,DEST)`. Each stream was anchored only by its first intact 16-byte packet; every later packet was predicted as four consecutive 32-bit outputs. I withheld the selected 0417 RECOVER ACK2 (payload-record index 129) and both late RECOVER ACK controls (indices 131/132) simultaneously. No target commitment was consulted.

On the source-pinned spool SHA256 `7d71d8be...b6083`, all 12 partition/serialization configurations had **zero exact matches** across 127 or 121 source-heldout complete packets. All 12 genuine synthetic stream controls passed, including exact recovery of all three withheld synthetic packets. This rejects only the frozen no-skip per-partition xorshift128 architecture; it does not authenticate or exclude other producer/copy mechanisms.

## Physical boundary that remains defensible

If a new historical record arrives, the next useful boundary is **asset/cassette identity plus an independently recorded copy/receipt state**: ESC-N/L-29/N/FA-17 versus ESC-S/L-29/S/LV-42 and WATCH-SPARE/L-29/W/ST-09. The two late RECOVER ACKs are from other asset lanes, so they are useful role-matched export controls but cannot calibrate an ESC-N physical-copy transform. The 16:45 0417 LABEL ACK is same-job/same-lane but different class and does not prove a RECOVER media-copy rule.

A new L-29/N paper receipt, scanner/copy log, media checksum or original cassette image would create a testable bridge. Without one, inventing a byte operator from ticket names or ACK status would be retrospective.

Original source, mask, route, acceptance, verifier and canonical candidate remain untouched. K04/K08 remain missing.
