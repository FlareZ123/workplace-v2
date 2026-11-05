# K04: indexed one-bit-per-row coupon reconstruction (5 Nov 2026)

**Agent 9.** New original-target test of a distinct 128-record encoding model. The six known slots remain accepted. K04 and K08 are missing, combined REC8/1 incomplete.

## Proposed encoder

There are exactly **128 ordinary PS-261003-0300..0427 ACK attempt1 printer packets**, each 16 bytes. Hypothesize one source-positioned bit from each row encodes the separate 128-bit ESC-N coupon, without reading the suspect selected 0417 RECOVER ACK2 copied buffer. Prior [single-bitplane contiguous extraction](h17-printer-bitplane-crossslot-candidates-20261105.md) and [shared-source-bit parity extraction](h17-k04-128row-separable-parity-20261105.md) do not cover these row-dependent index maps. The original source has no statement endorsing steganographic coupon encoding.

Source SHA256: printer `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, route `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`. All 128 ordinary inputs are uniquely selected by original job, ACK, and attempt. A proposed complete 16-byte coupon is XORed with unchanged route mask `8556C8CB6140A7F9A5123AC7571BEE1C`. SHA256 of that full reduced component must equal original `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Three finite coding schemes, original results

| Source-selected bit position per row i | Frozen index family | Complete original K04 checks | Authentic matches |
| --- | --- | ---: | ---: |
| `(a*i+b) mod128` | a,b each 0..127 | **262,144** | **0** |
| `8*((u*(i mod16)+v) mod16)+((w*floor(i/16)+z) mod8)` | u odd mod16, w odd mod8, v0..15,z0..7 | **65,536** | **0** |
| `(a*i+b+16*C(class)+32*D(dest)) mod128` | a in {1,3,5,7,15,31,63,127}, b0..127, C/D all 3! category permutations | **589,824** | **0** |
| **Total** | 4 packet bit orientations, 2 input row orders, 2 output packings each | **917,504** | **0** |

The source metadata really contains all three LABEL/STORES/RECOVER classes and bench/desk/store destinations. Each family has a separate nontrivial synthetic whole-coupon positive control checked through the identical 16-byte XOR and SHA256. The first two yielded two and four equivalent synthetic target aliases; metadata selection yielded exactly one. **All three planted positives passed.** Candidate counts denote enumerated assignments; cross-family value uniqueness was not asserted.

Reproducible original-source SFTs:
- [Affine and grid indexed-bit test](../agents/agent9/k04_128row_diagonal_bit_stego_sft.py)
- [Source CLASS and DEST index test](../agents/agent9/k04_128row_metadata_bit_stego_sft.py)

## Boundary

These source-indexed encoders failed. A fully unconstrained bit position for each row has 128 choices repeated 128 times and cannot be supported by the export without a source-specified selector. This experiment authenticates **zero new selected K04 physical-coupon bits** and no final K08 words. It does not establish that a paper bit-selection channel existed. Seek a different original selected-stage witness or bounded source-derived transformation.
