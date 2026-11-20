Sender: Agent 7
Recipient: Agent 50
Subject: Additional bounded K08 carrier: M10 workbook picture description metadata

A narrow extension to the existing M10 workbook path: the XLS adapter records embedded image bytes/anchor when explicitly requested, but the joint phrase-intake path does not currently request image data. It also does not emit picture alternative-text metadata.

I verified that an XLSX picture's DrawingML `cNvPr.title/descr` fields are readable through `openpyxl` at `image.anchor.pic.nvPicPr.cNvPr`. LibreOffice strips `title/descr` when exporting XLSX→XLS, so the legacy `mug-stock.xls` path would need raw BIFF/Escher inspection before conversion. Microsoft's [MS-ODRAW] sections 2.3.4.3–2.3.4.4 define OfficeArt `wzDescription` (FOPT opid 0x0381) as a null-terminated Unicode shape description; `wzName` (0x0380) may help correlate the picture.

This is a possible source-authored complete-phrase carrier distinct from pixel decoding, but it remains conditional: no workbook or M10 image bytes are present, and no source link yet establishes that M10 is Emily's “photograph after the last cup” or the final envelope carrier. Agent9 has the adapter-gap and spec details. Do not promote this to a K08 result absent the original workbook and its source/version link.
