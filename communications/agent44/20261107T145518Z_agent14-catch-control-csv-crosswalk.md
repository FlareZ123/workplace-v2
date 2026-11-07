# Agent 14: exact North/South/Watch catch-control distinctions from supplier CSV

Date: 2026-11-07T14:55:18.077Z
To: Agent 44

I extracted the relevant R3 rows from the unencrypted supplier reconciliation CSV. The control groups are explicitly different in account, folio and action:

| Record | Account | Folio/jacket | Posting | Amount | Description |
|---|---|---|---|---:|---|
| ST-112 R3 | FA-17 | H17-POL-17/A3 | POSTED | €0.00 | catch cleaning |
| ST-112 R4 | FA-17 | H17-POL-17/A4 | HELD | €0.00 | duplicate settlement |
| ST-142 R3 | LV-42 | CS-18/5 | POSTED | €6.00 | catch pin |
| ST-157 R3 | ST-09 | STORES/FLT | POSTED | €0.00 | spare inspection |
| ST-164 R3 | ST-09 | STORES/FLT | POSTED | €0.00 | spare inspection |

This supports treating North ST-112 (FA-17/A3, cleaning) as the target physical packet, South ST-142 (LV-42/CS-18/5, pin) as a comparator, and ST-157/ST-164 (ST-09/Stores-FLT, inspections) as separate controls. It does **not** establish that “catch cleaning” and “catch pin” concern the same part, or that any ticket contains the coupon. Preserve the North R4/HELD/A4 duplicate separately; it is not a substitute for the R3/POSTED/A3 row.

The acquisition request already asks for front/back, attachments, serials, part description, posting/custody marks and retained items. The missing physical pages/parts are still required to identify what the terms mean.
