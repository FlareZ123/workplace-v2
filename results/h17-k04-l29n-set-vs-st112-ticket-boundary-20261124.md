# K04: L-29/N set versus ST-112 ticket boundary

**Date:** 2026-11-24T04:27:22.237Z

## Question

Does tab05 ST-112 identify the physical coupon or native media for PS-0417?

## Evidence

- The retained print-fleet retirement note lists five L-29/N binder tabs: ST-094, ST-081, ST-106, ST-099 and ST-112. The return-register relationship preserved in the source is **PS-0417 → L-29/N set**; it does not select ST-112 as the job's individual ticket.
- The supplier reconciliation contains ST-112 R3/POSTED/FA-17/H17-POL-17/A3 and a separate R4/HELD/A4 duplicate. These identify a docket and comparison record, but the supplied CSV is not the original physical ticket or coupon.
- Agent43's +304 analysis supports a strong empirical **ST-ticket → PTW permit/bay** mapping: within the frozen +200..+400 scan, +304 is the only offset with at least 4/5 North PTW hits, four distinct bays, and 2/2 L28 PTW holdout hits. It maps ST-112 to PTW-416, bay D.
- The same +304 result does **not** establish a ticket→PS-job join. In the frozen 201-offset scan, 97 offsets already produce 5/5 North PS-job presence and 2/2 L28 PS-job presence because the spool export contains a dense, nearly continuous PS-261003-0300..0427 run. The PS-job hit count is therefore non-discriminating. The explicit PS-0417→L-29/N set-level entry remains the only supported PS relationship.
- Agent43 also tested the four +304-mapped serials in the documented B/D/A/C order, XORed with the K04 mask; the resulting candidate does not match the immutable K04 commitment.

Primary analysis: [Agent43 +304 PTW-vs-PS review](../communications/agent12/20261120T222115Z_agent43-plus304-ptw-vs-ps-review.md). The ST-112 ticket/bay boundary was also sent to Agent35 in [this note](../communications/agent35/20261120T222402Z_agent43-st112-plus304-boundary.md).

## Conclusion

ST-112 is a member of the L-29/N return set, not an authenticated ticket-level foreign key to PS-0417. The earlier synthesis that singled out the ST-112 docket as the “most specific” PS-0417 physical target was too strong and has been corrected.

The complete five-tab L-29/N binder and native return index remain a reasonable physical retrieval lead because the register links the set to PS-0417. Preserve ST-112 R3 and R4 as part of that set, but do not substitute either for the full binder, the native PS-0417 queue/media, or the physical coupon.

## Next action and limits

If an independently authorized local copy becomes available, retrieve all five tabs and the native return index, including front/back images, receipts, inserts, carbonless underlays, print strips, coupons and barcodes. Continue to require native PS-0417 job/host evidence for any ticket-level mapping.

Do not expand the +304 offset into a PS-job mapping, use the 0417 suffix as a foreign key, or run more ticket-offset arithmetic. No K04 component was recovered by this analysis; the original source and acceptance commitment remain unchanged.


## Bounded source-order serial candidate: binder tab A/B/C/D

The +304 mapping provides four signed, CLOSED, AS_LEFT PTW receipts among the five L-29/N tickets:

| L-29/N tab | Ticket | Empirical PTW mapping | Serial |
|---|---|---|---|
| 01 | ST-094 | PTW-398 / bay A | 0AEF4A08 |
| 02 | ST-081 | PTW-385 / no receipt | — |
| 03 | ST-106 | PTW-410 / bay B | F8C5E995 |
| 04 | ST-099 | PTW-403 / bay C | CCCCF4B8 |
| 05 | ST-112 | PTW-416 / bay D | 0C814A5E |

The L-29/N binder's tab order therefore supplies one concrete A/B/C/D order for the four available serials. Concatenating the four 4-byte serial values in that order gives coupon candidate `0AEF4A08F8C5E995CCCCF4B80C814A5E`. Applying the official K04 XOR mask gives component `8FB982C399854E6C69DECE7F5B9AA442`, whose SHA-256 is `468d6493a22a93b667b8b2f77bf21103a4b650316be3ebf604e738ff0d1fb938`, not the K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

For comparison, the MAIL-04 B/D/A/C witness order yields raw serial payload `F8C5E9950C814A5E0AEF4A08CCCCF4B8`, masked component `7D93215E6DC1EDA7AFFD70CF9BD71AA4`, and SHA-256 `e6fb90e2c728abc336af6cd5050710d498eb90bbae7ecb2dd94e62b05fa36609`, also not the K04 commitment. These are the two source-derived orders; this is not an exhaustive permutation search and does not establish a coupon source. The empirical +304 ticket→PTW mapping is not a ticket→PS-job foreign key.
