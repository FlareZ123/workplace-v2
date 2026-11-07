# PTW-417 revision-1 blocks in the past-gap two-donor K04 inverse

**Date:** 2026-11-07  
**Author:** Agent43  
**Status:** bounded negative; closes one explicit source-derived donor-corpus gap.

## Question

Agent11 identified a complete PTW-417 revision-1 asset-annotated B,D,A,C block that was absent from the 533-carrier corpus used by Agent4's past-gap two-donor MT inverse. Could either revision-1 bay-A interpretation, assembled in MAIL-04's witness order, produce the K04 component when paired with every original donor under the existing inverse?

## Source-derived donor variants

The local seal-receipts export has four PTW-417 revision-1 AS_LEFT/CLOSED/signed rows with asset and inspector fields:

- A = SG-7E73B4CC
- B = SG-AD1D814B
- C = SG-5CB72EE5
- D = SG-64B2EE4A

MAIL-04's B,D,A,C witness order gives the asset-annotated block:

`AD1D814B64B2EE4A7E73B4CC5CB72EE5`

A fifth signed revision-1 bay-A row, SG-574A9232, has no asset or inspector fields. Preserving that distinct alternative gives:

`AD1D814B64B2EE4A574A92325CB72EE5`

Both 16-byte blocks were absent from the exact 533-value donor TSV. The underlying record ambiguity remains unresolved; neither A row is silently selected here.

## Method

1. Rebuilt Agent11's original donor corpus from the uploaded 46-member ZIP using the existing builder. It reproduced exactly **533 donors** and TSV SHA256 `e67fd3e2867f335a692c7280d03560530866a63b0f37c7ee2db61dde21d45f37`.
2. Appended both revision-1 blocks as separate, source-labelled donors, producing 535 values.
3. Ran Agent4's existing past-gap two-donor MT inverse with only its donor-count guard changed from 533 to 535. The search retained every ordered donor pair, all four existing endian/temper interpretations for each operand, both missing predecessor high-bit choices, the unchanged route mask and the full unchanged K04 SHA256 commitment.
4. Retained the engine's seeded synthetic MT positive control. It passed in both the baseline and extended run.

## Results

| Run | Donors | Ordered-pair / interpretation / high-bit checks | Synthetic control | K04 hits |
|---|---:|---:|---|---:|
| Baseline reproduction | 533 | 9,090,848 | PASS | 0 |
| Both revision-1 blocks added | 535 | 9,159,200 | PASS | 0 |

The extension adds 68,352 checks. **Neither revision-1 block yields a K04 hit** in either operand position or any tested interpretation.

## Interpretation and limits

This closes the specific omission identified in Agent11's donor-gap report for Agent4's past-gap two-donor inverse. It does not resolve which revision-1 bay-A record belongs to the physical seal rack, and it does not establish that PTW-417 is causally related to the ESC-N coupon. The original signed receipt, export lineage, revision/void history and field-sketch/closeout correspondence remain necessary.

The result is limited to this exact inverse, its four endian/temper interpretations and the two source-preserved revision-1 blocks. It does not rule out other source-defined relationships or transformations. Do not respond by expanding generic transforms or donor permutations; the remaining useful evidence is the original receipt/copy-stage source and the native PS-0417 selected object.

## Reproduction

Using the original ZIP and existing repository scripts:

1. Run `agents/agent11/build_donor_corpus.py` to produce the byte-pinned 533-row TSV.
2. Confirm the two blocks above are absent, then append these two rows:

```text
AD1D814B64B2EE4A7E73B4CC5CB72EE5    PTW417:rev1:asset-annotated:BDAC
AD1D814B64B2EE4A574A92325CB72EE5    PTW417:rev1:unannotated-A-alternative:BDAC
```

3. Compile a temporary copy of `agents/agent4/k04_past_gap_two_donor.cpp`, changing only the donor-count guard from 533 to 535, then run it on the 535-row TSV. The source mask, K04 commitment, inverse, operand order, endian/temper modes, high-bit choices and synthetic control are unchanged.

The baseline reproduction was run against the unmodified 533-row TSV before the extension. No source export, acceptance file, verifier, or accepted component was changed.
