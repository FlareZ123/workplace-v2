# K04: 16-bit serial scrambler, complete-codebook exhaustive test

**Agent 18, 3 November 2026. Original commitment NO_MATCH.** The six previously verified slots remain accepted; K04/K08 remain unresolved and combined REC8 INCOMPLETE.

## Alternative physical readback channel

The selected original 3 October ESC-N `PS-261003-0417` RECOVER attempt-2 ACK at 18:02 UTC has unverified physical coupon integrity. The original crew note N22 describes the printer as behaving “like a fax” in ordinary conversation; this is an informal scene clue, **not** engineering documentation of a data link.

This test considers whether a *single additive 16-bit linear-feedback shift register (LFSR) scrambler* inverted all 128 serial data bits between original coupon and recovered spool fragment. Unlike previously exhausted one-to-four-byte faults, periodic XOR, global hex-glyph substitution and raster scan permutations, an LFSR's 128-bit error stream can change virtually every byte while being determined by only 16 state bits.

The copy transformation is `original_coupon = copied_ACK XOR LFSR_keystream`; the original K04 route's XOR mask remains unchanged. The five hypothesized feedback polynomials are `0x1021` (CRC16 CCITT), `0x8005` (IBM), `0x3D65` (DNP), `0x8BB7` (T10-DIF) and `0xC867` (CRC16-CDMA2000). Test both left/right shift with reciprocal polynomial, both within-byte bit emission orderings and forward/reversed byte order, each over **all 65,536 initial 16-bit states**. The selected 16-byte copied buffer is exactly `A9A9DC5731A5E2AE879C47215C2559D5`, the unchanged mask `8556C8CB6140A7F9A5123AC7571BEE1C`, and original K04 SHA256 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Computation and controls

The source-pinned [read-only single-file reproducer](../agents/agent18/k04_lfsr_scrambler_sft.py) authenticates spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` and selected ACK selector. All 128 keystream bits are **linear functions of the 16-bit seed**, so precompute the 16 single-bit basis streams and walk the entire 16-bit seed space in Gray-code order, toggling only one precomputed basis stream per seed. Every resulting 16-byte candidate is checked against the **original unchanged full SHA256 slot digest**.

| Calculation | Result |
| --- | --- |
| Feedback polynomials | 5 |
| Recurrence directions × bit orders × byte orders | 8 |
| All 16-bit initial seeds | 65,536 each |
| Original masked complete K04 digest checks | **2,621,440** |
| Original K04 matches | **0** |
| Planted nonzero-seed full coupon recovered | **1**, seed `A53D` under CCITT/left/MSB/forward |

The exact locally executed source-equivalent Python script completed in 2.22 seconds and passed all assertions. A planted independent artificial digest under a nonzero scrambler state is found exactly once within its named four-parameter branch, proving the real code explores the intended family and hashes the correct full coupon. The checked-in version differs only by resolving the `resources` input path relative to the GitHub checkout.

## Limits

This **excludes the specified 16-bit LFSR serial-link channel family** under unchanged copied ACK, byte-composition order and XOR mask. The original company archive contains no confirmed serial-link polynomial or evidence that an additive scrambler was applied. A 32-bit scrambler, per-byte nonlinear error correction, a different producer, a damaged mask or an original paper coupon entirely unlike the retained ACK remains outside the tested family. The commitment hit rate cannot authenticate source bytes without a hit.

No originally authenticated K04 selected bit, K08 final caption word or additional verifier PASS has been obtained. Original sources, verifier, commitments and canonical candidate were left unchanged.
