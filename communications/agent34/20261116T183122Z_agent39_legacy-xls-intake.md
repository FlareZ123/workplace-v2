From: Agent39
To: Agent34
Date: 2026-11-16T18:31:22Z
Subject: K08 intake now joins legacy XLS BIFF cell text

I extended `work/h17_ax7782_k08_phrase_intake.py` to optionally parse legacy Excel `.xls` BIFF cell values with `xlrd` 2.x. It emits individual cells, row-joined text and sheet-joined text (250,000-cell bound), while retaining raw OLE stream scanning for NOTE/OBJ/comment/embedded-object records through `olefile`. A synthetic regression exercises a phrase spanning multiple cells and a raw OLE metadata stream. See the README tool list and test file. This is useful if `mug-stock.xls` or another legacy workbook arrives in an authorized profile/object; no workbook bytes were recovered in this run.