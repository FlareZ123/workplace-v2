# K08 Falcon native JPX raster control — 2026-11-23

## Outcome

**No exact K08 HMAC/acceptance hit** was found in any of the four native JPX image objects embedded on the two rear-foldout PDF pages. The pre-registered six-slot grayscale coordinate decoder also produced no coherent six-byte text on either page.

This is a bounded exploratory control only. The public *Falcon on the Baltic* edition is **not authenticated as David's physical book**, and neither the map nor its page images are authenticated as the K08 carrier. This result does not close the original keeper-envelope / N23 final-margin path.

## Source identity and limitation

Retrieved the retained GitHub Actions artifact `14479741922` (`agent41-k08-falcon-map-control.zip`). Its embedded PDF identifies the Internet Archive item `falcononbalticc00knig`, E. F. Knight, *The “Falcon” on the Baltic*, W. H. Allen, 1889; its metadata records 350 pages and a two-page foldout.

The PDF in this artifact is 19,125,467 bytes with SHA-256:

`0f237b073f5768b77b5badc78836a76e35fc84cd67e5c3542175831b87564d3b`

**Important:** this differs from the SHA-256 recorded by the earlier acquisition report (`071e2f…00167`). The title, author, publication year, Internet Archive item identifier and page count agree, but byte identity with that earlier PDF has not been established. Results below are explicitly tied to the artifact PDF hash above, not asserted as a byte-identical reproduction of the earlier acquisition.

The foldout is on PDF pages **343–344** (1-based; zero-based indices 342–343). Extracted embedded image objects with:

```sh
pdfimages -f 343 -l 344 -all falcononbalticc00knig.pdf img
```

## Native image-object inventory

| PDF page | Extracted object | Dimensions | Bytes | SHA-256 | Teal-mask pixels |
|---:|---|---:|---:|---|---:|
| 343 | `img-000.jp2` (preview) | 1209×723 | 6,148 | `a0f8d2dfd7fa2e8497d5dcf233e57835172ba6bf7c3c10cb593807630d01494c` | 17 |
| 343 | `img-001.jp2` (native) | 3626×2167 | 31,201 | `72579cdc18d555fb43cfbb46897b724f1b0c3d79bbb06a9137755bad63883c21` | 1,065 |
| 344 | `img-003.jp2` (preview) | 1199×707 | 6,312 | `3722bf0041bbe50bdc25293985b4bb6fdfb2181442e3402c0107ec8117f05e9f` | 0 |
| 344 | `img-004.jp2` (native) | 3595×2119 | 32,892 | `8ce15ec1d5c56b1472464a642d10d17ba36270337c20fb05a071e9b5ba6b1053` | 24,720 |

Each page also has a separate 1-bit JBIG2 soft-mask object. Those masks were not fed to the teal decoder: its frozen layouts operate on RGB/HSV channels of the JPX image objects. The high-resolution JPX codestreams declare the reversible 5/3 wavelet transform; decoding them to RGB and saving PNG copies for the grayscale coordinate control did not resize or interpolate the source pixels.

## Tests

### 1. Frozen source-literal teal-bit decoder

Applied the exact two `SOURCE_LITERAL_LAYOUTS` from `work/h17_k08_teal_bit_image_scan.py` to each of the four JPX objects through the existing byte-input path:

- teal/cyan HSV mask (H 110–150, S ≥64, V ≥32);
- green or blue channel low bit selected by absolute row-major pixel-index parity;
- all eight bit offsets, both pack orders, and normal/inverted packed streams;
- existing K08 normalization, HMAC-SHA256/16, then SHA-256 commitment check.

**Result: zero exact K08 matches across all four image objects.** No resize, perspective warp, resampling, denoising, palette conversion or pixelwise merge was applied.

### 2. Frozen six-slot grayscale coordinate control

Applied the existing 256-configuration coordinate decoder from `agents/agent41/k08_multislot_teal_coordinate_control.py` separately to each high-resolution native JPX page after lossless PNG serialization and the decoder's own grayscale conversion.

- Page 343: six configurations had at least five printable output bytes; best was hex `2B317B5E2B36`, ASCII `+1{^+6`.
- Page 344: four configurations had at least five printable output bytes; best was hex `60B149677C2E`, escaped ASCII `\\x60.Ig|.`.

Neither output is a coherent six-byte string. This is a printability control, not a K08 phrase or HMAC candidate.

## Methodological correction

The earlier Agent50 wrapper renders PDF pages at 2× and uses `cv2.warpPerspective` plus `np.minimum` to create a stitched raster. Those operations change pixel values and absolute pixel-index parity, so that stitched image cannot support a bit-exact LSB conclusion. The present test avoids that defect by testing the four native embedded JPX objects separately. It does **not** attempt to stitch the two-page foldout: no pixel-preserving source-defined raster order or alignment has been established.

## Interpretation / next step

- The individual native image objects in this artifact PDF do not yield a K08 hit under the frozen teal-bit layouts.
- The separate coordinate decoder yields only non-coherent printable noise.
- The Falcon map remains an unauthenticated exploratory carrier, not evidence of Emily's final envelope inscription.
- The authoritative K08 dependency remains the original keeper-envelope wording / N23 margin or a source-authenticated carrier with a documented adoption path.

No candidate, acceptance commitment, verifier, routing rule, original ZIP member or source file was changed.
