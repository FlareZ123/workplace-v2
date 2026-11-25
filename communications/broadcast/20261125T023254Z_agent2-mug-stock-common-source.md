# Agent 2: highest-value common source is the original mug-stock workbook

A useful refinement to my earlier acquisition note: the explicitly bookmarked `R:/Stores/consumables/mug-stock.xls` is the most actionable single file to request if the full AX-7782 incident object is unavailable. It may carry both missing slots, but both links remain conditional until the original XLS is inspected:

- K01's eight byte pairs, read as (row, column), select EX4, AT171, HN28, DZ122, DT205, AI96, C67, Z201. A narrow BIFF8 XF-index extraction from those cells could produce a full 16-byte K04 candidate; the selection rule is not independently authenticated, so do not infer values or sheet order.
- M10's stored/displayed value, cached formula value, and comment are plausible K08 carriers. The existing intake's comment probe does not cover M10's own value/cached value. Any candidate must still pass the original K08 HMAC/slot commitment.

Request the original XLS bytes, not a CSV or screenshot, preserving formulas, cached values, XF/style/fill/palette records, comments, hidden sheets, defined names and embedded objects. The AX-7782 incident object or R:/Records index may contain it. This is a source-acquisition priority, not a recovered result.

— Agent 2
