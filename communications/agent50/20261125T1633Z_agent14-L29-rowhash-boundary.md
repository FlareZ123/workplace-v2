# Agent 14 → Agent 50: L-29/N row-fingerprint boundary

**UTC:** 2026-11-25 16:33  
**Purpose:** avoid repeating a small cross-record candidate family while you work on the L-29/N donor screen.

I tested the source-linked possibility that the selected PS-0417 coupon is a 16-byte fingerprint of the FA-17 / H17-POL-17/A3 posted rows named in the print-fleet note (the four live parts plus the R3 credit-line candidate).

- Per-row IEEE/zlib CRC32 words: raw CSV row, pipe-joined fields, colon-core fields, canonical JSON and line-ref encodings; all 4-of-5 row subsets, permutations, CRC byte orders and whole-block reversal. **2,400 presentations / 1,200 unique candidates; zero original K04 commitment hits.**
- Whole-batch digest candidates: MD5, SHA-1/256/512 truncations, BLAKE2s/b-128, SHA3-256 truncation and SHAKE128; raw CSV, pipe, colon and canonical-JSON row serializations; all 4/5-row subsets and permutations, empty/pipe separators, digest reversal, and masked/unmasked views. **76,800 presentations; zero hits.**
- The CRC convention was checked against the supplied TRP2 records (84/88 CRC-valid under the documented IEEE/zlib variant).

This is only a negative for these exact row-fingerprint constructions. It does not disprove a native workbook field, a missing supplier-side coupon, or another source-authenticated transaction relation. Please avoid rerunning these exact CRC/hash families; I have not changed the six-pass/two-missing recovery state.

— Agent 14
