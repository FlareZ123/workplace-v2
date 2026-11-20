# Agent 12 — North-ticket offset validation (K04 join)

A source-field bug in `agents/agent12/st_ptw_ps_offset_scan.py` was masking the ticket groups: the CSV header is `folio_or_jacket`, and the LV-42 / ST-09 folios are `CS-18/5` and `STORES/FLT`. I corrected the script and re-ran the bounded +200..+400 scan against the local export.

Within that scan, +304 is the strongest empirical join:
- L29/N FA-17: 4/5 tickets map to four distinct singleton PTW bays (A-D); all 5/5 map to PS jobs.
- L28 FA-17 holdout: 2/2 tickets map to PTW permits and PS jobs.
- L29/S LV-42 control: only 1/5 map to PS jobs; Watch ST-09: 0/2.
- North binder-order mapping: ST-094 -> PTW-398 / PS-0398 (bay A); ST-081 -> PTW-385 (no receipt) / PS-0385; ST-106 -> PTW-410 / PS-0410 (bay B); ST-099 -> PTW-403 / PS-0403 (bay C); ST-112 -> PTW-416 / PS-0416 (bay D).

This is strong cross-source support for +304 as an inferred FA-17 ticket join, not an explicit source-authored foreign key. Important exception: the return register separately maps PS-0417 to ST-112; the supplier extract has ST-112 R3 POSTED/A3 and R4 HELD/A4, while +304 maps ST-112 to PTW-416 / PS-0416. Do not silently collapse PS-0416 and PS-0417 or the R3/R4 versions. The A3 folio in the return register also does not align cleanly with the R4/A4 duplicate row.

I tested the resulting four-bay serial blocks and several bounded complete-output constructions (direct/masked blocks, hashes, HMAC/AES, CRC, lane assemblies/permutations); none matched K04. The offset finding improves the source join but does not solve the coupon. The next valuable action is to resolve the ST-112 R3/R4 ↔ PS-0416/PS-0417 relationship from an independent source record, then obtain the native PS-0417 spool/coupon. Avoid expanding ungrounded payload permutations.
