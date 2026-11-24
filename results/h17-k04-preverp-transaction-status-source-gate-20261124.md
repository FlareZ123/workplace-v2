# K04: PrevERP transaction-status source gate for the L-29 return sets

**Status:** source-derived classification and retrieval lead; no coupon value or construction recovered.

## Question

Do the retained L-29 records establish a complete set of live posted item references that can be used to construct the 16-byte ESC-N escrow coupon?

## Sources inspected

- `resources/evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt` — maps PS-261003-0417 to ESC-N / L-29/N / FA-17 / H17-POL-17/A3 and lists the five North tabs in binder order: ST-094, ST-081, ST-106, ST-099, ST-112. It separately maps PS-261003-0448 to South L-29/S and PS-261003-0420 to WATCH-SPARE.
- `resources/evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv` — AP service-docket extract; its preamble says run values identify vendor settlement batches and credit entries retain earlier versions.
- `resources/evidence/mail/04.eml` — Simon's PTW-417 closeout bay-order email. It concerns the B/D/A/C witness walk and seal-rack closeout; it does **not** describe L-29 binder tabs, a credit line, prior card, supplier adjustment, or “three live posted parts.”

## Relevant CSV rows

| Ticket | Run / posting | Account / folio | Amount | Description |
|---|---|---|---:|---|
| ST-094 | R3 / POSTED | FA-17 / H17-POL-17/A3 | €18.40 | lid-plate labour |
| ST-081 | R3 / POSTED | FA-17 / H17-POL-17/A3 | €4.20 | guide rail |
| ST-106 | R3 / POSTED | FA-17 / H17-POL-17/A3 | €12.50 | separator fitting |
| ST-099 | R2 / VOID | FA-17 / H17-POL-17/A2 | €0.00 | prior docket card |
| ST-099 | R3 / POSTED | FA-17 / H17-POL-17/A3 | €0.00 | hinge realignment |
| ST-112 | R3 / POSTED | FA-17 / H17-POL-17/A3 | €0.00 | catch cleaning |
| ST-112 | R4 / HELD | FA-17 / H17-POL-17/A4 | €0.00 | duplicate settlement |
| ST-151 | R3 / POSTED | LV-42 / CS-18/5 | €0.00 | guide shim credit |
| ST-121 | R2 / VOID | LV-42 / CS-18/4 | €0.00 | supplier adjustment |
| ST-121 | R3 / POSTED | LV-42 / CS-18/5 | €7.60 | separator replacement |

The South set also contains ST-130, ST-135 and ST-142; Watch-Spare has ST-157 and ST-164. The complete CSV contains additional risk inward-transfer and L28/L30 control rows.

## What is and is not established

1. The three positive-value North postings are ST-094, ST-081 and ST-106. This fact alone does **not** establish that these are the only three live parts: ST-099 R3 and ST-112 R3 are also marked POSTED at zero value.
2. ST-099 R2 is explicitly a VOID prior docket card; ST-112 R4 is a HELD duplicate settlement.
3. ST-121 R2 is a VOID supplier adjustment on the South LV-42 / CS-18/4 account. ST-151 is a South LV-42 / CS-18/5 guide-shim credit.
4. The exact “three live parts + credit line” selection, the relevant transaction-reference fields, and their source-authenticated order are **not established by the supplied CSV**. In particular, the credit entry is ST-151 on the South set, not one of the five North tabs.
5. No 16-byte transaction/reference field is present in the supplied CSV. No four-reference coupon candidate was constructed or tested.

## Interpretation

The bookmarked PrevERP records `R:/Finance/PrevERP/posted-items-26.xls` and `R:/Finance/PrevERP/reversal-register.htm` are a bounded source-side join because the original workbook/HTML may preserve native transaction IDs, row references, posting state, account/folio, reversal lineage and revision history omitted by the AP extract. They may also reveal whether the four-reference hypothesis has any basis. This is a retrieval target, not evidence that a four-reference construction is correct.

Do not attribute the binder classification to MAIL-04; that message is the PTW-417 closeout. Do not assume the three positive-value North rows plus the South credit form the coupon, or promote ticket suffixes into a foreign key.

## Next evidence

If an independently authorized local copy appears, preserve the native workbook's formulas, cached values, hidden sheets, comments, row IDs and transaction references, plus the reversal register's original links and transaction identifiers. Join by native transaction/line IDs, run, account and folio; resolve revision and reversal status before considering any 16-byte field or ordered 4×4-byte references. Keep all five North tabs and the South/Watch-Spare controls intact.

No R:/ access, protected-service probing, custodian contact, K04 candidate, or acceptance change was performed.


## Conditional four-reference hypothesis (not source-established)

The print-fleet note's North tab order is ST-094, ST-081, ST-106, ST-099, ST-112. One possible construction, **only if the original PrevERP ledger and physical binder confirm the row roles**, is a 16-byte coupon formed from four native 4-byte transaction/reference fields for tabs 01, 02, 03 and 05 in that order (three live parts plus a tab-05 credit line), excluding tab 04's prior-card history. This is Agent45's bounded structural hypothesis, not a current finding: the supplied CSV labels ST-112 R3 as catch cleaning and R4 as a held duplicate, not as a credit; the visible guide-shim credit is ST-151 on the South set. The original records must resolve this apparent discrepancy before any four-reference candidate is assembled. Test a literal 16-byte coupon/reference field first; do not substitute ticket suffixes or infer that four references exist.
