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

The selected rows contain a second, independent-looking instruction. Decode each selected note's body-word count with A=0. The eight count letters are:

`NLOWIF?V`

Rows 2–4 are exactly **LOW**. The first selected body head is `A`; the final three selected body heads are `BIT`. Replacing the middle `TEAL` segment of the head string with the count-derived directive therefore yields:

**A LOW BIT**

This relationship is unique across the same seven valid one-row lowerings:

| Lowering | Head string | Count string | A + count[2:4] + final BIT-position heads |
|---|---|---|---|
| N02 -> N03 | `STTALBIT` | `MLZWIF?V` | `SLZWBIT` |
| N06 -> N07 | `APTALBIT` | `NMZWIF?V` | `AMZWBIT` |
| **N10 -> N11** | **`ATEALBIT`** | **`NLOWIF?V`** | **`ALOWBIT`** |
| N13 -> N14 | `ATTILBIT` | `NLZOIF?V` | `ALZOBIT` |
| N18 -> N19 | `ATTALSIT` | `NLZWIW?V` | `ALZWSIT` |
| N20 -> N21 | `ATTALBPT` | `NLZWIFKV` | `ALZWBPT` |
| N23 -> N24 | `ATTALBIE` | `NLZWIF?L` | `ALZWBIE` |

Thus the same target-blind row choice yields both **A TEAL BIT** in note heads and **A LOW BIT** from the aligned count/head features. This materially strengthens the interpretation of `LOW` as a bit-significance instruction.

The exact normalized phrase `a low bit` was checked once under the unchanged K08 desk nonce and route normalization. Its HMAC16 component is `3301765E937F40CE02707DCE602AEF3E`; SHA-256 is `bcc2405b9995bc184ee698ca522c16e91abf58b82a8e297331572fa158a0518c`, so it is **NO_MATCH** for the original K08 commitment. Treat it as an instruction, not keeper wording.

### 4. A SEAL BIT closes a source-only fixed point on N10

The winning selected count string is `NLOWIF?V`. Positions 2–6 read **LOWIF**, and replacement row N11 begins with the literal word **Even**, giving the secondary internal cue **LOW IF EVEN**. Applying that cue to the aligned ASCII heads by note-number parity produces `0x41 = A`, but that parity complement is interpretive and is not needed for the stronger loop below.

Among all seven valid one-row lowering outputs, **only N10→N11 contains the contiguous substring `TEA`**, inside `ATEALBIT`. N10 itself says:

`I kept going back to the photograph after the last cup.`

The source has exactly four explicit photograph-labelled notes, N01/N04/N08/N14. Of those, **only N01 contains the word `tea`**, and N01 explicitly contrasts it with **sea**:

`The sea looks different when you have finally finished your tea.`

Applying that source-local tea→sea substitution to `A TEA L BIT` yields:

**A SEAL BIT**

This phrase is itself a K08 direct negative: normalized `a seal bit` gives HMAC16 `B0204E96F94447A103FD495595D70154` and component SHA-256 `c7ec5846db20b1fe953bd93ef85aa6ac5f06d4badf0a9c3887f0bd33676ebe68`.

The seal instruction nevertheless gives an independent source check. From `resources/evidence/maintenance/seal-receipts.jsonl` (SHA-256 `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`), apply the already-established K03 receipt rule: PTW-417, signed, CLOSED, AS_LEFT, greatest revision per bay, witness order B,D,A,C. The four serials are:

- B: `D7DAD6BC`
- D: `9714519B`
- A: `7DAD0AD4`
- C: `BE8E87FD`

Take one **low bit** from each 32-bit serial. Their least-significant bits in B,D,A,C order are:

`0 1 0 1`

Using the same first-bit-as-LSB convention gives integer **10**. That points exactly to **N10**, the original row whose one-step lowering to N11 produced the winning `ATEALBIT` / `ALOWBIT` pair.

N10 then supplies an unusually literal transition rule. Across all 24 note bodies, the standalone word `cup` occurs only in N09 ("first cup") and N10 ("last cup"). N10 itself says:

`I kept going back to the photograph after the last cup.`

Therefore N10 is the **last cup** row, and the note **after the last cup** is exactly N11. The seal selector and N10's own wording independently reproduce the same N10→N11 move.

This is a fixed-point consistency check: N10→N11 is the only lowering that creates the TEA-bearing instruction; N10 points back to the unique tea-bearing photograph N01; N01 turns TEA into SEA; the independent seal source returns N10; and N10's literal "after the last cup" returns N11. The tea→sea wordplay is still an inferred decoder, so this is strong corroboration rather than a standalone proof of the historical encoding.

### 5. LOW BIT yields M, which uniquely selects Mug shelf

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

### 6. M + 10 names MAIL-10 and reproduces accepted K05

The two independently derived outputs can also be read together:

- `ATEALBIT` ASCII low bits -> **M**
- PTW-417 B,D,A,C seal low bits -> **10**

That gives **M10**, which has an exact archive referent: **MAIL-10**.

MAIL-10 is unusually specific. It says the wanted recorder node is `0x31`, the four-byte control words are opaque byte strings copied exactly as stored, CRC failures must be ignored even when their sequence is higher, and the route sheet supplies the event and freeze window.

Those instructions are sufficient to reproduce the already-accepted K05 route without using K05's accepted value as a selector:

1. parse the pinned TRP2 export;
2. retain CRC-valid records only;
3. node `0x31 = 49`;
4. event `0x52 = 82` from the route sheet;
5. UTC window `21:14:00 <= t < 21:14:08`;
6. greatest sequence per latch 0..3;
7. concatenate each four-byte control word exactly as stored.

The selected sequences are `300,301,302,303` and the resulting component is:

`FF8B78200A56E8586DCDA00EF01E4572`

This equals the independently accepted **K05** component exactly.

MAIL-10 SHA-256 is `ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48`; the TRP2 source SHA-256 is `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`.

This is the strongest calibration in the chain because it lands on a complete, previously accepted archive component rather than merely readable English. It still does not reveal K08's terminal wording. The mapping `M10 -> MAIL-10` is a compact archive-reference interpretation and should be treated as corroboration unless another source explicitly states that convention.

Reproducibility workflow run **44424382364** passes the complete current SFT, including this K05 known-answer calibration.

## What this changes

The earlier objection that the preferred ATEALBIT note set had no reproducible selection rule is materially weakened. Two source-local continuations now converge on the same row choice: the seal-bit fixed point returns N10, while the low-bit M path resolves to N11 `Mug shelf` and MAIL-12's small shelf card. These constructions use the unchanged K08 digest only for direct phrase rejection, never to choose the row, seal serials or note sequence.

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

The script pins the crew-note, seal-receipt, MAIL-10 and TRP2 sources; reproduces CREW4 and David's LOW; enumerates every valid one-row lowering; asserts that N10->N11 uniquely yields both `ATEALBIT` and `ALOWBIT`; proves N10→N11 is the only lowering containing `TEA`; identifies N01 as the only tea-bearing photograph-labelled note; applies the N01 tea→sea transformation; derives the PTW-417 B,D,A,C seal low bits `0101` and selector value 10; verifies that N10 is the source's last `cup` row and that "after the last cup" is N11; decodes the ATEALBIT ASCII low bits as `M`; and finally checks that `M10 -> MAIL-10` reproduces the complete accepted K05 component under MAIL-10's own byte-order/CRC instructions.

## Remaining boundary

K08 still requires a complete normalized keeper phrase that passes the unchanged nonce/HMAC/slot commitment. The strongest missing primary sources remain Emily's final WN-14 margin/envelope and the associated photo/galley-caption material. If the shelf-card or `mug-stock.xls` source arrives, the newly grounded ATEALBIT selection materially strengthens that narrow intake path, but it does not authorize a broad teal/image/workbook sweep.
