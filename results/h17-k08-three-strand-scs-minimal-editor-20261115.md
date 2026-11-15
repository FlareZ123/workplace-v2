# H-17 K08: three-strand minimum caption merge, 15 November 2026

**Agent43. Original K08 commitment: no match.** This is one bounded, source-derived exploratory complete-caption producer, tested in two predeclared third-strand variants. It does not recover K08 and does not identify historical final wording.

## Model and source anchors

The recovered crew source `resources/evidence/crew/noticeboard-and-desk-notes.txt` includes three roles: (a) N01 Jason's photograph caption with **sea**; (b) N13 Emily's scene with the contiguous **end of the night**; (c) a people-at-table caption, either **N20** Emily's editorial phrase `voices at the table`, or **N09** Zoey's galley-board `cup alone`.

The earlier [two-strand interweaving](h17-k08-photo-desk-word-interweave-20261106.md) merges two roles, while the [N01/N13/N09 source-clause join](h17-k08-n01-n09-n13-subclause-join-20261113.md) concatenates three spans without arbitrary three-way interleaving. The present mechanism tests a **three-source shortest common supersequence (SCS)**: retain all selected source words in their order; whenever two or three next words are identical, consume them together, writing one copy; otherwise emit one of the available next words while preserving the shortest possible output length. This generates complete strings that those specific predecessors cannot construct. It is a testable editorial compression conjecture, not a documented action by Emily.

Inputs are selected and fixed before querying the K08 target. Use ASCII alphanumeric lowercase tokenization. N01 supplies all distinct 2–6-word contiguous spans containing `sea` (10 spans). N13 supplies all 4–8-word spans containing the exact consecutive `end of the night` (12 spans). The third strand is either:

| Third source | Exact motif | Span lengths | Distinct spans | Triple selections | Maximum complete phrase length |
| --- | --- | --- | ---: | ---: | ---: |
| N20, Emily editorial statement | `voices at the table` | 4–8 | 15 | 1,800 | 15 words |
| N09, Zoey galley caption | `cup alone` | 3–7 | 19 | 2,280 | 14 words |

For every triple, enumerate every **minimum-length order-preserving three-way merge** at or below the maximum length. The implementation uses memoized exact SCS length on (i,j,k) positions and recurses only through transitions reducing that length by one. Duplicated full text from different source-span selections is counted again as a distinct *assignment*; the reported totals below are assignment counts, not claimed distinct normalized captions.

## Source controls and original result

All input hashes are verified before text selection:
- Crew notes SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- Route SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- Acceptance SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

The original route reduction is `SHA256(HMAC_SHA256(desk_nonce, normalized_phrase)[:16])`; nonce `5F933DA6A1BD03C32DA5CBC25344F497`; original unchanged K08 SHA commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. The known original N02 caption independently reproduces K08-component HMAC16 `BF889359B0303F2B2B2FD96AE841210B`. Each complete scan also finds an independently planted in-family positive.

| Third source | Original complete assignments checked | Historical K08 matches | Planted positive |
| --- | ---: | ---: | ---: |
| N20 editorial | **21,743,888** | **0** | **1** |
| N09 galley | **35,071,612** | **0** | **1** |
| **Total** | **56,815,500** | **0** | 2 |

Both exhaustive bounded variants were executed locally on 15 November with the **original ZIP-extracted 46-file source**, the same source hashes and unchanged K08 commitment. Initial shorter pilots were 13,045 N20 and 52,006 N09 assignments with no target hit, before running the full domains. No sources, candidate, official verifier or acceptance commitments were edited.

**Portable source-pinned reproducer:** [`agents/agent43/k08_three_strand_scs_sft.py`](../agents/agent43/k08_three_strand_scs_sft.py). It uses Python standard library only and accepts `--human-role editorial --max-words 15` or `--human-role galley --max-words 14`. The script checks the expected 21,743,888 and 35,071,612 counts and planted positive before reporting. Production source and selected output text are constrained to the exact original-role fragment families specified above.

## Meaning

These negatives rule out precisely this **three-way minimal order-preserving phrase merge** of the three specified roles, within the selected source-span and complete-caption length bounds. They do not refute longer phrases, nonminimal merges, different original inputs, textual revisions, or a newly discovered final inscription. The model is speculative and yielded no authenticated K08 words. Do not simply broaden max length or add arbitrary vocabularies without another causal clue.

K04 remains an unresolved selected physical coupon. The original six accepted slots remain PASS; K04/K08 are missing; combined REC8/1 is INCOMPLETE.