# Agent45 correction: PrevERP source attribution and four-reference hypothesis

I need to correct my earlier note and README wording. I incorrectly attributed the “three live posted parts plus a credit line, a prior card, and a separate supplier adjustment” classification to MAIL-04. Agent14 is right: `evidence/mail/04.eml` is Simon's PTW-417 bay-order/closeout email; it says nothing about L-29/N or PrevERP. Please disregard my MAIL-04 attribution and the preselected four-row ST-094/ST-081/ST-106/ST-112 constructor.

The source-grounded facts are narrower:
- `print-fleet-retirement-note.txt` explicitly maps PS-261003-0417 / ESC-N to L-29/N, FA-17, H17-POL-17/A3 and lists five tabs in order: ST-094, ST-081, ST-106, ST-099, ST-112.
- `supplier-reconciliation-L29.csv` has three positive-value North postings (ST-094, ST-106, ST-081), plus zero-value POSTED North rows ST-099/R3 and ST-112/R3; it also has ST-099/R2 VOID (“prior docket card”) and ST-112/R4 HELD (“duplicate settlement”).
- The South set includes ST-151/R3 POSTED “guide shim credit” (LV-42/CS-18/5) and ST-121/R2 VOID “supplier adjustment” (LV-42/CS-18/4). These are not L-29/N rows.
- No supplied source labels a specific North row as the “credit line” or defines a four-reference coupon assembly. Do not invent that classification or transfer MAIL-04's PTW bay order to the binder.

The **PrevERP acquisition lead remains valid**, but only as a request to inspect the original `posted-items-26.xls` and `reversal-register.htm` for native transaction IDs, row references, revision/status history, and any literal 16-byte coupon/reference field. The renewal ledger may corroborate the FA-17/H17-POL-17/A3 folio. A four-reference construction is conditional on the originals actually defining such a tuple; it is not presently source-supported. No K04 value is recovered.

— Agent45
