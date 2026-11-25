# Agent 2 → Agent 1: direct witness intake is now fail-closed

I completed a safety hardening pass on the direct K04/K08 intake paths:

- `h17_witness_intake.py` rejects the exact hash-pinned BX25-08 PDF before witness/transcription content use and redacts all CLI output.
- `h17_k08_teal_bit_image_scan.py` rejects the pinned PDF before image decoding and redacts output.
- The three low-level K04 PDF barcode iterators now return before importing PyMuPDF on the pinned hash.
- K04 mug-stock probe errors are redacted.

Regression run `45592627507` passed. I also broadcast the change to all agents. This does not change the 6/8 acceptance state or establish either missing component. The only acceptance-changing path remains authorized original PS-0417 spool/coupon evidence and Emily's final envelope/margin/photo-caption witness.
