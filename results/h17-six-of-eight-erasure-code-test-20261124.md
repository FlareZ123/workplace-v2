# Six-of-eight erasure-code hypothesis: bounded negative result

**Date:** 2026-11-24  
**Researcher:** Agent14  
**Scope:** K01, K02, K03, K05, K06, K07 are the six commitment-verified 16-byte components; K04 and K08 are the two unresolved components.

## Question

Can the two missing components be reconstructed from the six accepted components by treating the eight slots as a conventional six-of-eight erasure code, rather than following the source-specific K04 and K08 routes?

This was a structurally motivated hypothesis: exactly two of eight 16-byte slots remain unresolved. It is not evidence that the archive actually uses erasure coding.

## Method

The probe at [`work/h17_erasure_code_probe_20261124.py`](../work/h17_erasure_code_probe_20261124.py) reads the existing `candidate.json` and `resources/acceptance.json`. It emits only trial counts and commitment-match booleans; it never prints candidate component bytes.

The bounded search covered:

1. **Byte-wise generalized Reed–Solomon/Shamir interpolation over GF(256).**
   - All 30 irreducible degree-eight binary polynomials.
   - Consecutive slot abscissas 0–7 and 1–8.
   - Primitive-power abscissas α^i for every primitive element in every field, with both zero- and one-based exponents.
   - 15,480 candidate-slot trials.

2. **Word-wise interpolation over GF(2^16).**
   - All 4,080 irreducible degree-sixteen binary polynomials.
   - Eight 16-bit symbols per component, both big- and little-endian interpretations.
   - Consecutive slot abscissas 0–7 and 1–8.
   - 32,640 candidate-slot trials.

3. **Whole-block interpolation over GF(2^128).**
   - The standard GHASH field polynomial (x^{128}+x^7+x^2+x+1).
   - Big- and little-endian interpretations, plus whole-block bit reversal.
   - Consecutive slot abscissas 0–7 and 1–8.
   - 16 candidate-slot trials.

4. **Systematic six-data/two-parity constructions.**
   - XOR P parity and weighted Q parity over GF(256), including both possible parity-slot assignments.
   - Recovery of missing K04 when K07 is treated as P or Q, followed by verification of the other parity slot as K08.
   - Cauchy 6+2 parity constructions using consecutive zero- and one-based x/y choices, including cases where K07 is the surviving parity symbol.
   - 38,883 candidate-slot trials.

Every reconstructed 16-byte value was checked against its own SHA-256 slot commitment. No candidate bytes were written to the repository or printed by the probe.

## Result

**No K04 or K08 commitment matched.** The tested conventional binary-field interpolation, primitive-power Reed–Solomon, systematic RAID-6 P/Q, and bounded Cauchy constructions do not explain the six surviving components.

This is a bounded negative result, not proof that no custom linear code or source-specific relationship exists. In particular, it does not test arbitrary secret generator matrices, undocumented coordinate assignments, or a nonstandard encoding.

## Research consequence

Do not keep expanding generic finite-field or parity-code variants without a source-derived reason for a different field, coordinate map, or generator matrix. The source-defined routes remain the best-supported recovery paths:

- **K04:** obtain an authenticated native PS-0417 RECOVER queue/spool record or the physical escrow coupon and its source register. The reconstructed spool ACK alone does not establish media integrity.
- **K08:** obtain the original keeper-envelope face/margin, the final desk-note version, or authenticated photo-caption sidecars. The surviving notes establish the intended theme, not the final wording.

The absent `mug-stock.xls` workbook remains a conditional intake lead only; this experiment does not establish that it contains either missing component.

## Integrity

- No changes to `candidate.json`, `resources/acceptance.json`, source evidence, or verifier behavior.
- No K04/K08 candidate values, partial credentials, or derived recovery material were committed.
- Re-run from the repository root with `python work/h17_erasure_code_probe_20261124.py`.
