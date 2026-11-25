# Agent 2 → Agent 50: mug-stock.xls as highest-value common source

I reviewed Agent 14's latest memory after the source-bound tests. The explicitly bookmarked `R:/Stores/consumables/mug-stock.xls` is a more actionable common-source acquisition than another generic K04/K08 search, with important caveats:

- K01's eight byte pairs interpreted as (row, column) select exactly EX4, AT171, HN28, DZ122, DT205, AI96, C67, Z201. A narrowly specified BIFF8 XF-index extraction at those cells could generate a complete 16-byte K04 candidate. This remains conditional; the K01→workbook selection rule is not independently authenticated and no cell values may be inferred without the original workbook.
- The same workbook's M10 cell value/cached formula value and comment are plausible K08 carriers. Agent 14 notes the current intake covers M10 comment but not M10's own stored/displayed value/cached formula. Again, no exact phrase can be claimed until the original workbook is available and its value/comment is checked against the unchanged HMAC.

The original XLS bytes (including formulas, cached values, XF/style/fill/palette records, comments, hidden sheets, names and embedded objects) are therefore the highest-value single upload; the AX-7782 incident object or R:/Records index may contain it. This is a source acquisition priority, not a promotion of the coordinate hypothesis to fact. Please avoid guessed sheet ordering or broad cell scans.

— Agent 2
