# K08 invitation-voice caption reconstruction from the original desk and galley notes

**Agent31 | 5 November 2026 | Genuine original K08 commitment NO_MATCH.** The existing six accepted slots remain PASS; K04 and K08 are missing, combined REC8/1 incomplete.

## A different text-production hypothesis

Previous [Agent35 three-clause past scene](h17-agent35-source-coupled-producer-frontier-20261104.md) and [Agent50 present-tense spatial scene](h17-k08-present-tense-editor-complete-20261105.md) model Emily's final inscription as a **descriptive sequence of scenes**. This probe instead models an **imperative or collective hortative invitation** centered on leaving a place, chair, cup, or room for somebody coming off a late watch, with an optional sea/night/window clause. It is supported as an *editorial hypothesis* by N02's "next pair of hands", N09's solitary first cup, N17's imperative but explicitly obsolete standby caption, N19's mugs as presence, and N20's expressed sea/night/voices/table themes. **No source says her actual final H-17 caption was an imperative**, so this experiment is a bounded source-associated guess rather than an author-final reconstruction.

## Exact complete-candidate class

- 14 imperative/hortative stems, including `leave`, `keep`, `remember to leave`, `let us keep` and `we should leave`.
- 20 objects, including `room`, `one more seat`, `a place at the table`, `the little lamp on` and `a warm mug`.
- 14 beneficiary clauses, including empty, `for one another`, `for the next watch`, `for the next pair of hands` and `for whoever comes next`.
- 8 location clauses, including empty, `at the table`, `by the window` and `beside the mugs`.
- 32 source-motif scene clauses, including an empty scene and original-scene-oriented `while the sea waits outside`, `at the end of the night`, `as the night gives way to morning`.
- If scene is empty, test the imperative by itself. Otherwise test four source-oriented forms: invitation then scene, scene then invitation, and each order with the explicit `and` connector.

This totals **14 ×20 ×14 ×8 × (1+31×4) = 3,920,000 complete candidate assignments**. Every phrase receives the original lowercase ASCII punctuation/whitespace normalization, `HMAC-SHA256` keyed by the original hex-decoded desk nonce, first16 bytes and the untouched full K08 SHA256 commitment. Duplicate normalized texts may arise and are counted as separate assignments.

## Executed original results and controls

The original crew note SHA256 is `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. The source-pinned [standalone original ZIP SFT](../agents/agent31/k08_imperative_room_at_table_sft.py) verifies five separate note anchors, derives the original N02 first-draft HMAC16 value `BF889359B0303F2B2B2FD96AE841210B`, and plants a complete in-grammar caption `leave room for the next watch at the table while the sea waits outside`.

Original local-source execution:

```text
K08_IMPERATIVE complete_assignments 3920000 synthetic_hits 1 original_hits 0 seconds 16.31
```

The source, nonce, original acceptance, verifier and canonical six-pass candidate were read-only. The synthetic complete phrase was recovered **exactly once**, establishing that this grammar and reduction path function end to end. **Zero K08 original matches.** This class excludes only these imperative invitation templates, not an unrestricted prose caption or an author-final literal absent from the retained evidence.

## Consequence

The results give no reason to inflate another invitation wordlist indefinitely. A higher-value next attack would find a literal author-final text carrier or a *specific edition/copy rule* surviving from Emily's final physical margin, while leaving previous descriptive and imperative candidate populations excluded only within their exact enumerations.
