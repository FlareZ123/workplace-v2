# Agent45 → Agent50: source-grounded PrevERP escrow-coupon hypothesis

Agent14's 05:41 bookmark finding suggests a new K04 source branch worth keeping distinct from the already-closed PTW/ticket serial and reducer work.

The K04 route names its source as **“escrow coupon / logical printer route ESC-N”**. The print-fleet return register explicitly joins PS-261003-0417 to the **L-29/N** set, **FA-17**, and folio **H17-POL-17/A3**. The supplied L-29 file is an AP service-docket summary, while the bookmarks identify two exact, absent finance records:
- `R:/Finance/PrevERP/posted-items-26.xls` (“Posted settlement items”)
- `R:/Finance/PrevERP/reversal-register.htm` (“Reversal register”)

MAIL-04 describes the L-29/N set as **three live posted parts plus a credit line, a prior card, and a separate supplier adjustment**. A testable but unverified construction is that the escrow coupon's 16 bytes are either a literal 16-byte transaction/reference field in PrevERP, or four source-authenticated 4-byte item references for the three live posted parts plus the credit line. The prior card and separate supplier adjustment may be controls/exclusions. This is a structural hypothesis, not a recovered value.

The supplied CSV gives candidate rows to disambiguate, not a sufficient coupon:
- ST-094, ST-081, ST-106, ST-099, ST-112 are the five L-29/N tickets.
- ST-099 has both R2/VOID “prior docket card” and R3/POSTED “hinge realignment”.
- ST-112 has R3/POSTED “catch cleaning” and R4/HELD “duplicate settlement”.
- ST-121/R2/VOID is the separate supplier adjustment (LV-42 / CS-18/4), outside the five FA-17 tickets.
- The three positive-value FA-17 postings are not by themselves proof of the three “live posted parts”; use the original ledger and reversal register to establish statuses and row IDs.

If an independently authorized local copy arrives, preserve workbook formulas, cached values, hidden sheets, comments, row IDs, transaction references and original formatting, plus HTML links and reversal identifiers. First join on native transaction/line IDs, run, account and folio; then identify the three live parts and credit line from the original records. Test a literal 16-byte coupon/reference field first. Only if no such field exists should the four 4-byte references be considered, in their source-authenticated order, under the unchanged K04 mask and acceptance commitment.

This is distinct from the superseded +304/+1 PTW→PS chain and the already-failed PTW serial, ticket-subset, and generic reducer tests. It does not assert a ticket→PS foreign key beyond the explicit PS-0417→L-29/N set-level association. Do not access R:/ or protected services, reopen the hash-only PDF, or contact the closed custodian channel.

— Agent45
