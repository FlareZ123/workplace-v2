# Agent 11: follow-on K08 carrier-decoding correction

The K08 scanner now decodes conventional hex and Base64 carriers as UTF-16LE/BE when the decoded bytes have a BOM or sufficient NUL structure. The previous code decoded these carriers as UTF-8 only, which could miss PDF-style hex text or Base64-wrapped UTF-16 text.

A positive regression covers hex-encoded UTF-16BE and Base64-encoded UTF-16LE; both recover the exact phrase and reach the original K08 commitment check. A bounded corrected pass over all 46 supplied ZIP files plus the ten decrypted BX25-08 PDF page-content streams evaluated 129 text variants and found zero K08 hits. The full committed scanner suite has not yet been run end-to-end in this shell.

The 8 MiB AX-7782 object/profile source remains absent; no component or acceptance status changed. Details are in results/h17-k08-intake-correctness-and-snapshot-hardening-20261114.md.
