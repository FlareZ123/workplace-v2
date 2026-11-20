# FA-17 ticket → PTW/PS offset join: +304 is the strongest empirical mapping

**Status:** source-supported inference, not an explicit foreign key. This does not recover K04.

## Question

Can the five FA-17 North binder tickets in the print-fleet return register be joined to PTW permit IDs and print-spool job IDs using a stable numeric offset? Earlier K04 work used +304 as a candidate locator but correctly treated it as unverified. The earlier offset scanner was not actually reading the supplier folio field: the CSV header is `folio_or_jacket`, not `folio`. Its LV-42 and ST-09 control folios were also wrong.

## Method

- Read `evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv`, keeping only `POSTED` rows.
- Read `evidence/maintenance/seal-receipts.jsonl`; define the 27 singleton PTW permits 390–416 by their one signed receipt and recorded bay.
- Read `evidence/print/spool-reconstruction.log`; collect observed PS job suffixes.
- Scan offsets +200 through +400. Score the North FA-17 set by PTW coverage, distinct-bay coverage, North PS-job coverage, and the independent L28 FA-17 holdout. Use the correct control groups: L29/S LV-42 folio `CS-18/5`; Watch ST-09 folio `STORES/FLT`.
- Preserve the print-fleet register's North binder order: ST-094, ST-081, ST-106, ST-099, ST-112.

The corrected executable is `agents/agent12/st_ptw_ps_offset_scan.py`.

## Result

Within the bounded +200..+400 scan, +304 is the strongest combined result:

| Group at +304 | PTW coverage | PTW bay coverage | PS-job coverage |
|---|---:|---:|---:|
| L29/N FA-17 (5 tickets) | 4/5 | 4 distinct bays (A–D) | 5/5 |
| L28 FA-17 holdout (2 tickets) | 2/2 | 2 distinct bays | 2/2 |
| L29/S LV-42 control (5 tickets) | not in PTW 390–416 window | — | 1/5 |
| Watch ST-09 control (2 tickets) | not in PTW 390–416 window | — | 0/2 |

Nearest alternatives show why the L28 holdout matters: +300 also maps 4/5 North tickets to four bays and 5/5 to PS jobs, but only 1/2 L28 tickets to PTW permits; +309 and +310 map 4/5 North tickets but cover only three distinct bays. +304 is the only top-scoring offset that combines 4/4 North bays with the 2/2 L28 PTW holdout.

### North binder-order mapping

| Ticket | +304 ID | PTW evidence | PS job |
|---|---:|---|---|
| ST-094 | 398 | PTW-398, bay A | PS-0398 |
| ST-081 | 385 | no PTW receipt in this export | PS-0385 |
| ST-106 | 410 | PTW-410, bay B | PS-0410 |
| ST-099 | 403 | PTW-403, bay C | PS-0403 |
| ST-112 | 416 | PTW-416, bay D | PS-0416 |

### L28 holdout

- ST-087 → 391: PTW-391 bay C and PS-0391.
- ST-098 → 402: PTW-402 bay A and PS-0402.

The +304 mapping is not merely a fit to the five North tickets: both older L28 FA-17 tickets independently land on singleton PTW records and PS jobs. The different-account controls do not show comparable PS coverage.

## Important ST-112 exception and unresolved versioning

The return register separately states that **PS-0417** was charged to L-29/N tab05 ST-112. The supplier export contains ST-112 R3 POSTED/A3 and R4 HELD/A4 rows. The +304 join maps ST-112 to PTW-416 / PS-0416, while the explicit return-register reference maps it to PS-0417 (+305). The print-spool log contains both PS-0416 (RECOVER/ACK) and PS-0417 (LABEL/ACK followed by RECOVER attempts); the latter's last ACK is attempt 2.

Do not silently equate PS-0416 and PS-0417, or collapse ST-112 R3/A3 and R4/A4. The return register's A3 filing reference does not cleanly resolve the R4/A4 duplicate. The +304 result is an empirical join; the source still lacks an explicit ticket→job foreign key.

## K04 consequence and limits

The four PTW records reached through the North join provide one signed serial per bay A–D. Their raw 16-byte blocks, in A-B-C-D and B-D-A-C order, were tested as direct and route-mask-XOR candidates; neither matches the K04 acceptance commitment. Additional bounded hash/MAC, lane assembly/permutation, and transition tests also produced no K04 match. Thus the offset join improves record linkage but does not reveal the coupon bytes.

The decisive missing evidence remains the native PS-0417 spool object or an independently preserved copy/image of the physical coupon. The selected dispatch-log payload is explicitly marked integrity-unverified; its last-ACK value XOR the route mask does not satisfy the K04 commitment.

## Reproduction and next action

Run:

```bash
python agents/agent12/st_ptw_ps_offset_scan.py /path/to/workplace-v2
```

Next, resolve the ST-112 R3/R4 ↔ PS-0416/PS-0417 discrepancy from an independent return-register or native spool record. Do not expand arbitrary payload permutations or treat +304 as source-authored fact.
