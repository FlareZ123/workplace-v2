# K04: systematic parity-fragment inverse construction across QR/DataMatrix-style GF(256) models

**Agent 3 | 12 November 2026 | original K04 commitment: zero matches**

## New construction

The historical printer was a label printer, and its retained 16-byte payload is acknowledged only as a dispatch field, not independently checked against physical media. As an exploratory alternative, interpret the copied 16-byte word as a **mixture of original coupon data and its systematic Reed–Solomon parity**. This is different from an RS(16,8) packet-syndrome gate: the presumed original message is the complete 16-byte coupon, and the hypothetical full codeword has length 16+p, where p parity symbols have replaced p data symbols in the recovered 16-byte fragment.

Given any p parity symbols and 16-p consecutive intact data symbols, GF(256) parity is a full-rank linear system for the p missing message symbols. Invert that system, reconstruct all 16 physical coupon bytes, and compare SHA256(coupon XOR original mask) to the original K04 SHA256 commitment. As an explicitly alternative masking-stage hypothesis, also compare SHA256(coupon) to the unchanged original K04 commitment.

## Original observations and complete model

Pinned source: resources/evidence/print/spool-reconstruction.log, SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Canonical selected ACK2 retained fragment: A9A9DC5731A5E2AE879C47215C2559D5. Official mask: 8556C8CB6140A7F9A5123AC7571BEE1C. Original target: 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

- GF(256) primitive polynomials 0x11D (QR-style) and 0x12D (DataMatrix-style); generator first roots 0 and 1.
- Parity count p = 1 through 16; all p+1 distinct placements of the contiguous 16-p original data bytes (one placement for p=16).
- Both original/reversed data and parity byte orders; both fragment section orders. Redundant byte-order variants are suppressed for p=16.
- Six preserved printer packets: same job PS-0417 earlier LABEL ACK (index 117), RECOVER REQUESTED1 (128), selected RECOVER ACK2 (129), RECOVER REQUESTED3 (130), ESC-S ACK (131) and WATCH-SPARE ACK (132).

**All 4,328 model layouts** exactly recovered an independent planted entire 16-byte message from its encoded partial copy. Across the six historical inputs this yielded **25,968 complete 16-byte coupon presentations**, with **51,936 exact original K04 SHA256 comparisons** (with and without the official mask), **zero matches**. This is a completed full-candidate investigation, not a new original physical-coupon bit.

## Scope

This result excludes precisely the specified partially retained, contiguous-data/full-parity RS(16+p,16) models and source presentations. It does not show the actual printer used barcode ECC or that its historical fragment combines parity and data; the genuine route rule still requires the physical coupon itself. Prior source-only RS(16,8) codeword-rank checks are a different format hypothesis and also fail. No K08 words or seventh accepted component were obtained.

**Reproducer:** agents/agent3/k04_rs_partial_codeword_sft.py (Python 3 standard library). No source, commitments, official verifier, or canonical candidate were edited.
