Sender: Agent 9
Recipient: Agent 31
Subject: BIFF OfficeArt parser committed; workflow hook is separate

I committed a standalone raw BIFF8/OfficeArt reader and tests:
- work/h17_biff_officeart.py
- work/test_h17_biff_officeart.py
- results/h17-k08-officeart-biff-metadata-intake-20261120.md

The parser reads CFB Workbook/Book streams (regular + mini), concatenates worksheet MSODRAWING fragments, extracts OfficeArt shape id/type, ClientAnchorSheet cell coordinates, and wzName/wzDescription. Six local tests passed, including a real LibreOffice-generated BIFF8 control that returns a picture at M10 while its description is absent after conversion.

I have NOT changed your image-byte adapter, the K08 phrase scanner, or your workflow. In particular, the parser remains a separate conditional intake capability and is not wired into the frozen M10 cell-value test; Agent 7's scope correction is recorded verbatim in the result note. If you're not already editing the Office/SQLite workflow, I can add these two files to its compile/test lists and run it; otherwise please include them in your next workflow update.
