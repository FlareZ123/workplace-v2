# K08 N14 teal-image carrier: pre-registered exploratory construction

**Owner:** Agent 50  
**State:** hypothesis / no historical image tested  
**Created:** 2026-11-20T02:12Z

## Hypothesis

The complete normalized K08 phrase may be carried in a low-bit image channel of the N14 “Sunrise photograph” or a photograph explicitly linked to N14 in the pre-incident crew/galley/noticeboard archive. This is distinct from phrase grammars, direct caption adoption, and the M10 single-cell text hypothesis.

## Source-derived motivation (not proof)

- The existing target-blind K08 note-routing analysis maps both the K04 mask and K08 desk nonce to selector 14, which lands on N14, attributed to Gabriel and labelled “Sunrise photograph”.
- The CREW4/ALOWBIT subset bridge produces the strings `ATEALBIT` and `LOW`. These could be an instruction for a teal-channel low-bit carrier, but the subset/codebook/parser choices are not an authenticated source instruction.
- N10 references “the photograph after the last cup”; N20 describes the sea, end of night and voices at the table. Neither note explicitly links N14 to N10 or Emily's final envelope wording.
- The local export contains no relevant original photo or caption archive. The N14 selector is only a note locator until a physical/digital image relationship is independently established.

## Frozen image construction

If an independently authorized original N14 image or a source-linked image member is supplied, run the existing `work/h17_k08_teal_bit_image_scan.py` unchanged:

1. Preserve and hash the original image and sidecars; do not edit or resave it.
2. Use the scanner's fixed teal mask: PIL HSV hue 110–150, saturation ≥64, value ≥32; row-major pixel order.
3. For the source-literal `LOW IF EVEN` branch, use pixel-index parity to select green/blue bit 0 for even pixels and bit 1 for odd pixels.
4. Keep green and blue channels separate. Use the existing scanner's fixed bit alignments 0–7, big/little packing, and active-low inversion. Do not add new channel combinations, thresholds, or image transforms after seeing the target.
5. Decode only ASCII/UTF-16 text runs within the scanner's existing bounded caption length; apply the exact K08 normalization, HMAC nonce and unchanged slot commitment.
6. Report the exact source image, frame, layout and complete phrase only on an exact commitment hit.

## Carrier admission and controls

- Primary target: N14's actual sunrise photograph, if an original image can be linked to that note by album/board membership, caption sidecar, timestamp, author, or original print position.
- Secondary target: an image embedded in `mug-stock.xls` only if workbook metadata or a source link ties it to the same N14/crew-photo class. A generic mug-stock image is not enough.
- Do not scan every workbook image or every image in a profile. Restrict to the N14-linked image or a small source-defined set of pre-incident crew/galley photos.
- Positive control: the local synthetic XLSX→BIFF XLS→XLSX test embedded a PNG at M10; the extracted image survived conversion and the exact `teal-mask-green-low-if-even` decoder recovered the planted phrase and matched a planted HMAC. This proves pipeline mechanics only.
- Negative controls: source-linked non-N14 crew images (if any) processed with the same frozen decoder; a non-teal channel/layout control; and the exact literal N14 caption text checked against K08. Preserve all results.
- Historical authenticity requires the image-to-N14/Emily-final-caption source link separately from an HMAC hit. A hit in an unrelated image is not K08.

## Stop conditions

- If no N14-linked original image or source-linked workbook image is available, no target image test is possible; do not substitute the PDF page, book scans, unrelated images, or synthetic fixtures.
- If the frozen decoder finds no exact HMAC hit in the admitted target image, this exact image/layout hypothesis is falsified for that image. Do not expand to arbitrary transforms, bit planes, channels, or generic profile image sweeps.
- A synthetic positive control is not historical evidence; a selector convergence is not a photo identity; a candidate commitment hit is not by itself proof of historical authorship.

## Tooling status

- Existing decoder: `work/h17_k08_teal_bit_image_scan.py`.
- Legacy BIFF adapter: `work/h17_xls_lo_fallback.py` now emits bounded style metadata for M10/C3 and the eight K01 coordinates. It does not yet extract embedded images as of this preplan.
- Agent 50 asked Agent 9 to add bounded image extraction from converted XLSX drawings with sheet/anchor/format/size/hash metadata, restricted to the source-relevant anchors. Synthetic round-trip tests show LibreOffice preserves a PNG embedded at M10 through XLSX→XLS→XLSX, but no H-17 image has been tested.
- Joint object intake: `work/h17_ax7782_joint_intake.py` coordinates the existing AX-7782 transfer validation, K04 binary-window scan and K08 recursive text/image intake when an authorized object is supplied.

## Current conclusion

The new source relation motivates one bounded, falsifiable image construction, but the image identity and source-to-caption relationship are unresolved. No K08 words or bytes have been recovered. Do not promote this hypothesis to a result without a source-linked image and exact original commitment hit.
