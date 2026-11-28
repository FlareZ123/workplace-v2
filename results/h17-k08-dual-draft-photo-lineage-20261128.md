# K08: THE and MHI independently select first/second drafts with the same photograph

**Agent 42 | 28 November 2026 | target-blind version-lineage refinement | final wording still unresolved**

## Result

Two independently emitted three-letter source tokens now collapse onto an unexpectedly coherent version lineage.

### THE branch

N10 is independently selected elsewhere by the official PTW-417 signed/CLOSED/AS_LEFT seal LOW BIT value **10**. Under the already-established note-word transform, N10's fixed opening window `the / desk / copy` uniquely emits **THE**.

Read `THE` under the existing A1Z26 note-address convention:

- T -> N20
- H -> N08
- E -> N05

Their normalized post-label word counts are **30 / 13 / 14**. Taking one low bit from each count and packing first-bit-as-LSB gives:

`0,1,0 -> 2 -> N02`

N02 is source-labelled **First draft for the crew board**.

Now take the A1Z26 low bit of the first body-word initial at those same three addressed notes. Their heads are **I / B / T**, whose parity bits are:

`1,0,0 -> 1 -> N01`

N01 is source-labelled **photograph of the empty bench**.

Thus the source-selected THE branch resolves to:

**N02 first draft + N01 photograph**

### MHI branch

The independent N20 raw-body first-24-character LOW BIT channel emits **MHI**, already established before this result.

A1Z26 gives N13/N08/N09. Their normalized post-label counts are **22 / 13 / 13**:

`0,1,1 -> 6 -> N06`

N06 is source-labelled **Second desk draft**.

The first body-word heads of N13/N08/N09 are **A / B / N**:

`1,0,0 -> 1 -> N01`

Again the same source-labelled **photograph of the empty bench** is selected.

Thus the MHI branch resolves to:

**N06 second desk draft + N01 photograph**

## Version structure

Together the two independently emitted source tokens give an ordered editorial lineage:

- **THE -> N02 First draft + N01 photograph**
- **MHI -> N06 Second desk draft + N01 photograph**

This is directly consonant with MAIL-11's surviving provenance statement that Emily used **desk notes and photograph captions** to work out the keeper wording. It also sharpens N10's source statement about the desk copy and returning to a photograph after the last cup.

The shared photograph is not selected by thematic guessing: both branches independently reduce to note selector **1** through the same declared head-parity operation.

## Specificity / denominator caveat

The downstream three-note parity reductions are not intrinsically unique. Across all `24^3 = 13,824` ordered A1Z26 note triples:

- **300** triples have the same downstream pair `count selector 2 / head selector 1`;
- **600** triples have `count selector 6 / head selector 1`.

Therefore the evidence comes from the **independent upstream emission of THE and MHI**, not from post-selecting triples that happen to land on draft/photo labels. The reproducer enumerates this full denominator explicitly.

## Consequence

The K08 source program has advanced from a loose set of thematic donor notes to a mechanically selected **first-draft -> second-draft + shared-photograph** lineage. That gives a substantially tighter input set for the still-missing terminal authoring operation.

It does **not** authenticate any exact word of Emily's final N23 margin, and it does not license a new free-form splice or aligned palette. The immediate N01/N06 aligned LOW-BIT continuation was separately tested in `h17-k08-mhi-n06-n01-fixed-editor-20261128.md` and misses the original commitment.

Future work should ask for a source-selected **version operation over the now-fixed N02/N06/N01 lineage**, ideally one that reproduces an authored holdout before being applied to the unquoted final version.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing.

## Reproducer

`agents/agent42/k08_dual_draft_photo_lineage_sft.py`

The SFT pins the crew-note source, independently reproduces THE and MHI, computes both A1Z26 address triples, count/head parity selectors, verifies the source labels for N02/N06/N01, and enumerates all 13,824 possible note triples as a specificity control. It reads no K08 nonce or acceptance target.
