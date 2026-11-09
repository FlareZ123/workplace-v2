# K04: ACK-only printer issuance model, whole-packet GF(2^128) interpolation

**Agent42 | 9 November 2026 | Source-derived complete-coupon negative, six originals still PASS.**

## Source stage choice and relationship to predecessors

The 128 regular five-minute PS-0300..0427 print records are all **ACK1**. The following five exceptional log rows are of two distinct statuses: PS-0417 **REQUESTED1**, PS-0417 **ACK2** (historical K04 selector), PS-0417 **REQUESTED3**, PS-0448 **ACK1**, PS-0420 **ACK2**. The predecessor [Agent4 whole-packet GF(2^128) interpolation](h17-k04-128-plus-five-systematic-rs-original-holdouts-20261109.md) treated every logged late row, including unacknowledged requests, as one consecutive field output; tested two coordinate grids and eight source presentations, all target and historical ACK holdouts failed.

This investigation isolates a different physical-issuance hypothesis: a printer coupon is committed to a field stream **only on an ACK**, with REQUESTED-but-unacknowledged entries consuming zero codeword positions. Then the surviving 128 ordinary ACK packets map to inputs0..127 and the **three** exceptional ACKs map to output positions128..130. A second model uses the original recorded UTC minutes: inputs0,5,...,635, and late ACK output positions **662 (18:02 selected)**, **684 (18:24 ESC-S)**, **685 (18:25 spare)**. The recorded REQUESTED-only moments 661 and663 are never incorrectly counted as printed coupons.

The source does not attest that the printer operated a polynomial encoder, that ACK is the actual generation event, or that no randomness was consumed for REQUESTED. The difference is a falsifiable, status-aware complete-coupon alternative to Agent4's log-entry-count model.

## Exact original-source reconstruction

Use the unchanged source print log SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Each complete 16-byte ordinary packet is one element of `GF(2^128)`, reduced modulo the conventional polynomial `x^128+x^7+x^2+x+1`. Treat original 128 elements as evaluations of a polynomial of degree at most127. Compute exact finite-field Lagrange interpolation values at the three **ACK-only** output indices, using batch inversions to avoid 128 independent inverse exponentiations. Apply the original recorded physical-to-component XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C` to the selected complete 16-byte output and compare all 256bits of the original K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Exactly **eight** distinct complete producer assignments: two ACK-only index geometries × two whole-packet endian views × source forward/reverse. The selected raw ACK2 bytes are **never input**, and both PS-0448 and PS-0420 copied ACK payloads are withheld from the interpolation, preserving two real complete historical source controls.

## Original outcome and reproducibility

| Source/acceptance test | Actual |
| --- | ---: |
| Complete ACK-only GF(2^128) issuer assignments | **8** |
| Canonical-width 16-byte selected K04 components | **8** |
| Exact historical ACK holdout matches, independently retained 16-byte PS-0448 and PS-0420 | **0 / 16** |
| Original selected K04 full-SHA256 acceptance matches | **0 / 8** |
| Planted source-to-three-ACK whole-field polynomial positive controls | **6 / 6 PASS** |

The successful synthetic controls use independently seeded degree-eight GF(2^128) polynomial coefficients, fit only the 128 source-point outputs, and exactly reconstruct all three withheld ACK target values under both coordinate grids. Full original intact-source ZIP hash `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7` is checked in ZIP mode. The same original execution with extracted source gives identical results.

[Reproducible standard-library ACK-only SFT](../agents/agent42/k04_gf128_ackonly_sft.py), run from repository root with optional original ZIP/directory argument, includes self-checking exact original counts, source and routing SHA/fields, and the full polynomial/field operations. No original evidence, route, acceptance, verifier, or canonical candidate was changed.

## Decision and surviving alternative

The **ACK-only** issuance correction is a legitimate separate stage mapping because REQUESTED does not prove a job printed. It is therefore important to distinguish this from merely re-running the previous 128+5 field interpolation. Nonetheless, the **complete original late ACK records reject every tested exact 128+3 GF(2^128) interpolation**, even before the selected K04 commitment negative. The alternative 128+3 prime-field interpolation on three odd moduli independently fails 0/48 whole original ACK checks and 0/16 canonical selected candidate commitments; see [Agent42 full-coupon prime-field report](h17-k04-primefield-128plus5-fullcoupon-original-holdouts-20261109.md).

These failures do **not** rule out a producer that consumes hidden state for REQUESTED, a nonlinear encoder, independent physical payload production, a true original copy-stage fault, or unarchived equipment state. They give no authenticated original selected K04 bits. K01/K02/K03/K05/K06/K07 PASS; K04 and K08 MISSING, REC8/1 combined INCOMPLETE.
