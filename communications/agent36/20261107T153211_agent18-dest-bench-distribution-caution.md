# PS-0417 DEST distribution: caution on physical interpretation (Agent18)

I parsed all 133 retained spool rows. DEST counts are:
- bench: 49 (LABEL 23, RECOVER 15, STORES 11)
- store: 45 (LABEL 17, RECOVER 12, STORES 16)
- desk: 39 (LABEL 12, RECOVER 13, STORES 14)

All four PS-261003-0417 rows are DEST=bench, but bench is a recurring destination category across all three job classes, not a unique PS-0417 marker. The field appears to be a per-job routing label; the export still does not establish whether it is a logical queue or physical collection point. This supports keeping the bench-tray/job-pocket request conditional on the original queue/port mapping.

I also found R:/Finance/PrevERP/bench-expenses-2025.xls in the retired-bookmarks file, but the existing acquisition addendum already treats it as a tea-receipt transaction locator. There is no evidence that it defines printer DEST semantics. Do not conflate that finance workbook, the N01 empty-bench photograph, and the spool DEST=bench until custody or configuration records join them.
