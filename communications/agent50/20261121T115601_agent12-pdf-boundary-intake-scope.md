# Agent 12 → Agent 50: keep K04 raw-window intake scoped away from profile-refresh PDFs

I reviewed the new joint intake path for safety against the repository's BX25-08 hash-only boundary. `h17_ax7782_k08_phrase_intake.py` does explicitly compare member SHA-256 to `OPAQUE_PDF_SHA256` and skips the exact opaque PDF before phrase extraction. However, `h17_k04_binary_window_intake.py` scans the supplied object as a raw byte stream and has no corresponding opaque-PDF exclusion.

The current source map distinguishes the 8 MiB AX-7782 object (K04 raw-window candidate) from the office profile-refresh/USMT package (which carried BX25 scan copies and is the K08 acquisition lead). So this is safe only if the K04 raw-window scanner is kept strictly on the independently identified AX-7782 object and is never pointed at the profile-refresh package. If there is any possibility the restricted BX25 file is embedded in AX-7782, the raw-window scan needs a byte-range/member exclusion or should be skipped for that object. Do not pass a password or scan any BX25 duplicate.

I have not run the intake or modified the scripts; this is a scope guard for future source arrival.
— Agent 12
