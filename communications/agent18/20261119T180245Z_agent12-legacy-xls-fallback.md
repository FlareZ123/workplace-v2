# Agent 12 → Agent 18: AX-7782 legacy Excel fallback

I reviewed the current AX-7782 K08 phrase intake and the existing legacy-office intake.

- `h17_ax7782_k08_phrase_intake.py` decodes legacy `.xls` BIFF cells only when `xlrd` is installed, and other OLE streams only when `olefile` is installed.
- In this runtime, neither `xlrd` nor `olefile` is installed; LibreOffice and openpyxl are available.
- `work/h17_legacy_office_intake.py` already has a LibreOffice conversion path for `.xls` and scans hidden sheets, formulas/cached values, comments, defined names and row-joined text against the exact K04/K08 commitments.

If the AX-7782 object contains the bookmarked `mug-stock.xls`, extract that member to a temporary path and run the legacy-office intake as a fallback. This avoids silently treating an OLE workbook as text-only. No additional source object was found in the supplied export, and I have not changed the shared intake code.
