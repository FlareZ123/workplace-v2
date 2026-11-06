# K08: authentic selected-draft holdout veto on cross-crew one/two-new-bigram editor models

**Agent2 | 6 November 2026 | Original-source, entire-caption withholding | four genuine historical captions lie OUTSIDE the proposed grammar.**

## Why this matters more than another hash search

The 6 November 20:55 [Critic's selected-object intervention](../communications/broadcast/20261106T2055Z_Critic_selected-object-prediction-over-search-volume.md) correctly notes that the new 465.49m one-edge and 393.46m two-edge searches have only *synthetic* positive controls, which prove algorithmic search completeness but do not show the modeled edit process predicts a genuine historical **selected caption**. We therefore made the closest original real-text holdout the *next experiment*, with full target text hidden from candidate-graph formation.

There is no surviving exact final K08 object to use as an authentic selected-final holdout. What survives in the same official source are N02 Emily first draft, N06 Emily second draft, N17 standby-envelope label, and N18 commissioning-envelope label. They are **different historic caption versions** with whole original wording independently present. They do not establish the same generative process as the final. Withhold one entire target note at a time from the graph's word and bigram inventory, then measure whether its authentic full caption could even belong to either previously tested search grammar. This tests **eligibility**, not a blind rank or full-text recovery; ineligible complete labels cannot be recovered by the search algorithm regardless of search power.

## Original source and predeclared predicates

Input unmodified `resources/evidence/crew/noticeboard-and-desk-notes.txt` SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. For each held-out note, normalize its entire actual inscription following the original colon, then build a **separate** 23-note word set and original directed-bigram set excluding that entire note's body.

Compute four quantities before any hash: complete target length; all three required scene-theme groups (sea/water, night/watch/morning, room/voices/table/people); novel source word types that do not occur in any of the other 23 notes; and number of target bigram occurrences absent from the other 23 notes. One-edge model requires 6..12 words, all three motifs, **zero** novel words and exactly one absent source-bigram occurrence. Two-edge model requires 6..9 words, all three motifs, zero novel words and exactly two absent source-bigram occurrences.

## Authentic, complete historical holdouts

| Entire historic selected caption | Words | Present motif groups (sea/night/room) | OOV word occurrences | Previously unseen adjacent-pair occurrences | Eligible one-edge / two-edge |
| --- | ---: | --- | ---: | ---: | --- |
| N02, first draft | 13 | no / yes / yes | 5 | 10 | **no / no** |
| N06, second draft | 11 | no / no / no | 4 | 8 | **no / no** |
| N17, actual standby label | 8 | no / yes / no | 1 | 4 | **no / no** |
| N18, actual commissioning label | 5 | no / no / no | 0 | 4 | **no / no** |

The independently source-recorded original N02/N06 and distinct N17/N18 are legitimate complete historical wording references, but **none passes the structural gate of either crosscrew editor** after its own source line is withheld. The known N02 caption, for example, needs five word occurrences not preserved anywhere in the 23 surrounding notes and ten genuinely new adjacent pairs; an operation that allows only one or two new bigrams cannot reproduce it. N06 similarly uses novel words `stays`, `until`, `corridor`, `quiet` absent from all other notes. All four also miss the later N20 triad motif gate in at least one position.

A local read-only Python 3 original-source calculation produced these exact numbers. [Permanent source-pinned single-file implementation](../agents/agent2/k08_crosscrew_authentic_holdout_eligibility_sft.py) reproduces the analysis with explicit original SHA verification and all 24 note ID assertions; it does not modify sources.

## Consequence and limits

**No authentic available historic selected wording is usable as a positive missingness-matched holdout for either editor family.** These two tested grammars cannot reconstruct the actual N02/N06 draft outputs from the other surviving notes, so their source-grounded *selection-stage predictive performance* is unestablished, regardless of tens or hundreds of millions of synthetic-controlled hash checks. This does **not** mean the unknown final was impossible under the grammar. N20 describes later final themes, while N02/N06 prefinal outputs understandably lack all three motifs. The holdouts reveal that there is no calibration matching the full final selection stage in the retained source.

**Decision:** Stop multiplying graph-walk candidates after these finite negatives. To advance K08, acquire a true author-final word source or identify a new source-version transformation that exactly recovers at least one authentic held-out whole caption from eligible historical ancestors, before targeting the missing final margin. The K04 original printed coupon has a separate absent-media problem requiring its own independent physical source/producer witness.

Original K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined REC8/1 INCOMPLETE.
