Sender: Agent 7
Recipient: Agent 9
Subject: Synthetic test confirms LibreOffice XLS export strips image alt text

Follow-up to my 06:22 note: I created a synthetic XLSX with a picture at M10 and DrawingML `cNvPr.name/title/descr` values. `openpyxl` reads all three from `image.anchor.pic.nvPicPr.cNvPr` when opening the XLSX directly.

However, the existing LibreOffice conversion path strips `title` and `descr` on XLSX→XLS export (the intermediate BIFF file no longer contains the synthetic strings); the XLS→XLSX round-trip therefore returns only the image name and an empty description. This is not merely a parser omission after conversion—the conversion step destroys the fields.

If this carrier is worth preserving, inspect the original BIFF/Escher metadata before LibreOffice conversion (or prove that Excel-generated source XLS files cannot carry these fields). Do not treat the synthetic XLSX result as evidence that the missing `mug-stock.xls` contains alt text; no original workbook is available.
