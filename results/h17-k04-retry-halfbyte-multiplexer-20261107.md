# K04: source retry *half-byte* copier reconstructions, 215,233,605 complete original checks

**Agent36 | 7 November 2026 | authentic K04 commitment NO_MATCH; source selected coupon still unobserved.**

## New target-reaching hypothesis

The retained spool has three original `PS-261003-0417` `RECOVER` job records: attempt1 REQUESTED, attempt2 ACK, and attempt3 REQUESTED. Agent7 previously exhausted the **43,046,721 position-preserving whole-byte mosaics** of these three records, with zero K04 commitment hits. A different possible printer-buffer reconstruction fault mixes **high and low hexadecimal half-bytes** from different attempts. This generates full coupons containing byte values impossible in the earlier byte mosaic.

This is a bounded *copy-codec hypothesis*. The evidence describes a retained-fragment print spool with unverified payload integrity; it does **not** assert half-byte copying, that REQUESTED payloads reached paper, or that the selected physical coupon is reconstructible from these three copies. The chosen small periodic patterns make a finite test possible without pretending to exhaust arbitrary nibble-level mixing.

## Original source, direct selected-stage reduction

Read the untouched original `resources/evidence/print/spool-reconstruction.log`, pinned SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Require exactly one of each `0417 RECOVER` attempt and exact ACK/REQUESTED states. Read-only source controls additionally pin the unmodified route SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` and acceptance SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

Original three attempted payloads:

- Attempt1 REQUESTED: `CD3E4F216ADB2FB180DA2AA90B33F7A4`
- Attempt2 ACK, copied and disputed: `A9A9DC5731A5E2AE879C47215C2559D5`
- Attempt3 REQUESTED: `44D53DFC29D7943A95D89371DA58EC64`

Let each selector `d[i]` be 0, 1 or 2 for the three original records, `i=0..15`. For every one of the **3^16 = 43,046,721** selector maps, assemble the sixteen coupon bytes using original source-position high and low hexadecimal nibbles from the two row selectors below:

| Model | High nibble record at byte i | Low nibble record at byte i |
| --- | --- | --- |
| repeat16_halfbyte | `d[(2*i) mod 16]` | `d[(2*i+1) mod 16]` |
| shift1_halves | `d[i]` | `d[(i+1) mod 16]` |
| different_retry_plus1 | `d[i]` | `(d[i]+1) mod 3` |
| different_retry_plus2 | `d[i]` | `(d[i]+2) mod 3` |
| shift8_halves | `d[i]` | `d[(i+8) mod 16]` |

For each complete 16-byte coupon, XOR with the **unchanged** route mask `8556C8CB6140A7F9A5123AC7571BEE1C`. Compare SHA256 of all resulting 16 component bytes against the original **full 256-bit** K04 slot commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

These models are genuinely different complete candidate classes relative to whole-byte mosaics. For example, from fixed planted selector index `1234567`, model `different_retry_plus1` yields coupon `A4393F5C39A7E4BE90DA9AA1DB35F9A5`. Its bytes at **15 of 16 positions** are absent at those positions from *all three* original source attempts, so Agent7's exhaustive original byte mosaic could never have tested it. The other four models at the same index each have at least eight such new-position byte values. This proves incremental reachability, not that the copier historically used one of these patterns.

## Completed original-data execution

The [source-pinned, read-only C SFT](../agents/agent36/k04_retry_nibble_mux_sft.c) uses OpenSSL SHA256 and checks the full original route reduction. It plants one independently defined **complete synthetic coupon hash** per model, directly generated from source records and selector index1234567; the same full enumerator must retrieve the planted candidate.

| Model | Complete original K04 candidate assignments | Full authentic hits | Exact planted hits |
| --- | ---: | ---: | ---: |
| repeat16_halfbyte | 43,046,721 | 0 | 1 |
| shift1_halves | 43,046,721 | 0 | 1 |
| different_retry_plus1 | 43,046,721 | 0 | 1 |
| different_retry_plus2 | 43,046,721 | 0 | 1 |
| shift8_halves | 43,046,721 | 0 | 1 |
| **Total** | **215,233,605** | **0** | **5** |

Executed locally on the genuine uploaded 46-file preservation ZIP extraction with source SHA pins and five planted successes. These are **candidate assignments**, not 215m distinct coupons; cross-family and within-family duplicate values were not deduplicated. Reproducible original source revision and C code were committed with an independently confirmed exact Git blob, and the same local compiled code was rerun after a source-reading modernization without changing any candidate geometry or conclusions.

## Boundary

These five position-coupled original retry *nibble multiplexer* classes produce **zero accepted K04 components**, so they provide no original paper coupon byte. A freely position-varying choice of three source nibbles at each of 32 half-byte positions, an independent full coupon, a printer producer transformation, or physical evidence absent from the export remains untested. With no original witness for a half-byte copier, another arbitrary stripe layout lacks justification; prefer an actual selected-stage source.

Original accepted slots remain K01, K02, K03, K05, K06, K07; K04 and K08 missing; combined REC8/1 INCOMPLETE. Original archive evidence, verifier, acceptance commitments and canonical candidate remain unchanged.