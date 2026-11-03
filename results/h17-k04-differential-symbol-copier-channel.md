# K04: exhaustive short-symbol differential copier serialization tests

**Agent18 | 3 November 2026 | Original target NO_MATCH, no K04 coupon recovered.**

## Different complete-component copy hypothesis

The copied original printer buffer for the 18:02 ESC-N RECOVER attempt-2 ACK lacks independent physical integrity verification. A standard serial-data possibility is that bytes were stored under a *differential* or NRZI-like representation, where adjacent data symbols are XORed, differenced, integrated or accumulated. Such transformations can change every byte through one simple operation and need not preserve the multiset of bits/bytes, so they are outside prior bit-raster, byte-lane permutation, repeated short XOR and global nibble-codebook tests.

The original source does **not** assert NRZI, differential byte addition or any physical codec. We test a sharply scoped family because an exact commitment hit would produce the full component, with the source file otherwise unchanged.

## Frozen complete transforms

Start with the original copied ACK `A9A9DC5731A5E2AE879C47215C2559D5`, original XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C` and original commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

- Stage: independently apply the transform to **copied payload**, the 16-byte route **mask**, or their existing **XOR-reduced component**.
- Symbol widths: **1, 2, 4, 8, 16, 32** bits, keeping total 128-bit coupon length fixed.
- Direction: forward or backward across the symbol array; retain source assignment to each output position.
- Symbol interpretation: normal binary or bit-reversed per symbol.
- Arithmetic and operation: adjacent **XOR** or addition/subtraction modulo `2^width`; apply **encoding/differencing** or **decoding/accumulation**.
- Boundary: first previous symbol **zero** or the original immediately preceding symbol; start at each cyclic symbol origin independently.

All `3×32×(128+64+32+16+8+4)=24,192` stage-and-codec assignments were checked with full K04 slot SHA256. **0 original hits** among **7,110 distinct complete 16-byte components**. Original target, original route and copied ACK are held fixed.

[Executable source-pinned SFT](../agents/agent18/k04_differential_codec_sft.py) checks spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` and exact ACK selector before search. An independently planted right-to-left, nonzero-origin, 8-bit modular-additive cumulative decoding with wraparound previous-symbol boundary gives **one full SHA256 positive assignment**. The source-equivalent local script completed and asserted all exact counts. These controls verify the entire transform/reduction path, not any historical printer codec.

## Decision boundary

This eliminates only the specified differential coding family when applied to one of three listed source layers. It does not exclude a run-length-based restoration, separately missing physical paper coupon, a modified mask, unknown producer key or other transformation. It yields zero independently authenticated K04 selected bits, and K08's exact final caption remains unavailable. **K01,K02,K03,K05,K06,K07 PASS; K04,K08 MISSING; combined INCOMPLETE.** All original source and acceptance files remain untouched.
