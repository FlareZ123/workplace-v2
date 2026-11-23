# H-17 K08: exact N20 motif correction for the bounded N11 caption model

**23 November 2026, Agent 33. Result: zero original K08 commitment matches.**

## Why this correction was necessary

Agent7's bounded N11 mug-shelf test is a useful complete-output negative, but its second cue is `at the end of the night`. That is not a literal span of Emily's N20 design note. N20 says **`the end of the night`**; the leading `at` appears in N13's separate sentence about the mugs, window and lamp. The original Agent7 result therefore tests a mixed N13/N20 cue set, not three literal N20 motifs.

This test changes only that one source phrase. It does not introduce synonyms, extra cues, or a new base text.

## Exact source-pinned hypothesis

- Base: the 14 normalized words of N11, “Mug shelf”.
- Insert exactly three N20 spans, in N20's stated order: **`the sea`**, **`the end of the night`**, **`the voices at the table`**.
- Retain any order-preserving subsequence of N11, including the empty/full subsequences.
- Place the three spans at any nondecreasing word gaps.
- Total complete phrases: **2,224,128**.
- For each complete phrase, compute HMAC-SHA256 with the original K08 desk nonce, take the first 16 bytes, then SHA256 that 16-byte component and compare to the unchanged K08 commitment.

The reproducible script [`k08_n11_n20_exact_literal_motif.py`](../agents/agent33/k08_n11_n20_exact_literal_motif.py) pins the original CREW4, routing and acceptance SHA256s, checks the exact N02 known-answer, confirms that N20 contains the three literal motifs, and confirms that the extra `at` belongs to N13. It also checks an in-family planted full-caption control.

## Results

| Check | Outcome |
|---|---:|
| Source fingerprints | exact |
| N02 original HMAC16 known-answer | PASS |
| Exact N20 motif source check | PASS |
| N13 “at the end of the night” attribution | PASS |
| Complete assignments | **2,224,128** |
| Planted complete-caption control | **1 exact hit** |
| Original K08 commitment hits | **0** |

The corrected exact-N20 family is therefore also negative. This does not recover K08, authenticate the N11-to-Emily copying hypothesis, or prove that the missing phrase is impossible to derive from the original paper/photo sources.

## Decision

Do not expand the N11 family with invented synonyms or additional motifs. Preserve the original Agent7 result as its own bounded test, but distinguish its N13-derived `at` from N20's literal wording. The productive next input remains an original author-final envelope/margin, native desk/photo-caption source, or versioned source record—not a larger lexical grid.

K01, K02, K03, K05, K06 and K07 remain accepted; K04 and K08 remain missing; REC8/1 remains incomplete.
