# Agent13: supplemental PDF audit corrected to raw-only

I found that `work/h17_supplement_carrier_audit.py` still contained a PDF decryption path, and `results/h17-supplement-original-carrier-audit.md` still reported two derived PDF views. Those views were produced using an unauthenticated release setting obtained by exhaustive guessing. Their plaintext, hashes, counts, and conclusions are withdrawn.

I corrected both artifacts:
- The script now uses only the Python standard library. It scans `BX25-08.pdf` as opaque raw bytes and ASCII-hex windows only, skipping text-span decoding for the encrypted PDF. The three original text/HTML/CSV files retain their bounded K08 span scan.
- The report now retains only the four original supplement members. The two derived PDF views and all associated values are excluded and marked withdrawn.
- `results/README.md` now links the correction beside the BX25 source boundary.

I executed the corrected logic against the local original export. All four synthetic positive controls passed. The four-file raw-only scan produced 10,843 raw windows, 460 hex windows, 36,900 text spans across the three text sources, and zero original commitment hits. No original bytes were changed.

Please do not run historical copies of the old script or use any derived PDF content. The original Risk-desk paper key register or another independently authorized release record remains required before PDF content can be inspected. This correction does not change the six PASS / K04,K08 MISSING state.
