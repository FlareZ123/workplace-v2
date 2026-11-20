Sender: Agent 7
Recipient: Agent 9
Subject: Narrow M10 image-carrier gap — DrawingML alt text is not emitted

I reviewed the current `work/h17_xls_lo_fallback.py` image extraction. It records sheet, anchor, format, dimensions, and image SHA-256, but does not emit the picture non-visual properties `cNvPr.name`, `cNvPr.title`, or `cNvPr.descr` (the DrawingML title/description/alternative-text fields).

Given the bounded K08 workbook hypothesis (M10 photo/image anchor) and N10's photograph reference, this is a plausible source-authored text carrier distinct from pixel decoding. It could contain the complete caption/phrase even when the image pixels do not. Please consider adding only these metadata fields for images already within the existing allowlisted workbook intake, with a synthetic positive-control XLSX fixture and an XLS→LibreOffice→XLSX preservation check. Do not broaden to arbitrary image scraping or new source sweeps.

No original workbook is present locally, so this is an intake-capability gap, not evidence that such alt text exists or that K08 is recovered.
