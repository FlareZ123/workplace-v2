# K08: recover the final component from a printer packet through arbitrary 128-bit wiring

**Agent 1 | 9 November 2026 | New component-inversion method, no original acceptance.**

## Complete recovery mechanism

If the original Nxx desk/crew note and PS-(0300+xx) printer packet shared a common issuer, the printer's sixteen bytes might be an opaque rearrangement of the 128-bit HMAC component of that note. Unlike AES, whole-block GF128 or byte-affine transport, model **every one of the 128 printer output bits as an arbitrarily selected, distinct input HMAC bit XOR a constant per-wire bit**:

P[j] = H[permutation(j)] XOR pad[j].

This is an invertible channel with 128! possible source-to-output wirings and a 128-bit unknown pad. The permutation and pad are *learnt from original whole-caption/plaintext–spool pairs*, without consulting the unknown final caption or its acceptance hash. Once calibrated, invert the surviving PS-0323 packet and obtain a **complete 16-byte K08 HMAC component**, even though the true final handwritten N23 margin was never transcribed.

The original Nxx→PS-(0300+xx) association is **only a hypothesis**, detailed in [the source metadata alignment report](h17-k08-note-spool-metadata-bytechannel-holdouts-20261109.md). The original records do not assert that the entire note body was encoded into a printer payload. Also, N23 is a note about the missing margin, so its own preserved body must not be substituted for the unknown final text.

## Source controls and fitted inverse

The two immutable original source SHA256s are:

- Crew note extract: 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb.
- Printer spool: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.

For each of notes N01 through N24 except N23, reduce the note through the exact original desk-nonce HMAC16 stage. Compare two text readings: whole note body and, where a colon occurs, the actual caption following its introductory role label. This second interpretation correctly reproduces N02's independently published first-draft HMAC16 **BF889359B0303F2B2B2FD96AE841210B**.

Train a fully arbitrary bit permutation and per-wire XOR pad on **20 actual source pairs (N01..N20 ↔ PS0301..0320)**. Withhold **three entire additional original text/payload pairs (N21, N22, N24)** from fitting. For each printer output bit and every possible HMAC input bit, count the mismatches across the 20 authentic observations with or without a fixed output XOR bit; solve the minimum-total-error one-to-one assignment exactly with the Hungarian algorithm. This is a source-only 128×128 assignment and a full reversible component producer.

## Executed original result

| Metric | Full note body | Text after colon |
| --- | ---: | ---: |
| Source calibration pairs | 20 | 20 |
| Entire authentic holdout pairs | 3 | 3 |
| Minimum training bit mismatches / 2,560 | **525** | **532** |
| Zero-error possible input/output wire edges | **0** | **0** |
| Heldout bit mismatches / 384 | **183** | **184** |
| Original full K08 SHA256 matches | **0** | **0** |

For completeness, the inverse of the actual PS-0323 packet under each *best-fitting though invalid* original wiring emits two entire K08 candidates:

- Whole-body reading: BE4B7F991235A6E347E0937B20F4F02D
- Text-after-colon reading: FBA0BCE8C91FDCD574C30E7788F06893

Both fail the unchanged 256-bit official K08 commitment. Neither is asserted as a recovered historical component. The absence of even one zero-error original wire edge is decisive against an *exact common wiring* for these full-note source hypotheses, before target acceptance.

**Strong planted controls:** using the *same real 20 HMAC16 input values* rather than manufactured easy inputs, apply a seeded random full 128-bit permutation and random unknown pad to generate synthetic printer packets. The calibration recovers the valid wiring, predicts all three fully withheld synthetic note packets, and inverts a blinded synthetic N23 component **exactly** under both original text readings. Both positives PASS.

## Implications and boundary

This tests a much larger invertible transport family than the earlier four packet views, whole-block additive/AES and 16-byte-lane affine models. It still does not prove a printer ever stored note HMAC values, and the 24-note index correlation alone cannot establish that link. Other document versions, conditional device classes, nonlinear encryption, or a physical final envelope may yield a different source relationship.

**Reproduce:** [Agent1 source-pinned bitwire inversion SFT](../agents/agent1/k08_note_spool_bitwire_inverse_sft.py), using Python 3, NumPy and SciPy (linear_sum_assignment). It reads the original sources and acceptance commitments without modifying them.

The six accepted REC8 values are preserved. Authentic K04 and K08 remain unrecovered; combined REC8/1 remains INCOMPLETE.

**Nearest prior art:** [metadata-selective Nxx/PS pairing and byte-level models](h17-k08-note-spool-metadata-bytechannel-holdouts-20261109.md), [temporal affine component transport](h17-k08-temporal-note-spool-affine-holdout-20261108.md), and [AES transport](h17-k08-note-spool-relative-aes-20261109.md). This report's incremental scope is arbitrary *bit-level* bijective wiring and pad, a genuine 20-source-fit / 3-whole-holdout split, and complete blinded HMAC-component inversion.