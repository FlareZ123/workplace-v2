# K04: bounded CCITT T.4 Group-3 Modified-Huffman copy-stage test

**Agent 43 · 13 November 2026 · complete-candidate attempt**

## Question

Could the selected PS-261003-0417 attempt-2 ACK payload be a one-dimensional CCITT T.4 Group-3 Modified-Huffman representation of a single 128-pixel coupon line, with the decoded 128-bit raster being the original 16-byte coupon?

The source motivation is crew note N22: the label printer had spent another morning "thinking it is a fax machine". The payload is explicitly opaque binary. This is a narrow codec hypothesis, not evidence that the printer actually used fax encoding.

## Frozen method

The source-pinned implementation is `agents/agent43/k04_t4_mh_1d_copy_stage_sft.py`; the preregistration is `agents/agent43/20261113T1536_k04_t4_mh_preregistration.md`.

- Exact selector: PS-261003-0417, attempt 2, ACK, RECOVER, 16-byte PAYLOAD.
- Standard CCITT MH terminating codes 0..63 and 64/128 makeup codes; alternating white/black runs, starting with the white run (which may be zero); exactly 128 output pixels.
- Finite framing: forward/reversed payload byte order; MSB/LSB fill order; optional EOL prefix/suffix with 0..7 zero fill bits; 0..7 trailing zero pad bits; both pixel polarities and output bit packing.
- Candidate construction: pack decoded pixels into 16 bytes, XOR the unchanged K04 route mask, compare to the unchanged K04 SHA-256 commitment.
- No 2D reference row, guessed codewords, arbitrary bit edits, candidate padding, or official-source mutation.

The exact source pins were checked: spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, N22 notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, route `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`, acceptance `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

## Result

**Result: no valid decode.**

- Synthetic controls: 256 deterministic random 128-pixel rows round-trip exactly through the pure-standard-library MH encoder/decoder; half include an EOL prefix. A fixed independent Pillow/libtiff Group-3 strip fixture (13-byte stream, EOL + alternating 8-pixel runs + four zero pad bits) also decodes exactly.
- Declared framing/polarity parameterizations: 10,368.
- Selected source payload: `A9A9DC5731A5E2AE879C47215C2559D5`.
- Strict valid 128-pixel decodes: **0**.
- Complete 16-byte coupon candidates: **0**.
- K04 commitment comparisons reached: **0**; no candidate or accepted component was produced.

A preliminary, unregistered Pillow/libtiff wrapper was lenient and returned raster-like outputs for several orientations, but none hit K04. Those permissive outputs are excluded from the result; the strict codeword parser is the registered test.

## Interpretation and limits

The selected payload is not a valid one-line 128-pixel T.4 Group-3 1D Modified-Huffman stream under the declared standard framing set. This closes only that exact one-line 1D model. It does not test multi-line strips, 2D coding, other fax codecs, a different raster width, or an independently evidenced physical copy-stage transform. There is no eligible historical same-role raster holdout, so synthetic round-trips validate the decoder implementation, not the historical producer.

No original source, route, candidate, acceptance commitment, or verifier was changed. K04 remains unresolved; K08 is unaffected.
