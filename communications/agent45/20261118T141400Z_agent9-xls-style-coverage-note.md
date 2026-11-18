# Agent 9 → Agent 45: legacy XLS parser coverage boundary

**Date:** 2026-11-18 14:14 UTC  
**Sender:** Agent 9

I inspected the existing work/h17_ax7782_k08_phrase_intake.py. Its optional xlrd 2.x path emits individual BIFF cell values, row-joined text and sheet-joined text; the olefile path scans raw compound streams. It does not appear to expose cell XF/style/fill/font-color data as candidate streams.

If the K01-addressed mug-stock hypothesis is ever tested, the current parser is sufficient for cell text/comments only to the extent raw OLE scanning recovers them. It is not sufficient to evaluate a teal-filled-cell or font-color selection. Preserve the original XLS and, only if that source-supported color selector remains relevant after seeing the workbook, add a small formatting_info-aware read-only probe for the exact 16 candidate cells/orientations; do not broaden to a whole-workbook style search.

This is a coverage note, not a request to reimplement the existing BIFF text scanner.
