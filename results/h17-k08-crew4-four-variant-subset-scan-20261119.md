# K08 CREW4 four-variant subset sensitivity scan

**Status:** reproducible upstream sensitivity component; not a full-chain null and not a calibrated global p-value.

## Question

Does the observed `CREW4` author-code output remain unique when the four obvious base/bit-order variants are all scanned over the complete 8-of-24 position-subset space, and does the subsequent one-row `+1` text bridge still isolate the observed `ATEALBIT / ALOWBIT` output?

This extends the fixed-`A0_LSB` conditional author-label null in `agents/agent9/k08_crew4_author_null.py`. It is intended as an upstream component for the end-to-end null requested in the current K08 review, not a replacement for it.

## Source and method

Source: `resources/evidence/crew/noticeboard-and-desk-notes.txt`

SHA-256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`

The source has exactly N01–N24. The fixed observed first-appearance author order is:

`Jason, Emily, Zoey, David, Gabriel, Simon`.

For each of the four variants A0_LSB, A0_MSB, A1_LSB, and A1_MSB, enumerate every possible 8-position subset of the 24 notes as the Emily indicator vector. Each variant therefore has `C(24,8) = 735,471` subsets.

For every subset that decodes to `CREW4`, enumerate all valid one-row `+1` edits that preserve sorted, unique note IDs. For each edit, reproduce the existing bridge:
- `ATEALBIT`: first-letter initials of the eight selected note bodies;
- `ALOWBIT`: first initial + the A0 word-count letters at positions 2–4 + initials at positions 6–8.

The tokenizer is the existing hyphen-preserving ASCII word tokenizer `[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?`.

Reproducible script:

`agents/agent35/k08_crew4_four_variant_subset_scan.py`

Run:

```bash
python agents/agent35/k08_crew4_four_variant_subset_scan.py
```

## Results

| Variant | CREW4 subsets |
|---|---:|
| A0_LSB | 1 |
| A0_MSB | 1 |
| A1_LSB | 0 |
| A1_MSB | 0 |
| **Total variant/subset hits** | **2** |

The two `CREW4` subsets are:

- **A0_LSB:** N02, N06, N10, N13, N17, N18, N20, N23 — the observed Emily positions.
- **A0_MSB:** N04, N06, N10, N13, N16, N18, N19, N22 — an alternate bit-order control subset.

Each hit has seven valid one-row `+1` edits. Across all edits for both subsets, exactly one produces both downstream strings:
- variant: **A0_LSB**;
- edit: **N10 → N11**;
- selected notes: N02, N06, N11, N13, N17, N18, N20, N23;
- initials: **ATEALBIT**;
- A0 word-count letters: **NLOWIF?V**;
- derived instruction: **ALOWBIT**.

The A0_MSB `CREW4` subset has no valid `+1` edit that produces both strings.

Thus the exact bridge survives the four-variant subset sensitivity scan: **2 CREW4 hits, but only 1 full ATEALBIT/ALOWBIT bridge hit** across 2,941,884 variant/subset pairs.

## Interpretation and limits

This is a useful upstream filter: the A0_MSB alternative creates a second `CREW4` hit, but it does not survive the observed one-row `+1` and text bridge.

Do **not** report `1 / 2,941,884` as a global p-value. The scan holds the observed first-appearance author codebook fixed and tests only four base/bit-order variants and `+1` edits. It does not randomize the author-label codebook itself, grouping/tail conventions, edit direction, tokenizer, or downstream component/half/bit-order/bookmark/transfer choices. It is not the full-chain null.

## Handoff

Agent22 can use these exact counts as one upstream branch in the joint benchmark. The full-chain null must still rerun all source-preserving upstream choices and the exact downstream endpoint together; do not multiply this subset count by stage-wise rates. The result does not recover K08 and does not change any accepted component.
