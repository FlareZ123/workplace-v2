# K08 Falcon native JPX raster control — 2026-11-23

## Outcome

**No exact K08 HMAC/acceptance hit** was found in any of the eight embedded JPX image objects examined from the public 1889 *Falcon on the Baltic* scan: the front/back cover objects and the two rear-foldout pages. The pre-registered six-slot grayscale coordinate decoder also produced no coherent six-byte text on either foldout page.

This is a bounded exploratory control only. The public *Falcon on the Baltic* edition is **not authenticated as David's physical book**, and neither its covers nor its map are authenticated as the K08 carrier. This result does not close the original keeper-envelope / N23 final-margin path.

## Source identity and limitation

Retrieved the retained GitHub Actions artifact **14479741922** (`agent41-k08-falcon-map-control.zip`). Its embedded PDF identifies the Internet Archive item `falcononbalticc00knig`, E. F. Knight, *The “Falcon” on the Baltic*, W. H. Allen, 1889; its metadata records 350 pages and a two-page foldout.

The PDF in this artifact is 19,125,467 bytes with SHA-256:

`0f237b073f5768b77b5badc78836a76e35fc84cd67e5c3542175831b87564d3b`

**Important:** this differs from the SHA-256 recorded by the earlier acquisition report (`071e2f…00167`). The title, author, publication year, Internet Archive item identifier and page count agree, but byte identity with that earlier PDF has not been established. Results below are tied to the artifact PDF hash above, not asserted as a byte-identical reproduction of the earlier acquisition.

The two-page foldout is on PDF pages **343–344** (1-based; zero-based indices 342–343). The book covers are PDF pages **1** and **350**.

## Native image-object inventory

Extracted embedded image objects with `pdfimages -f PAGE -l PAGE -all`. The “small” and “large” labels below describe dimensions only; they do not assert the PDF objects' semantic roles.

| PDF page | Object | Dimensions | Bytes | SHA-256 | Teal-mask pixels |
|---:|---|---:|---:|---|---:|
| 1 | `front-000.jp2` (small) | 817×1228 | 8,663 | `bc5586e65e4ab3ea11b48e86473b04f9b443f0c247e71e57062c8e1767cfdf32` | 524,946 |
| 1 | `front-001.jp2` (large) | 2449×3683 | 3,645 | `c75756d0dc3da002779edbe4bcff6fe3fe2fe4f181250dc83ec0812f770981d5` | 15,549 |
| 343 | `img-000.jp2` (small) | 1209×723 | 6,148 | `a0f8d2dfd7fa2e8497d5dcf233e57835172ba6bf7c3c10cb593807630d01494c` | 17 |
| 343 | `img-001.jp2` (large) | 3626×2167 | 31,201 | `72579cdc18d555fb43cfbb46897b724f1b0c3d79bbb06a9137755bad63883c21` | 1,065 |
| 344 | `img-003.jp2` (small) | 1199×707 | 6,312 | `3722bf0041bbe50bdc25293985b4bb6fdfb2181442e3402c0107ec8117f05e9f` | 0 |
| 344 | `img-004.jp2` (large) | 3595×2119 | 32,892 | `8ce15ec1d5c56b1472464a642d10d17ba36270337c20fb05a071e9b5ba6b1053` | 24,720 |
| 350 | `back-000.jp2` (small) | 802×1232 | 4,926 | `2f3078ea847dd8eedc438591c71609d01bb7d3796519a3b18ef46d7fd402420f` | 680,341 |
| 350 | `back-001.jp2` (large) | 2405×3696 | 1,560 | `a238cd454be42b7f27430ecf3bd57ce4413bcdb717c8ea6f8c79f5531ee029b4` | 0 |

Each page also has a separate 1-bit JBIG2 soft-mask object. Those masks were not fed to the teal decoder: its frozen layouts operate on RGB/HSV channels of the JPX image objects. The two high-resolution foldout JPX codestreams declare the reversible 5/3 wavelet transform; decoding them to RGB and saving PNG copies for the grayscale coordinate control did not resize or interpolate their source pixels.

A 350-page **small-object preview screen** found nonzero teal-mask pixels only on pages 1, 343 and 350. Page 344's small object had none, but its large foldout object had 24,720; it was therefore included manually. This was a prioritization screen, not a full high-resolution census of every page object.

## Tests

### 1. Frozen source-literal teal-bit decoder

Applied a direct reimplementation of the two `SOURCE_LITERAL_LAYOUTS` in `work/h17_k08_teal_bit_image_scan.py` to all eight JPX objects:

- teal/cyan HSV mask (H 110–150, S ≥64, V ≥32);
- green or blue channel low bit selected by absolute row-major pixel-index parity;
- all eight bit offsets, both pack orders, and normal/inverted packed streams;
- existing K08 normalization, HMAC-SHA256/16, then SHA-256 commitment check.

**Result: zero exact K08 matches across all eight image objects.** No resize, perspective warp, resampling, denoising, palette conversion or pixelwise merge was applied. The source scanner's N14-specific manifest gate was not invoked: this is an exploratory test of a different, unauthenticated public book carrier.

### 2. Frozen six-slot grayscale coordinate control

Applied the existing 256-configuration coordinate decoder from `agents/agent41/k08_multislot_teal_coordinate_control.py` separately to each high-resolution native JPX foldout page after lossless PNG serialization and the decoder's own grayscale conversion.

- Page 343: six configurations had at least five printable output bytes; best was hex `2B317B5E2B36`, ASCII `+1{^+6`.
- Page 344: four configurations had at least five printable output bytes; best was hex `60B149677C2E`, escaped ASCII bytes `60 2E 49 67 7C 2E`.

Neither output is a coherent six-byte string. This is a printability control, not a K08 phrase or HMAC candidate. The coordinate decoder was not run on the covers.

## Methodological correction

The earlier Agent50 wrapper renders PDF pages at 2× and uses `cv2.warpPerspective` plus `np.minimum` to create a stitched raster. Those operations change pixel values and absolute pixel-index parity, so that stitched image cannot support a bit-exact LSB conclusion. The present test avoids that defect by testing the eight individual embedded JPX objects separately. It does **not** attempt to stitch the two-page foldout: no pixel-preserving source-defined raster order or alignment has been established.

## Interpretation / next step

- The examined cover and foldout image objects in this artifact PDF do not yield a K08 hit under the frozen teal-bit layouts.
- The separate foldout coordinate decoder yields only non-coherent printable noise.
- The full high-resolution all-page census was not completed; the completed preview screen is not proof that every body-page high-resolution object lacks teal pixels.
- The Falcon map and covers remain unauthenticated exploratory carriers, not evidence of Emily's final envelope inscription.
- The authoritative K08 dependency remains the original keeper-envelope wording / N23 margin or a source-authenticated carrier with a documented adoption path.

No candidate, acceptance commitment, verifier, routing rule, original ZIP member or source file was changed.
