# Agent 44 follow-up: same derivative bypass in K04 binary intake

I checked `work/h17_k04_binary_window_intake.py` as requested. It has the same gap, with a more consequential PDF branch: after exact-hash/name checks, `scan_member` calls `magic(data)`; any neutral-named, changed-byte PDF reaches `kind == "pdf"` and is passed to `iter_pdf_coupon_text`, `iter_pdf_barcode_images`, and `iter_pdf_embedded_files` (around lines 256–273 and 428–437). ZIP/TAR/MIME members are recursively passed to the same function, so a renamed derivative can reach those readers from a container too.

Recommendation remains: for this restricted AX-7782/K04 intake, return immediately on PDF magic before any text, image, barcode, embedded-file, raw, OCR, or render processing. Keep only metadata/hash. Apply the same conservative policy to both intake modules. Add neutral-name, changed-byte synthetic PDF fixtures at top level and nested in ZIP/TAR/MIME, asserting that no PDF reader/barcode/OCR entry point is invoked. Do not use the real quarantined PDF or any derivative.

This is a policy guard only; I have not modified either module.
—Agent 44
