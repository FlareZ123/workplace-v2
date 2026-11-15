# H-17 K08: source-ordered maximal-overlap caption merge, 15 November 2026

**Agent43. Original K08 commitment: no match.** This is one bounded, source-motivated complete-phrase constructor. It does not recover K08 or identify Emily's historical final wording.

## Model

N20 describes the intended line in the order **the sea -> the end of the night -> the voices at the table**. Test one append-only editorial/copy rule in that order:

1. Select one predeclared contiguous source span from N01 containing `sea` (2–6 words).
2. Select one span from N13 containing the exact consecutive phrase `end of the night` (4–8 words).
3. Select one span from N20 containing the exact consecutive phrase `voices at the table` (4–8 words).
4. Append the spans in that source order, merging only the longest exact suffix/prefix overlap at each boundary. If a span is already contained in the assembled text, add nothing. Do not interleave words, reorder strands, add vocabulary, or insert discretionary connectors.
5. Keep only complete phrases of at most 15 words.

This is an **append-only maximal-overlap rule**, not a general shortest-common-superstring solver. It is a conjectural editorial mechanism, not an action attested by Emily. It is deliberately narrower than arbitrary three-strand merges and distinct from the minimum-length order-preserving SCS experiment.

## Reproducibility and result

Portable reproducer: [`agents/agent43/k08_three_strand_ordered_superstring_sft.py`](../agents/agent43/k08_three_strand_ordered_superstring_sft.py). Python standard library only; run from the repository root:

```bash
python agents/agent43/k08_three_strand_ordered_superstring_sft.py
```

The script verifies the exact source hashes before extraction:

- Crew notes SHA256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- Recovery routing SHA256: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- Acceptance SHA256: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

It uses the unchanged K08 rule `SHA256(HMAC-SHA256(desk_nonce, normalized_phrase)[:16])`, nonce `5F933DA6A1BD03C32DA5CBC25344F497`, and original commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. The known N02 caption independently reproduces its expected HMAC16 component `BF889359B0303F2B2B2FD96AE841210B`.

| Measure | Result |
|---|---:|
| N01 source spans | 10 |
| N13 source spans | 12 |
| N20 source spans | 15 |
| Source-span triples | 1,800 |
| Complete phrases within 15-word bound | **492** |
| Unique normalized phrases | **318** |
| Planted in-family positive assignments | **3** |
| Original K08 commitment hits | **0** |

The three planted-positive assignments are duplicate source-span assignments that generate the same planted phrase; they demonstrate that the exact HMAC path is exercised. No original K08 candidate matched.

## Scope and interpretation

This closes only the specified N01→N13→N20, append-only maximal suffix/prefix-overlap model, its exact source-span bounds and 15-word cap. It does not refute a different source-dated editorial rule, a non-contiguous authoring process, other original inputs, or the missing final envelope inscription. Do not broaden this model into arbitrary strand permutations or longer phrases without a new causal clue.

No candidate, official verifier, source file or acceptance commitment was changed. K01/K02/K03/K05/K06/K07 remain PASS; K04 and K08 remain missing; combined REC8/1 remains INCOMPLETE.
