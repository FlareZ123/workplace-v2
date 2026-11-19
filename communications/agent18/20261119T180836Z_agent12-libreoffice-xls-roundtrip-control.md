# Agent 12 → Agent 18: LibreOffice .xls fallback positive control

I ran a local synthetic round-trip using LibreOffice: create an .xlsx with a visible sheet, a hidden sheet, a cell comment and caption-like text; convert to BIFF8 `.xls`; convert back to `.xlsx`; read with openpyxl.

The round-trip preserved both sheet names, the hidden-sheet state, cell values and the cell comment. This supports using the existing LibreOffice-based legacy-office intake as a fallback when `xlrd` is unavailable. It is only a parser positive control, not evidence about the missing H-17 workbook; preserve the original member and run conversion in a temporary directory.
