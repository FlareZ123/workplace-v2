# K08: Prufrock literal and one-source-word adaptation exclusion

**Agent 40 | 11 November 2026 | bounded original K08 commitment test, zero matches.**

## Why this source was tested

A previously untested literary-source hypothesis emerged from the semantic overlap between Emily's surviving K08 material and T. S. Eliot's 1915 *The Love Song of J. Alfred Prufrock*. The poem contains, in close concentration, evening/night imagery, window panes, hands, a room, a table, tea/cups, lamplight, the sea and voices. Those motifs overlap the independently preserved N02/N06/N10/N13/N20 and MAIL-11 descriptions closely enough to justify a finite literal/allusion check.

Repository searches in both workplace-v1 and workplace-v2 returned no prior Prufrock/Eliot K08 experiment. The supplied H-17 source itself contains no `eliot`, `prufrock`, `michelangelo`, `coffee spoons`, `human voices` or `chambers of the sea` literal, so this remains a literary hypothesis rather than a source-authenticated provenance claim.

Text source used for the experiment: University of Virginia, Literature in Context, first-publication transcription from *Poetry* (1915), https://anthology.lib.virginia.edu/work/Eliot/eliot-prufrock. The experiment retained 131 numbered poem lines and 1,063 normalized body words, excluding the Italian epigraph, title and attribution.

## Exact K08 route

The unchanged H-17 route was used: lowercase, replace non-ASCII-alphanumeric/non-whitespace with spaces, collapse whitespace, HMAC-SHA256 under decoded desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`, retain the first 16 HMAC bytes, then compare their full SHA256 to K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

### Literal spans

Every normalized contiguous poem word span of length 2 through 64 was tested: **64,953** complete phrases.

Every consecutive poem-line span of length 1 through 12 was also tested after the same normalization: **1,506** complete phrases.

Total literal assignments: **66,459**. Original K08 matches: **0**.

### One-word Emily-source adaptation

To test the stronger "Emily adapted a remembered line" possibility without opening a free-form caption lottery, every contiguous poem span of length 4 through 24 was subjected to exactly one of two operations:

1. substitute one existing poem token with one word from a frozen 36-word K08 source vocabulary;
2. insert one word from that same source vocabulary at one boundary.

The vocabulary was restricted to surviving H-17 K08 cue words from Emily/crew material, including room, watch, hands, lamp, corridor, quiet, photograph, cup/cups, mugs, end, night, window, sea, water, voices, table, light, boat, wording, margin, envelope, crew, one/another/each/other, morning, late, finished, outside, making and place.

Complete one-edit assignments tested: **22,964,760**. Original K08 matches: **0**.

The one-edit runner used precomputed SHA256 HMAC pad states and eight local OpenMP workers. The final corrected normalized poem had exactly 1,063 words. No target prefix or partial digest criterion was used: each candidate received the complete HMAC16 then SHA256 acceptance comparison.

## Result and boundary

This excludes a literal Prufrock quotation within the tested span bounds and the defined one-source-word insertion/substitution adaptation family. It does **not** prove the poem was historically consulted, exclude multiword paraphrase/allusion, or establish any missing K08 word. Because the surviving H-17 export provides no Eliot/Prufrock locator, further transformed-poem brute force is not justified without a new source cue.

K04 and K08 remain unresolved. Six existing REC8 components remain independently accepted; combined recovery remains incomplete.
