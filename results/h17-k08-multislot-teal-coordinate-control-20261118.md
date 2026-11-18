# K08 six-slot ATEALBIT coordinate decoder: preserved Falcon page control

**Agent 41 | 18 November 2026 | exploratory multi-slot construction, zero recovered K08 words.**

## Question

The eight selected desk-note openings spell `ATEALBIT`, plausibly segmented as
`A TEAL BIT`. Earlier image work treated the eight K01 byte pairs as possible
pixel coordinates, which yields only one extracted byte and therefore has a
capacity problem for a caption.

A materially different reading is available from the archive structure itself:
each already accepted REC8/1 component is exactly 16 bytes, hence eight unsigned
byte pairs. The six accepted components K01, K02, K03, K05, K06 and K07 can
therefore select **48 image bits**, producing **six bytes from the same image**.
This does not establish that the relation is historical. It gives the image
hypothesis a prospective discriminator that can reject ordinary rasters before
K04 or K08 is known.

This is distinct from `work/h17_k08_teal_bit_image_scan.py`, which scans
sequential image-channel bitplanes for embedded text. Here the accepted
components themselves define the sample coordinates.

## Frozen decoder

For each accepted component, interpret bytes as eight ordered `(x,y)` pairs.
For a single image:

1. Apply one of the eight D4 orientations in the native 0..255 coordinate square.
2. Use either raw pixel coordinates or scale each byte coordinate from 0..255 to
   the image width/height.
3. Sample one grayscale bitplane, 0 through 7, at all eight coordinates.
4. Pack the eight bits MSB-first or LSB-first to produce one byte.
5. Concatenate slot outputs in K01,K02,K03,K05,K06,K07 order.

The portable decoder is
[`agents/agent41/k08_multislot_teal_coordinate_control.py`](../agents/agent41/k08_multislot_teal_coordinate_control.py).

No K04 value, K08 candidate, desk nonce, or K08 acceptance commitment enters
the construction.

## Preserved-source control

I ran the decoder against the 16 distinct full-size signed 1889 *Falcon on the
Baltic* page scans already preserved by Agent7. No source was refetched.

- workflow run: `44381971905`
- artifact: `14463738331`, `agent7-k08-falcon-signed-dual`
- artifact digest: `sha256:2ddcc5fd1d58c97b9f0995885592d0f864206a7043ced296fbaf1581ee1ff020`
- pages: 4, 28, 30, 31, 67, 96, 122, 143, 151, 171, 180, 201, 205, 215, 229, 239
- images are grayscale page scans around 1025 pixels wide and 1546-1599 pixels high.

The complete control grid is:

`16 images × 2 coordinate mappings × 8 orientations × 8 bitplanes × 2 pack orders = 4096 six-byte outputs`.

**Result:** zero outputs contained five or six printable ASCII bytes. The best
outputs contained only two printable bytes out of six.

This printability check is only a carrier discriminator. It is not an
acceptance test, and ordinary monochrome book pages are not expected to encode
a caption. The result therefore does not falsify the coordinate construction.
It shows that the construction does not manufacture an obvious six-byte text
signal from the already-preserved body-page rasters.

## What changes

The earlier one-K01-coordinate objection that `A TEAL BIT` yields only one
byte is incomplete: the six accepted components provide six independently
derived coordinate bytes on a common raster. That makes an authenticated map
or desk/photo carrier test substantially more informative.

The next bounded test is **not another body-page scan and not another title or
offset search**. If the already-identified exact Falcon rear-map scan becomes
available through the current signed-viewer work, or an independently
authorized original desk/photo carrier is supplied, apply this exact frozen
decoder first. A coherent six-byte output would be a prospective discriminator
worth investigating; another noise-like output would retire this exact
multi-slot bit-coordinate interpretation for that carrier.

K08 remains unrecovered.
