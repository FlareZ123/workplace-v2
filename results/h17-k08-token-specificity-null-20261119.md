# K08 A1 / low-bit token specificity benchmark

**Agent:** 9  
**Date:** 19 November 2026  
**Question:** Are the K01 byte-pair A1 coordinates and the C3/M10/P212 low-bit tokens sufficiently unusual to support a workbook-carrier inference?

## Frozen test

Applied one parser without slot-specific tuning to the six accepted 16-byte components in canonical candidate.json:

- Raw A1 pairs: interpret each adjacent byte pair as (row, column) and also report the swapped orientation. A pair is syntactically valid when both bytes are 1..255 (legacy BIFF8 positive row/column range).
- Low-bit pack: take each byte's least significant bit, pack first bit as bit 0 in each eight-bit group, and obtain two output bytes.
- Low-bit A1 parser: accept either fixed orientation, ASCII uppercase A–Z plus a row 1..255, or row 1..255 plus ASCII uppercase A–Z.
- Exact-token panel: C3, M10 and P212, in either byte orientation.

A deterministic null panel used 1,000,000 uniform random 16-byte strings, Python Random seed 20261119. The script is [h17_k08_token_specificity.py](../work/h17_k08_token_specificity.py).

## Observed accepted-component results

All six accepted components have eight syntactically valid raw A1 pairs in both orientations. This is not a discriminator: for a uniform random 16-byte string the exact probability that all 16 bytes are nonzero is (255/256)^16 = 0.9392981; across six independent strings the probability is approximately 0.6868.

The fixed low-bit parser yields only two A1-looking tokens among the six accepted components:

| Slot | Low-bit bytes | A1 token |
| --- | --- | --- |
| K01 | 04 79 | none under uppercase-only rule |
| K02 | F9 61 | none under uppercase-only rule |
| K03 | 25 1C | none |
| K05 | 03 43 | C3 |
| K06 | 83 45 | E131 |
| K07 | 87 CC | none |

K06's E131 is an additional A1-looking token with no source-address interpretation. Under the uniform null A1-token probability, observing at least two such tokens among six is not unusual: P(X >= 2) = 0.3250 for X ~ Binomial(6, 0.1920166).

## Null-panel results

| Statistic | Observed | Exact uniform-null probability |
| --- | ---: | ---: |
| All eight raw pairs valid A1 | 939,543 / 1,000,000 (0.939543) | 0.9392981 |
| Low-bit pair is any A1 token, either orientation | 192,308 / 1,000,000 (0.192308) | 0.1920166 |
| Low-bit pair is A1 with row 1..24 (mail/note-sized) | 19,381 / 1,000,000 (0.019381) | 0.0190430 |
| Exact C3, M10 or P212 token, either orientation | 85 / 1,000,000 (0.000085) | 0.00009155 |

The observed null frequencies agree with the exact probabilities. The K01 observation that all eight byte pairs are valid Excel coordinates is therefore expected under a random-byte null. The fact that a low-bit pair can be read as an A1 cell is also common (about 19.2%). K06's E131 is a useful in-panel false positive.

## Interpretation and limits

- The authentic bookmark to R:/Stores/consumables/mug-stock.xls remains a real source lead.
- The K05 C3 and alternate-stratum M10 equalities remain potentially useful cross-carrier low-bit observations; this benchmark does not falsify the low-bit route.
- The byte-to-cell readings do **not** independently establish that the workbook is the active K08 carrier. C3 and M10 already have archive-address interpretations, and E131 shows that the same parser emits another cell from an accepted component.
- P212 remains a conditional locator from the mixed AX-7782 retry selector, not the committed K07 chain. Its cell/page interpretation is not authenticated.
- WRAPT resembling “wrap text” remains descriptive, not a source-selected workbook-format rule.

The next workbook-specific discriminator remains the pre-registered native-workbook test: preserve native BIFF bytes and sheets; test only C3, M10 and the eight published K01 cells in the fixed row-byte/column-byte orientation; if the eight cells are numeric, test the predicted LSB vector 1,0,1,1,0,0,1,0. Do not switch orientation, sheet, cell surface or coordinate family after failure. No workbook was present in the supplied ZIP or current repository, and no K08 phrase was tested or recovered.
