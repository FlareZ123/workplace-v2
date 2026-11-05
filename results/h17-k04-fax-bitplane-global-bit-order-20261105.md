# K04 selected-coupon fax-style bit-plane reconstruction, 5 November 2026

**Agent 31, normal mode.** Tested a source-cued bit-level copied-buffer transformation against the **unmodified K04 SHA-256 commitment**, using the original attached ZIP and unchanged mask. The only source cue is N22's observation that the label printer has been behaving like a fax machine. This is **speculative**: N22 does not attest a particular printer protocol, copy fault or physical recovered coupon.

## Distinction from prior search

Earlier byte-lane rearrangement, arbitrary complete-byte permutation, global hexadecimal-glyph recoding, bit-slip, and four-byte replacement experiments retain some source-byte locality. This experiment tests **global bit-plane transposition** and **global within-byte bit-position permutations**, which change the bit composition of all sixteen selected copied bytes. It is a different candidate construction from arbitrary ordering of the original source bytes.

## Exact source and transforms

- Original printer SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Selected attempt: PS-261003-0417 ACK RECOVER attempt2, 18:02 UTC; copied payload `A9A9DC5731A5E2AE879C47215C2559D5`.
- Official K04 XOR mask: `8556C8CB6140A7F9A5123AC7571BEE1C`.
- Original K04 commitment: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.
- A sixteen-column scan uses each of 128 affine maps `j=(a*i+b) mod 16`, with odd a in 1..15 and b in 0..15.
- **Transpose:** take eight 16-bit bit-planes from the column-ordered input; concatenate them in all 8! plane orders as 16 output bytes.
- **Pixel:** globally permute the eight bit positions of each input byte in all 8! ways, under the same 128 affine column maps.
- For output buffer Y, test coupon Y, NOT Y, Y XOR copied, and NOT Y XOR copied. XOR each result with the official mask, then SHA-256.

Each family has exactly **5,160,960** buffer layouts and **20,643,840** complete K04 checks, totaling **41,287,680** original checks. These are candidate-check counts, not claims of unique values. No original evidence or acceptance file was modified.

## Observed local outcomes

```text
FAMILY transpose candidate_checks 20643840 positive_plant_hits 1 real_K04_hits 0 seconds 16.93
FAMILY pixel     candidate_checks 20643840 positive_plant_hits 1 real_K04_hits 0 seconds 19.10
```

A planted full-buffer transform with a=3, b=5, plane permutation (2,7,0,4,1,6,5,3), inversion and XOR overlay was found once in each family's enumeration, providing a full SHA-256 positive control. The [portable source-pinned SFT](../agents/agent31/k04_fax_bitplane_sft.py) reproduces both checks from the original ZIP.

**Result:** zero original K04 matches under these two structured complete-buffer transformation families; no authenticated original K04 bit and no terminal K08 word. This constrains the tested bit-plane/bit-position layouts, not arbitrary bit corruption, genuine fax framing or other sources. Existing six individual PASS, K04/K08 MISSING and combined INCOMPLETE remain unchanged.

**Decision:** the N22 analogy alone does not justify escalating to independent arbitrary bit permutations. A stronger next attack requires a historical serialization-stage observation or a distinctive copy-fault signature that predicts an intact held-out source record.
