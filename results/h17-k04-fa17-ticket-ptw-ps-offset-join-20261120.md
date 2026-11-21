# FA-17 ticket → PTW offset join: +304 is strongest; PS suffix presence is non-discriminating

**Status:** source-supported inference, not an explicit foreign key. This does not recover K04.

## Question

Can the five FA-17 North binder tickets be joined to singleton PTW permit IDs using a stable numeric offset, and does the same arithmetic say anything useful about PS jobs? Earlier K04 work used +304 as a candidate locator. The earlier offset scanner was not actually reading the supplier folio field: the CSV header is `folio_or_jacket`, not `folio`. Its LV-42 and ST-09 control folios were also wrong.

## Method

- Read `evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv`, keeping only `POSTED` rows.
- Read `evidence/maintenance/seal-receipts.jsonl`; define the 27 singleton PTW permits 390–416 by their one signed receipt and recorded bay.
- Read `evidence/print/spool-reconstruction.log`; collect observed PS job suffixes.
- Scan offsets +200 through +400. Score the North FA-17 set by PTW coverage, distinct-bay coverage, and the independent L28 FA-17 PTW holdout. Report PS-job suffix presence separately as a low-discrimination observation. Use the correct control groups: L29/S LV-42 folio `CS-18/5`; Watch ST-09 folio `STORES/FLT`.
- Preserve the print-fleet register's North binder order: ST-094, ST-081, ST-106, ST-099, ST-112.

The corrected executable is `agents/agent12/st_ptw_ps_offset_scan.py`.

## Result

Within the bounded +200..+400 scan, +304 is the strongest PTW-permit/bay result. PS-job suffix presence does not add independent support:

| Group at +304 | PTW coverage | PTW bay coverage | PS-job suffix presence (not discriminating) |
|---|---:|---:|---:|
| L29/N FA-17 (5 tickets) | 4/5 | 4 distinct bays (A–D) | 5/5 |
| L28 FA-17 holdout (2 tickets) | 2/2 | 2 distinct bays | 2/2 |
| L29/S LV-42 control (5 tickets) | not in PTW 390–416 window | — | 1/5 |
| Watch ST-09 control (2 tickets) | not in PTW 390–416 window | — | 0/2 |

Nearest alternatives show why the L28 holdout matters: +300 also maps 4/5 North tickets to four bays and 5/5 to PS jobs, but only 1/2 L28 tickets to PTW permits; +309 and +310 map 4/5 North tickets but cover only three distinct bays. +304 is the only top-scoring offset that combines 4/4 North bays with the 2/2 L28 PTW holdout.

### North binder-order arithmetic predictions (PS suffixes not authenticated)

| Ticket | +304 PTW ID | PTW evidence | Arithmetic PS suffix if +304 were applied (not authenticated) |
|---|---:|---|---|
| ST-094 | 398 | PTW-398, bay A | PS-0398 |
| ST-081 | 385 | no PTW receipt in this export | PS-0385 |
| ST-106 | 410 | PTW-410, bay B | PS-0410 |
| ST-099 | 403 | PTW-403, bay C | PS-0403 |
| ST-112 | 416 | PTW-416, bay D | PS-0416 |

### L28 PTW holdout (PS suffixes not authenticated)

- ST-087 → PTW-391 bay C; arithmetic suffix 0391 falls within the retained PS range but is not a validated ticket→job link.
- ST-098 → PTW-402 bay A; arithmetic suffix 0402 falls within the retained PS range but is not a validated ticket→job link.

The +304 PTW mapping is not merely a fit to the five North tickets: both older L28 FA-17 tickets independently land on singleton PTW records. The apparent PS-job suffix coverage is not a discriminator: a frozen scan found 97 of 201 offsets already give 5/5 North and 2/2 L28 PS-job presence because the retained spool suffixes are dense. The different-account controls do not rescue that PS-presence statistic as a ticket→job foreign key.

## ST-112 version resolution and PS-0416 boundary

The source-authored filing reference resolves the supplier revision for the registered PS-0417 return:

- The print-fleet return register identifies PS-261003-0417 as ESC-N / L-29/N / FA-17 with filing reference `H17-POL-17/A3`.
- The binder index identifies L-29/N tab05 as ST-112.
- The supplier CSV has ST-112 R3 `POSTED` / FA-17 / `H17-POL-17/A3`, and a separate ST-112 R4 `HELD` / FA-17 / `H17-POL-17/A4` row explicitly described as a duplicate settlement.

The exact A3 reference therefore joins the registered PS-0417 return to the posted R3/A3 row, not the held R4/A4 duplicate. This is stronger than the numeric +304 inference and supports retaining PS-0417 as the selected route/job. It does not establish the native output bytes or prove that the dispatch-log payload is the physical coupon.

The +304 join maps ST-112 to PTW-416 (bay D). The arithmetic suffix 0416 is not evidence that ST-112 maps to PS-0416; PS-job presence is non-discriminating. Do not infer a ticket→PS-0416 link. The return register separately names PS-0417 for the L-29/N set, while PS-0416 is a distinct spool job.

The selected PS-0417 spool sequence remains LABEL/ACK at 16:45Z, RECOVER/REQUESTED at 18:01Z, RECOVER/ACK at 18:02Z (attempt 2), and RECOVER/REQUESTED at 18:03Z. The route selects attempt 2. Its payload XOR the published mask still fails the unchanged K04 commitment. The A3 version join resolves the supplier revision/producer-selection ambiguity but does not recover the coupon bytes.

## K04 consequence and limits

The four PTW records reached through the North join provide one signed serial per bay A–D. Their raw 16-byte blocks, in A-B-C-D and B-D-A-C order, were tested as direct and route-mask-XOR candidates; neither matches the K04 acceptance commitment. Additional bounded hash/MAC, lane assembly/permutation, and transition tests also produced no K04 match. Thus the offset join improves record linkage but does not reveal the coupon bytes.

The decisive missing evidence remains the native PS-0417 spool object or an independently preserved copy/image of the physical coupon. The selected dispatch-log payload is explicitly marked integrity-unverified; its last-ACK value XOR the route mask does not satisfy the K04 commitment.

## Reproduction and next action

Run:

```bash
python agents/agent12/st_ptw_ps_offset_scan.py /path/to/workplace-v2
```

Next, authenticate the original North return index and native PS-0417 queue/job manifest. Do not treat arithmetic suffix 0416 as a PS-job mapping, expand arbitrary payload permutations, or treat +304 as source-authored fact.
