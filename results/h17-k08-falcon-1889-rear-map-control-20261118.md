# K08 exact 1889 Falcon rear-map control

**Agent 41 | 18 November 2026 | exact public carrier acquisition and bounded six-slot coordinate test.**

## Result

A distinct Internet Archive item, `falcononbalticc00knig`, supplies an 1889 scan of
*The "Falcon" on the Baltic: a coasting voyage from Hammersmith to Copenhagen in
a three-ton yacht*. The scan metadata reports two foldouts. Its only two
landscape PDF pages are page indices 342 and 343, and visual inspection shows
that they are the two halves of one rear **GENERAL MAP** covering the voyage
area.

This gives the project an actual 1889 rear-map raster for the existing Falcon
candidate-title branch. It remains an exploratory carrier because MAIL-09 says
only that David owned a book with a map in the back. The surviving H-17 source
does not name *Falcon* or authenticate this public scan as David's copy.

The frozen six-slot `ATEALBIT` coordinate construction does not produce a
coherent six-byte text signal from the reconstructed map.

## Source acquisition

The bounded public-source workflow is
[`.github/workflows/agent41-k08-falcon-map-control.yml`](../.github/workflows/agent41-k08-falcon-map-control.yml)
with acquisition/scanning code in
[`agents/agent41/k08_falcon_map_control.py`](../agents/agent41/k08_falcon_map_control.py).

Successful GitHub Actions run: `44415254566`.

Uploaded artifact:

- artifact id: `14479741922`
- artifact name: `agent41-k08-falcon-map-control`
- artifact digest: `sha256:3076683771302b80c789e9f1a3606e6cbe065ccc298a3f25d0683ee24dfc8e8b`

Captured item metadata:

- Internet Archive identifier: `falcononbalticc00knig`
- title: *The "Falcon" on the Baltic : a coasting voyage from Hammersmith to Copenhagen in a three-ton yacht*
- date/year: `1889`
- publisher: `London : W.H. Allen`
- contributor: `University of British Columbia Library`
- reported `foldoutcount`: `2`
- PDF filename: `falcononbalticc00knig.pdf`
- PDF pages: `350`
- downloaded PDF size: `55,286,911` bytes
- downloaded PDF SHA-256: `071e2f16f2a172478e82e7172cabac21960d4b5bc9bd96a7ba90a1152f200167`
- landscape page indices: `342,343`

The first urllib acquisition encountered repeated CDN TLS EOF errors. After the
required retry/backoff sequence, the download was changed to bounded
`curl -fL --retry 4 --retry-all-errors`; the next source run completed
successfully. This is an acquisition-path detail rather than evidence about the
book.

## Foldout reconstruction

The two landscape renders are adjacent halves of the same map. The reproducible
stitch control is
[`agents/agent41/k08_falcon_foldout_stitch_control.py`](../agents/agent41/k08_falcon_foldout_stitch_control.py).

The control uses source-image SIFT features in the expected overlap, Lowe
ratio 0.70, and a RANSAC homography with 3-pixel reprojection threshold. It
does not load the K08 nonce, K08 commitment, a phrase dictionary, or any
candidate K08 wording.

Observed reconstruction:

- accepted feature matches: **362**
- RANSAC inliers: **272**
- joined canvas: **2367 × 780** pixels

The joined raster visibly reconstructs one continuous rear map spanning London,
the North Sea, the Low Countries, Denmark and southern Scandinavia. The source
map therefore resolves the earlier ambiguity caused by scanning the two
foldout halves separately.

## Frozen coordinate test

The tested construction is documented in
[`h17-k08-multislot-teal-coordinate-control-20261118.md`](h17-k08-multislot-teal-coordinate-control-20261118.md).

Each already accepted 16-byte component K01, K02, K03, K05, K06 and K07 is
split into eight unsigned-byte coordinate pairs. A single sampled image
bitplane at those eight points yields one output byte per slot, giving six
bytes from one common carrier. The fixed grid is:

- raw or 0..255-scaled coordinate mapping;
- eight D4 orientations in the unsigned-byte coordinate square;
- grayscale bitplanes 0 through 7;
- MSB-first or LSB-first packing.

This is **256 complete six-byte outputs** for the stitched foldout.

The strongest printability result was:

- scaled mapping;
- orientation 6;
- grayscale bitplane 3;
- MSB-first;
- output hex `FE696A785734`;
- printable rendering `.ijxW4`.

It has five printable bytes and four ASCII letters, yet it is not coherent
caption text. The other high-printability outputs are similarly noise-like.
A simple Otsu black/white threshold control is poorer and yields no comparable
text signal.

The test does not use K08 acceptance to rank pixel configurations, so this
negative is free of target-oracle tuning.

## Teal-as-water semantic control

The map makes one literal reading of `A TEAL BIT` more concrete: a coordinate
could encode a water-versus-land bit. I therefore made a bounded exploratory
control using the visible map topology, with coastlines converted into barriers
and connected open sea treated as the water class. Several nearby threshold
and one/two-pixel morphology settings were checked only to measure stability of
the classification.

The resulting six-byte outputs remain noise-like. Across the plausible
topology masks and all eight orientations / bit orders, the strongest outputs
contain at most three ASCII letters and no coherent six-byte string. This
control is less canonical than the grayscale test because a scanned historical
map does not supply a machine-readable water mask. It should therefore be
treated as a negative exploratory semantic check rather than as a formal
exclusion.

## Decision

The exact 1889 rear foldout is now available as a finite source-motivated
carrier and should not be reacquired or replaced by an unrelated body-page
scan. The simple six-slot grayscale-coordinate and water/land-coordinate
interpretations do not expose a usable caption signal on this carrier.

Future work on this book should require an independent source rule selecting a
different map operation, bookmark extraction, or edition-specific text
operation. The surviving MAIL-09 tea-receipt bookmark is absent from the
archive, so it cannot currently provide that selector.

K08 remains unrecovered. K04 is unchanged. The six established REC8/1
components remain individually accepted and the combined recovery remains
incomplete.
