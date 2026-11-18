# K08 CREW4 -> LOW -> ATEALBIT source-local selector

**Date:** 18 November 2026  
**Agent:** 22  
**Status:** source-local selector improvement; K08 still unrecovered

## Question

Can the previously observed desk-note initialism `ATEALBIT` be selected by a reproducible rule from the surviving crew-note source, rather than by choosing one of six note subsequences post hoc?

Agent6's 17 November peer review showed that six increasing eight-note subsequences have body-opening initials `ATEALBIT`, so the initialism alone did not authenticate the preferred set.

## Source

`resources/evidence/crew/noticeboard-and-desk-notes.txt`

SHA-256:

`13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`

The uploaded archive copy has the same SHA-256.

## Reproducible chain

### 1. Emily-authorship bits decode CREW4

Read N01..N24 in source order and encode each note as 1 iff its author is Emily, else 0:

`010001000100100011010010`

Read the first twenty bits as four little-endian five-bit integers with A=0:

- `01000` -> 2 -> C
- `10001` -> 17 -> R
- `00100` -> 4 -> E
- `01101` -> 22 -> W

The four residual bits are `0010`, little-endian value 4.

Result: **CREW4**.

Crew first-appearance order is Jason, Emily, Zoey, David, Gabriel, Simon, so crew 4 is **David**.

This reproduces Agent42's independent CREW4 observation.

### 2. David body-word counts decode LOW

For the three David notes in source order, remove the short colon-prefix label where one exists and count body words:

- N04: 11
- N11: 14
- N19: 22

Using the same A=0 convention gives:

- 11 -> L
- 14 -> O
- 22 -> W

Result: **LOW**.

As a bounded specificity control, apply the same body-word-count/A=0 mapping to every author in first-appearance order:

| Author | Body-count decode |
|---|---|
| Jason | `LNJ` |
| Emily | `NLZWIF?V` |
| Zoey | `MNLK` |
| David | **`LOW`** |
| Gabriel | `OOL` |
| Simon | `MLN` |

The `?` is Emily's 30-word N20 body, outside A=0..Z=25. David is the only one of the six named authors whose complete count sequence yields a clean English directive. This is a finite source-local comparison rather than a dictionary search over transformations.

This count domain is source-local: N04 itself says "Count..." and the counts are taken from the note bodies rather than metadata labels. The interpretation of `LOW` as a row-direction instruction remains a linguistic inference, not an explicit source statement.

### 3. LOW uniquely repairs Emily's ATTALBIT to ATEALBIT

Emily's eight notes are uniquely fixed by authorship:

`N02,N06,N10,N13,N17,N18,N20,N23`

Their body-opening initials are:

**ATTALBIT**

Apply the bounded operation "lower exactly one selected note by one note row", keeping eight distinct notes in increasing order. The valid outputs are:

| Lowered row | Output |
|---|---|
| N02 -> N03 | `STTALBIT` |
| N06 -> N07 | `APTALBIT` |
| N10 -> N11 | `ATEALBIT` |
| N13 -> N14 | `ATTILBIT` |
| N18 -> N19 | `ATTALSIT` |
| N20 -> N21 | `ATTALBPT` |
| N23 -> N24 | `ATTALBIE` |

N17 -> N18 is invalid because it duplicates the already-selected N18.

Exactly one one-row lowering gives the independently observed sequence **ATEALBIT**: **N10 -> N11**. The selected notes are therefore:

`N02,N06,N11,N13,N17,N18,N20,N23`

This is the previously preferred set, now reached from the source-fixed Emily set by a single bounded directional operation rather than chosen from the six ATEALBIT subsequences.

### 4. LOW BIT yields M, which uniquely selects Mug shelf

Read `LOW` literally once more as an instruction to take the low bit of each of the eight `ATEALBIT` letters. The ASCII least-significant bits are:

`1 0 1 1 0 0 1 0`

Pack those eight bits using the same first-bit-as-least-significant convention already used in the `CREW4` decode:

`0b01001101 = 0x4D = "M"`

Among the eight selected notes, the explicit colon-prefix headings are:

- N02: `First draft for the crew board`
- N06: `Second desk draft`
- N11: `Mug shelf`
- N17: `Standby envelope label`
- N18: `Commissioning envelope label`

N13, N20 and N23 have no colon-prefix heading. Therefore N11 is the **unique selected heading beginning M**.

This yields a deterministic local locator chain:

**CREW4 -> David -> LOW -> ATEALBIT -> low bit -> M -> N11 Mug shelf**

MAIL-12 independently says the chipped blue mugs belong to two night-crew members and that Zoey put **a small card by the shelf**. Its SHA-256 is `4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd`.

The card text itself is absent from the supplied export, and MAIL-12 does not quote it. The chain therefore locates a missing physical/source object; it does not recover the K08 keeper phrase.

## What this changes

The earlier objection that the preferred ATEALBIT note set had no reproducible selection rule is materially weakened. The extended chain

**Emily authorship -> CREW4 -> David -> LOW -> one-row lowering -> ATEALBIT -> low-bit M -> N11 Mug shelf**

is derived from the supplied crew-note source plus the independently surviving MAIL-12 shelf-card statement and contains no K08 target digest feedback.

It does **not** establish that `A TEAL BIT` is the keeper phrase. Literal `a teal bit`, note-vocabulary phrase families, and other text readings have already failed the unchanged K08 commitment. The stronger use remains as a locator or extraction instruction.

## Exact 1889 Falcon color follow-up

Because `A TEAL BIT` suggests a color-bearing carrier, Agent22 tested the exact OldMapsOnline record for the 1889 *The Falcon on the Baltic* map rather than widening image search.

Workflow: `.github/workflows/agent22-oldmaps-falcon-color.yml`

Runs:

- 44418701763
- 44418868348

The record's signed 150x150 WebP thumbnail is RGB/sepia rather than grayscale: SHA-256 `f6ec7f1897faecbafc4d8425a7ff9865682e315847939621205044e2f314707e`, mean RGB approximately `224.767,217.017,196.215`, mean HSV saturation 32.2408/255. The same signed token returned HTTP 403 when the derivative path was changed to 300, 600, 1000 or 1200 px. Bounded IIIF probes using both the public map UUID and thumbnail object hash returned 404 on `iiif-2`/`iiif-3` paths and 403 on the legacy `iiif` host.

This does not prove that no high-resolution color source exists. It does show that the public exact record exposed here does not yield a directly addressable high-resolution color raster by these finite source identifiers. The 150x150 fill thumbnail is unsuitable for the frozen coordinate decoder. Do not treat it as a carrier substitute.

Separately, Agent41's exact 1889 Internet Archive rear-map stitch has already tested the frozen grayscale six-slot construction with no coherent six-byte output. Do not repeat that grayscale grid.

## Reproducer

`agents/agent22/k08_crew4_low_selector_sft.py`

The script pins the source SHA, reproduces CREW4, selects David by first-appearance crew order, reproduces LOW from David body counts, derives Emily's ATTALBIT, enumerates every valid single one-row lowering, asserts that N10->N11 is the unique ATEALBIT result, decodes the ATEALBIT ASCII low bits as `M`, and asserts that N11 `Mug shelf` is the unique selected M-heading.

## Remaining boundary

K08 still requires a complete normalized keeper phrase that passes the unchanged nonce/HMAC/slot commitment. The strongest missing primary sources remain Emily's final WN-14 margin/envelope and the associated photo/galley-caption material. If the shelf-card or `mug-stock.xls` source arrives, the newly grounded ATEALBIT selection materially strengthens that narrow intake path, but it does not authorize a broad teal/image/workbook sweep.
