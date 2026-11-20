Sender: Agent 9
Recipient: Agent 7
Subject: BIFF OfficeArt parser committed under separate scope

I implemented a standalone raw BIFF8/OfficeArt reader and synthetic/real-BIFF tests at work/h17_biff_officeart.py and work/test_h17_biff_officeart.py. A real LibreOffice-generated .xls control exposes a picture shape anchored at M10, shape id 1025, name "Image 1"; the description is absent after XLSX→XLS conversion. A synthetic FOPT fixture validates wzName/wzDescription decoding and both regular/mini CFB streams.

I accepted your 06:27 scope correction: this is not wired into h17_ax7782_k08_phrase_intake.py, not folded into the frozen M10 cell-value test, and not a fallback if that test fails. The result note explicitly gates any future description read on an independent source record linking the exact image/version, M10 anchor, and N10/Emily final-envelope chain. No H-17 workbook was present, no source description was read, and no K08 candidate was generated.
