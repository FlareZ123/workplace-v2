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


## Reverse scan direction and two mask stages: second original-target experiment

An important distinction after the initial forward-transpose run: the inverse of an 8-by-16 bit-plane transpose need not be represented by either previous forward or per-byte bit permutation. The reverse operation interprets each consecutive **two-byte source pair** as one 16-pixel bit-plane, assigns the eight physical planes to eight output-bit positions in all 8! orders, and recombines the 16 pixels into 16 bytes using the same 128 invertible affine column maps.

Two complete reducer-stage hypotheses were independently checked:

- **Post-mask:** inverse-transpose the copied 16-byte coupon (plus inversion/XOR overlay alternatives), then XOR the official 16-byte mask to form K04.
- **Pre-mask:** XOR the copied coupon with the official mask first, inverse-transpose that tentative K04 component (plus inversion/XOR overlay alternatives), then SHA-256 directly. This addresses a different ordering of the two historical reduction operations.

Each stage again contains **20,643,840** full original K04 commitment checks. Independently run local original-archive results:

```text
STAGE pre  hash_checks 20643840 planted 1 real_hits [] elapsed 23.51
STAGE post hash_checks 20643840 planted 1 real_hits [] elapsed 22.72
```

Both independent stages passed a planted complete candidate control and found **zero** original K04 matches. [Portable inverse/postmask SFT](../agents/agent31/k04_fax_inverse_stage_sft.py), invoked with a ZIP path and optional stage argument, recomputes these exact families.

**Cumulative experimental scope:** four distinct family/stage runs, **82,575,360** complete commitment checks, zero original K04 hits and four planted positives. Overlap between the hypothetical candidate families has not been deduplicated. These are reversible complete-candidate transformations of the copied bytes and official mask; they cannot authenticate the actual historical coupon or rule out a different source or a lossy damaged copy.


## Shared exporter distortion applied to both route mask and copied payload (5 November, follow-on)

A new **joint-stage hypothesis** is that the same byte/bit copier transform affected **both** the source K04 printer coupon and the separately transcribed sixteen-byte route mask. Under a linear common binary transform T the tentative final component is T(copied XOR mask), rather than T(copied) XOR original-mask. The first forward-layout search used the second form; the prior inverse-layout stage pilot addressed only the inverse scan family. The new construction extends this to the two forward bit-plane families and changes the source stage instead of widening the per-byte corruption radius.

Using original unchanged source and the identical 128 invertible affine columns, 8! bit-plane layouts and four full-buffer inversion/XOR-overlay modes, the new source-pinned [joint source-transform SFT](../agents/agent31/k04_shared_exporter_prexor_bitplane_sft.py) executed:

- Forward transposition with **20,643,840** original full SHA-256 K04 checks, **zero matches**, planted complete-candidate positive PASS.
- Forward global within-byte bit relabeling with **20,643,840** additional original full checks, **zero matches**, planted complete-candidate positive PASS.

The new two families add **41,287,680** complete commitment checks and two full synthetic positives, for a cumulative **123,863,040** checks across six related family/stage attempts. No cross-family unique-output count is claimed. The historical source makes **no assertion** that the route mask and printed coupon shared a faulty exporter; this was a speculative, finite test. K04 remains missing, with zero authenticated paper bits; K08 unchanged, combined REC8/1 incomplete. Future work should use a distinct historically observable copy relationship rather than extending this arbitrary bit-plane family.
