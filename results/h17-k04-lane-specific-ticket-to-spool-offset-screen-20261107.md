# K04 lane-specific ticket-to-spool offset screen

**Date:** 2026-11-07  
**Identity:** Agent 44  
**Status:** Promising locator hypothesis; not an authenticated ticket/job join and not a K04 payload recovery.

## Question

Can the five-tab North and South L-29 return packets be linked to printer jobs by a lane-specific suffix offset, with the L-28/A2 FA-17 packet and the retained spool rows serving as holdouts?

## Source anchors and derivation

The print-fleet return register identifies:

- `PS-261003-0417` as `ESC-N / L-29/N / FA-17 / H17-POL-17/A3`, with tab 05 `ST-112` (catch, clean).
- `PS-261003-0448` as `ESC-S / L-29/S / LV-42 / CS-18/5`, with tab 05 `ST-142` (catch, retain).
- `PS-261003-0420` as a separate `WATCH-SPARE / L-29/W / ST-09` control.

The two tab-05 anchors yield composite suffix differences `417 - 112 = +305` for FA-17 and `448 - 142 = +306` for LV-42. The supplier reconciliation contains five R3/POSTED North tickets and five R3/POSTED South tickets, plus two R3/POSTED L-28/A2 FA-17 controls. R2/VOID and R4/HELD rows are excluded. The R4/HELD ST-112/A4 entry is a duplicate settlement, not a second selected North ticket.

The offsets can also be expressed as a two-stage hypothesis: the existing candidate ST→PTW relation is `+304`, followed by PTW→PS `+1` on FA-17 and `+2` on LV-42. The supplier CSV does not itself contain a PTW or PS foreign-key column. Both stages therefore remain inferred pending the original SEP26 return index or a native ticket/queue manifest.

## Predicted jobs and retained observations

| Packet | Binder tab | Ticket | Description | Candidate PS | Retained spool observation |
|---|---:|---|---|---:|---|
| North L-29/N | 01 | ST-094 | lid-plate labour | PS-0399 | ACK LABEL / store |
| North L-29/N | 02 | ST-081 | guide rail | PS-0386 | ACK STORES / bench |
| North L-29/N | 03 | ST-106 | separator fitting | PS-0411 | ACK LABEL / store |
| North L-29/N | 04 | ST-099 | hinge realignment | PS-0404 | ACK LABEL / desk |
| North L-29/N | 05 | ST-112 | catch cleaning | PS-0417 | LABEL ACK; RECOVER REQUESTED; RECOVER ACK2; RECOVER REQUESTED |
| South L-29/S | 01 | ST-130 | fastener kit | PS-0436 | absent from retained spool export |
| South L-29/S | 02 | ST-151 | guide shim credit | PS-0457 | absent from retained spool export |
| South L-29/S | 03 | ST-121 | separator replacement | PS-0427 | ACK RECOVER / desk |
| South L-29/S | 04 | ST-135 | hinge change | PS-0441 | absent from retained spool export |
| South L-29/S | 05 | ST-142 | catch pin | PS-0448 | ACK RECOVER / desk |
| L-28/A2 FA-17 holdout | — | ST-087 | old month cleaning | PS-0392 | ACK RECOVER / desk |
| L-28/A2 FA-17 holdout | — | ST-098 | old month seal | PS-0403 | ACK RECOVER / store |

The two L-28/A2 rows are independent of the two tab-05 anchors and support the FA-17 `+305` candidate: both predicted jobs are present as ACK/RECOVER rows. The South `+306` candidate has one non-anchor retained observation, ST-121→PS-0427, which is also ACK/RECOVER/desk like the ST-142→PS-0448 anchor. The other three predicted South jobs lie beyond the normal retained spool range, which ends at suffix 0427 apart from separately retained late rows; their absence is not a negative result.

The North packet's five job classes vary. That is not by itself adverse: the five tickets describe different maintenance categories. The key target-bearing observation is that the North tab-05 catch-cleaning ticket maps to PS-0417, whose selected K04 event is the RECOVER ACK2. The South tab-05 catch-pin control maps to PS-0448, also RECOVER. This is a role-specific locator hypothesis, not proof that the ticket physically carries the coupon.

## Distinguishing the two stages

The existing `+304` ticket→PTW work-order hypothesis and this `+305/+306` composite ticket→PS hypothesis need not compete. The former is supported by the PTW receipt/bay-order pattern and L-28/A2 permit holdouts; the latter proposes a further lane-specific print-job offset. A same-suffix PTW→PS comparison is a different second-stage assumption and should not be silently substituted for the `+1/+2` lane hypothesis.

Do not use the North `1/5` RECOVER count under `+305` versus `4/5` under same-suffix `+304` as a decisive rejection. Those are different joins, and the North packet contains different part categories. The L-28/A2 `+305` holdout and South `+306` same-role pair are the relevant new observations.

**PTW-stage coverage is asymmetric in the retained export:** North L-29/N has 4/5 candidate `+304` receipts (PTW-398/403/410/416 present; ST-081→PTW-385 absent); FA-17 L-28/A2 has 2/2 (PTW-391/402 present); South L-29/S has 0/5 (PTW-425/434/439/446/455 all outside the retained PTW-390..416 range). Therefore the FA-17 `PTW→PS +1` stage has two non-anchor PTW/PS holdouts, while the LV-42 `+2` stage is composite-only and has no retained PTW-level validation. The SFT now emits and asserts this coverage explicitly.

## Bounded serial-producer screen

The accompanying SFT `agents/agent44/k04_lane_specific_ticket_spool_sft.py` reproduces the source hashes, derives the two offsets from the print-fleet tab-05 anchors, enumerates the 12 North/South/L-28 predictions, and runs a narrow PTW-serial→PS-payload producer screen.

Six FA-17 controls are available through the candidate ST→PTW `+304` mapping and PTW→PS `+1` mapping: PTW-391→PS-0392, PTW-398→PS-0399, PTW-402→PS-0403, PTW-403→PS-0404, PTW-410→PS-0411 and PTW-416→PS-0417. For PS-0417 the SFT deliberately withholds the selected RECOVER ACK2 and uses only the earlier LABEL ACK as a logical-job control.

- CPython seed forms: 576 output comparisons, zero exact payload hits.
- HMAC-SHA256, BLAKE2b and BLAKE2s using four fixed serial-derived keys and three fixed source-field message forms: 216 comparisons, zero exact payload hits.

This rejects only the tested simple serial-seeded PRNG and keyed-hash producer families. It does not falsify the ticket→PTW→PS locator, because the serial need not be the spool payload's producer key. The selected PS-0417 RECOVER ACK2 payload was not used in fitting or control matching.

## Evidence integrity

Source SHA-256 values used by the SFT:

- `supplier-reconciliation-L29.csv`: `73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e`
- `print-fleet-retirement-note.txt`: `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`
- `seal-receipts.jsonl`: `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`
- `spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`

The retained spool payloads remain unverified fragments. ACK proves queue acceptance, not physical paper collection or media integrity. No coupon bytes or independent physical copy witness were recovered.

## Highest-value next evidence

1. Original `R:/Stores/returns/SEP26/index.htm` and its source schema, revision history and attachments, to authenticate the ST→PTW and lane-specific PTW→PS joins.
2. Native queue/job manifests and complete spool objects for the predicted South holdouts `PS-0436`, `PS-0441` and `PS-0457`, plus the retained non-anchor `PS-0427` and anchor `PS-0448`.
3. The FA-17 L-28/A2 control jobs `PS-0392` and `PS-0403`, and the North mapped jobs `PS-0386`, `PS-0399`, `PS-0404`, `PS-0411` and `PS-0417`. Preserve original source document path/hash and page/range, submitting user, print processor, queue, printer/device/port/route, native selector, attempt, class, destination/output tray, `.SPL/.SHD` (or equivalent), rendered output, ACK receipt and physical collection receipt. The source-document/page fields are the direct discriminator for the proposed shared page/job index.
4. The original North A3 and South CS-18/5 five-tab packets, especially ST-112 and ST-142, with both faces, attachments and underlays preserved.

Until those records authenticate the joins, keep `+305/+306` as a promising locator hypothesis. Do not treat it as a K04 selector, a payload producer, or proof that the physical coupon is attached to ST-112.
