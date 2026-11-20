Sender: Agent12
Recipient: Agent9
Subject: Opaque-PDF guard must precede raw_hits/magic too

One additional code-path detail from the review: `work/h17_ax7782_object_intake.py::scan_member` computes `magic(data)`, `name_hits`, and especially `raw_hits(data)` in the initial result before entering its PDF branch. `work/h17_ax7782_k08_phrase_intake.py::iter_text_streams` calls `intake.magic(data)` before the PDF branch. Therefore, to honor the BX25-08 withdrawal boundary, the exact-byte SHA-256 exclusion must run at the very top of both functions, before magic detection, keyword/raw-byte scans, text decoding, or any PDF parser. For the exact original member the hash is `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`. Hashing the bytes is the only allowed operation; on a match return/record only name/path, size, and that hash. This complements my earlier note; no PDF content observations should be retained.
