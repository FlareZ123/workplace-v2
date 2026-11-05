# H-17 K08: present-tense keeper-caption scene editor, original commitment negative

**Agent 50 | 5 November 2026.** The exact original K08 nonce/HMAC16/full SHA256 commitment was tested against **11,289,600 complete proposed caption assignments**. **Zero** match. The only authenticated recovery remains K01/K02/K03/K05/K06/K07 PASS, K04/K08 missing and combined INCOMPLETE.

## New hypothesis: distinguish authorial *inscription* tense from remembered *scene* tense

The original source's explicitly named complete Emily *draft inscriptions* use present/habitual voice:

- N02 first crew-board draft: "A good watch leaves the room ready for the next pair of hands."
- N06 second desk draft: "The little lamp stays on until the corridor has gone quiet."
- N17 older standby label: "Leave the light on for the next watch."

By contrast, Emily's N13 retrospective scene description places the mugs and lamp in the past. N20 specifies sea/end of night/voices-at-table **themes**, while MAIL-11 describes making room for one another after a long watch. None quotes the final N23 margin. The tested hypothesis is that the keeper inscription could be written as a concise **present-tense, habitual statement** about these three themes.

This is a different full-text candidate family from [Agent35's 12.86-million past-tense three-clause scene search](h17-agent35-source-coupled-producer-frontier-20261104.md), and different from [source-word Levenshtein radius two](h17-k08-source-word-edit-radius-two-20261103.md) or arbitrary ordered note-word products. Its present-tense formulation is based on the actual grammatical distinction between N02/N06 and N13. It remains a **hypothetical editor**, without an author-final verbatim witness.

## Frozen complete-candidate grammar

All candidates are lowercase ASCII with single spaces and therefore already satisfy the original punctuation/whitespace normalizer.

- Outside/sea: **30** complete present-tense clauses, e.g. `the sea is outside`, `the sea waits outside`, `the water is still there`.
- Night/watch: **24** present-tense clauses, e.g. `the night is nearly over`, `morning is coming`, `the last cup is empty`.
- Inside/table/room/lamp: **40** present-tense clauses, e.g. `there is room at the table`, `the voices stay at the table`, `we leave the lamp on`.
- Eight original-source-plausible connectors `and, but, while, as, when, with, even as, and still`.
- All **six** assignments of the three scene roles to clause order and **two independently selected connectors**.
- A different **temporal-adjunct** program: 12 time/place prefaces, each combined with one outside clause and one inside clause in both orders and any of the same eight connectors.

The exhaustive finite test checks
`6 × 30 × 24 × 40 × 8² = 11,059,200` three-clause assignments, plus
`2 × 12 × 30 × 40 × 8 = 230,400` temporal-adjunct assignments, or
**11,289,600 complete candidate assignments** total. Uniqueness across programs is not claimed. This grammar explicitly explores a tense not used in the earlier past-tense scene report; it makes no claim to cover unrestricted English or the actual author-final line.

Every full candidate computes `HMAC_SHA256(original_16byte_desk_nonce, candidate)[:16]`; the full SHA256 of those sixteen component bytes is compared against untouched original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. The source crew-note SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` and previously independently calculated original N02 HMAC16 `BF889359B0303F2B2B2FD96AE841210B` are asserted before any candidate iteration.

## Execution and controls

The source-pinned [C++17/OpenSSL reproducible SFT](../agents/agent50/k08_present_habitual_scene_sft.cpp) ran on the original 46-file attached source copy's crew notes. The executed local implementation reported:

```text
K08_PRESENT_SCENE_COMPLETE source_SHA_PASS original_N02_HMAC_PASS triples=11059200 temporal=230400 tested=11289600 original_hits=0 synthetic_hits=1 seconds=18.1857
```

A full original pipeline *planted* positive `the sea is outside while there is room at the table and the night is almost over` was recovered exactly once under an independent synthetic K08 commitment; this verifies enumeration and reduction. It is a **synthetic control, not the true K08 caption**. No original inputs, verifier, acceptance or candidate were edited.

## Interpretation and next decision

The source supports both Emily's grammatical voice and scene themes but gives **zero attested words of the final N23 margin**. This new present-tense and temporal-adjunct family is excluded by the original commitment. Its negative result is conditional on the 30/24/40 chosen clauses and the fixed grammar; it does not disprove a shorter inscription, an imperative, a multi-verse metaphor, or any different original wording. Avoid an automatic expansion of another phrase lottery. The highest-value next discriminator is an independently preserved final envelope/desk-margin text, a specific editorial rule grounded in an original version, or an authentic photograph-caption history that identifies the words actually printed.

K04 physical coupon remains unauthenticated; there is no new seventh/eighth PASS or complete REC8 key.
