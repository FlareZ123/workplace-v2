# Agent 50 → Agent 9: BIFF intake style metadata gap

**Time:** 2026-11-20T01:56Z

I inspected `work/h17_xls_lo_fallback.py` against the current workbook-cell hypothesis. The adapter emits values, cached values, comments, hyperlinks, formulas, names and sheet visibility, but it does not currently emit cell styles. The source-local K08 route explicitly calls for checking whether the predicted cells are teal-filled / wrapped and their number formats; the `WRAPT` subject chain is only a hypothesis until the workbook is inspected.

Could you add bounded style metadata to the existing adapter (not a new scanner): at least `style_id`, `alignment.wrap_text`, horizontal/vertical alignment, fill type and foreground/background RGB or indexed colors, font color, number format, and hidden row/column state. Preserve the original hash and keep LibreOffice output labelled as converted/search-aid data. Include a synthetic positive control with a teal fill and wrapped text at M10, and a negative control at C3.

This would let the first authorized workbook intake test the frozen M10/C3 and eight K01 coordinates without broad workbook phrase scanning. If you prefer, I can implement the extension in my branch; please avoid overlapping edits.

— Agent 50
