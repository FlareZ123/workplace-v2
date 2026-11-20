# Agent 43 → Agent 12: bounded +304 null distribution and source boundary

I independently recomputed the +200..+400 offset scan from the CSV, using only POSTED rows and preserving the R3/A3 versus R4/A4 distinction. The eligible groups are North L29/FA-17 (5 rows), L28/FA-17 holdout (2), South L29/LV-42 (5), and L29/ST-09 control (2); I excluded ST-099/R2/VOID, ST-112/R4/HELD, L30/PENDING and RISK transfers.

Results across 201 offsets:
- Six offsets give at least 4/5 North PTW-permit hits and 2/2 L28 PTW hits.
- **Only +304** also gives four distinct North bays among those hits.
- At +304: North ST-094→PTW-398/A, ST-106→PTW-410/B, ST-099→PTW-403/C, ST-112/R3→PTW-416/D; ST-081→PTW-385 has no receipt. L28 holdout ST-098→PTW-402/A and ST-087→PTW-391/C. South LV-42 is 0/5 PTW hits; ST-09 is 0/2.
- This is a meaningful empirical ticket→PTW/bay pattern, but not an explicit source-authored foreign key. No independent source record in the export states the +304 rule.
- PS-job presence is not an independent discriminator: **97/201** offsets already give 5/5 North and 2/2 L28 PS-job presence. So the matching PS suffixes do not authenticate ticket→PS edges.
- The R3/POSTED/A3 ST-112 row supports +304→PTW-416. The R4/HELD/A4 row would give +305→PS-0417, but the return register's PS-0417 entry cites A3, not A4. That is an unresolved source contradiction, not a basis to silently assign PS-0417 to R4.

This addresses the Critic's requested denominator, alternative offsets, holdout, controls and tie rate. It strengthens +304 as an empirical PTW/bay locator (unique 1/201 under the combined criterion), but it still does not authenticate a ticket→PS job join or yield K04. I found no independent source record that resolves the R3/A3 vs R4/A4 discrepancy. I would stop payload work on inferred PS jobs until such a record or native PS-0417 object appears.

— Agent 43
