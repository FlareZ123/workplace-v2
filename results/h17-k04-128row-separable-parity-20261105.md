# K04: 128-row separable parity transport from ordinary printer packets (5 Nov 2026)

**Agent 9, new normal invocation.** Complete original K04 target experiment, result **NO_MATCH** for the specified source-derived parity encoding. The six independently accepted K01/K02/K03/K05/K06/K07 remain unchanged. Neither the selected physical K04 coupon nor the final verbatim K08 inscription has been recovered; combined REC8/1 remains INCOMPLETE.

## Testable source mechanism

The original copied printer export has **exactly 128 ordinary five-minute JOB 0300 through 0427 ACK attempt-1 packets**, followed by five exceptional records. Each ordinary packet is **16 bytes**, giving a 128-row by 128-bit source matrix. Unlike prior [direct bit-plane stream extraction](h17-printer-bitplane-crossslot-candidates-20261105.md), this investigation asks whether the coupon is encoded as **one cross-byte XOR parity bit per ordinary row**. This models a simple strip/reducer or paper transmission parity channel, rather than a 16-byte packet, and yields a full 128-bit candidate without borrowing any disputed selected-copy byte.

For every nonempty **16-bit byte-column mask** (65,535) and every nonempty **8-bit bit-lane mask** (255), take the XOR parity of exactly the selected source bits in each of 128 chronological ordinary packets. Pack the 128 parity bits as 16 bytes in two distinct source-row bit orderings: first row as least-significant bit of the full 128-bit integer, with little-endian bytes; or first row as least-significant bit with big-endian bytes. These use the original unchanged route mask by XOR **after** packing. Compare SHA256 of each complete 16-byte reduced component against the original unchanged full K04 commitment.

The 128 original byte×bit column-vectors have **GF(2) rank 128**, measured directly from the original 128-row source matrix. Thus each nonzero outer-product byte×bit mask yields a distinct raw 128-bit stream within each packing view. This shows the producer of the data has enough apparent entropy to support many hypothetical encodings; it does not identify any authentic selector or make the parity-channel hypothesis true.

## Executed result and control

Pinned original SHA256:
- printer spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- recovery route `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`

The original mask is `8556C8CB6140A7F9A5123AC7571BEE1C` and original K04 component SHA256 is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Executed on the unmodified local surviving ZIP extraction using Python standard-library `hashlib.sha256`:

```text
65,535 byte masks × 255 bit masks × 2 packings = 33,422,850 complete original K04 SHA256 checks
authentic original K04 hits: 0
synthetic positive: byte_mask 0x3295, bit_mask 0xB4, packing=1, exactly one hit
128-by-128 source GF(2) column rank: 128
```

Original 128 JOBs are uniquely selected and the selected 18:02 RECOVER ACK2 is excluded. The synthetic target was generated from the exact same reducer but a **different planted SHA256 commitment**; it does not alter authentic acceptance. The runnable, source-pinned portable reproduction is [Agent 9's parity-carrier SFT](../agents/agent9/k04_128row_separable_parity_sft.py). Its main program implements this same two-view enumeration and asserts all cardinalities and the planted positive.

A broader reverse-within-byte packing variant was attempted locally but exceeded the execution time limit after partial enumeration. **No exhaustive result is claimed for that uncompleted variant**. Its partial output also contained zero original hits; it is omitted from the certified total.

## Consequence

This excludes a concrete **rank-one separable parity carrier**, structurally distinct from adjacent byte extraction and single-bit-plane streaming. It is **not** evidence for a real parity emitter; no original document asserts that the 128 ordinary jobs encoded the exceptional ESC-N coupon. The genuine physical selected K04 coupon remains unobserved, and the original K08 terminal caption is still absent. Do not extend to arbitrary 128-column selector masks, which can represent every 128-bit string given the observed full rank and would merely rephrase a 2^128 preimage search. A new source-defined checksum/channel-selection rule or selected-stage witness is needed to justify expansion.


## Follow-on: original-field-keyed full-rank 128×128 matrix (5 November, Agent 9)

The rank-one mask exclusion above leaves a conceptually different, **nonseparable dense-selector** possibility: the 128×128 printer source matrix may act as a linear transform with its 128-bit selector supplied by another already preserved original field. The route mask and K08 nonce are both exactly 128 bits, which supplies a source-sized selector without inventing 128 free coefficients.

Frozen source keys: K04 route mask, K08 desk nonce, six official accepted K01/K02/K03/K05/K06/K07 16-byte values, and four HMAC16 values of Emily's independently preserved N02, N06, N17 and N18 exact inscriptions under the original nonce. The correct N02 independent digest `BF889359B0303F2B2B2FD96AE841210B` is checked before candidate synthesis. For each of these **12 actual source fields**, test seven exact byte/bit/word-order views as input, four algebraically related full-rank source maps `M`, `Mᵀ`, `M⁻¹`, `(M⁻¹)ᵀ`, and both output byte orientations. The target coupon is fully determined and reduced under the official unmodified XOR mask.

The original source 128×128 GF(2) matrix was **explicitly inverted**, with all 128 pivot rows and identity reconstruction asserted. The executed original-source local test produced **12×7×4×2 = 672 full K04 candidates, zero authentic K04 commitment matches**. It also compared each produced full 16-byte coupon to **all 12 untouched source fields** as a cross-record calibration: **zero complete field-to-field matches**. A nontrivial source-mask-selected full candidate was planted under a separate SHA256 commitment and located exactly once in its expected mapping. Unlike the preceding 33.4m rank-one enumeration, this test fixes its 128-bit coefficient vector to a real surviving source object, explicitly testing both directions of the matrix rather than allowing an arbitrary free selector.

Portable source and controls: [Agent 9 dense source-keyed matrix SFT](../agents/agent9/k04_crossrow_128bit_field_matrix_sft.py). Both tests leave the original source, route, acceptance and verifier unchanged. There is still no authenticated K04 selected coupon bit or verbatim author-final K08 word. The finite negative disfavors these eight 128-bit fields and four known Emily-derived HMAC values as direct matrix selectors, with no justified extrapolation to every possible field or more complicated coding scheme.
