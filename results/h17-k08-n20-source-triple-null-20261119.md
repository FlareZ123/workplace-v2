# N20 source-triple calibration control (19 November 2026)

**Status:** exact source-wide control for the N20 positional decoder. This strengthens the source calibration of the LOW BIT route but does not recover the final envelope wording.

Reproducer: agents/agent9/k08_n20_source_triple_null.py

## Frozen corpus and operation

The script pins all 20 mail messages, the 24-note file, and the authoritative recovery-routing JSON. It tokenizes each email body and every string value in the routing file with the same ASCII word tokenizer used in the existing N20 SFT.

For every contiguous three-word window, it applies the established ASCII-character-LSB selector to each word. Windows whose three selectors all fall within N20's one-based word range are then used to index N20. No source phrase is selected manually. The JSON output retains every one of the 1,054 valid source windows, not just the two target hits.

## Result

| Corpus | Contiguous 3-word windows | Valid N20-index windows |
|---|---:|---:|
| All 20 email bodies | 961 | 961 |
| All routing-file string values | 93 | 93 |
| **Total** | **1,054** | **1,054** |

Exactly **two of 1,054** source windows map to the exact N20 phrase “end of the”:

| Source | Literal source triple | LOW BIT indices | N20 output |
|---|---|---|---|
| MAIL-11 | long watch with | 10, 11, 3 | end of the |
| K08 route / rule | late watch rather | 10, 11, 18 | end of the |

Separately, applying the fixed selectors 12,10,11 to every one of the 24 note bodies yields “the end of” only for N20.

## Interpretation

This is a meaningful positive control for the N20 indexing rule. The two source-ordered prose triples independently calibrate the same positions from distinct carriers, and no other contiguous three-word window in the full mail/routing corpus reproduces the exact target phrase. It materially strengthens Agent43's N20→N23 route beyond an isolated positional coincidence.

It remains a **stage-specific** control: it does not establish that all subsequent WRAP/SEAT/SEATS transformations are equally selective, does not identify the final inscription, and must not be multiplied by the author/component/transfer probabilities as if the tests were independent. The original N23 margin/envelope wording is still absent.
