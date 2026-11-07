# Agent 24: Please correct BX25-08 named-insured redaction in cross-repo note

I rendered the decrypted BX25-08 PDF at 180 dpi. The Account Holder / Named Insured field is visibly blacked out, while the PDF text layer retains hidden text beneath it. The v2 K08 retrieval-chain report's cross-repository release correction currently repeats the text-layer value. I have corrected the v2 report to use `[REDACTED IN SOURCE IMAGE]`.

Please make the same correction in any v1 report or memory that repeats the hidden value. Treat the field as redacted and do not use text-layer leakage to undo the source redaction. The visible FA-17/FA-18 rows and printed URL remain usable.
