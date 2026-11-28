# K08: 13-word position-aligned source editor is commitment-negative

**Agent 14 | 28 November 2026 | complete-output editor falsification | no recovered K08 component**

## Question

The 28 November AT/MT/ET/PT chain now fixes a complete 13-word N20 semantic payload with a source-visible stop. Can the missing author-final wording be a literal position-wise edit among same-length antecedents that the surviving records independently identify as desk/photo/galley wording inputs?

This is a complete-output test, not another note selector or synonym grammar.

## Frozen source rows

Before consulting the K08 acceptance result, use four 13-token rows from the unchanged crew-note source:

1. **N02** — Emily's explicitly labelled first draft for the crew board.
2. **N08** — the window photograph caption, carrying the water/outside image class.
3. **N09** — the galley-board caption, carrying the social/late-night cup image class.
4. **P20** — the exact 13-token N20 motif payload fixed independently by the 28 November AT/MT/ET/PT overlap/transfer chain and its PT prohibition boundary.

MAIL-11 independently says that Emily worked out the keeper wording from desk notes and photograph captions, and describes the intended social handoff after a long watch. That makes a literal crossover among these fixed rows a source-shaped authoring hypothesis. The source does **not** say that Emily actually edited by aligned word columns, so the result below is a bounded falsification of this editor, not evidence for the historical process.

Pinned crew-note SHA-256:

`13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`

The P20 normalized-payload fingerprint is pinned in the reproducer rather than printed here. Candidate wording, nonce and target diagnostics are not emitted.

## Exact editor and denominator

All four rows have exactly 13 normalized tokens. At each token position 1..13, choose the token from any one of the four rows, preserving column position and emitting exactly 13 tokens.

That is exactly:

- **4^13 = 67,108,864 source-row assignments**;
- **25,165,824 distinct normalized captions**, because eleven columns have four distinct tokens, one column has three and one has two.

No synonyms, insertions, deletions, reordering, free joiners or target-driven lexical choices are allowed.

Every complete candidate is reduced through the unchanged K08 normalization/HMAC16/SHA256 acceptance rule from the preserved route and acceptance files.

## Controls

The standalone reproducer checks:

- the crew-note source SHA;
- all four 13-token invariants;
- the independently fixed P20 payload fingerprint;
- the known historical N02 first-draft HMAC16 fixture;
- one deliberately planted in-family complete caption whose selected token is unique in every column. The exhaustive search recovers that planted commitment **exactly once**.

The historical N02 fixture validates the original reducer. The plant validates the full enumeration. There is no independently surviving author-final version pair that calibrates aligned crossover as Emily's actual editing rule.

## Original result

Executed locally against the unchanged original source:

```text
K08_ALIGNED4 assignments=67108864 original_hits=0 planted_hits=1 historical_n02_control=PASS source13=PASS
```

Runtime on the available 4-core OpenMP execution was about 25 seconds. **No original K08 commitment match exists anywhere in this complete editor family.**

## Prior-art boundary

Repository search finds earlier photo/galley clause splices and broad source grammars involving N02/N08/N09, including the 16.3M photo-triptych family and larger clause editors. Those concatenate selected spans and connectors. No prior result found a position-aligned N02/N08/N09/P20 13-column crossover or the exact domain above.

The natural three-row N02/N09/P20 crossover tested during development is a strict subset of this four-row run and should not be counted separately.

## Consequence

This closes a concrete interpretation of MAIL-11's “making room”/draft-and-caption provenance: the author-final line is not obtained by choosing one source word per aligned position across these four fixed 13-token rows.

The result does **not** weaken the deterministic P20 payload or prove that P20 is the historical final-editor input. It instead removes one complete-output editing mechanism. The useful next K08 experiment must change the authoring operation itself — for example a source-selected reordering/version transform — rather than enlarge the same aligned columns with synonyms or arbitrary extra rows.

K01/K02/K03/K05/K06/K07 remain accepted; K04 and K08 remain missing; REC8/1 remains incomplete.

## Reproducer

`agents/agent14/k08_13word_aligned_source_editor_sft.cpp`

Build with C++17/OpenMP and OpenSSL libcrypto, then pass the extracted `resources`-style root containing `evidence/` and `acceptance.json`.
