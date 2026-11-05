# K04 copied raster: two-dimensional neighbor-predictive (fax-style) decoding

**Agent31 | 5 November 2026 | No original K04 match in 884,736 complete candidates.** Unchanged six individual original slots PASS, K04/K08 missing, combined REC8/1 incomplete.

## Distinct producer/copy mechanism

The original crew note N22 says the label printer sometimes behaved "like a fax machine"; MAIL-16 explains why the copied payload has no independent paper integrity. This motivates an exploratory **two-dimensional differential bitmap** channel: every bit of an 8×16 or similarly factored source raster may encode an XOR with the bit **above** or **left**, or with **both** neighbors, and a copied raster may need deterministic 2D differential decoding. A 2D predictor changes bit values across many bytes. It differs from the earlier [Agent25 raster-scan-only bijections](h17-k04-bit-raster-readback-model.md), which just relocate original pixels, and [Agent18 flat serial differential symbols](h17-k04-differential-symbol-copier-channel.md), which accumulate along one unbroken 1D array. No original record attests that this printer used such a 2D predictor, so the hypothesis is provisional.

## Exact candidate class and original source

Official selected copied payload: `A9A9DC5731A5E2AE879C47215C2559D5`, printer SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The source-selected original K04 mask is `8556C8CB6140A7F9A5123AC7571BEE1C`, and the original K04 SHA256 commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The historical physical coupon is still unknown.

For **each** of six 128-bit raster factorizations **2×64,4×32,8×16,16×8,32×4,64×2**:

- For both source bit-endian orders, choose row-major or column-major input, straight or serpentine scan, independently reflect each axis, and cyclically vary each row and column origin. Each raster shape has **4,096 scan-parameter assignments** before neighbor prediction; some assignments may generate identical geometric maps or outputs.
- Apply any of **six** binary predictors: above-source XOR, cumulative above-output XOR, left-source XOR, cumulative left-output XOR, above+left-source XOR, or cumulative above+left-output XOR. At a first row/column, the absent neighbor is zero.
- Try all **three** exact reducer stages: transform copied payload then original-mask XOR, transform original mask then XOR with unmodified copy, or transform existing copied-payload XOR original-mask component. Also test both image polarities.
- Every complete 16-byte candidate goes through the untouched original full SHA256 commitment. Stage count is **147,456** per raster shape, totaling **884,736** complete assignments. Output collisions are possible and were not deduplicated.

## Original result and positive controls

The read-only [source-pinned original-ZIP SFT](../agents/agent31/k04_fax_2d_differential_sft.py) asserts the SHA256 of the original printer, unique selected ACK2 identity and 16-byte original mask. A synthetic planted transformed component at a deliberately nontrivial **8×16, row origin3, col origin5, column-major serpentine, reflected, reverse bits, cumulative both-neighbor, post-reducer and inverted** state is pinned independently as:

```text
PLANTED_COMPONENT 7B68DAAA4C2AE2D6A2C042B921315267
PLANTED_SHA256 4e1b5884d0260954fdc6918a4cff646179d9e0ea16f5d2f5fff7d60b117ed3dc
```

An independent Python SHA256 reference of those fixed bytes passes, and the enumeration reproduces that full source-to-component value (twice across geometrically equivalent assignments). The tested original source-equivalent implementation returned:

```text
GRID  2x64 CHECKS 147456 ORIGINAL_HITS 0
GRID  4x32 CHECKS 147456 ORIGINAL_HITS 0
GRID  8x16 CHECKS 147456 ORIGINAL_HITS 0
GRID 16x8  CHECKS 147456 ORIGINAL_HITS 0
GRID 32x4  CHECKS 147456 ORIGINAL_HITS 0
GRID 64x2  CHECKS 147456 ORIGINAL_HITS 0
FINAL source-pinned original checks 884736 real 0 planted_positive 2 seconds 12.4
```

No original artifact, mask, commitment, verifier or candidate was modified. This excludes the stated six finite 2D predictor-and-layout families only, with no authenticated selected coupon bit or K08 exact final phrase. The absence of an observed real fax codec makes further arbitrary predictor permutations poor-return without an original integrity clue.
